from xml.dom.minidom import parse
#import xml.etree.ElementTree as ET
import argparse
import logging
from collections import defaultdict
from typing import List, Dict
import math

MAX_HPO_ID = 8999

def prepare_data(xml_input: str) -> Dict:
    document = parse(xml_input)

    diseases = document.getElementsByTagName("Disorder")
    disease_symptom_map = defaultdict(set)
    mn_hpo_id = math.inf
    mx_hpo_id = -1
    for disease in diseases:
        id = disease.getAttribute("id")
        symptoms = disease.getElementsByTagName("HPO")
        vect = [0] * (MAX_HPO_ID+1)
        for symptom in symptoms:
            symp_id = int(symptom.getAttribute("id"))
            vect[symp_id] = 1
            mn_hpo_id = min(symp_id, mn_hpo_id)
            mx_hpo_id = max(mx_hpo_id, symp_id)
            disease_symptom_map[id].add(symp_id)
        logging.info(f"{len(symptoms)} symptoms loaded for disease {id}")

    logging.info(f"{len(diseases)} is loaded, min HPO id is {mn_hpo_id}, max HPO id is {mx_hpo_id}")
    return disease_symptom_map

'''
since disease size is just 4000, do brute force and ranking
input: 
    a list of HPO ids
output:
    a sorted list of (disease, score)
'''
def select_ranking(disease_symptom_map: Dict, hpo_ids:List, top_k: int) -> List:
    ret = []
    for disease_id, associated_hpo_set in disease_symptom_map.items():
        matched = 0
        for hpo_id in hpo_ids:
            if hpo_id in associated_hpo_set:
                matched +=1
        score = matched / len(associated_hpo_set)
        ret.append((disease_id, score))
    ret.sort(key=lambda t: t[1], reverse=True)

    return ret[:top_k]

if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser(prog="mult_class", description="multi-class classification trainer", epilog="")
    arg_parser.add_argument("-i", "--input", required=True)
    arg_parser.add_argument("-o", "--output", required=True)
    args = arg_parser.parse_args()
    logging.getLogger().setLevel(logging.INFO)
    mp = prepare_data(args.input)
    ret = select_ranking(disease_symptom_map=mp, hpo_ids=[64, 67], top_k=10)
    print(ret)

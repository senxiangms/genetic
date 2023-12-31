from xml.dom.minidom import parse
#import xml.etree.ElementTree as ET
import argparse
import logging
from collections import defaultdict
from typing import List, Dict
import math
import os
import json
import sys
import torch
import inspect

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.insert(0, currentdir) 

from ML.model import MultiClassClassifier, input_size, hidden_size, num_classes
import numpy as np

DIR_SLASH = "\\" if os.name == "nt" else "/"

MAX_HPO_ID = 8999

def load_model_from_checkpoint(ckp_path, diseases_meta_path):
    if not os.path.exists(ckp_path):
        return None, None
    
    model = MultiClassClassifier(input_size=input_size, hidden_size=hidden_size, num_classes=num_classes )
    ckp = torch.load(ckp_path)
    model.load_state_dict(ckp)
    model.eval()
    remapping = {}
    
    with open(diseases_meta_path) as fp:
        id_name = json.load(fp)
        ids = []
        for id, name in id_name.items():
            ids.append(int(id))
        ids.sort()
        remapping = {i: id for i, id in enumerate(ids)}
    return model, remapping


def prepare_data(xml_input: str) -> tuple:
    document = parse(xml_input)

    diseases = document.getElementsByTagName("Disorder")
    disease_symptom_map = defaultdict(list)
    disease_signals_map = defaultdict(list)
    disease_meta = {}
    symptom_meta = {}
    mn_hpo_id = math.inf
    mx_hpo_id = -1
    for disease in diseases:
        id = disease.getAttribute("id")
        name_element =  next(element for element in disease.getElementsByTagName("Name") if element.parentNode == disease)
        disease_meta[id] = name_element.childNodes[0].nodeValue

        symptoms = disease.getElementsByTagName("HPO")
        vect = [0] * (MAX_HPO_ID+1)
        for symptom in symptoms:
            symp_id = int(symptom.getAttribute("id"))
            vect[symp_id] = 1
            mn_hpo_id = min(symp_id, mn_hpo_id)
            mx_hpo_id = max(mx_hpo_id, symp_id)
            disease_symptom_map[id].append(symp_id)
            hpo_term_elm = symptom.getElementsByTagName("HPOTerm")
            hpo_term = hpo_term_elm[0].childNodes[0].nodeValue
            symptom_meta[symp_id] = hpo_term

        disease_signals_map[id].append(vect)
        logging.info(f"{len(symptoms)} symptoms loaded for disease {id}")

    logging.info(f"{len(diseases)} is loaded, min HPO id is {mn_hpo_id}, max HPO id is {mx_hpo_id}")
    return disease_symptom_map, disease_signals_map, disease_meta, symptom_meta

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

def select_ranking2(disease_symptom_map: Dict, hpo_ids:List, top_k: int, model, remapping) -> List:
    if model is None:
        return []
    vec = [0.0] * input_size
    for hpo_id in hpo_ids:
        vec[hpo_id] = 1.0
    output = model(torch.tensor(np.array(vec).astype(np.float32)))
    values, indices = torch.topk(output, top_k)
    ret = [ (remapping[id_p], score ) for score, id_p  in zip(values.detach().numpy(), indices.detach().numpy())]

    return ret

if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser(prog="mult_class", description="multi-class classification trainer", epilog="")
    arg_parser.add_argument("-i", "--input", required=True)
    arg_parser.add_argument("-o", "--output", required=True)
    arg_parser.add_argument("-n", "--nodump", type = bool, required=False, default=False, action=argparse.BooleanOptionalAction)
    arg_parser.add_argument("-m", "--modelpath", required=False, default="")
    args = arg_parser.parse_args()
    logging.getLogger().setLevel(logging.INFO)
    disease_symptom_map, disease_signals_map, disease_meta, symptom_meta  = prepare_data(args.input)

    if not args.nodump:
        with open(args.output + DIR_SLASH + "disease_symptom_map.json", "w") as f:
            json.dump(disease_symptom_map, f, indent = 4 )
        #for training
        with open(args.output + DIR_SLASH + "disease_signals_map.json", "w") as f:
            json.dump(disease_signals_map, f, indent = 1 )
        #for UI
        with open(args.output + DIR_SLASH + "disease_meta.json", "w") as f:
            json.dump(disease_meta, f, indent = 4 )
        with open(args.output + DIR_SLASH + "symptom_meta.json", "w") as f:
            json.dump(symptom_meta, f, indent = 4 )
    
    ret = select_ranking(disease_symptom_map=disease_symptom_map, hpo_ids=[64, 67], top_k=10)
    logging.info(f'select_ranking test case: [64, 67]\n return {ret}')
    model, remapping = load_model_from_checkpoint(args.modelpath + "\\model_epoch_10.pt", args.modelpath+ "\\disease_meta.json")
    ret = select_ranking2(disease_symptom_map=disease_symptom_map, hpo_ids=[64, 67], top_k=10, model=model, remapping=remapping)
    logging.info(f'select_ranking2 test case: [64, 67]\n return {ret}')

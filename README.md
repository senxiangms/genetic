# genetic

## Installation

git clone https://github.com/senxiangms/genetic.git

cd genetic

pip install -r requirements.txt

## Start backend http api service

cd djservice

python manage.py runserver --noreload

## Test 

open http://localhost:8000/classify/diagnose to test diagnose API interface through browser. 

here is one test case to fill in content textbox: {"hpo_ids": [64, 67]}

#You will get top 10 disorder Ids and ranking score in json format.
like :
{"disorder_ids": [["535", 0.25], ["1199", 0.14285714285714285], ["11925", 0.14285714285714285], ["12674", 0.14285714285714285], ["3143", 0.13333333333333333], ["12675", 0.13333333333333333], ["11689", 0.125], ["20867", 0.125], ["12668", 0.11764705882352941], ["498", 0.1111111111111111]]}

## run web frontend.

cd front_end\assistant

npm install 

npm start

open http://localhost:3000/, check some symtoms, click Diagnose. then you will see top possbile diseases


## train a multiclass classifier, and do scoring

1. preprocess raw data

python djservice\libs\multi_class.py --input orphadata.org_data_xml_en_product4.xml --output .\

#you will get disease_signals_map.json in .\

2. run trainer for at least 10 epochs

python djservice\libs\ML\train.py --input disease_signals_map.json --output djservice\libs\ML\ckpt\

you will find checkpoints in djservice\libs\ML\ckpt\.model_epoch_10.pt


3. inference test

python djservice\libs\multi_class.py --input orphadata.org_data_xml_en_product4.xml --output .\ --nodump --modelpath .\djservice\libs\ML\ckpt\

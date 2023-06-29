# genetic

git clone https://github.com/senxiangms/genetic.git

#start backend http api service
cd djservice

python manage.py runserver

#open http://localhost:8000/classify/diagnose to test diagnose API interface through browser. 
#here is one test case to fill in content textbox.
#You will get top 10 disorder Ids and ranking score in json format.
like :
{"disorder_ids": [["535", 0.25], ["1199", 0.14285714285714285], ["11925", 0.14285714285714285], ["12674", 0.14285714285714285], ["3143", 0.13333333333333333], ["12675", 0.13333333333333333], ["11689", 0.125], ["20867", 0.125], ["12668", 0.11764705882352941], ["498", 0.1111111111111111]]}

#run web frontend.
cd front_end\assistant
npm start

#open http://localhost:3000/, check some symtoms, click Diagnose. then you will see top possbile diseases

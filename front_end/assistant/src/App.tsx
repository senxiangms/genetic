import React, { useState } from "react";
import logo from './logo.svg';
import './App.css';
import symptom_meta from './symptom_meta.json'
import disease_meta from './disease_meta.json'
import { text } from "stream/consumers";

const TextComponent = ({diseases, onChange}) =>{
  return (<div><textarea  className="text-area" id="outputText" value={diseases} onChange={(e)=>onChange(e)}/></div>)
};

const CheckboxComponent = ({ list, onChange }) => {
  return (
  <div>
  {
    list?.map((item, index) => (
      <div key={item.id}>
        <input
          style={{ fontStyle: "normal"}}
          type="checkbox"
          id={item.id}
          value={item.name}
          checked={item.isAdded}
          
          onChange = {(e)=> onChange(e, item, index)}
          />
    
      <label  htmlFor={item.id}> {item.id}. {item.name}
      </label>
  </div>
  ))}
  </div>
  );
  };


function App() {
  var symptoms = []
  var top_k = 20
  for (let k in symptom_meta) {
    symptoms.push({id: k, name: symptom_meta[k], isAdded: false})
    top_k = top_k - 1
    if (top_k == 0) break
  }
  //console.log(symptoms)
  const [focusArea, setFocusArea] = useState(symptoms);
    const handleOnChange = (event, option, index) => {
       const values = [...focusArea];
       values[index].isAdded = event.target.checked;
       setFocusArea(values);
    };

  var disorder_names = []
  const  [diseases, setDiseases] = useState(disorder_names)
  const handleOnChangeOutput = (event) =>{
      console.log("handleonChangeoutput")
      setDiseases(diseases)
  };
    const diagnoseClick =  (event) => {
      
      var selected = []
      focusArea.forEach(x=>{if (x.isAdded) selected.push(parseInt(x.id))})
      
      var body_str = "{\"hpo_ids\":" + JSON.stringify(selected, null, 4) + "}"
      console.log(body_str);
      //var idScores = []
      
      fetch('http://127.0.0.1:8000/classify/diagnose', 
        { method: 'POST', headers: {'Accept': 'application/json', 'Content-Type': 'application/json'}, body: body_str})
          .then(response => response.json())
          .then(data => {
            var outtext = "" 
            data['disorder_ids'].forEach(x => {
              diseases.push(disease_meta[x[0]]+"\n"); 
              outtext = outtext + "\n " + disease_meta[x[0]]
              })
            var textarea_elm = document.getElementById("outputText"); 
            textarea_elm.innerHTML = outtext
            })
      }

  return (
    <div className="App">
      <header className="App-header">
        <img src={logo} className="App-logo" alt="logo" />

        <button onClick={diagnoseClick}>Diagnose</button>
          <TextComponent 
            diseases={diseases} 
            onChange = {(e) => handleOnChangeOutput(e)} />
          
          <CheckboxComponent
            list = {focusArea}
            onChange = {(e, item, index) => handleOnChange(e, item, index)}
            
          />
          <p>
          Edit <code>src/App.tsx</code> and save to reload.
          </p>
        <a
          className="App-link"
          href="https://reactjs.org"
          target="_blank"
          rel="noopener noreferrer"
        >
          Learn React
        </a>
      </header>
    </div>
  );
}
  
export default App;

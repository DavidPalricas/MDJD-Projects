import json
import xml.etree.ElementTree as ET
from web_app_conextions_files.conextion_config import *
import asyncio
import websockets
from consts import HOST
from web_assistant.assistant import Assistant
from web_assistant.index import Index

def nlu_extractor(message, assistant):
  """
  The nlu_extractor exctracts the nlu from the websocket's message
  
  Args:
    message (str): The message received from the websocket

  """ 
   # Find all the command tags in the message
  comand_tags = ET.fromstring(message).findall(".//command")
   
   # Removes the text from the comand tag 
  message = json.loads(comand_tags.pop(0).text)

  modality = message["recognized"][0]

  print(f"modalityyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy: {modality}")

  if modality == "SPEECH":
    nlu = json.loads(message["nlu"])

    print(f"nlu: {nlu}")

    if "entities" not in nlu or len(nlu["entities"]) == 0:
      return assistant.speech_action({"intent": nlu["intent"] ["name"]})
    
    confidence = round(nlu["entities"][0]["confidence_entity"] * 100) 
    
    return assistant.speech_action({"intent": nlu["intent"] ["name"], "entity": nlu["entities"][0]["value"],"confidence": confidence})
  
  elif modality == "GESTURES":
    return assistant.gesture_action(message["recognized"][1])
  
  elif modality == "FUSION":
    nlu = None
    
    for command in comand_tags:
      if "nlu" in command.text:
        speech_tag = json.loads(command.text)

        nlu = json.loads(speech_tag["nlu"])

        print(f"nlu: {nlu}")
        
        if "entities" not in nlu or len(nlu["entities"]) == 0:
           nlu = {"intent": nlu["intent"] ["name"]}
        else:
          confidence = round(nlu["entities"][0]["confidence_entity"] * 100) 

          nlu = {"intent": nlu["intent"] ["name"], "entity": nlu["entities"][0]["value"],"confidence": confidence}

        break

    return assistant.fusion_action(message["recognized"][1:],nlu)


def ignore_certificates():
  """
  The ignore_certificates function is responsible for ignoring the web certificates
  """
  ssl_context = ssl.SSLContext(protocol=ssl.PROTOCOL_TLS_CLIENT)
  ssl_context.check_hostname = False
  ssl_context.verify_mode = ssl.CERT_NONE

  return ssl_context

async def main():
  """
   The main function is responsible for starting the assistant, and make the conection to the WebApp's websocket
   It also is responsible for receiving messages and calling the nlu_extractor function to extract the nlu from the message
   After that, the function calls the assistant's speech action method to execute the voice action based on the nlu
  """
  # Opens the html index file, the variable is not used, but it is necessary to open the file
  index = Index()

  assistant = Assistant()

  # Websocket url adress
  mmi_cli_out_Add = f"wss://{HOST}/IM/USER1/APP"
  
  ssl_context = ignore_certificates()

  async with websockets.connect( mmi_cli_out_Add,ssl = ssl_context) as websocket:
      print("Connected Websocket")

      while assistant.running:
          try:
            print("Waiting for messages")
            message = await websocket.recv()
            print(f"Message received APPPPPPPP.PY -----------: {message}")
            
            if message not in ["OK","RENEW"] or message is not None:  
              # mudar nome, depois
              nlu = nlu_extractor(message, assistant)
              print(f"Message received:  {nlu}")
                      
          except Exception as ex:
                print(f"Exception {ex}")
                      
if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
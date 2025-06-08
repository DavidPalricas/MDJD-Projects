import requests
import xml.etree.ElementTree as ET
import time
import base64
import json

#a= requests.post("http://127.0.0.1:5005/model/parse", '{"text":"ligar as luzes na sala"}')
#print(a.text)

im_url_app = 'https://127.0.0.1:8000/IM/USER1/APP'
im_url_appx = 'https://127.0.0.1:8000/IM/USER1/APPX'



def send_to_IM(data, source=None):
    """constroi e envia a mensagem para o IM"""

    #if source == "SPEECHIN":
    #    source = "APPSPEECH"
    #else:
    
    source = "APPX"  #-->GRAPHICS

    # source = "APP"
    #if isinstance(data, str):
    #    data_string = str(base64.standard_b64encode(data.encode('utf-8')))
    #    data_string = '''"&lt;speak version=\"1.0\" xmlns=\"http://www.w3.org/2001/10/synthesis\" xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xsi:schemaLocation=\"http://www.w3.org/2001/10/synthesis http://www.w3.org/TR/speech-synthesis/synthesis.xsd\" xml:lang=\"pt-PT\"&gt;&lt;p&gt;''' + data_string + '''&lt;/p&gt;&lt;/speak&gt;"'''


    message = '''<mmi:mmi xmlns:mmi="http://www.w3.org/2008/04/mmi-arch" mmi:version="1.0">
  <mmi:startRequest mmi:context="ctx-1" mmi:requestId="app-1" mmi:source=\"%s\" mmi:target="IM">
    <mmi:data>
      <emma:emma xmlns:emma="http://www.w3.org/2003/04/emma" emma:version="1.0">
        <emma:interpretation emma:confidence="1" emma:id="app-" emma:medium="display" emma:mode="command" emma:start="0">
          <command>%s</command>
        </emma:interpretation>
      </emma:emma>
    </mmi:data>
  </mmi:startRequest>
</mmi:mmi>''' % (source, data)

    print(message)
    print(data)

    try:
        headers = {'Content-Type': 'application/xml'}  # set what your server accepts
        requests.post(im_url_appx, data=message, headers=headers, verify=False)
    except requests.exceptions.ConnectionError \
           or requests.exceptions.Timeout \
           or requests.exceptions.TooManyRedirects \
           or requests.exceptions.RequestException:
        print("Connection error")



def polling():
    while True:
        response = None
        try:
            response = requests.get(im_url_app, verify=False)
            if not response.text == "RENEW":
                print(response.text)
                root = ET.fromstring(response.content)

                for child in root.iter('*'):
                    if child.tag == "command":
                        json_data = json.loads(child.text)
                        if "recognized" not in json_data:
                            continue
                        if len(json_data['recognized']) > 0:

                            source = None
                            if len(json_data['recognized']) > 1:
                                source = json_data['recognized'][1]

                            message = None
                            if json_data['recognized'][0] == "SPEECH" and "text" in json_data:
                                query = base64.b64decode(json_data['text']).decode('utf-8')
                                print(query)
                                print("------------------")

                            rasa_resp=requests.post("http://localhost:5005/model/parse",json={"text": query.strip()})
                            #rasa_resp.json()["intent"]["name"]
                            send_to_IM({"recognized": { "intent": rasa_resp.json()["intent"]["name"]}}, source)


        except (requests.exceptions.SSLError, requests.exceptions.ConnectionError,
                    requests.exceptions.Timeout, requests.exceptions.TooManyRedirects,
                    requests.exceptions.RequestException) as e:
            print("error")
            print(e)
            print(response)
        time.sleep(1)

polling()
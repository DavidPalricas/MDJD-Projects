from web_app_conextions_files.conextion_config import  LifeCycleEvent, EMMA, MMIClient
import json

class IndexConnections():
    def __init__(self, IMAdd=None, FusionAdd=None) -> None:
        self.mmiCli = MMIClient(IMAdd, FusionAdd)

    def sendToIM(self,mmi_event,emma_value):
        self.mmiCli.sendToIM(LifeCycleEvent(f"{mmi_event}", "IM", "text-1", "ctx-1").doStartRequest(EMMA("text-", "text", "command", 1, 0).setValue(emma_value)))

class TTS(IndexConnections):
     def __init__(self,IMAdd=None, FusionAdd=None) -> None:
        super().__init__(IMAdd, FusionAdd)

     def sendToVoice(self, message):
        speak = f"\"<speak version=\"1.0\" xmlns=\"http://www.w3.org/2001/10/synthesis\" xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xsi:schemaLocation=\"http://www.w3.org/2001/10/synthesis http://www.w3.org/TR/speech-synthesis/synthesis.xsd\" xml:lang=\"pt-PT\"><p>{message}</p></speak>\""
        self.sendToIM("APPSPEECH", speak)

class Confirmation(IndexConnections):
    def __init__(self,IMAdd=None, FusionAdd=None) -> None:
        super().__init__(IMAdd, FusionAdd)

    def confirm(self):
        self.sendToIM("SPEECH_ANSWER", json.dumps({"text":"confirmation"}))

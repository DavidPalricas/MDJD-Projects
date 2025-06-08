# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

# from typing import Any, Text, Dict, List
#
# from rasa_sdk import Action, Tracker
# from rasa_sdk.executor import CollectingDispatcher
#
#
# class ActionHelloWorld(Action):
#
#     def name(self) -> Text:
#         return "action_hello_world"
#
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#
#         dispatcher.utter_message(text="Hello World!")
#
#         return []

from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, UserUtteranceReverted

import json


def write_log(text):
    with open("log.txt", "a") as log:
        log.write(text)

class ActionDefaultFallback(Action):
    """Executes the fallback action and goes back to the previous state
    of the dialogue"""

    def name(self) -> Text:
        return "action_default_fallback"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        write_log("Actions: " + "No_understand: " + "enter\n")
        
        print("Confiança: ", tracker.latest_message["intent"].get("confidence"))
        write_log("Confiança: " + str(tracker.latest_message["intent"].get("confidence")) + "\n")
        
        if tracker.latest_message["intent"].get("confidence") > 0.5:
            dispatcher.utter_message(response="utter_default")
        
        #publish.single(topic="comandos/voz/UI", payload=json.dumps({"comando": "no_understand"}), hostname="localhost")
        
        write_log("Actions: " + "No_understand: " + "exit\n")
        
        # Revert user message which led to fallback.
        return [UserUtteranceReverted()]

class SwitchLightsAction(Action):
    def name(self) -> Text:
        return "action_switch_lights"
   
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
       
        print(tracker.get_slot("switch") + "--" + tracker.get_slot("place"))   
        #tracker.lastest_message["entities"]  [0] - entity - value
        print("Confiança: ", tracker.latest_message["intent"].get("confidence"))          
        if tracker.latest_message["intent"].get("confidence") < 0.8:
            dispatcher.utter_message(response="utter_default")
            return [UserUtteranceReverted()]
        """
        switcher = homecontrol.SwitchLights(lightsimulator)
        message = switcher.switchlight(tracker.get_slot("switch"), tracker.get_slot("place"))
        dispatcher.utter_message(message)
        return [SlotSet("place", None), SlotSet("switch", None)]
         """

class ActionAfirmar(Action):
    
    def name(self) -> Text:
        return "action_afirmar"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        write_log("Actions: " + "Afirmar: " + "enter\n")
        print("Confiança: ", tracker.latest_message["intent"].get("confidence"))
        write_log("Confiança: " + str(tracker.latest_message["intent"].get("confidence")) + "\n")
        
        msg = {"comando": "confirmar"}
    #    publish.single(topic="comandos/voz/UI", payload=json.dumps(msg), hostname="localhost")
        
        write_log("Actions: " + "Afirmar: " + "exit\n")
        
        return []

class ActionNegar(Action):
    
    def name(self) -> Text:
        return "action_negar"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        write_log("Actions: " + "Negar: " + "enter\n")
        print("Confiança: ", tracker.latest_message["intent"].get("confidence"))
        write_log("Confiança: " + str(tracker.latest_message["intent"].get("confidence")) + "\n")
        
        msg = {"comando": "negar"}
        #publish.single(topic="comandos/voz/UI", payload=json.dumps(msg), hostname="localhost")
        
        write_log("Actions: " + "Negar: " + "exit\n")
        
        return []
    
from rasa.core.agent import Agent
import asyncio

# path of your model
rasa_model_path = ".\models"

# create an interpreter object
print("loading model")
interpreter = Agent.load(model_path=rasa_model_path)
print("model loaded")

"""
Function to get model output
Args:
  text  (string)  --  input text string to be passed)
For example: if you are interested in entities, you can just write result['entities']
Returns:
  json  --  json output to used for accessing model output
"""

def rasa_output(text):
    message = str(text).strip()
    #result = interpreter.parse_message(message_data=message)
    result=asyncio.run(interpreter.parse_message_using_nlu_interpreter(
                message_data='Hello there'))
    return result

print(rasa_output("ligar as luzes no quarto"))
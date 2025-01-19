from openai import OpenAI
import os
import json
from copy import deepcopy
from .utils import get_chatbot_response,double_check_json_output
import dotenv
dotenv.load_dotenv()

class GuardAgent():
    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"), # runpod_token
            base_url=os.getenv("OPENAI_API_URL"), # runpod_chatbot_url
        )
        self.model_name = os.getenv("OPENAI_MODEL_NAME") # model_name

    def get_response(self,messages):
        messages = deepcopy(messages)

        system_prompt="""
            You are a helpful assistant for a coffee shop application which serves drinks and pastries.
            You ask is to determine whether the user is asking something relevant to the coffee shop or not.
            The user is allowed to:
            1. Ask questions about the coffee shop, like locaton, working hours, menu items and coffee shop related questions.
            2. Ask questions about menu items, they can ask for ingredients in an item and more details about the item.
            3. Make an order.
            4. Ask about recommendations of what to buy.

            The user is not allowed to:
            1. Ask questions about anything else other than our coffee shop.
            2. Ask questions about the staff or how to make a certain menu item.

            Your output should be in a structured json format like so. each key is a string and each value is a string. Make sure to follow the format exactly:
            {
            "chain of thought": "go over each of the points above and see if the message lies under this point or not. Then your write some thoughts about what point is this input relevant to."
            "decision": "allowed" or "not allowed". Pick one of those. and only write the word.
            "message": leave the message "" empty if it's allowed, otherwise write "Sorry, I can't help with that. Can I help you with your order?"
            }
        """

        input_messages = [{"role": "system", "content": system_prompt}] + messages[-3:]

        chatbot_output = get_chatbot_response(self.client, self.model_name, input_messages)
        chatbot_output = double_check_json_output(self.client, self.model_name, chatbot_output)
        output = self.postprocess(chatbot_output)

        return output

    def postprocess(self, output):
        output = json.loads(output)

        dict_output = {
            "role":"assistant",
            "content":output["message"],
            "memory":{
                "agent":"guard_agent",
                "guard_decision":output["decision"],
            }
        }

        return dict_output
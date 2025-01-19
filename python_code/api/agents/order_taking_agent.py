import os 
import json 
from .utils import get_chatbot_response,double_check_json_output
from openai import OpenAI
from copy import deepcopy
from dotenv import load_dotenv
load_dotenv()

class OrderTakingAgent():
    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"), # runpod_token
            base_url=os.getenv("OPENAI_API_URL"), # runpod_chatbot_url
        )
        self.model_name = os.getenv("OPENAI_MODEL_NAME") # model_name

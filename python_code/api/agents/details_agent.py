from dotenv import load_dotenv
import os
from .utils import get_chatbot_response,get_embedding
from openai import OpenAI
from copy import deepcopy
from pinecone import Pinecone
load_dotenv()

class DetailsAgent():
    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"), # runpod_token
            base_url=os.getenv("OPENAI_API_URL"), # runpod_chatbot_url
        )
        self.model_name = os.getenv("OPENAI_MODEL_NAME") # model_name   
        self.embedding_client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"), # runpod_token
            base_url=os.getenv("OPENAI_EMBEDDING_URL"), # runpod_embedding_url
        )
        self.pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY")) # runpod_pinecone_api_key
        self.index_name = os.getenv("PINECONE_INDEX_NAME")
    
    def get_closest_results(self,index_name,input_embeddings, top_k=2):
        index = self.pc.Index(index_name)

        results = index.query(
            namespace='ns1',
            vector=input_embeddings,
            top_k=top_k,
            include_values=False,
            include_metadata=True
        )

        return results

    def get_response(self,messages):
        messages = deepcopy(messages)

        user_message = messages[-1]['content']
        embeddings = get_embedding(self.embedding_client, self.model_name, user_message)[0]
        result = self.get_closest_results(self.index_name,embeddings)
        source_knowledge = "\n".join([x['metadata']['text'].strip()+'\n' for x in result['matches']])

        prompt = f"""
        Using the contexts below answer the query:

        Contexts:
        {source_knowledge}

        Query:
        {user_message}
        """

        system_prompt = """You are a customer support agent for a coffee shop called Merry's way. You should answer every question as if you are waiter and provide the necessary information to the user regarding their orders """
        messages[-1]['content'] = prompt
        input_messages = [{'role': 'system', 'content': system_prompt}] + messages[-3:]

        chatbot_output = get_chatbot_response(self.client, self.model_name, input_messages)
        output = self.postprocess(chatbot_output)

        return output

    def postprocess(self,output):
        output={
            "role":"assistant",
            "content":output,
            "memory":{
                "agent":"details_agent"
            }
        }

        return output
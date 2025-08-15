### author: Peter Karacsonyi
### date:   8/15/2025
### purpose: openrouter class for general LLM use cases. there is nothing model specific

#pypi
import os
import json
import requests
from dotenv import dotenv_values

# local
from model import LLMConfig

class OpenRouter:
    '''general class to execute an API call to openrouter
    abstracts away the HTTP request basically'''

    config = dotenv_values(".env")
    openrouter_api_key = config.get("OPENROUTER_API_KEY", os.getenv("OPENROUTER_API_KEY"))

    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {openrouter_api_key}",
        "Content-Type": "application/json"
    }

    def __init__(self, llmconfig: LLMConfig):

        self.structured_output = None
        self.llmconfig = llmconfig

        if llmconfig._response_schema:
            self.structured_output = {
                "response_format": {
                    "type": "json_schema",
                    "name": "asset_analytics_report",
                    "schema": llmconfig.response_schema_str,
                    "strict": True,
                }
            }
    
    def query(self, prompt_data: str | dict):
        ''' prompt data is appended after the superprompt (if set)
        '''

        prompt = None
        if self.llmconfig.superprompt_str:
            prompt = str(self.llmconfig.superprompt_str) + "\n" + str(prompt_data)
        else:
            prompt = str(prompt_data)


        if self.llmconfig.response_schema_str:
            payload = {
                "models": [self.llmconfig.model_name],
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "response_format": self.structured_output
            }
        else:
            payload = {
                "models": [self.llmconfig.model_name],
                "messages": [
                    {"role": "user", "content": json.loads(prompt)}
                ]
            }
        

        try:
            response = requests.post(self.url, headers=self.headers, json=payload)
        except Exception as e:
            print('unexpected error: ', e)
            return {}

        if response.status_code != 200:
            raise Exception(f"Error {response.status_code}: {response.text}")

        # TODO: set this up when we have working structured outputs
        # try:
        #     validate(instance=response_json, schema=self.llmconfig.response_schema)
        # except ValidationError as ve:
        #     print(f"Validation failed: {ve.message}")
        #     print(f"Location in instance: {list(ve.path)}")
        #     print(f"Schema path: {list(ve.schema_path)}")
        #     print(f"Invalid value: {ve.instance}")
        # except SchemaError as se:
        #     print(f"The schema {self.llmconfig.response_schema} seems to be bad, error: {se.message}")

        return response.json()

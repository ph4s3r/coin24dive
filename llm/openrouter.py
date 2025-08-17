### author: Peter Karacsonyi
### date:   8/15/2025
### purpose: openrouter class for general LLM use cases. there is nothing model specific

#pypi
import re
import os
import json
import time
import requests
from dotenv import dotenv_values

# 3rd party
from jsonschema import validate, ValidationError, SchemaError
from tenacity import retry, stop_after_attempt, wait_random_exponential, retry_if_exception_type

# local
from llm.model import LLMConfig

# Define a custom exception
class RateLimitExceeded(Exception):
    '''OpenRouter API might return RateLimit issues specific to models
    we try to cover them here'''
    def __init__(self, message):
        super().__init__(message)
        self.message = message


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

        if llmconfig.response_schema_dict:
            self.structured_output = {
                    "type": "json_schema",
                    "json_schema": {
                        "name": "asset_analytics",
                        "strict": True,
                        "schema": llmconfig.response_schema_dict,
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


        if self.llmconfig.response_schema_dict:
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
        
        @retry(stop=(stop_after_attempt(6)), wait=wait_random_exponential(min=1, max=60),retry=retry_if_exception_type(RateLimitExceeded))
        def query_llm(**kwargs):
            try:
                response = requests.post(**kwargs)
                if (openrouter_error := response.json()['choices'][0].get('error', 0)) != 0:
                        raise RateLimitExceeded(openrouter_error.get("message", "got an empty error message from openrouter, please check"))
                return response
            except RateLimitExceeded as openrouter_error_message:
                # try to parse hnow much we should wait
                COMPONENT_WAIT_SEC = '(?<wait_sec>\d+)\.\d+s'
                matches = re.search(COMPONENT_WAIT_SEC , openrouter_error_message)
                if not matches:
                    wait_sleep = 60
                else:
                    wait_sleep = matches.group('wait_sec')
                if self.WAIT_SLEEP:
                    # time.sleep(int(re.response.headers.get("x-ratelimit-reset-tokens", 60))) just leaving this here because this is what works with the openai SDK
                    time.sleep(int(wait_sleep))
                response = requests.post(**kwargs)
                return response


        try:
            response = query_llm(url=self.url, headers=self.headers, json=payload)
        except Exception as e:
            print('unexpected error: ', e)
            return {}

        if response.status_code != 200:
            raise Exception(f"Error {response.status_code}: {response.text}")
        if (openrouter_error := response.json()['choices'][0].get('error', 0)) != 0:
            raise RateLimitExceeded(openrouter_error.get("message", "got an empty error message from openrouter, please check"))

        # TODO: set this up when we have working structured outputs
        try:
            validate(instance=json.loads(response.json()['choices'][0]['message']['content']), schema=self.llmconfig.response_schema_dict)
        except ValidationError as ve:
            print(f"Validation failed: {ve.message}")
            print(f"Location in instance: {list(ve.path)}")
            print(f"Schema path: {list(ve.schema_path)}")
            if isinstance(ve.instance, str):
                print(f"Invalid value: {ve.instance[:120]}...")
        except SchemaError as se:
            print(f"The schema {self.llmconfig.response_schema_dict} seems to be bad, error: {se.message}")

        return response.json()

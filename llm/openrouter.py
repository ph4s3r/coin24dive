### author: Peter Karacsonyi
### date:   8/12/2025
### purpose: provides an interface to call various LLMs with structured outputs
### inputs: API keys, prompt, superpromt, response json format



# scam checks:
# https://docs.chainabuse.com/docs/getting-started-2-1
# https://tech-doc.api.scorechain.com/
# https://developers.elliptic.co/docs/getting-started



import os
import json
import requests
from dotenv import dotenv_values

class OpenLLM:

    config = dotenv_values(".env")
    openrouter_api_key = config.get("OPENROUTER_API_KEY", os.getenv("OPENROUTER_API_KEY"))

    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {openrouter_api_key}",
        "Content-Type": "application/json"
    }

    # models supporting structured outs
    # https://openrouter.ai/models?order=newest&supported_parameters=structured_outputs
    models = [
        # OpenAI requires bringing your own API key to use GPT-5 over the API. Set up here: https://openrouter.ai/settings/integrations
        "openai/gpt-5",                         # 400,000 context $1.25/M input tokens $10/M output tokens
        "openai/o4-mini-high",                  # 200,000 context $1.10/M input tokens $4.40/M output tokens $0.842/K input imgs
        "openai/o3",                            # 200,000 context $2/M input tokens $8/M output tokens
        "openai/gpt-oss-120b",                  # 131,072 context $0.073/M input tokens $0.29/M output tokens

        "x-ai/grok-4",                          # 256,000 context $3/M input tokens   $15/M output tokens
        "google/gemini-2.5-pro"                 # 1M context      $1.25/M input tokens   $10/M output tokens
        "google/gemini-2.5-flash"               # 1,048,576 context $0.30/M input tokens $2.50/M output tokens
        # "anthropic/claude-opus-4.1",          # does not support structured output
        
        "qwen/qwen3-235b-a22b-2507",            # 262,144 context $0.078/M input tokens $0.312/M output tokens
        "qwen/qwen3-30b-a3b",                   # 40,960 context $0.02/M input tokens $0.08/M output tokens
        # "switchpoint/router",                 # need to test this later...
        "mistralai/magistral-medium-2506:thinking", # 40,960 context $2/M input tokens $5/M output tokens


    ]

    @classmethod
    def prompt(cls, prompt: str):
        """Send a prompt to the API using only class variables."""
        payload = {
            "models": cls.models,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }

        response = requests.post(cls.url, headers=cls.headers, json=payload)

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Error {response.status_code}: {response.text}")
        

result = OpenLLM.prompt("If you built the world's tallest skyscraper, what would you name it?")
print(json.dumps(result, indent=2))

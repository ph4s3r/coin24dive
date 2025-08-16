
### author: Peter Karacsonyi
### date:   8/15/2025
### purpose: sample test building an openrouter query

from pathlib import Path

from model import LLMConfig
from openrouter import OpenRouter

# reading a coindata file
coindata = ''
with open(r'data/coindata/cyberyen.json', encoding="utf-8") as f:
    coindata = f.read()

# create gpt5 model settings
gpt5 = LLMConfig(
    model_name = 'openai/gpt-5',
    provider = 'openrouter',
    superprompt = Path("llm/superprompt"), 
    response_schema = Path("llm/schemas/analytics_schema.json")
)

# create an instance of the openrouter for this specific model settings
gpt5_analytics_report = OpenRouter(
    llmconfig=gpt5
)

response        : dict  = gpt5_analytics_report.query(prompt_data=coindata)
asset_report    : dict  = response['choices'][0]['message']['content']
pass

### author: Peter Karacsonyi
### date:   8/15/2025
### purpose: model specific settings stored in a custom class

#pypi
from pathlib import Path


# models supporting structured outs
# https://openrouter.ai/models?order=newest&supported_parameters=structured_outputs
MODELS_WITH_STRUCTURED_OUTPUT = [
    
        "openai/gpt-5",                             # 400,000 context $1.25/M input tokens $10/M output tokens
        "openai/o4-mini-high",                      # 200,000 context $1.10/M input tokens $4.40/M output tokens $0.842/K input imgs
        "openai/o3",                                # 200,000 context $2/M input tokens $8/M output tokens
        "openai/gpt-oss-120b",                      # 131,072 context $0.073/M input tokens $0.29/M output tokens

        "x-ai/grok-4",                              # 256,000 context $3/M input tokens   $15/M output tokens
        "google/gemini-2.5-pro"                     # 1M context      $1.25/M input tokens   $10/M output tokens
        "google/gemini-2.5-flash",                  # 1,048,576 context $0.30/M input tokens $2.50/M output tokens
        
        "qwen/qwen3-235b-a22b-2507",                # 262,144 context $0.078/M input tokens $0.312/M output tokens
        "qwen/qwen3-30b-a3b",                       # 40,960 context $0.02/M input tokens $0.08/M output tokens
        "switchpoint/router",                       # need to test this later...
        "mistralai/magistral-medium-2506:thinking", # 40,960 context $2/M input tokens $5/M output tokens
    ]

MODELS_WITHOUT_STRUCTURED_OUTPUT = [
        "anthropic/claude-opus-4.1",                # does not support structured output
    ]

class LLMConfig():
    '''describes everything that is model and request specific
    this class can be handed over to the OpenRouter class
    '''

    def __init__(self, 
                model_name: str,
                provider: str,
                superprompt: str | Path | None, 
                response_schema: dict | Path | None,   # if None, no structured output is enforced
                 ):
        self.model_name         = model_name
        self.provider           = provider             # currently unused - planned to use it to change params e.g. openrouters openai SDK
        self._superprompt        = superprompt
        self._response_schema    = response_schema

        self.superprompt_str    = ''
        self.response_schema_str= ''

        if self.model_name not in MODELS_WITH_STRUCTURED_OUTPUT + MODELS_WITHOUT_STRUCTURED_OUTPUT:
            print(f'warning: model {self.model} is not listed in our list, might be unsupported')

        if isinstance(self._superprompt, Path):
            try:
                with open(superprompt, encoding="utf-8") as f:
                    self.superprompt_str = f.read()
            except Exception as e:
                print('failed to load superprompt from file, will not use it then..', e)
                self.superprompt = None
        elif isinstance(self.superprompt, str):
            self.superprompt_str = superprompt
        else:
            print('superprompt is not a path or str, will not use it then..')
            self.superprompt_str = None

        if isinstance(self._response_schema, Path):
            try:
                with open(response_schema, encoding="utf-8") as f:
                    self.response_schema_str = f.read()
            except Exception as e:
                print('failed to load response_schema from file, will not enforce structured output then..', e)
                self.response_schema_str = None
        elif isinstance(self.response_schema, str):
            self.response_schema_str = response_schema
        else:
            print('response_schema is not a path or str, will not enforce structured output then..')
            self.response_schema_str = None

    # bad naming maybe
    @property
    def superprompt(self):
        raise AttributeError("use 'superprompt_str'")
    
    @superprompt.setter
    def superprompt(self, v):
        self._superprompt = v

    @property
    def response_schema(self):
        raise AttributeError("use 'response_schema_str'")

    @response_schema.setter
    def response_schema(self, v):
        self._response_schema = v

    
        
        

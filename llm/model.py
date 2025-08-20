"""Manage model specific settings with a custom class.

author: Peter Karacsonyi
date:   8/20/2025
"""

#pypi
import json
from pathlib import Path
from typing import NoReturn


# models supporting structured outs
# https://openrouter.ai/models?order=newest&supported_parameters=structured_outputs
MODELS_WITH_STRUCTURED_OUTPUT = [

        'openai/gpt-5',                             # 400,000 context $1.25/M input tokens $10/M output tokens
        'openai/o4-mini-high',                      # 200,000 context $1.10/M input tokens $4.40/M output tokens
        'openai/o3',                                # 200,000 context $2/M input tokens $8/M output tokens
        'openai/gpt-oss-120b',                      # 131,072 context $0.073/M input tokens $0.29/M output tokens

        'x-ai/grok-4',                              # 256,000 context $3/M input tokens   $15/M output tokens
        'google/gemini-2.5-pro'                     # 1M context      $1.25/M input tokens   $10/M output tokens
        'google/gemini-2.5-flash',                  # 1,048,576 context $0.30/M input tokens $2.50/M output tokens

        'qwen/qwen3-235b-a22b-2507',                # 262,144 context $0.078/M input tokens $0.312/M output tokens
        'qwen/qwen3-30b-a3b',                       # 40,960 context $0.02/M input tokens $0.08/M output tokens
        'switchpoint/router',                       # need to test this later...
        'mistralai/magistral-medium-2506:thinking', # 40,960 context $2/M input tokens $5/M output tokens
    ]

MODELS_WITHOUT_STRUCTURED_OUTPUT = [
        'anthropic/claude-opus-4.1',                # does not support structured output
    ]

class LLMConfig:

    """Describe everything that is model and request specific.

    this class can be handed over to the OpenRouter class.
    superprompt and response_schema are inputs.
    they will be loaded to the respective
    self.superprompt_str      = ''
    self.response_schema_dict = ''

    """

    def __init__(self,
                model_name: str,
                provider: str,
                superprompt: str | Path | None,
                response_schema: dict | Path | None,   # if None, no structured output is enforced
                 ) -> None:
        """Create an instance of LLM configuration with the model, superprompt & respons_schema."""
        self.model_name          = model_name
        self.provider            = provider
        # currently unused - planned to use it to change params e.g. openrouters openai SDK
        self._superprompt        = superprompt
        self._response_schema    = response_schema

        self.superprompt_str      = None
        self.response_schema_dict = None

        if self.model_name not in MODELS_WITH_STRUCTURED_OUTPUT + MODELS_WITHOUT_STRUCTURED_OUTPUT:
            print(f'warning: model {self.model_name} is not listed in our list, might be unsupported')

        # loading superprmopt
        if isinstance(self._superprompt, Path):
            try:
                self.superprompt_str = Path(superprompt).read_text()
            except Exception as e:
                print('failed to load superprompt from file, will not use it then..', e)
                self.superprompt = None
        elif isinstance(self.superprompt, str):
            self.superprompt_str = superprompt
        else:
            print('superprompt is not a path or str, will not use it then..')
            self.superprompt_str = None

        # loading response schema for structured outputs
        if isinstance(self._response_schema, Path):
            try:
                self.response_schema_dict = json.loads(Path(response_schema).read_text())
            except Exception as e:
                print('failed to load response_schema from file, will not enforce structured output then..', e)
        elif isinstance(self.response_schema, dict):
            self.response_schema_dict = response_schema
        else:
            print('response_schema is not a path or dict, will not enforce structured output then..')
            self.response_schema_dict = None

    # bad naming maybe
    @property
    def superprompt(self) -> NoReturn:
        raise AttributeError("get 'superprompt_str'")

    @superprompt.setter
    def superprompt(self, v: str) -> None:
        self._superprompt = v

    @property
    def response_schema(self) -> NoReturn:
        raise AttributeError("get 'response_schema_dict'")

    @response_schema.setter
    def response_schema(self, v):
        self._response_schema = v





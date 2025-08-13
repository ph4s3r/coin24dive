
import json

import llm.openrouter as ai

coindata = None

with open(r'coindata/catex.json', encoding="utf-8") as f:
    coindata = f.read()

if len(coindata) > 0:
    result = ai.OpenLLM.analyze_asset_prompt(coindata)
    print('coin analytics returned:')
    print(json.dumps(result, indent=2))

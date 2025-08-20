# pypi
import os
import json
from pathlib import Path

from llm.model import LLMConfig
from llm.openrouter import OpenRouter
from utils.clog import log_fail, log_ok, log_task


def llm_analytics(coinmetrics_full: list, analytics_folder: str, today_date: str) -> dict:
    print()

    prompt_tokens = 0
    completion_tokens = 0
    error_counter = 0  # we tolerate max 2 errors, then give up

    # setting up LLM for analytics queries
    # gpt5 = LLMConfig(
    #     model_name = 'openai/gpt-5',
    #     provider = 'openrouter',
    #     superprompt = Path('llm/superprompt'),
    #     response_schema = Path('llm/schemas/analytics_schema.json')
    # )

    # setting up LLM for analytics queries
    o4mini = LLMConfig(
        model_name='openai/o4-mini',
        provider='openrouter',
        superprompt=Path('llm/superprompt'),
        response_schema=Path('llm/schemas/analytics_schema.json'),
    )

    o4mini_analytics_report = OpenRouter(llmconfig=o4mini)
    dead_scores = {}

    for coin_data_dict in coinmetrics_full:
        if error_counter > 1:
            log_fail('too many errors, skipping future promises')
            break

        coin_id = coin_data_dict.get('id')  # this is the id from coingecko, sometimes different from the 'symbol'
        analytics_file_full_path = (
            Path(analytics_folder) / Path(today_date) / Path(f'{o4mini.model_name.replace("/", "-")}-{coin_id}.json')
        )

        if analytics_file_full_path.exists():
            try:
                with open(analytics_file_full_path, encoding='utf-8') as f:
                    dead_scores[coin_id] = json.load(f)['content']['dead_score']
                    log_ok(f'analytics already exists as {analytics_file_full_path} , loaded successfully')
            except Exception as e:
                log_fail(f'could not load coin analytics from file {analytics_file_full_path}, Error: {e}')
            continue

        # passing the detailed coin_data_dict from coinmetrics_full to the LLM for analysis
        llm_api_response = None

        try:
            llm_api_response: dict = o4mini_analytics_report.query(prompt_data=coin_data_dict)
            asset_report_structured = json.loads(llm_api_response['choices'][0]['message']['content'])
            log_ok(f'coin analytics returned for symbol {coin_id} from {o4mini.model_name}')
        except Exception as e:
            log_fail(f'could not get the structured output for {coin_id=} from the model. Error: {e}')
            error_counter += 1
            continue

        if not llm_api_response:
            continue

        prompt_tokens += int(llm_api_response.get('usage').get('prompt_tokens', 0))
        completion_tokens += int(llm_api_response.get('usage').get('completion_tokens', 0))

        analytics_data = {
            'content': asset_report_structured,
            'exchange_info': coin_data_dict.get('detail_platforms'),
            'links': coin_data_dict.get('links'),
        }

        analytics_file_full_path.write_text(json.dumps(analytics_data, indent=4, ensure_ascii=False), encoding='utf-8')
        log_ok(f'analytics successfully saved to {analytics_file_full_path}')
        dead_scores[coin_id] = asset_report_structured['dead_score']

    log_task('Calculating LLM usage prices')

    print(f'used {prompt_tokens=}')
    print(f'used {completion_tokens=}')
    print(
        'price of the move with gpt-5: ',
    )  # (w/o openrouter\'s margin of $0.0001 on every 1k tokens, which seems to be negligible...)

    # 400,000 context $1.25/M input tokens $10/M output tokens
    price_prompt_tokens = 1.25 * prompt_tokens / 1_000_000
    price_completion_tokens = 10 * completion_tokens / 1_000_000

    print(f'{price_prompt_tokens=}')
    print(f'{price_completion_tokens=}')

    return dead_scores

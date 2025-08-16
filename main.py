import os
import json
import diver
import getter
from pathlib import Path
from datetime import datetime

from llm.model import LLMConfig
from llm.openrouter import OpenRouter
from notifications import notificationsClass
from utils.clog import log_fail, log_ok, log_task


def main():
   
    coins = []

    print("*"*20, "COINGECKO MARKET SCANNER", "*"*20)

    
    os.makedirs("data", exist_ok=True)
    os.makedirs("data/dives", exist_ok=True)
    os.makedirs("data/coindata", exist_ok=True)
    os.makedirs("data/exchangedata", exist_ok=True)
    os.makedirs("data/analytics", exist_ok=True)
    
    # 1 get per day is enough for us

    today_date = datetime.now().strftime('%Y%m%d')

    fname_coins         = f"data/marketdata/coins{today_date}.json"
    fname_dives         = f"data/dives/dives{today_date}.json"
    analytics_folder    = 'data/analytics'

    log_task("Daily market scanning")
    if not os.path.exists(fname_coins):
        log_task("we don't have data for today, getting coins")
        coins = getter.get_coins_markets_all(fname_coins)
    else:
        log_ok("we already have the data for today, let's just open it :)")
        try:
            with open (fname_coins, "rt", encoding="utf-8") as f:
                coins = json.load(f)
                if not isinstance(coins[0], dict):
                    log_fail(":( something is off with the file, please check")
                    return
        except Exception as e:
            log_fail(f":( could not read coins from file: {e.args[0]}")


    log_task("Searching for coins with specific criteria")
    if len(coins) > 0:
        top_divers = set(diver.diver(fname_dives, coins, min_dive_percentage=-75))


    log_task("Getting detailed coin data for each coin")
    top_divers_dict = {} # keyed with id

    # here we just load all the individual detailed coindata to a list
    coinmetrics_full = []

    # enriching the coin data with exchange information
    for d in top_divers:
        coin_id = d[0]
        coindata, ex_inf = getter.get_coindata(coin_id, refresh=False)
        t = list(d)
        t.extend(ex_inf.get(coin_id))
        top_divers_dict[coin_id] = t
        coinmetrics_full.append(coindata)


    log_task("Analyzing the top divers with LLM")
    print()
    
    prompt_tokens       = 0
    completion_tokens   = 0
    error_counter       = 0 # we tolerate max 2 errors, then give up
    
    # setting up LLM for analytics queries
    gpt5 = LLMConfig(
        model_name = 'openai/gpt-5',
        provider = 'openrouter',
        superprompt = Path("llm/superprompt"), 
        response_schema = Path("llm/schemas/analytics_schema.json")
    )

    gpt5_analytics_report = OpenRouter(
        llmconfig=gpt5
    )

    dead_scores = {}

    for coin_data_dict in coinmetrics_full:

        if error_counter > 1:
            log_fail('too many errors, skipping future promises')
            break

        coin_id                     = coin_data_dict.get('id')    # this is the id from coingecko, sometimes different from the 'symbol'
        analytics_file_full_path    = Path(analytics_folder + r'/' + today_date + r'/' + gpt5.model_name.replace('/', '-') + '-' + coin_id +'.json')

        if os.path.exists(analytics_file_full_path):
            log_ok(f'analytics already exists as {analytics_file_full_path} , skipping this one for now..')
            continue


        # passing the detailed coin_data_dict from coinmetrics_full to the LLM for analysis
        llm_api_response = None

        try:
            llm_api_response            : dict  = gpt5_analytics_report.query(prompt_data=coin_data_dict)
            asset_report_structured     : dict  = json.loads(llm_api_response['choices'][0]['message']['content'])
            log_ok(f'coin analytics returned for symbol {coin_id} from {gpt5.model_name}')
        except Exception as e:
            log_fail(f'could not get the structured output for {coin_id=} from the model. Error:', e)
            error_counter += 1
            continue

        if not llm_api_response:
            continue

        prompt_tokens       += int(llm_api_response.get('usage').get('prompt_tokens', 0))
        completion_tokens   += int(llm_api_response.get('usage').get('completion_tokens', 0))

        analytics_data = {
            **{"content": asset_report_structured},
            **{"exchange_info": coin_data_dict.get('detail_platforms')},
            **{"links": coin_data_dict.get('links')},
        }

        Path(analytics_file_full_path).write_text(json.dumps(analytics_data, indent=4, ensure_ascii=False), encoding='utf-8')
        log_ok(f'analytics successfully saved to {analytics_file_full_path}')

        dead_scores[coin_id] = asset_report_structured['dead_score']

    log_task("Calculating LLM usage prices")

    print(f'used {prompt_tokens=}')
    print(f'used {completion_tokens=}')
    print('price of the move with gpt-5: ') # (w/o openrouter\'s margin of $0.0001 on every 1k tokens, which seems to be negligible...)
    
    # 400,000 context $1.25/M input tokens $10/M output tokens
    price_prompt_tokens = 1.25 * prompt_tokens / 1000000
    price_completion_tokens = 10 * completion_tokens / 1000000
    
    print(f'{price_prompt_tokens=}')
    print(f'{price_completion_tokens=}')


    log_task("Filtering daily coin analytics based on dead scores")

    if len(dead_scores) == 0:
        analytics_path_today = Path(analytics_folder) / today_date
        for json_file in analytics_path_today.iterdir():
            if json_file.is_file() and json_file.suffix == '.json':
                with json_file.open(encoding='utf-8') as f:
                    coin_analytics = json.load(f)
                    # not sure the coin_id is always reliable, need to watch out for this..
                    coin_id = coin_analytics['content']['coin_id']
                    dead_scores[coin_id] = coin_analytics['content']['dead_score']

    log_task("Results")
    print("        id                    | symbol | dead_score | chg_%_24h | exchanges-traded-on")
    nc = notificationsClass()    
    for coin_id, ex_data in top_divers_dict.items():

        coin_exchange_data = ', '.join(ex_data[3:])

        if dead_scores.get(coin_id, 10) < 7:
            nc.add_to_notifications(
                ex_data[1],                                             # symbol
                dead_scores[coin_id],                                   # dead score
            ex_data[2],                                                 # drop_percent
                f"https://www.coingecko.com/en/coins/{coin_id}",
                ", ".join(str(x) for x in coin_exchange_data)           # exchange info
            )
        print(f"{coin_id:32} {ex_data[1]:6} {dead_scores.get(coin_id, '?'):9} {ex_data[2]:11}% {coin_exchange_data:24}" )

    # will not send empty message
    nc.send_notifications()

if __name__ == '__main__':
    main()

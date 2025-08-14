import os
import json
import diver
import getter
from pathlib import Path
from datetime import datetime

import llm.openrouter as ai
from notifications import notificationsClass
from utils.clog import log_info, log_fail, log_ok, log_task

def replace_escaped_newlines(obj):
    if isinstance(obj, str):
        return obj.replace("\\n", "\n")
    elif isinstance(obj, list):
        return [replace_escaped_newlines(item) for item in obj]
    elif isinstance(obj, dict):
        return {k: replace_escaped_newlines(v) for k, v in obj.items()}
    return obj

def main():
   
    coins = []

    print("*"*20, "COINGECKO MARKET SCANNER", "*"*20)

    os.makedirs("dives", exist_ok=True)
    os.makedirs("data", exist_ok=True)
    os.makedirs("coindata", exist_ok=True)
    os.makedirs("exchangedata", exist_ok=True)
    # 1 get per day is enough for us
    fname_coins = f"data/coins{datetime.now().strftime('%Y%m%d')}.json"
    fname_dives = f"dives/dives{datetime.now().strftime('%Y%m%d')}.json"

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

    if len(coins) > 0:
        top_divers = diver.diver(fname_dives, coins, min_dive_percentage=-75)

    log_task("Getting coin exchange information for each coin")

    top_divers_full = []
    top_divers = set(top_divers)

    coinmetrics_full = []

    # enriching the coin data with exchange information
    for d in top_divers:
        coin_id = d[0]
        coindata, ex_inf = getter.get_ex_inf(coin_id, refresh=False)
        t = list(d)
        t.extend(ex_inf.get(coin_id))
        top_divers_full.append(t)
        coinmetrics_full.append(coindata)

    log_task("Results")

    nc = notificationsClass()

    log_info("   id           |  symbol  |     chg_%_24h     |  exchanges-traded-on")
    for d in top_divers_full:
        nc.add_to_notifications(
            d[1], # symbol
            d[2], # drop_percent
            f"https://www.coingecko.com/en/coins/{d[0]}",
            ", ".join(str(x) for x in d[3:]) # exchange info
        )
        print(f"{d[0]:24} {d[1]:6} {d[2]:20}%", d[3:])

    # analyze full coin data with llm

    analytics_folder = 'analytics'

    prompt_tokens       = 0
    completion_tokens   = 0
    error_counter       = 0 # we tolerate max 2 errors, then quit

    print()

    for coin_data_dict in coinmetrics_full:

        if error_counter > 1:
            print('too many errors, skipping future promises')
            break

        symbol                      = coin_data_dict.get('id')  # symbol is somethins misleading
        model_name                  = 'openai-gpt-5'
        analytics_file_full_path    = Path(analytics_folder + r'/' + model_name + '-' + symbol +'.json')

        if os.path.exists(analytics_file_full_path):
            print(f'analytics already exists as {analytics_file_full_path} , skipping this one for now..')
            continue

        result = ai.OpenLLM.analyze_asset_prompt(coin_data_dict)
        if not result:
            error_counter += 1
            continue 
        print(f'coin analytics returned for symbol {symbol} from {model_name}')

        prompt_tokens       += int(result.get('usage').get('prompt_tokens', 0))
        completion_tokens   += int(result.get('usage').get('completion_tokens', 0))

        # model_name = result.get('model').replace(r'/', '-') # this is for dynamic running
        
        # print(json.dumps(result, indent=4))

        data_content    = result.get('choices')[0].get('message').get('content')
        data_reasoning  = result.get('choices')[0].get('message').get('reasoning')
        data_exinfo     = coin_data_dict.get('detail_platforms')
        data_links      = coin_data_dict.get('links')

        data_full = {
            **{"content": data_content},
            **{"reasoning": data_reasoning},
            **{"exchange_info": data_exinfo},
            **{"links": data_links},
        }

        data_cleaned = replace_escaped_newlines(data_full)

        with open(analytics_file_full_path, 'w', encoding='utf-8') as f:
            json.dump(data_cleaned, f, indent=4, ensure_ascii=False)

   
        print(f'analytics successfully saved to {analytics_file_full_path}')

    print(f'used {prompt_tokens=}')
    print(f'used {completion_tokens=}')
    print('price of the move with gpt-5: ') # (w/o openrouter\'s margin of $0.0001 on every 1k tokens, which seems to be negligible...)
    
    # 400,000 context $1.25/M input tokens $10/M output tokens
    price_prompt_tokens = 1.25 * prompt_tokens / 1000000
    price_completion_tokens = 10 * completion_tokens / 1000000
    
    print(f'{price_prompt_tokens=}')
    print(f'{price_completion_tokens=}')


    # nc.send_notifications()

if __name__ == '__main__':
    main()

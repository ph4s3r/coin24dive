import os
import sys
import time
import json
import requests
from typing import Dict, List
from dotenv import dotenv_values
from datetime import datetime, timezone
from tenacity import retry, stop_after_attempt, wait_random_exponential

from utils.clog import log_info, log_fail, log_ok

config = dotenv_values(".env")

@retry(stop=(stop_after_attempt(6)), wait=wait_random_exponential(min=1, max=60))
def get_ex_inf(id: str, refresh = False, write_ex_only = False) -> Dict[str, List[str]]:
    """
    get all detailed coin data about a symbol from coingecko,
    extract & save exchange data as well.
    
    Args:
        coin_id: Coin identifier in coingecko (not necessarily the symbol)
        refresh: Refresh data even if cached
        write_ex_only: Save only exchange info instead of full data
    """

    exchange_info = {}
    
    fname_exchangedata = f"data/exchangedata/{id}.json"
    fname_coindata = f"data/coindata/{id}.json"

    if os.path.exists(fname_exchangedata) and os.path.exists(fname_coindata):
        if not refresh:
            log_ok(f"{id}: exchange & coin data already exist, and refresh is not set, loading from file.")

            coindata = {}
            exchangedata = {}
            try:
                with open(fname_coindata, "rt") as f:
                    coindata = json.load(f)
            except Exception:
                print(f'warning, could not load coindata from {fname_coindata}')

            try:
                with open(fname_exchangedata, "rt") as f:
                    exchangedata = json.load(f)
            except Exception:
                print(f'warning, could not load coindata from {fname_coindata}')

            return coindata, exchangedata
        else:
            log_info(f"{id}: exchange data already exist but refresh is set.")
        
    
    url = f"https://api.coingecko.com/api/v3/coins/{id}"
    headers = {
        "accept": "application/json",
        "x-cg-demo-api-key": config.get("COINGECKO_API_KEY", os.getenv("COINGECKO_API_KEY")),
    }
    r = requests.get(url, headers=headers)
    if r.ok:
        try:
            data = json.loads(r.text)
            ticker_info = data.get("tickers")
            es = list()
            for ei in ticker_info:
                es.append(ei.get("market").get("name"))
            exchange_info = {id: list(set(es))}
            with open(fname_exchangedata, "w", encoding="utf-8") as f:
                json.dump(exchange_info, f, indent=2)
            if len(exchange_info) > 0:
                log_ok(f"saved exchange info of {id} to file {fname_exchangedata}")
            else:
                log_fail(f"saved empty exchange info of {id} to file {fname_exchangedata} (not found)")
        
            # save complete coin data separately
            if not os.path.exists(fname_coindata) and not write_ex_only:
                with open(fname_coindata, "w", encoding="utf-8") as f2:
                    json.dump(data, f2, indent=2)

        except Exception as e:
                    log_fail(f":( could not write coin/exchange data to file: {e.args[0]}")

    else:
        log_fail(f"got {r.status_code} ({r.reason}), exiting")

    return data, exchange_info



def get_coins_markets_all(fname: str) -> list :
    """gets the raw list of coins from coingecko & writes it into the file fname
    """

    
    base_url = "https://api.coingecko.com/api/v3/coins/markets"
    # https://docs.coingecko.com/v3.0.1/reference/coins-markets

    payload = {
        'x_cg_demo_api_key'         : config.get("COINGECKO_API_KEY", os.getenv("COINGECKO_API_KEY")),
        'vs_currency'               : 'usd', 
        'price_change_percentage'   : "24h",
        'per_page'                  : "250",
        'page'                      : 0
        }

    headers = {
        "accept"                    : "application/json"
        }

    coins = []
    num_coins = -1

    while True:
        try: 
            r = requests.get(base_url, headers=headers, params=payload)
            total_coins = r.headers.get('total', 20000)
            if num_coins >= int(total_coins):
                print("finished gathering coins :)")
                break
            if not r.ok:
                if r.status_code == 429:
                    reset_header = r.headers.get('x-ratelimit-reset')
                    if reset_header:
                        reset_time = datetime.strptime(reset_header, '%Y-%m-%d %H:%M:%S %z')
                        now = datetime.now(timezone.utc)
                        seconds_to_wait = int((now - reset_time).total_seconds()) + 5
                        if seconds_to_wait > 0:
                            print(f"rate limit hit. sleeping for {seconds_to_wait} seconds.")
                            time.sleep(seconds_to_wait)
                    else:
                        # fallback if header is missing
                        print("rate limit hit. sleeping for 60 seconds.")
                        time.sleep(60)
                    continue
                sys.exit(f"got {r.status_code} ({r.reason}), exiting")
            try:
                r_json = r.json()
            except json.JSONDecodeError as j:
                sys.exit(f"got {j}, exiting")
            coins.extend(r_json)
            if len(coins) <= num_coins:
                print("finished gathering coins :)")
                break
            payload['page'] += 1
            num_coins = len(coins)
            print(f"coins so far: {num_coins} (page{payload['page']})")
        except Exception as e:
            print(f"unhandled error: {e}")
            print(f"{len(coins)=}")
            break

    if len(coins) > 0:
        try:
            with open(fname, "w", encoding="utf-8") as f:
                json.dump(coins, f, indent=2)
            print(f"success writing coin list into a file {fname}")
        except Exception as e:
            print(f"failed writing coin list into a file: {e}")

    return coins

    


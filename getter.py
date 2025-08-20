from os import getenv
import sys
import time
import json
import datetime
from typing import Any
from pathlib import Path

import requests
from dotenv import dotenv_values
from tenacity import retry, stop_after_attempt, wait_random_exponential

from utils.clog import log_info, log_fail, log_ok, log_task


config = dotenv_values('.env')
HTTP_STATUS_CODE_RATELIMIT = 429


def market_scan(fname_coins: str) -> list[dict]:
    """Get all coin market data from coingecko."""
    if not Path(fname_coins).exists():
        log_task('we dont have data for today, getting coins')
        coins = get_coins_markets_all(fname_coins)
    else:
        log_ok('we already have the data for today, lets just open it :)')
        try:
            coins = json.loads(Path(fname_coins).read_text())
        except Exception as e:
            log_fail(f':( could not read coins from file: {e.args[0]}')
            return None

    return coins


@retry(stop=(stop_after_attempt(6)), wait=wait_random_exponential(min=1, max=60))
def get_coindata(coin_id: str, refresh: bool = False, write_ex_only: bool = False) -> tuple[Any, dict[str, list[Any]]]:
    """Get all detailed coin data about a symbol from coingecko.

    extract & save exchange data as well.

    Args:
        coin_id: Coin identifier in coingecko (not necessarily the symbol)
        refresh: Refresh data even if cached
        write_ex_only: Save only exchange info instead of full data

    """
    exchange_info = {}
    fname_exchangedata = f'data/exchangedata/{coin_id}.json'
    fname_coindata = f'data/coindata/{coin_id}.json'

    ioerror = False # true if file-reading was not successful

    if Path(fname_exchangedata).exists() and Path(fname_coindata).exists():
        if not refresh:
            log_ok(f'{coin_id}: exchange & coin data already exist, and refresh is not set, loading from file.')

            coindata = {}
            exchangedata = {}
            try:
                coindata = json.loads(Path(fname_coindata).read_text())
            except Exception as e:
                log_fail(f'warning, could not load coindata from {fname_coindata}. Error: {e}')
                ioerror = True

            try:
                exchangedata = json.loads(Path(fname_exchangedata).read_text())
            except Exception as e:
                log_fail(f'warning, could not load coindata from {fname_coindata}. Error: {e}')
                ioerror = True

            if not ioerror:
                return coindata, exchangedata

        log_info(f'{coin_id}: exchange data already exist but refresh is set.')

    url = f'https://api.coingecko.com/api/v3/coins/{coin_id}'
    headers = {
        'accept': 'application/json',
        'x-cg-demo-api-key': config.get('COINGECKO_API_KEY', getenv('COINGECKO_API_KEY')),
    }
    r = requests.get(url, headers=headers, timeout=60)

    if not r.ok:
        log_fail(f'got {r.status_code} ({r.reason}), exiting')
        return None, None

    try:
        data = json.loads(r.text)
        ticker_info = data.get('tickers')
        es = {ei.get('market').get('name') for ei in ticker_info}
        exchange_info = {coin_id: list(es)}

        Path(fname_exchangedata).write_text(json.dumps(exchange_info, indent=2))

        if exchange_info:
            log_ok(f'saved exchange info of {coin_id} to file {fname_exchangedata}')
        else:
            log_fail(f'saved empty exchange info of {coin_id} to file {fname_exchangedata} (not found)')

        # save complete coin data separately
        if not Path(fname_coindata).exists() and not write_ex_only:
            Path(fname_coindata).write_text(json.dumps(data, indent=2))
    except Exception as e:
        log_fail(f':( could not write coin/exchange data to file: {e.args[0]}')


    return data, exchange_info


def get_coins_markets_all(fname: str) -> list[dict]:
    """Get the raw list of coins from coingecko & writes it into the file fname."""
    base_url = 'https://api.coingecko.com/api/v3/coins/markets'
    # https://docs.coingecko.com/v3.0.1/reference/coins-markets

    payload = {
        'x_cg_demo_api_key': config.get('COINGECKO_API_KEY') or getenv('COINGECKO_API_KEY'),
        'vs_currency': 'usd',
        'price_change_percentage': '24h',
        'per_page': '250',
        'page': 0,
    }

    coins = []
    num_coins = -1

    while True:
        try:
            r = requests.get(base_url, headers={'accept': 'application/json'}, params=payload, timeout=60)
            total_coins = r.headers.get('total', 20000)
            if num_coins >= int(total_coins):
                log_ok('finished gathering coins :)')
                break

            if not r.ok:
                if r.status_code == HTTP_STATUS_CODE_RATELIMIT:
                    if reset_header := r.headers.get('x-ratelimit-reset'):
                        reset_time = datetime.datetime.strptime(reset_header, '%Y-%m-%d %H:%M:%S %z')
                        now = datetime.datetime.now(datetime.UTC)
                        seconds_to_wait = int((now - reset_time).total_seconds()) + 5
                        if seconds_to_wait > 0:
                            log_info(f'rate limit hit. sleeping for {seconds_to_wait} seconds.')
                            time.sleep(seconds_to_wait)
                    else:
                        # fallback if header is missing
                        log_info('rate limit hit. sleeping for 60 seconds.')
                        time.sleep(60)
                    continue
                sys.exit(f'got {r.status_code} ({r.reason}), exiting')

            try:
                r_json = r.json()
            except json.JSONDecodeError as exc:
                sys.exit(f'got {exc}, exiting')

            coins.extend(r_json)

            if len(coins) <= num_coins:
                log_ok('finished gathering coins :)')
                break

            payload['page'] += 1
            num_coins = len(coins)
            log_ok(f"coins so far: {num_coins} (page{payload['page']})")
        except Exception as e:
            log_fail(f'unhandled error: {e}')
            log_fail(f'{len(coins)=}')
            break

    if coins:
        Path(fname).write_text(json.dumps(coins, indent=2))
        log_ok(f'success writing coin list into a file {fname}')

    return coins

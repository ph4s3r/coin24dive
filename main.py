# pypi
import os
import json
from pathlib import Path
from datetime import datetime

# local
import diver
import getter
from llm.llm_analyze import llm_analytics
from notifications import notificationsClass
from utils.clog import log_task
from utils.display_rich_table import display_table


def main():
   
    print("*"*20, "COINGECKO MARKET SCANNER", "*"*20)
    
    # creating directories
    os.makedirs("data", exist_ok=True)
    os.makedirs("data/dives", exist_ok=True)
    os.makedirs("data/coindata", exist_ok=True)
    os.makedirs("data/exchangedata", exist_ok=True)
    os.makedirs("data/analytics", exist_ok=True)
    today_date = datetime.now().strftime('%Y%m%d')
    os.makedirs(f"data/analytics/{today_date}", exist_ok=True)

    # declaring filenames
    fname_coins         = f"data/marketdata/coins{today_date}.json"
    fname_dives         = f"data/dives/dives{today_date}.json"
    analytics_folder    = 'data/analytics'

    ##########################################################################
    # EXECUTING TASKS ########################################################
    ##########################################################################


    log_task("Daily market scanning")
    coins: list = getter.market_scan(fname_coins)


    log_task("Searching for coins with specific criteria")
    top_divers: dict = diver.diver(fname_dives, coins, min_dive_percentage=-75)


    log_task("Getting detailed coin data for each coin")
    coinmetrics_full = []   # all detailed data about every coin: in a list
    # adding the exchange info & detailed coin data to the top_divers
    for diver_key, diver_data in top_divers.items():
        coindata, ex_inf = getter.get_coindata(diver_key, refresh=False)
        top_divers[diver_key] = diver_data + (ex_inf.get(diver_key),)
        coinmetrics_full.append(coindata)


    log_task("Analyzing the top divers with LLM")
    dead_scores = llm_analytics(coinmetrics_full, analytics_folder, today_date)


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


    log_task("Display Results")
    display_table(top_divers, dead_scores)


    log_task("Filter coins by dead score and send notifications")
    nc = notificationsClass()
    for coin_id, ex_data in top_divers.items():
        if dead_scores.get(coin_id, 10) < 7:
            nc.add_to_notifications(
                coin_id,                                                # coingecko id
                str(ex_data[1]) + '%',                                  # drop_percent
                'deadscore: ' + str(dead_scores.get(coin_id, '?')),     # dead score
                str(ex_data[2])                                         # exchange info
            )


    # will not send empty message
    nc.send_notifications()

if __name__ == '__main__':
    main()

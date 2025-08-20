"""Main entry point of the project; executes tasks in a sequence like getting data and working with it.

author: Peter Karacsonyi
date:   8/20/2025
"""

from pathlib import Path
import datetime

from diver import diver, dead_score_filter
from getter import market_scan, get_coindata
from llm.llm_analyze import llm_analytics
from notifications import PushoverMessage
from utils.clog import log_task
from utils.display_rich_table import display_table


def main() -> None:
    """Execute the tasks of gathering data & processing it."""
    print(f"{' COINGECKO MARKET SCANNER ':*^66}")  # noqa: T201

    # creating directories
    now = datetime.datetime.now(datetime.UTC)
    today_date = now.strftime('%Y%m%d')
    directories = [
        'data',
        'data/dives',
        'data/coindata',
        'data/exchangedata',
        'data/analytics',
        f'data/analytics/{today_date}']
    [Path(_).mkdir(exist_ok=True, parents=True) for _ in directories]

    # declaring filenames
    fname_coins = f'data/marketdata/coins{today_date}.json'
    fname_dives = f'data/dives/dives{today_date}.json'
    analytics_folder = 'data/analytics'

    ##########################################################################
    # EXECUTING TASKS ########################################################
    ##########################################################################

    log_task('Daily market scanning')
    all_coingecko_coins: list = market_scan(fname_coins)


    log_task('Searching for coins with specific criteria')
    top_divers: dict = diver(fname_dives, all_coingecko_coins, min_dive_percentage=-75)


    log_task('Getting detailed coin data for each coin')
    coinmetrics_full = []   # all detailed data about every coin: in a list
    # adding the exchange info & detailed coin data to the top_divers
    for diver_key, diver_data in top_divers.items():
        coindata, ex_inf = get_coindata(diver_key, refresh=False)
        top_divers[diver_key] = (*diver_data, ex_inf.get(diver_key))
        coinmetrics_full.append(coindata)


    log_task('Analyzing the top divers with LLM')
    dead_scores = llm_analytics(coinmetrics_full, analytics_folder, today_date)


    log_task('Display Results')
    display_table(top_divers, dead_scores)


    log_task('Filter coins by dead score and send notifications')
    notifications: PushoverMessage = PushoverMessage()
    # creating message content from the filtered coin list
    dead_score_filter(
        top_divers, notifications, dead_scores, dead_score_maximum=7,
    )
    notifications.send_notifications()


if __name__ == '__main__':
    main()

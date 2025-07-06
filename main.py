import os
import json
import diver
import getter
from datetime import datetime

from notifications import notificationsClass
from utils.clog import log_info, log_fail, log_ok, log_task

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
        top_divers = diver.diver(fname_dives, coins, min_dive_percentage=-45)

    log_task("Getting coin exchange information for each coin")

    top_divers_full = []
    top_divers = set(top_divers)

    # enriching the coin data with exchange information
    for d in top_divers:
        coin_id = d[0]
        ex_inf = getter.get_ex_inf(coin_id, refresh=False)
        t = list(d)
        t.extend(ex_inf.get(coin_id))
        top_divers_full.append(t)

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

    nc.send_notifications()

    


if __name__ == '__main__':
    main()

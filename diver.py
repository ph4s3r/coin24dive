import json

from utils.clog import log_info, log_fail, log_ok

def diver(fname: str, coins: list, min_dive_percentage: int):

    log_info(f"criteria: coins dropped at least {abs(int(min_dive_percentage))}% in the last 24h")
    top_divers = []

    for coin in coins:
        if (change := coin.get("price_change_percentage_24h", 42)) is not None and change < min_dive_percentage:
            top_divers.append((coin.get("id", "N/A"), coin.get("symbol", "N/A"), int(change)))

    bd_sorted = sorted(top_divers, key=lambda x: x[1])
    if len(bd_sorted) > 0:
        log_ok(f"found {len(bd_sorted)} coins matching the criteria. returning only the top 20")
    else:
        log_fail("not found any coins matching the criteria")

    try:
        with open (fname, "w") as f:
            json.dump(bd_sorted[:20], f, indent=2)
        log_ok(f"success writing top 20 dives list into a file {fname}")
    except Exception as e:
        log_fail(f"failed writing top 20 dives list into a file: {e}")

    return bd_sorted[:20]

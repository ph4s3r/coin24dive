import sys
import json

from utils.clog import log_info, log_fail, log_ok


def diver(fname: str, coins: list, min_dive_percentage: int) -> dict[tuple[str, str]]:
    ''' filtering a list of coins based on a criteria'''
    if not coins:
        sys.exit('no coins to analyze this time! Exiting')

    log_info(f'criteria: coins dropped at least {abs(int(min_dive_percentage))}% in the last 24h')
    top_divers = []

    for coin in coins:
        if (change := coin.get('price_change_percentage_24h')) and change < min_dive_percentage:
            top_divers.append((coin.get('id', 'N/A'), coin.get('symbol', 'N/A'), int(change)))

    bd_sorted = sorted(top_divers, key=lambda x: x[1])

    if bd_sorted:
        log_ok(f'found {len(bd_sorted)} coins matching the criteria. returning only the top 20')
    else:
        log_fail('not found any coins matching the criteria')

    try:
        with open(fname, 'w', encoding='utf-8') as f:
            json.dump(bd_sorted[:20], f, indent=2)
        log_ok(f'success writing top 20 dives list into a file {fname}')
    except Exception as e:
        log_fail(f'failed writing top 20 dives list into a file: {e}')

    bd_dict = {k: (v1, v2) for k, v1, v2 in bd_sorted[:20]}

    return bd_dict

def dead_score_filter(
        top_divers: dict,
        notifications, 
        dead_scores,
        dead_score_maximum: int = 7
    ):
    '''enriches the notification list (notifications) with coins filtered by a certain dead score limit'''
    for coin_id, ex_data in top_divers.items():
        if dead_scores.get(coin_id, 10) <= dead_score_maximum:
            notifications.add_to_notifications(
                coin_id,  # coingecko id
                str(ex_data[1]) + "%",  # drop_percent
                "deadscore: " + str(dead_scores.get(coin_id, "?")),  # dead score
                str(ex_data[2]),  # exchange info
            )

    return notifications
    

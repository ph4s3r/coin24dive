"""Filtering list of coins based on specific criteria.

author: Peter Karacsonyi
date:   8/20/2025
"""

# pypi
import sys
import json
from pathlib import Path
from operator import itemgetter

# local
from notifications import PushoverMessage
from utils.clog import log_info, log_fail, log_ok


def diver(fname: str, coins: list, min_dive_percentage: int) -> dict[tuple[str, str]]:
    """Filter a list of coins based on a criteria."""
    if not coins:
        sys.exit('no coins to analyze this time! Exiting')

    log_info(
        f'criteria: coins dropped at least {abs(int(min_dive_percentage))}% in the last 24h',
    )
    divers = []

    for coin in coins:
        if (
            change := coin.get('price_change_percentage_24h')
        ) and change < min_dive_percentage:
            divers.append(
                (coin.get('id', 'N/A'), coin.get('symbol', 'N/A'), int(change)),
            )

    if divers:
        log_ok(
            f'found {len(divers)} coins matching the criteria. returning only the top 10',
        )
    else:
        log_fail('not found any coins matching the criteria')
        return None

    divers_sorted: list = sorted(divers, key=itemgetter(1))
    top_divers: dict = {k: (v1, v2) for k, v1, v2 in divers_sorted[:10]}

    try:
        Path(fname).write_text(json.dumps(top_divers, indent=2))
        log_ok(f'success writing top 10 dives list into a file {fname}')
    except Exception as e:
        log_fail(f'failed writing top 10 dives list into a file: {e}')

    return top_divers


def dead_score_filter(
    notifications: PushoverMessage,
    top_divers: dict,
    dead_scores: dict,
    dead_score_maximum: int = 7,
) -> None:
    """Enrich the notification list (notifications) with coins filtered by a certain dead score limit."""
    for coin_id, ex_data in top_divers.items():
        if dead_scores.get(coin_id, 10) <= dead_score_maximum:
            notifications.add_to_notifications(
                coin_id,  # coingecko id
                str(ex_data[1]) + '%',  # drop_percent
                'deadscore: ' + str(dead_scores.get(coin_id, '?')),  # dead score
                str(ex_data[2]),  # exchange info
            )

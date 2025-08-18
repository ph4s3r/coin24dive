from rich.console import Console
from rich.table import Table


def display_table(top_divers, dead_scores):
    """Configure console table."""
    console = Console()
    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("ID", width=20)
    table.add_column("Symbol", width=10)
    table.add_column("Dead Score", justify="right")
    table.add_column("24h Change", justify="right")
    table.add_column("Exchanges",  no_wrap=False)

    for coin_id, ex_data in top_divers.items():
        chg = float(ex_data[1])
        # redder if drop is bigger
        color = f"rgb(255,{max(0,int(255 + chg * 2.5))},{max(0, int(255 + chg * 2.5))})"
        table.add_row(
            coin_id,
            ex_data[0],
            str(dead_scores.get(coin_id, "?")),
            f"[{color}]{ex_data[1]}%[/]",
            ", ".join(ex_data[2])
        )

    console.print(table)

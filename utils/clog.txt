'''
helper functions to log information using click

Author: Peter Karacsonyi
Email: peter.karacsonyi@gs.com
Date: 13/06/2025
'''
import os

import click


try:
    TERMWIDTH = os.get_terminal_size().columns
except OSError:
    TERMWIDTH = 80  # Default width for non-interactive environments


def log_info(text: str) -> None:
    click.echo(
        click.style(
            f"info: {text}",
            fg="bright_yellow",
        )
    )

def log_ok(text: str) -> None:
    click.echo(
        click.style(
            f"ok: {text}",
            fg="green"            
        )
    )


def log_fail(text: str) -> None:
    click.echo(
        click.style(
            f"fail: {text}",
            fg="red",
        )
    )


def log_task(text: str) -> None:
    stars = TERMWIDTH - len(text) - 9

    click.echo(
        click.style(
            f"\r\nTASK: [{text.upper()}] " + "*" * stars,
            fg="blue",
            bold=True
        )
    )

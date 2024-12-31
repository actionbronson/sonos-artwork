from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable

import time
from urllib.parse import parse_qs, urlparse

import flet as flt
from flet_timer.flet_timer import Timer
from typer import Typer

from sonos.utils import change_volume, get_hostname, get_zone_details, load_config

logger = logging.getLogger(__name__)

app = Typer()


def generate_volume_action(increment: int):
    def toggle_icon_button(e: flt.TapEvent) -> None:
        control: flt.Control = e.control
        control.selected = True
        control.update()
        time.sleep(0.2)
        change_volume(increment)
        control.selected = False
        control.update()

    return toggle_icon_button


def guess_artwork(config: dict, current_track: dict) -> str | None:
    album_art_uri = current_track.get("albumArtUri")

    if 'sonosradio' in album_art_uri:
        parsed_url = urlparse(album_art_uri)
        url = parse_qs(parsed_url.query)["mark"][0]
    else:
        hostname = config['zones'][0]['hostname']  # get the first controlled sonos zone
        logger.info("albumArtUri is '%s'", album_art_uri)
        url = f'http://{get_hostname(hostname)}:1400{album_art_uri}'

    logger.info("Will resolve from url '%s'", url)
    return url


def whats_playing(config: dict) -> dict:
    zones = [z["name"] for z in config["zones"]]
    if zones:
        details = get_zone_details(zones)
        if details:
            state = details[zones[0]]["state"]
            if "currentTrack" in state:
                return state["currentTrack"]
    return {}


def flet_app_updater(config_file: str | None = None) -> Callable[..., None]:
    config = load_config(config_file)

    def update_sonos_app(page: flt.Page) -> None:
        page.window.height = config["display"]["height"]
        page.window.width = config["display"]["width"]
        page.window.title_bar_hidden = True

        def refresh() -> flt.Container:
            track = whats_playing(config)
            artwork = guess_artwork(config, track)
            if page.controls:
                for control in page.controls:
                    if isinstance(control, flt.Container):
                        if artwork is None or control.image.src == artwork:
                            logger.warning("Artwork hasn't changed...")
                            return
                        page.controls.remove(control)
            container = flt.Container(
                image=flt.DecorationImage(
                    src=artwork,
                    fit=flt.ImageFit.COVER,
                ),
                expand=True,
                width=page.window.width,
                height=page.window.height,
                content=flt.Row(
                    [
                        flt.IconButton(
                            icon=flt.Icons.VOLUME_DOWN_ROUNDED,
                            on_click=generate_volume_action(-1),
                            selected=False,
                            style=flt.ButtonStyle(
                                color={
                                    "selected": flt.Colors.GREEN,
                                    "": flt.Colors.WHITE,
                                }
                            ),
                        ),
                        flt.IconButton(
                            icon=flt.Icons.VOLUME_UP_ROUNDED,
                            on_click=generate_volume_action(1),
                            selected=False,
                            style=flt.ButtonStyle(
                                color={
                                    "selected": flt.Colors.GREEN,
                                    "": flt.Colors.WHITE,
                                }
                            ),
                        ),
                    ],
                    vertical_alignment=flt.CrossAxisAlignment.END,
                    alignment=flt.MainAxisAlignment.SPACE_BETWEEN,
                ),
            )
            page.add(container)
            page.update()

        page.horizontal_alignment = flt.CrossAxisAlignment.CENTER
        page.vertical_alignment = flt.MainAxisAlignment.CENTER
        page.add(Timer(name="timer", interval_s=2, callback=refresh))
        page.update()

    return update_sonos_app


@app.command()
def run(config_file: str | None = None) -> None:
    flt.app(target=flet_app_updater(config_file))

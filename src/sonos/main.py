from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable

import functools
import socket
from urllib.parse import parse_qs, urlparse

import flet as flt
from flet_timer.flet_timer import Timer
from typer import Typer

from sonos.utils import get_zone_details, load_config

logger = logging.getLogger(__name__)

app = Typer()


@functools.cache
def get_hostname(hostname: str) -> str:
    return socket.gethostbyname(hostname)


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
                        if artwork is None or control.image_src == artwork:
                            logger.warning("Artwork hasn't changed...")
                            return
                        page.controls.remove(control)
            container = flt.Container(
                image_src=artwork,
                image_fit=flt.ImageFit.COVER,
                expand=True,
                width=page.window.width,
                height=page.window.height,
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

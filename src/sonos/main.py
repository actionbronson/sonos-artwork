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

from sonos.utils import (
    PlayAction,
    change_volume,
    control_play,
    get_hostname,
    get_status_info,
    get_zone_details,
    load_config,
)

logger = logging.getLogger(__name__)

app = Typer()


def generate_play_control_action(
    config: dict, action: PlayAction
) -> Callable[..., None]:
    def _control_play(e: flt.TapEvent) -> None:
        control: flt.Control = e.control
        control.selected = True
        control.update()
        time.sleep(0.2)
        control_play(config, action)
        control.selected = False
        control.update()

    return _control_play


def generate_volume_action(config: dict, increment: int) -> Callable[..., None]:
    def _change_volume(e: flt.TapEvent) -> None:
        control: flt.Control = e.control
        control.selected = True
        control.update()
        time.sleep(0.2)
        change_volume(config, increment)
        control.selected = False
        control.update()

    return _change_volume


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


def build_play_controls(config: dict) -> flt.Row:
    icon_height = config['display']['height'] / 4
    icon_width = config['display']['width'] / 4
    icon_size = config['display']['height'] / 6
    return flt.Row(
        controls=[
            flt.IconButton(
                icon=flt.Icons.SKIP_PREVIOUS_ROUNDED,
                on_click=generate_play_control_action(config, PlayAction.SKIP_PREVIOUS),
                selected=False,
                height=icon_height,
                width=icon_width,
                icon_size=icon_size,
                style=flt.ButtonStyle(
                    color={
                        "selected": flt.Colors.GREEN,
                        "": flt.Colors.TRANSPARENT,
                    }
                ),
            ),
            flt.IconButton(
                icon=flt.Icons.PAUSE_CIRCLE,
                on_click=generate_play_control_action(config, PlayAction.PLAY_PAUSE),
                selected=False,
                height=icon_height,
                width=icon_width,
                icon_size=icon_size,
                style=flt.ButtonStyle(
                    color={
                        "selected": flt.Colors.GREEN,
                        "": flt.Colors.TRANSPARENT,
                    }
                ),
            ),
            flt.IconButton(
                icon=flt.Icons.SKIP_NEXT_ROUNDED,
                on_click=generate_play_control_action(config, PlayAction.SKIP_NEXT),
                selected=False,
                height=icon_height,
                width=icon_width,
                icon_size=icon_size,
                style=flt.ButtonStyle(
                    color={
                        "selected": flt.Colors.GREEN,
                        "": flt.Colors.TRANSPARENT,
                    }
                ),
            ),
        ],
        alignment=flt.MainAxisAlignment.SPACE_BETWEEN,
    )


def build_current_track(config: dict) -> flt.Row:
    text = flt.Text(
        size=config['display']['height'] / 30,
        text_align=flt.TextAlign.CENTER,
        font_family="Kanit",
        color=flt.Colors.WHITE,
        expand=True,
    )

    def pretty_print(play_tuple: tuple) -> str:
        artist, album, title = play_tuple
        return f"""{artist} - {album}\n{title}"""

    def on_click(e: flt.TapEvent) -> None:
        text.value = pretty_print(get_status_info(config))
        e.control.update()
        time.sleep(3)
        text.value = None
        e.control.update()

    return flt.Row(
        height=config['display']['height'] / 3,
        alignment=flt.MainAxisAlignment.CENTER,
        vertical_alignment=flt.CrossAxisAlignment.STRETCH,
        controls=[
            flt.Container(
                content=text,
                expand=True,
                border_radius=10,
                bgcolor=flt.Colors.TRANSPARENT,
                on_click=on_click,
            )
        ],
    )


def build_volume_control_row(config: dict) -> flt.Row:
    icon_height = config['display']['height'] / 3
    icon_width = config['display']['width'] / 3
    icon_size = config['display']['height'] / 4
    return flt.Row(
        controls=[
            flt.IconButton(
                icon=flt.Icons.VOLUME_DOWN_ROUNDED,
                on_click=generate_volume_action(config, -1),
                selected=False,
                height=icon_height,
                width=icon_width,
                icon_size=icon_size,
                style=flt.ButtonStyle(
                    color={
                        "selected": flt.Colors.GREEN,
                        "": flt.Colors.TRANSPARENT,
                    }
                ),
            ),
            flt.IconButton(
                icon=flt.Icons.VOLUME_UP_ROUNDED,
                on_click=generate_volume_action(config, 1),
                selected=False,
                height=icon_height,
                width=icon_width,
                icon_size=icon_size,
                selected_icon_color=flt.Colors.GREEN,
                style=flt.ButtonStyle(
                    color={
                        "selected": flt.Colors.GREEN,
                        "": flt.Colors.TRANSPARENT,
                    }
                ),
            ),
        ],
        vertical_alignment=flt.CrossAxisAlignment.END,
        alignment=flt.MainAxisAlignment.SPACE_BETWEEN,
    )


def flet_app_updater(config_file: str | None = None) -> Callable[..., None]:
    config = load_config(config_file)

    def update_sonos_app(page: flt.Page) -> None:
        page.window.height = config["display"]["height"]
        page.window.width = config["display"]["width"]
        page.window.title_bar_hidden = True
        page.fonts = {
            "Kanit": "https://raw.githubusercontent.com/google/fonts/master/ofl/kanit/Kanit-Bold.ttf",
            "Inter": "https://raw.githubusercontent.com/google/fonts/main/ofl/inter/Inter%5Bopsz%2Cwght%5D.ttf",
        }

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
                content=flt.Column(
                    alignment=flt.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        build_play_controls(config),
                        build_current_track(config),
                        build_volume_control_row(config),
                    ],
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

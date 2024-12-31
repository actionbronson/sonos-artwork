from __future__ import annotations

import functools
import logging
import socket
from enum import Enum
from pathlib import Path
from typing import Any

import requests
import yaml

logging.basicConfig(
    level="INFO",
    format="%(asctime)s %(levelname)s %(filename)s %(message)s",
)
logger = logging.getLogger(__name__)


class PlayAction(Enum):
    SKIP_PREVIOUS = "previous"
    PLAY_PAUSE = "playpause"
    SKIP_NEXT = "next"


@functools.cache
def load_config(config_file: str | None = None) -> dict[str, Any] | None:
    filename = (
        config_file
        if config_file
        else Path(__file__).resolve().parent / "etc" / "settings.yaml"
    )
    logger.info("Loading config file from '%s'", filename)
    with open(filename) as stream:
        try:
            settings: dict[str, Any] = yaml.safe_load(stream)
        except yaml.YAMLError:
            logger.exception("Error parsing yaml file: '%s'", filename)
        else:
            return settings
    return None


def get_enabled_zone_names(config: dict) -> set[str]:
    zone_names = [z['name'] for z in config.get('zones', [])]
    return set(get_zone_details(config, zone_names).keys())


def get_zone_details(config: dict, zones: list[str] | None = None) -> dict[str, Any]:
    def is_wanted_zone(zone: str) -> bool:
        return True if not zones else zone in zones

    config = load_config()
    url = f"{config['endpoint']}/zones"
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    zones_json = resp.json()
    return {
        zone["roomName"]: zone
        for zone_json in zones_json
        for zone in zone_json["members"]
        if is_wanted_zone(zone["roomName"])
    }


def get_status_info(config: dict) -> tuple:
    zones = get_enabled_zone_names(config)
    zone_details = get_zone_details(config, zones)
    if zone_details:
        zone_data = next(iter(zone_details.values()))
        if 'currentTrack' in zone_data['state']:
            artist, title, album = (
                zone_data['state']['currentTrack'][x]
                for x in ['artist', 'album', 'title']
            )
            logger.info(
                "Retrieved artist: '%s', album: '%s', title: '%s'", artist, album, title
            )
            return (artist, album, title)
    return None


def control_play(config: dict, action: PlayAction) -> bool:
    for zone in get_enabled_zone_names(config):
        url = f"""{config['endpoint']}/{zone}/{action.value}"""
        logger.info("Issuing a play control: '%s'.  Url is '%s'", action.name, url)
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        resp_json = resp.json()
        if resp_json['status'] != 'success':
            logger.error("Response was not a success.  Received: %s", resp_json)
            return False
    return True


def change_volume(config: dict, increment: int) -> bool:
    for zone in get_enabled_zone_names(config):
        url_vol_increment: str = f"+{increment}" if increment > 0 else str(increment)
        url = f"""{config['endpoint']}{zone}/volume/{url_vol_increment}"""
        logger.info(
            "Volume in zone: '%s' changing by %d.  Url is '%s'", zone, increment, url
        )
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        resp_json = resp.json()
        if resp_json['status'] != 'success':
            logger.error("Response was not a success.  Received: %s", resp_json)
            return False
    return True


@functools.cache
def get_hostname(hostname: str) -> str:
    return socket.gethostbyname(hostname)

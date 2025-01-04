import json
from unittest import mock

from sonos.utils import (
    get_enabled_zone_names,
    get_hostname,
    get_zone_details,
    load_config,
)

config = load_config('src/sonos/etc/settings.yaml')


class MockResponse:
    def __init__(self, json_data, status_code):
        self.json_data = json_data
        self.status_code = status_code

    def json(self):
        return self.json_data

    def raise_for_status(self):
        pass


def gen_mocked_req(url: str, file_name: str):
    def mocked_requests_get(*args, **kwargs) -> MockResponse:
        def from_file(file_name: str) -> dict:
            with open(file_name) as file:
                return json.load(file)

        if args[0] == url:
            return MockResponse(from_file(f'tests/sonos/resources/{file_name}'), 200)

        return MockResponse(None, 404)

    return mocked_requests_get


def test_load_config():
    config = load_config('src/sonos/etc/settings.yaml')
    assert config is not None and isinstance(config, dict)


def test_load_config_no_file():
    config = load_config()
    assert config is not None and isinstance(config, dict)


def test_get_hostname():
    assert get_hostname('SonosKitchen') is not None


@mock.patch(
    'sonos.utils.requests.get',
    side_effect=gen_mocked_req(f"{config['endpoint']}/zones", "zones_not_playing.json"),
)
def test_get_zone_details_not_playing(_):
    config = load_config()
    details = get_zone_details(config)
    assert len(details.keys()) == 7


@mock.patch(
    'sonos.utils.requests.get',
    side_effect=gen_mocked_req(f"{config['endpoint']}/zones", "zones_all_playing.json"),
)
def test_get_zone_details(_):
    config = load_config()
    details = get_zone_details(config, ['Kitchen'])
    assert len(details.keys()) == 1

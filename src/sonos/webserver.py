import logging
import socket
import threading
from typing import Literal

import requests
from flask import Flask, jsonify, request
from flask.wrappers import Response

logger = logging.getLogger(__name__)


def run_flask_app(config: dict, event: threading.Event):
    port = config['webhook']['port']
    registrar = config['webhook']['registrar']
    flask_app = Flask('sonos-artwork')

    @flask_app.route("/webhook", methods=["POST"])
    def webhook() -> tuple[Response, Literal[200]]:
        data = request.json
        logger.info("Embedded flask app, received a webhook: '%s'", data)
        if data.get('type') == 'transport-state':
            logger.info("Received a transport-state change.")
            event.set()
        return jsonify(isError=False, message="Success", statusCode=200), 200

    ip_address = socket.gethostbyname(socket.gethostname())
    try:
        resp = requests.post(
            registrar,
            json={'host': ip_address, 'port': port},
            headers={'content-type': 'application/json'},
            timeout=10,
        )
        resp.raise_for_status()
        logger.info(
            "Registered %s:%d with registrar: %s.  Now starting Flask server.",
            ip_address,
            port,
            registrar,
        )
    except Exception:
        logger.exception("Could not register with the registrar.")
    flask_app.run(host=ip_address, port=port, use_reloader=False)

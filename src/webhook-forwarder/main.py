import json
import logging

import aiohttp
from fastapi import FastAPI

logging.basicConfig(
    level="INFO",
    format="%(asctime)s %(levelname)s %(filename)s %(message)s",
)
logger = logging.getLogger('uvicorn.error')

app = FastAPI()

registered = set()


@app.post("/webhook")
async def web_hook(data: dict) -> None:
    logger.info("Received data: '%s'.  Looping over registered: '%s'", data, registered)
    for url in registered:
        logger.info("Sending POST to url '%s', data: '%s'", url, json.dumps(data))
        async with aiohttp.ClientSession() as session:
            if url != '':
                try:
                    async with session.post(
                        url,
                        data=json.dumps(data),
                        headers={'content-type': 'application/json'},
                    ) as resp:
                        resp.raise_for_status()
                except Exception:
                    logger.exception("Could not forward to URL '%s'", url)


@app.post("/echo")
async def echo(data: dict) -> None:
    logger.info("Echoing back data: '%s'", data)


@app.post("/register")
async def register(data: dict) -> None:
    logger.info("Registering host: '%s', port: '%d'", data['host'], data['port'])
    registered.add(f"http://{data['host']}:{data['port']}/webhook")
    return 200

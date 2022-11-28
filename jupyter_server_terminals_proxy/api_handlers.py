import json
from pathlib import Path
from typing import Optional

import httpx
from tornado import web

from jupyter_server.auth.decorator import authorized
from jupyter_server.base.handlers import APIHandler


AUTH_RESOURCE = "terminals"


class TerminalAPIHandler(APIHandler):
    auth_resource = AUTH_RESOURCE


class TerminalRootHandler(TerminalAPIHandler):
    @web.authenticated
    @authorized
    async def get(self):
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.settings['proxy_url']}/api/terminals")
        self.set_status(response.status_code)
        self.finish(response.text)

    @web.authenticated
    @authorized
    async def post(self):
        data = self.get_json_body() or {}
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{self.settings['proxy_url']}/api/terminals", data=data)
        self.set_status(response.status_code)
        self.finish(response.json())


class TerminalHandler(TerminalAPIHandler):
    SUPPORTED_METHODS = ("GET", "DELETE")  # type:ignore[assignment]

    @web.authenticated
    @authorized
    async def get(self, name):
        url = f"{self.settings['proxy_url']}/api/terminals/{name}"
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
        self.set_status(response.status_code)
        self.finish(response.json())

    @web.authenticated
    @authorized
    async def delete(self, name):
        url = f"{self.settings['proxy_url']}/api/terminals/{name}"
        async with httpx.AsyncClient() as client:
            response = await client.delete(url)
        self.set_status(response.status_code)
        self.finish()


default_handlers = [
    (r"/api/terminals", TerminalRootHandler),
    (r"/api/terminals/(\w+)", TerminalHandler),
]

import asyncio

from tornado.websocket import WebSocketHandler
from tornado import web
from websockets import connect

from jupyter_server._tz import utcnow
from jupyter_server.auth.utils import warn_disabled_authorization
from jupyter_server.base.handlers import JupyterHandler

AUTH_RESOURCE = "terminals"


class TermSocket(WebSocketHandler, JupyterHandler):

    auth_resource = AUTH_RESOURCE

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.websocket = None

    def origin_check(self):
        return True

    def get(self, *args, **kwargs):
        user = self.current_user

        if not user:
            raise web.HTTPError(403)

        # authorize the user.
        if not self.authorizer:
            # Warn if an authorizer is unavailable.
            warn_disabled_authorization()
        elif not self.authorizer.is_authorized(self, user, "execute", self.auth_resource):
            raise web.HTTPError(403)

        return super().get(*args, **kwargs)

    async def open(self, name):
        proxy_url = self.settings['proxy_url']
        ws_url = "ws" + proxy_url[proxy_url.find(":"):]
        self.websocket = await connect(f"{ws_url}/terminals/websocket/{name}")
        asyncio.create_task(self.process_message())

    async def on_message(self, message):
        await self.websocket.send(message)
        self._update_activity()

    async def process_message(self):
        while True:
            try:
                message = await self.websocket.recv()
                self.write_message(message, binary=False)
                self._update_activity()
            except Exception:
                break

    def on_close(self):
        asyncio.create_task(self.websocket.close())
        self.websocket = None

    def _update_activity(self):
        self.application.settings["terminal_last_activity"] = utcnow()

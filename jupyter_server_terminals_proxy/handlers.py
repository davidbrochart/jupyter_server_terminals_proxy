import asyncio

from anyio import Event, TASK_STATUS_IGNORED, create_task_group
from anyio.abc import TaskStatus
from httpx import AsyncClient
from httpx_ws import aconnect_ws
from tornado.websocket import WebSocketHandler
from tornado import web

from jupyter_server._tz import utcnow
from jupyter_server.auth.utils import warn_disabled_authorization
from jupyter_server.base.handlers import JupyterHandler

AUTH_RESOURCE = "terminals"


class TermSocket(WebSocketHandler, JupyterHandler):

    auth_resource = AUTH_RESOURCE

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_event = Event()
        self.stop_event = Event()

    def check_origin(self, origin):
        return True

    async def get(self, *args, **kwargs):
        user = self.current_user

        if not user:
            raise web.HTTPError(403)

        # authorize the user.
        if not self.authorizer:
            # Warn if an authorizer is unavailable.
            warn_disabled_authorization()
        elif not self.authorizer.is_authorized(self, user, "execute", self.auth_resource):
            raise web.HTTPError(403)

        return await super().get(*args, **kwargs)

    async def open(self, name):
        self._task = asyncio.create_task(self._open(name))
        await self.start_event.wait()

    async def _open(self, name):
        proxy_url = self.settings["proxy_url"]
        ws_url = "ws" + proxy_url[proxy_url.find(":"):]
        async with AsyncClient() as client:
            async with aconnect_ws(
                f"{ws_url}/terminals/websocket/{name}",
                client,
                keepalive_ping_interval_seconds=None,
                keepalive_ping_timeout_seconds=None,
            ) as self.websocket:
                async with create_task_group() as tg:
                    await tg.start(self.send_to_frontend)
                    self.start_event.set()
                    await self.stop_event.wait()
                    tg.cancel_scope.cancel()

    async def on_message(self, message):
        # receive from frontend
        try:
            await self.websocket.send_text(message)
            self._update_activity()
        except Exception:
            self.stop_event.set()

    async def send_to_frontend(self, *, task_status: TaskStatus[None] = TASK_STATUS_IGNORED):
        task_status.started()
        while True:
            try:
                message = await self.websocket.receive_text()
                self.write_message(message, binary=False)
                self._update_activity()
            except Exception:
                self.stop_event.set()
                return

    def on_close(self):
        self.stop_event.set()

    def _update_activity(self):
        self.application.settings["terminal_last_activity"] = utcnow()

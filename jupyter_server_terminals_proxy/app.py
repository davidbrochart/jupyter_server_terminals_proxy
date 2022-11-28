from jupyter_server.extension.application import ExtensionApp
from traitlets import Unicode

from . import api_handlers, handlers


class TerminalsProxyExtensionApp(ExtensionApp):

    name = "jupyter_server_terminals_proxy"

    proxy_url = Unicode(
        help="The URL from where to proxy terminals."
    ).tag(config=True)

    def initialize_settings(self):
        #self.settings.update(dict(terminals_available=True, terminal_manager=self.terminal_manager))
        self.settings.update(dict(terminals_available=True, proxy_url=self.proxy_url))

    def initialize_handlers(self):
        self.handlers.append(
            (
                r"/terminals/websocket/(\w+)",
                handlers.TermSocket,
                #{"term_manager": self.terminal_manager},
            )
        )
        self.handlers.extend(api_handlers.default_handlers)
        #self.serverapp.web_app.settings["terminal_manager"] = self.terminal_manager
        self.serverapp.web_app.settings["terminals_available"] = self.settings[
            "terminals_available"
        ]

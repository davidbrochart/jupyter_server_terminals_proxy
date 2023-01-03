from .app import TerminalsProxyExtensionApp


__version__ = "0.1.4"


def _jupyter_server_extension_points():  # pragma: no cover
    return [
        {
            "module": "jupyter_server_terminals_proxy.app",
            "app": TerminalsProxyExtensionApp,
        },
    ]

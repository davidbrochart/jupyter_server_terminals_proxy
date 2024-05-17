# Jupyter Server Terminals Proxy

In one terminal/environment:

```console
pip install jupyverse-api
pip install fps-terminals
pip install fps-noauth

# launch a terminal server at http://127.0.0.1:8000
jupyverse --port=8000
```

In another terminal/environment:

```console
pip install jupyter_server_terminals_proxy
pip install jupyterlab

# launch JupyterLab at http://127.0.0.1:8888 and proxy terminals at http://127.0.0.1:8000
jupyter lab --port=8888 --ServerApp.jpserver_extensions=jupyter_server_terminals=False --TerminalsProxyExtensionApp.proxy_url='http://127.0.0.1:8000'
```

Terminals should now be served from http://127.0.0.1:8000.

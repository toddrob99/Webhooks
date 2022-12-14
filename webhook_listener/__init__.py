#!/usr/bin/env python
"""Webhook Listener

Author: Todd Roberts

https://github.com/toddrob99/Webhooks
"""
import logging
import cherrypy
import threading
from . import version

__version__ = version.__version__


class Listener(object):
    def __init__(self, *args, **kwargs):
        self.logger = logging.getLogger("webhooks")
        self.logger.debug("Logging started!")
        self.port = kwargs.get("port", 8090)
        self.host = kwargs.get("host", "0.0.0.0")
        self.threadPool = kwargs.get("threadPool", 10)
        self.logScreen = kwargs.get("logScreen", False)
        self.autoReload = kwargs.get("autoReload", False)
        self.handlers = kwargs.get("handlers", {})
        self.sslModule = kwargs.get("sslModule", "builtin")
        self.sslCert = kwargs.get("sslCert", "")
        self.sslPrivKey = kwargs.get("sslPrivKey", "")
        self.sslCertChain = kwargs.get("sslCertChain", "")

    def start(self):
        self.WEBTHREAD = threading.Thread(
            target=self._startServer, name="webhooks_websever"
        )
        self.WEBTHREAD.daemon = True
        self.WEBTHREAD.start()

    def stop(self):
        cherrypy.engine.exit()
        self.WEBTHREAD = None

    def _startServer(self):
        globalConf = {
            "global": {
                "server.socket_host": self.host,
                "server.socket_port": self.port,
                "server.thread_pool": self.threadPool,
                "engine.autoreload.on": self.autoReload,
                "log.screen": self.logScreen,
                "server.ssl_module": self.sslModule,
                "server.ssl_certificate": self.sslCert,
                "server.ssl_private_key": self.sslPrivKey,
                "server.ssl_certificate_chain": self.sslCertChain,
            }
        }
        apiConf = {
            "/": {
                "request.dispatch": cherrypy.dispatch.Dispatcher(),
                "tools.response_headers.on": True,
                "tools.response_headers.headers": [("Content-Type", "text/plain")],
            }
        }
        cherrypy.config.update(globalConf)
        cherrypy.tree.mount(WebServer(handlers=self.handlers), "/", config=apiConf)
        cherrypy.engine.start()
        self.logger.debug(
            "Started web server on {}{}{}...".format(self.host, ":", self.port)
        )


class WebServer(object):
    def __init__(self, *args, **kwargs):
        self.logger = logging.getLogger("webhooks")
        self.handlers = {}
        for m, h in kwargs.get("handlers", {}).items():
            if callable(h):
                self.logger.debug(
                    "Registered callable object {} for the {} method.".format(h, m)
                )
                self.handlers.update({m: h})
            else:
                self.logger.error(
                    "Object {} is not callable; the {} method will not be supported.".format(
                        h, m
                    )
                )

    @cherrypy.expose()
    def default(self, *args, **kwargs):
        self.logger.debug(
            "Received {} request. args: {}, kwargs: {}".format(
                cherrypy.request.method, args, kwargs
            )
        )

        if cherrypy.request.method not in self.handlers.keys():
            # Unsupported method
            self.logger.debug("Ignoring request due to unsupported method.")
            cherrypy.response.status = 405  # Method Not Allowed
            return
        else:
            if self.handlers.get(cherrypy.request.method):
                self.logger.debug(
                    "Calling {} to process the request...".format(
                        self.handlers[cherrypy.request.method]
                    )
                )
                handler_response = self.handlers[cherrypy.request.method](
                    cherrypy.request, *args, **kwargs
                )
            else:
                self.logger.error(
                    "No handler available for method {}. Ignoring request.".format(
                        cherrypy.request.method
                    )
                )
                cherrypy.response.status = 500  # Internal Server Error
                return

        return handler_response or "OK"

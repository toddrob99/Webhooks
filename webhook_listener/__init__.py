#!/usr/bin/env python
"""
Webhook Listener

Author: Todd Roberts

https://github.com/toddrob99/Webhooks
"""
import os
import sys
import logging, logging.handlers
import cherrypy
import json
import time
import threading

__version__ = '0.0.1'

class Listener(object):
    def __init__(self, *args, **kwargs):
        self.logger = logging.getLogger('webhooks')
        self.logger.debug('Logging started!')
        self.port = kwargs.get('port', 8090)
        self.host = kwargs.get('host', '0.0.0.0')
        self.threadPool = kwargs.get('threadPool', 10)
        self.logScreen = kwargs.get('logScreen', False)
        self.autoReload = kwargs.get('autoReload', False)
        self.handlers = kwargs.get('handlers', {})

    def start(self):
        self.WEBTHREAD = threading.Thread(target=self._startServer, name='webhooks_websever', daemon=True)
        self.WEBTHREAD.start()

    def stop(self):
        cherrypy.engine.stop()
        self.WEBTHREAD = None

    def _startServer(self):
        globalConf = {
            'global' : {
                'server.socket_host' : self.host,
                'server.socket_port' : self.port,
                'server.thread_pool' : self.threadPool,
                'engine.autoreload.on' : self.autoReload,
                'log.screen': self.logScreen
            }
        }
        apiConf = {
            '/': {
                'request.dispatch': cherrypy.dispatch.Dispatcher(),
                'tools.response_headers.on': True,
                'tools.response_headers.headers': [('Content-Type', 'text/plain')]
            }
        }
        cherrypy.config.update(globalConf)
        cherrypy.tree.mount(WebServer(handlers=self.handlers), '/', config=apiConf)
        cherrypy.engine.start()
        self.logger.debug('Started web server on {}{}{}...'.format(self.host, ':', self.port))

class WebServer(object):
    def __init__(self, *args, **kwargs):
        self.logger = logging.getLogger('webhooks')
        self.handlers = {}
        for m,h in kwargs.get('handlers',{}).items():
            if callable(h):
                self.logger.debug('Registered callable object {} for the {} method.'.format(h, m))
                self.handlers.update({m : h})
            else:
                self.logger.error('Object {} is not callable; the {} method will not be supported.'.format(h, m))

    @cherrypy.expose()
    def default(self, *args, **kwargs):
        self.logger.debug('Received {} request. args: {}, kwargs: {}'.format(cherrypy.request.method, args, kwargs))

        if cherrypy.request.method not in self.handlers.keys():
            # Unsupported method
            self.logger.debug('Ignoring request due to unsupported method.')
            cherrypy.response.status = 405 # Method Not Allowed
            return
        else:
            if self.handlers.get(cherrypy.request.method):
                self.logger.debug('Calling {} to process the request...'.format(self.handlers[cherrypy.request.method]))
                self.handlers[cherrypy.request.method](cherrypy.request, *args, **kwargs)
            else:
                self.logger.error('No handler available for method {}. Ignoring request.'.format(cherrypy.request.method))
                cherrypy.response.status = 500 # Internal Server Error
                return

        return 'OK'

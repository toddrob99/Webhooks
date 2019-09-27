# Webhook Listener
Very basic webserver module to listen for webhooks and forward requests to predefined functions.

Author: Todd Roberts

https://pypi.org/project/webhook_listener/

https://github.com/toddrob99/Webhooks

## Install

Install from PyPI using pip

`pip install webhook_listener`

## Use

* Define a function to process requests
    * `request` parameter will be a cherrypy request object
    * `*args` parameter will be a tuple of URL path components
    * `**kwargs` parameter will be a dictionary of URL parameters
    * Get the body of a `POST` request from `request.body.read` passing the length of `request.headers['Content-Length']`: `request.body.read(int(request.headers['Content-Length'])) if int(request.headers.get('Content-Length',0)) > 0 else ''`

* Include webhook-listener in your project

* Create an instance of the webhook_listener.Listener class
    * handlers = Dictionary of functions/callables for each supported HTTP method. (Example: {'POST':process_post_request, 'GET':process_get_request})
    * port = Port for the web server to listen on (default: 8090)
    * host = Host for the web server to listen on (default: '0.0.0.0')
    * threadPool = Number of worker threads for the web server (default: 10)
    * logScreen = Setting for cherrypy to log to screen (default: False)
    * autoReload = Setting for cherrypy to auto reload when python files are changed (default: False)

* Start the Listener

* Keep your application running so the Listener can run in a separate thread

## Example

    import time
    import webhook_listener
    
    def process_post_request(request, *args, **kwargs):
        print('Received request:\n' + 
                    'Method: {}\n'.format(request.method) +
                    'Headers: {}\n'.format(request.headers) + 
                    'Args (url path): {}\n'.format(args) + 
                    'Keyword Args (url parameters): {}\n'.format(kwargs) + 
                    'Body: {}'.format(request.body.read(int(request.headers['Content-Length'])) if int(request.headers.get('Content-Length',0)) > 0 else '')
                )
        
        # Process the request!
        # ...
        
        return
    
    webhooks = webhook_listener.Listener(handlers={'POST':process_post_request})
    webhooks.start()
    
    while True:
        print('Still alive...')
        time.sleep(300)
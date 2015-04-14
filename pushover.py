"""
PushOverPy is a project to simplify the usage of Pushover.net's services.

While there are already a few projects in PyPi for this, this doesn't enforce using third-party libraries.

The API of Pushover is very simplistic, which aides in the development of such projects.  Also, no
scripts on PyPi currently support messages beyond the required fields, which is not always a good thing.

Why not support redis-py if possible?  It's handy and is actually quite beneficial.
"""
import httplib, urllib

class PushOver(object):
    def _block(self, txt, blocksize=512):
        import io
        iob = io.BytesIO(txt)
        
        b = None
        
        while True:
            b = iob.read1(blocksize)
            
            if b:
                yield b
            else:
                break
            
    def __init__(self, token="", key="", redis=('localhost', 6379)):
        if not token and not key:
            try:
                import redis
                
                try:
                    self.redis = redis
                    self.storage = redis.StrictRedis(host=redis[0], port=redis[1])
                    token = self.storage.get('token')
                    key = self.storage.get('key')
                except:
                    print "Unable to connect to Redis.  Ensure the redis server is installed on %s:%d" % (redis['host'], redis['port'])
            except:
                import sys
                print "Redis is not available.  Please provide a token and key."
                sys.exit(1)
                
        self.token = token
        self.key = key
                
        self.body = {"token" : token, "user" : key, "message" : ""}
    
    def store_api(self):
        try:
            import redis
            
            if not self.storage:
                self.storage = redis.StrictRedis(host=self.redis['host'], port=self.redis['port'])
            
            self.storage.set('token', self.token)
            self.storage.set('key', self.key)
        except:
            print "Redis is not installed.  Unable to save API information."
            
    """
    sendmsg()
    Sends 'msg' to PushOver's notification servers to be delievered.
    
    @param msg: The text body to send
    @param blocksize: How big of a message per call to make the request (512 is max)
    @param fmt: The format of response (JSON by standards)
    @param device: The device ID to send the push to (optional)
    @param title: The title of the push (optional)
    @param url: The URL to push to the device(s) (optional)
    @param url_title: Title of the URL (optional)
    @param priority: Priority of push (-1 = silent, 0 = normal, 1 = high) (optional)
    @param timestamp: Unix (epoch) timestamp to send the message as (optional)
    """
    def sendmsg(self, msg, blocksize=512, fmt="json", device = None, title = None, url = None, url_title = None, priority = 0, timestamp = None, html=None):
        import json

        
        if not html is None:
            self.body['html'] = 1
        conn = httplib.HTTPSConnection("api.pushover.net:443")
        
        if device:
            self.body['device'] = device
            
        # The message can only be 512 characters (title + message).  If this combined is over, adjust the blocksize.
        if title:
            header = len(title) + len(msg)
            
            if (header > 512):
                blocksize -= header
                
            self.body['title'] = title
        
        # URLs are limited to 500 characters
        if url:
            if len(url) > 500:
                url = url[:500]
                
            self.body['url'] = url
        
        # URL titles are restricted to 50 characters
        if url_title:
            if len(url_title) > 50:
                url_title = url_title[:50]
                
            self.body['url_title'] = url_title
        
        if priority != 0:
            self.body['priority'] = priority
        
        if timestamp:
            self.body['timestamp'] = timestamp
            
        for block in self._block(msg, blocksize):
            self.body['message'] = block
            
            conn.request("POST", "/1/messages.%s" % (fmt),
                         urllib.urlencode(self.body), { "Content-type" : "application/x-www-form-urlencoded"})
            
            x = conn.getresponse()
            resp = json.loads(x.read())
            
            if resp['status']:
                return True
            else:
                try:
                    return resp['errors']
                except:
                    return resp['status']

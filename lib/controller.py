from flask import redirect
from lib.router import Router

class Controller(Router):
    _abstract_ = True
    routerType = 'Controller'
    routes = {}
    method = None
    def doAuth(self):
        '''
        Return response if not authenticated or
        authorized to access the resource. Return
        nothing to pass
        '''
        raise NotImplementedError
    @classmethod
    def getNow(cls, *args, **kwargs):
        return cls().get(*args, **kwargs)
    def get(self, *args, **kwargs):
        raise NotImplementedError
    def post(self, *args, **kwargs):
        raise NotImplementedError
    def put(self, *args, **kwargs):
        raise NotImplementedError
    def delete(self, *args, **kwargs):
        raise NotImplementedError
    # flask convenience methods
    def redirect(self, url):
        return redirect(url)

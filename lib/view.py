from lib.router import Router

class View(Router):
    _abstract_ = True
    routerType = 'View'
    routes = {}

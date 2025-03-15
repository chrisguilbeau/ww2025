import importlib
from lib.controller import Controller
from lib.view import View
from lib.myflask import request
from lib.myflask import abort
from lib.myflask import app
from collections import namedtuple

modules = {}
Handler = namedtuple('Handler', 'controller view method args kwargs')

def yieldKwargs():
    # first yield any args passed on query string
    for key, value in request.args.items():
        yield key, value
    # then yield any args passed in form data
    for key, value in request.form.items():
        yield key, value
    # finally yield any args passed in json body
    if request.is_json:
        for key, value in request.json.items():
            yield key, value

def loadControllersAndViews():
    import os
    for root in ['c', 'v']:
        path = os.path.join(os.path.dirname(__file__), root)
        print('loading from', path)
        for file in os.listdir(path):
            print(file)
            if file.endswith(".py"):
                module_name = file[:-3]
                modulePath = f"{root}.{module_name}"
                modules[modulePath] = importlib.import_module(modulePath)
    print(modules)

def getRoute(router, path):
    '''
    Return longest matching route and args,
    args are extra parts not in route
    '''
    parts = path.split('/')
    route = None
    lenParts = len(parts)
    for i in range(len(parts)):
        route = '/'.join(parts[:lenParts-i])
        print('trying route', route)
        if route in router.routes:
            return route, parts[lenParts-i:]
    return None, None

def getHandler(path, method):
    print('getting handler for', path, method)
    route, args = getRoute(Controller, path)
    controller = Controller.routes.get(route)
    view = View.routes.get(route)
    method = request.method.lower()
    print(Controller.routes)
    print('using', controller, view, method)
    return Handler(controller, view, method, args, dict(yieldKwargs()))

@app.route('/', defaults={'path': ''}, methods=['GET', 'POST', 'PUT', 'DELETE'])
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def dispatcher(path):
    method = request.method.lower()
    handler = getHandler(path, method)
    doNow = handler.controller and getattr(handler.controller(), method, None)
    if doNow:
        return doNow(*handler.args, **handler.kwargs)
    else:
        return str((Controller.routes, path, handler.args, handler.kwargs))
        return abort(404)


# At the module level:
if not globals().get('_controllers_loaded'):
    loadControllersAndViews()
    _controllers_loaded = True

if __name__ == '__main__':
    app.run(
        debug=True,
        port=3000,
        )

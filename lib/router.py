class Router:
    _abstract_ = True
    routerType = 'Router'
    routes = None # must be overridden!

    @classmethod
    def _addRoute(cls, parts):
        path = '/'.join(parts)
        print('adding route', path)
        cls.routes[path] = cls
        return path

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        assert cls.routes is not None, 'Router subclass must define routes'
        if not cls.__dict__.get('_abstract_', False):
            print(f'initializing {cls.routerType} {cls.__module__}')
            parts = (*cls.__module__.split('.'), cls.__name__.lower())
            cls.url = '/' + cls._addRoute(parts[1:])
            if parts[-1] == 'index':
                cls._addRoute(parts[1:-1])


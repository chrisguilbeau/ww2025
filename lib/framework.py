from cgpy.lets      import let # noqa
from cgpy.lets      import letAs # noqa
from cgpy.lets      import returnAs # noqa
from cgpy.tags      import t
from html           import escape as html_encode
from itertools      import count
from json           import dumps as json_encode
from json           import loads as json_decode
from lib.controller import Controller

class ControllerPublic(Controller):
    @classmethod
    def clientRender(cls, url):
        id = Ids().getId()
        jsId = json_encode(id)
        jsUrl = json_encode(url)
        return t.div(
            t.img(src='/static/kappa.svg'),
            t.script(f'framework.clientRender({jsUrl}, {jsId});'),
            id=id,
            _class='flex-row-stretch flex-grow flex-center',
            style='justify-content: center;',
            )
    def doAuth(self):
        pass

class ControllerAuthN(ControllerPublic):
    user = None
    def doAuth(self):
        if not self.user:
            return self.redirect('/auth/login')

class ConttrollerAuthZ(ControllerAuthN):
    def doAuth(self):
        return super().doAuth() or self.doGroupAuth()
    def doGroupAuth(self):
        for group in self.groups:
            if group not in self.user.groups:
                return f'You are not a member of the following groups {self.groups}', 403

class Js(str):
    pass

class Ids():
    counter = count(0)
    def __init__(self):
        self.cache = {}
    def getId(self):
        print('newid!')
        return f'id_{next(Ids.counter)}'
    def __getattr__(self, name):
        if name not in self.cache:
            print('cache miss')
            self.cache[name] = self.getId()
        print('cache hit')
        return self.cache[name]

class Action(ControllerPublic):
    Ids = Ids
    @classmethod
    def getPrompt(cls, **kwargs):
        jsParams = json_encode(kwargs)
        jsUrl = json_encode(cls.url)
        return html_encode(f'''
            framework.prompt({jsUrl}, {jsParams});
            ''')
    @classmethod
    def byEval(cls, js):
        return Js(js)
    @classmethod
    def byId(cls, id):
        return Js(f'$("#{id}").val();')
    @classmethod
    def getNow(cls, *args, **kwargs):
        return cls().get(*args, **kwargs)
    @classmethod
    def getActJsRaw(cls, **kwargs):
        jsKwargs = json_encode(kwargs)
        jsUrl = json_encode(cls.url)
        jsJsKeys = json_encode([k for k, v in kwargs.items() if isinstance(v, Js)])
        return f'''
            framework.act({jsUrl}, {jsKwargs}, {jsJsKeys})
            '''
    @classmethod
    def getActJs(cls, **kwargs):
        return html_encode(cls.getActJsRaw(**kwargs))
    def validate(self, *args, **kwargs):
        raise NotImplementedError
    def act(self, *args, **kwargs):
        raise NotImplementedError
    def _validate(self, *args, **kwargs):
        result = self.validate(*args, **kwargs)
        # if it's a generator then make a messages dict
        if hasattr(result, '__iter__'):
            return {'messages': list(result)}
    def _act(self, *args, **kwargs):
        return self.act(*args, **kwargs)
    def post(self, *args, **kwargs):
        result = self._validate(*args, **kwargs) or self._act(*args, **kwargs)
        assert isinstance(result, dict), 'Action must return a dictionary or yield dict items'
        return json_encode(result)

class Stream(Action):
    announcer = None
    messageProcessor = None
    def __init_subclass__(cls, **kwargs):
        print('NEW SUBCLASS!!!')
        super().__init_subclass__(**kwargs)
        assert cls.announcer, 'Stream subclass must define announcer'
        assert cls.messageProcessor, 'Stream subclass must define messageProcessor'
    def get(self):
        return self.announcer.getStream()
    @classmethod
    def getInitJs(cls):
        return f'''
            function errorAction() {{framework.process("ww");}}
            framework.messageInit(
                {json_encode(cls.url)},
                {cls.messageProcessor},
                errorAction
                );
            '''
    @classmethod
    def announce(cls, message):
        cls.announcer.announce(message)

def page(headStuff=(), bodyStuff=(), title=None):
    title = t.title(title) if title else ''
    return '<!DOCTYPE html>' + t.html(
        t.head(
            title,
            '''
            <meta name="viewport"
                  content="width=device-width, initial-scale=1, user-scalable=no">
            ''',
            # set fave icon
            t.link(rel='icon', href='/static/favicon.ico'),
            t.link(rel='stylesheet', href='/static/framework.css'),
            '''
            <script
                src="https://code.jquery.com/jquery-3.7.1.min.js"
                integrity="sha256-/JqT3SQfawRcv/BIHPThkBvs0OEvtFFmqPF/lYI/Cxo="
                crossorigin="anonymous">
            </script>
            ''',
            t.link(rel='stylesheet', href='/static/flex.css'),
            t.script(src='/static/framework.js'),
            headStuff,
            ),
        t.body(bodyStuff),
        )

from c             import agenda
from c             import food
from c             import tasks
from c             import weather
from lib.framework import ControllerPublic
from lib.framework import page
from lib.framework import returnAs
from lib.framework import t

class index(ControllerPublic):
    def get(self, *args, **kwargs):
        return page(
            title='Wonder Wall',
            headStuff=(
                t.title('Wonder Wall'),
                t.script(src='/static/ww.js'),
                t.link(rel='stylesheet', href='/static/ww.css'),
                *tasks.headStuff,
                *food.headStuff,
                *agenda.headStuff,
                ),
            bodyStuff=ww.getNow(),
            )

class timeanddate(ControllerPublic):
    @returnAs(t.div, id='timeanddate', **{'data-url': '/timeanddate'},
              _class='flex-col-stretch flex-center',
              )
    def get(self):
        '''
        Thursday March 13 5:15 PM
        '''
        yield '--'
        yield t.script('ww.timeAndDateInit();')

def container(module, _class=''):
    url = module.index.url
    return t.div(
        t.a(
            '&#128241;',
            href=url,
            style='''
                position: absolute;
                top: 0;
                right: 0;
                font-size: 2em;
                text-decoration: none;
                opacity: 0.5;
                '''),
        t.iframe(src=url, _class='flex-grow'),
        _class='ww-cell flex-col-stretch ' + _class,
        style='position: relative;',
        )

class ww(ControllerPublic):
    @returnAs(t.div,
              _class='flex-col-stretch flex-expand',
              id='ww',
              **{'data-url': '/ww'},
              )
    def get(self):
        yield t.div(
            t.div(
                timeanddate.getNow(),
                container(weather, _class='flex-grow'),
                _class='flex-row-stretch',
                id='ww-top',
                ),
            t.div(
                container(agenda),
                container(tasks),
                container(food, _class='flex-grow'),
                _class='flex-row flex-grow',
                id='ww-main',
                ),
            _class='flex-col-stretch flex-expand',
            )

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
        # yield t.span(datetime.datetime.now().strftime('%A %B %d'))
        # yield t.span(datetime.datetime.now().strftime('%-I:%M %p'))

def container(controller, mobileUrl, _class=''):
    return t.div(
        t.a(
            '&#128241;',
            href=mobileUrl,
            style='''
                position: absolute;
                top: 0;
                right: 0;
                font-size: 2em;
                text-decoration: none;
                opacity: 0.5;
                ''') if mobileUrl else '',
        t.div(ww.clientRender(controller.url), _class='flex-grow'),
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
                container(weather.weather, None),
                _class='flex-row-stretch',
                id='ww-top',
                ),
            t.div(
                container(agenda.agenda, agenda.index.url),
                container(tasks.tasks, tasks.index.url),
                container(food.food, food.index.url, _class='flex-grow'),
                _class='flex-row flex-grow',
                id='ww-main',
                ),
            _class='flex-col-stretch flex-expand',
            )
        yield t.script('setInterval(framework.process, 1000 * 60 * 15, "weather");')
        yield t.script('setInterval(framework.process, 1000 * 60 * 15, "tasks");')
        yield t.script('setInterval(framework.process, 1000 * 60 * 15, "food");')
        yield t.script('setInterval(framework.process, 1000 * 60 * 60 * 5, "agenda");')

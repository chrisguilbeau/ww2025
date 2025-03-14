from c             import agenda
from c             import food
from c             import tasks
from c.weather     import weather
from lib.framework import ControllerPublic
from lib.framework import json_encode
from lib.framework import page
from lib.framework import returnAs
from lib.framework import t
import datetime

class index(ControllerPublic):
    def get(self, *args, **kwargs):
        return page(
            title='Wonder Wall',
            headStuff=(
                t.title('Wonder Wall'),
                t.link(rel='stylesheet', href='/static/ww.css'),
                ),
            bodyStuff=ww.getNow(),
            )

class timeanddate(ControllerPublic):
    @returnAs(t.div, id='timeanddate', **{'data-url': '/timeanddate'},
              _class='flex-col-stretch flex-center',
              style='font-size:3rem;',
              )
    def get(self):
        '''
        Thursday March 13 5:15 PM
        '''
        yield t.span(datetime.datetime.now().strftime('%A %B %d'))
        yield t.span(datetime.datetime.now().strftime('%-I:%M %p'))

def container(controller, _class=''):
    url = controller.index.url
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
                t.div(timeanddate.getNow()),
                t.div(weather.getNow(), _class='flex-grow',),
                _class='flex-row',
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
        for msg in ('weather', 'tasks', 'food'):
            jsMsg = json_encode(msg)
            yield t.script(f'setInterval(framework.process, 1000 * 60 * 15, {jsMsg});')
        yield t.script('setInterval(framework.process, 6000, "timeanddate");')
        yield t.script('setInterval(framework.process, 1000 * 60 * 60 * 5, "agenda");')

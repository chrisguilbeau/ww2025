from c             import food
from c             import tasks
from c             import weather
from lib.framework import ControllerPublic
from lib.framework import page
from lib.framework import returnAs
from lib.framework import stream
from lib.framework import t

class index(ControllerPublic):
    def get(self, *args, **kwargs):
        return page(
            title='Wonder Wall',
            headStuff=(
                t.title('Wonder Wall'),
                t.link(rel='stylesheet', href='/static/ww.css'),
                t.script(src='/static/tasks.js'),
                t.link(rel='stylesheet', href='/static/flex.css'),
                t.link(rel='stylesheet', href='/static/food.css'),
                t.script(src='/static/weather.js'),
                t.script(stream.getInitJs()),
                ),
            bodyStuff=self.content(),
            )
    @returnAs(t.div, _class='flex-col-stretch flex-expand')
    def content(self):
        return t.div(
            t.div(weather.weather().getNow(),),
            t.div(tasks.tasks().getNow(),),
            t.div(food.food().getNow(), _class='flex-grow',),
            id='ww-main',
            _class='flex-expand flex-row-stretch flex-gap',
            )

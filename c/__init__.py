from lib.framework import ControllerPublic
from lib.framework import page
from lib.framework import returnAs
from lib.framework import t
from c import weather
from c import tasks
from c import food

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
                t.script(src='/static/food.js'),
                ),
            bodyStuff=self.content(),
            )
    @returnAs(t.div, _class='flex-col-stretch flex-expand')
    def content(self):
        return t.div(
            t.div(weather.index().getNow(),),
            t.div(tasks.index().getNow(),),
            t.div(food.index().getNow(), _class='flex-grow',),
            id='ww-main',
            _class='flex-expand flex-row-stretch flex-gap',
            )

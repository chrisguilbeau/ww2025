from c.food        import food
from c.tasks       import tasks
from c.weather     import weather
from c.agenda      import agenda
from lib.framework import ControllerPublic
from lib.framework import page
from lib.framework import returnAs
from lib.framework import t
import datetime
from m.__init__ import stream
from lib.framework import json_encode

class index(ControllerPublic):
    def get(self, *args, **kwargs):
        return page(
            title='Wonder Wall',
            headStuff=(
                t.title('Wonder Wall'),
                t.link(rel='stylesheet', href='/static/ww.css'),
                # t.script(src='/static/tasks.js'),
                t.link(rel='stylesheet', href='/static/tasks.css'),
                t.link(rel='stylesheet', href='/static/food.css'),
                # t.script(src='/static/food.js'),
                # t.script(src='/static/weather.js'),
                t.script(stream.getInitJs()),
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

class weather(ControllerPublic):
    @returnAs(t.div, id='weather', **{'data-url': '/weather'})
    def get(self):
        return '''
<a class="weatherwidget-io" href="https://forecast7.com/en/43d97n73d03/ripton/?unit=us" data-theme="pure" >Ripton, VT, USA</a>
<script>
!function(d,s,id){var js,fjs=d.getElementsByTagName(s)[0];if(!d.getElementById(id)){js=d.createElement(s);js.id=id;js.src='https://weatherwidget.io/js/widget.min.js';fjs.parentNode.insertBefore(js,fjs);}}(document,'script','weatherwidget-io-js');
</script>
        '''

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
                t.div(agenda.getNow(), _class='ww-cell',),
                t.div(tasks.getNow(), _class='ww-cell',),
                t.div(food.getNow(), _class='flex-grow ww-cell',),
                _class='flex-row',
                id='ww-main',
                ),
            _class='flex-col-stretch flex-expand',
            )
        for msg in ('weather', 'tasks', 'food'):
            jsMsg = json_encode(msg)
            yield t.script(f'setInterval(framework.process, 1000 * 60 * 15, {jsMsg});')
        yield t.script('setInterval(framework.process, 6000, "timeanddate");')
        yield t.script('setInterval(framework.process, 1000 * 60 * 60 * 5, "agenda");')

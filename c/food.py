from cgpy.lets     import returnAs
from cgpy.tags     import t
from lib.framework import Action
from lib.framework import ControllerPublic
from lib.framework import html_encode
from lib.messager  import MessageAnnouncer
from m.food        import Food

import datetime

def page(content):
    return '<!DOCTYPE html>' + t.html(
        t.head(
            t.link(rel='stylesheet', href='/static/framework.css'),
            '''
            <script
                src="https://code.jquery.com/jquery-3.7.1.min.js"
                integrity="sha256-/JqT3SQfawRcv/BIHPThkBvs0OEvtFFmqPF/lYI/Cxo="
                crossorigin="anonymous">
            </script>
            ''',
            t.title('Food'),
            t.link(rel='stylesheet', href='/static/flex.css'),
            t.link(rel='stylesheet', href='/static/food.css'),
            t.script(src='/static/framework.js'),
            t.script(src='/static/food.js'),
            t.script(stream.getInitJs()),
            ),
        t.body(content),
        )

class stream(Action):
    announcer = MessageAnnouncer()
    messageProcessor = 'food.process'
    def get(self):
        return self.announcer.getStream()
    @classmethod
    def getInitJs(cls):
        return f'''
        var evtSource = new EventSource('{cls.url}');
        evtSource.onmessage = function(event) {{
            {cls.messageProcessor}(event.data);
        }};
        '''

class index(ControllerPublic):
    @returnAs(page)
    @returnAs(t.div, _class='flex-col-stretch')
    def get(self, *args, **kwargs):
        now = datetime.datetime.now()
        year = now.year
        for i in range(7):
            dt = now + datetime.timedelta(days=i)
            doy = dt.timetuple().tm_yday
            dayLetter = dt.strftime('%A')[0].upper()
            isToday = i == 0
            _class = 'today ' if isToday else ''
            _class += 'day flex-row flex-center'
            yield t.div(
                t.div(dayLetter, _class='day-letter flex-col flex-center'),
                t.div(
                    meal.getNow(year, doy, 1),
                    meal.getNow(year, doy, 2),
                    meal.getNow(year, doy, 3),
                    _class='flex-col',
                    ),
                _class=_class,
                )
    def post(self, *args, **kwargs):
        return 'Index page' + str(args) + str(kwargs)

class meal(Action):
    def get(self, year, doy, meal):
        row = Food.getOne(year=year, doy=doy, meal=meal)
        return t.button(
            html_encode(row.desc) if row else '--',
            id=f'food-{year}-{doy}-{meal}',
            onclick=editmeal.getPrompt(
                year=year,
                doy=doy,
                meal=meal,
                ),
            _class='meal',
            )

class editmeal(Action):
    def getDt(self, year, doy):
        year = int(year)
        doy = int(doy)
        return datetime.datetime(year, 1, 1) + datetime.timedelta(days=doy-1)
    @returnAs(t.div, _class='flex-col flex-gap')
    def get(self, year, doy, meal):
        dt = self.getDt(year, doy)
        dayName = dt.strftime('%A')
        mealName = ['Breakfast', 'Lunch', 'Dinner'][int(meal)-1]
        ids = self.Ids()
        row = Food.getOne(year=year, doy=doy, meal=meal)
        yield t.h1(f'{dayName} {mealName}')
        yield t.input(
            placeholder='Description',
            id=ids.desc,
            value=html_encode(row.desc) if row else '',
            )
        yield t.div(
            t.button('Save', onclick=editmeal.getActJs(
                year=year,
                doy=doy,
                meal=meal,
                desc=self.byId(ids.desc),
                )),
            t.button('Cancel', onclick='action.killPrompt(event.target);'),
            t.button('Delete', onclick=editmeal.getActJs(
                year=year,
                doy=doy,
                meal=meal,
                desc=None,
                )),
            _class='flex-row flex-gap',
            )
        yield t.script(
            f'''
            document.getElementById('{ids.desc}').focus();
            ''')
    def validate(self, year, doy, meal, desc):
        pass
    def act(self, year, doy, meal, desc):
        Food.execute(
            '''
            delete from food
            where year = ?
            and doy = ?
            and meal = ?
            ''',
            (year, doy, meal),
        )
        if desc:
            Food.execute(
                '''
                insert into food (year, doy, meal, desc)
                values (?, ?, ?, ?)
                ''',
                (year, doy, meal, desc),
                )
        id = f'food-{year}-{doy}-{meal}'
        url = f'/food/meal/{year}/{doy}/{meal}'
        stream.announcer.announce(f'{id}:{url}')
        return {'js': ['action.killTopScreen();']}

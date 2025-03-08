from cgpy.lets     import returnAs
from cgpy.tags     import t
from lib.framework import Action
from lib.framework import ControllerPublic
from lib.framework import html_encode
from lib.framework import let
from lib.framework import page as _page
from lib.framework import Stream
from lib.messager  import MessageAnnouncer
from m.food        import Food

import datetime

class stream(Stream):
    announcer = MessageAnnouncer()
    messageProcessor = 'food.process'

def page(content):
    return _page(
        headStuff=(
            t.title('Food'),
            t.link(rel='stylesheet', href='/static/flex.css'),
            t.link(rel='stylesheet', href='/static/food.css'),
            t.script(src='/static/food.js'),
            t.script(stream.getInitJs()),
            ),
        bodyStuff=content,
        )

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
        @let
        def radios():
            if not row:
                return
            statuses = ['Planned', 'Bought']
            for i in range(2):
                status = statuses[i]
                baseId = f'food-{year}-{doy}-{meal}'
                id = f'{baseId}-{i}'
                yield t.div(
                    t.input(
                        type='radio',
                        name=baseId,
                        value=str(i),
                        checked=i == row.status,
                        id=id,
                        onchange=self.getActJs(
                            year=year,
                            doy=doy,
                            meal=meal,
                            status=i,
                            ),
                        ),
                    t.label(status, for_=id),
                    _class='flex-col flex-center',
                    )
        return t.div(
            t.button(
                html_encode(row.desc) if row else '--',
                onclick=editmeal.getPrompt(
                    year=year,
                    doy=doy,
                    meal=meal,
                    ),
                _class='meal',
                ),
            radios if row else '',
            id=f'food-{year}-{doy}-{meal}',
            _class='flex-row flex-center flex-gap',
            style='margin: 1rem;',
            )
    def validate(self, year, doy, meal, status):
        pass
    def act(self, year, doy, meal, status):
        Food.execute(
            '''
            update food
            set status = ?
            where year = ?
            and doy = ?
            and meal = ?
            ''',
            (status, year, doy, meal),
            )
        id = f'food-{year}-{doy}-{meal}'
        url = f'/food/meal/{year}/{doy}/{meal}'
        stream.announcer.announce(f'{id}:{url}')
        return {}

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
                insert into food (year, doy, meal, desc, status)
                values (?, ?, ?, ?, ?)
                ''',
                (year, doy, meal, desc, 0),
                )
        id = f'food-{year}-{doy}-{meal}'
        url = f'/food/meal/{year}/{doy}/{meal}'
        stream.announcer.announce(f'{id}:{url}')
        return {'js': ['action.killTopScreen();']}

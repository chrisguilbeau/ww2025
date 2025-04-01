from c.stream      import stream
from cgpy.lets     import returnAs
from cgpy.lets     import let
from cgpy.tags     import t
from datetime      import datetime
from lib.framework import Action
from lib.framework import ControllerPublic
from lib.framework import html_encode
from lib.framework import page
from m.tasks       import Task
from time          import time

headStuff = (
    t.script(src='/static/tasks.js'),
    t.link(rel='stylesheet', href='/static/tasks.css'),
    # t.script(stream.getInitJs()),
    )

class index(ControllerPublic):
    def get(self):
        return page(
            title='Wonder Wall - Ta Da List',
            headStuff=headStuff,
            bodyStuff=tasks.getNow(),
            )

class tasks(Action):
    @returnAs(
        t.div,
        _class='flex-col-stretch flex-gap',
        id='tasks',
        **{'data-url': '/tasks/tasks'},
        )
    def get(self):
        return t.div(
            t.h1('Tada List'),
            t.button(
                'New Task',
                onclick=tasklist.getActJs(),
                ),
            tasklist.getNow(),
            _class='flex-col-stretch flex-gap',
            id='tasks',
            url='/tasks',
            )

class tasklist(Action):
    @returnAs(
        t.div,
        _class='flex-col-stretch flex-gap',
        id='tasklist',
        **{'data-url': '/tasks/tasklist'},
        )
    def get(self, *args, **kwargs):
        now = datetime.now()
        today = now.replace(hour=0, minute=0, second=0, microsecond=0)
        todayTime = today.timestamp()
        for row in reversed(list(Task.getAfter(todayTime))):
            yield task.getNow(row.id)
    def validate(self):
        pass
    def act(self):
        Task.insert(task='New Task')
        stream.announce('tasklist')
        return {}

class task(Action):
    def get(self, taskId):
        row = Task.getOne(id=taskId)
        ids = self.Ids()
        if row.done:
            dt = datetime.fromtimestamp(row.done)
            done = f'{dt:%-I:%M %p}'
        else:
            done = ''
        checkEmojiHtml = '&#x2705;'
        undoEmojiHtml = '&#x21A9;'
        @let
        def color():
            '''
            return a random crazy color, it doesn't matter which'
            '''
            if row.done:
                return '#f5f5f5'
            funkyColorList = (
                # lime green
                (0, 255, 0),
                # hot pink
                (255, 105, 180),
                # cyan
                (0, 255, 255),
                # yellow
                (255, 255, 0),
                # orange
                (255, 165, 0),
                # purple
                (128, 0, 128),
                # red
                (255, 0, 0),
                # blue
                (0, 0, 255),
                )
            index = row.id % len(funkyColorList)
            r, g, b = funkyColorList[index]
            return f'rgb({r}, {g}, {b})'
        return t.div(
            t.button(
                checkEmojiHtml if not row.done else undoEmojiHtml,
                onclick=self.getActJs(
                    id=row.id,
                    value=self.byId(ids.task),
                    done=time() if not done else 0,
                    ),
                ),
            t.input(
                value=html_encode(row.task),
                id=ids.task,
                disabled=bool(row.done),
                type='text',
                onchange=self.getActJs(
                    id=row.id,
                    value=self.byId(ids.task),
                    done=0,
                    ),
                _class='flex-grow' + (' ' if not row.done else ' tasks-done'),
                ),
            t.span(html_encode(done), style='white-space: nowrap;') if done else '',
            id='task' + str(row.id),
            **{'data-url': f'/tasks/task/{row.id}'},
            style=f'background-color: {color};',
            _class='flex-row flex-gap task',
            )
    def validate(self, id, value, done):
        pass
    def act(self, id, value, done):
        done = 0 if not done else float(done)
        if not value:
            Task.execute(
                '''
                delete from task
                where id = ?;
                ''',
                (id,),
                )
            stream.announce('tasklist')
            return {}
        if done:
            Task.execute(
                '''
                update task
                set done = ?
                where id = ?;
                ''',
                (done, id),
                )
            stream.announce('tasklist')
            return {}
        else:
            Task.execute(
                '''
                update task
                set task = ?, done = null
                where id = ?;
                ''',
                (value, id,),
                )
            stream.announce(f'task{id}')
            return {}

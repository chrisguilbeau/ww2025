from c.stream      import stream
from cgpy.lets     import returnAs
from cgpy.tags     import t
from datetime      import datetime
from lib.framework import Action
from lib.framework import ControllerPublic
from lib.framework import html_encode
from lib.framework import page
from m.tasks       import Task
from time          import time

class index(ControllerPublic):
    def get(self):
        return page(
            headStuff=(
                t.title('Wonder Wall - Ta Da List'),
                t.script(src='/static/tasks.js'),
                t.link(rel='stylesheet', href='/static/tasks.css'),
                t.script(stream.getInitJs()),
                ),
            bodyStuff=tasks.getNow(),
            )

class tasks(Action):
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
        return t.div(
            t.button(
                'DONE' if not row.done else 'UNDO',
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
            _class='flex-row flex-gap',
            )
    def validate(self, id, value, done):
        pass
    def act(self, id, value, done):
        if done:
            Task.execute(
                '''
                update task
                set done = ?, task = ?
                where id = ?;
                ''',
                (done, value, id),
                )
            stream.announce('tasklist')
            return {}
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
        Task.execute(
            '''
            update task
            set task = ?
            where id = ?;
            ''',
            (value, id,),
            )
        stream.announce(f'task{id}')
        return {}

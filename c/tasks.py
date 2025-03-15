from c.stream      import stream
from cgpy.lets     import returnAs
from cgpy.tags     import t
from lib.framework import Action
from lib.framework import ControllerPublic
from lib.framework import html_encode
from lib.framework import page
from m.tasks       import Task

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
        _class='flex-col-stretch',
        id='tasklist',
        **{'data-url': '/tasks/tasklist'},
        )
    def get(self, *args, **kwargs):
        for row in reversed(list(Task.getAll())):
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
        return t.div(
            t.button(
                'DONE',
                onclick=self.getActJs(
                    id=row.id,
                    value='',
                    ),
                ),
            t.input(
                value=html_encode(row.task),
                id=ids.task,
                onchange=self.getActJs(
                    id=row.id,
                    value=self.byId(ids.task),
                    ),
                ),
            id='task' + str(row.id),
            **{'data-url': f'/tasks/task/{row.id}'},
            _class='flex-row flex-gap',
            )
    def validate(self, id, value):
        pass
    def act(self, id, value):
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

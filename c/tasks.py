from cgpy.lets     import returnAs
from cgpy.tags     import t
from lib.framework import ControllerPublic
from lib.framework import page as _page
from lib.framework import Stream
from lib.messager  import MessageAnnouncer
from m.tasks       import Task
from lib.framework import Action
from lib.framework import html_encode

class stream(Stream):
    announcer = MessageAnnouncer('tasks')
    messageProcessor = 'tasks.process'

def page(content):
    return _page(
        headStuff=(
            t.title('Tasks'),
            t.script(src='/static/tasks.js'),
            t.script(stream.getInitJs()),
        ),
        bodyStuff=content,
        )

class index(ControllerPublic):
    @returnAs(page)
    def get(self, *args, **kwargs):
        return t.div(
            t.button(
                'New Task',
                onclick=tasklist.getActJs(),
                ),
            tasklist.getNow(),
            )

class tasklist(Action):
    @returnAs(t.ul, _class='flex-col-stretch', id='tasklist')
    def get(self, *args, **kwargs):
        for row in reversed(list(Task.getAll())):
            yield task.getNow(row.id)
    def validate(self):
        pass
    def act(self):
        Task.insert(task='New Task')
        stream.announcer.announce('tasklist:/tasks/tasklist')
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
            stream.announcer.announce('tasklist:/tasks/tasklist')
            return {}
        Task.execute(
            '''
            update task
            set task = ?
            where id = ?;
            ''',
            (value, id,),
            )
        stream.announcer.announce(f'task{id}:/tasks/task/{id}')
        return {}

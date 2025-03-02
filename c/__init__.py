from cgpy.lets     import letAs
from cgpy.lets     import returnAs
from cgpy.tags     import t
from html          import escape as html_encode
from lib.framework import Action
from lib.framework import ControllerPublic
from lib.messager  import MessageAnnouncer
from m             import Task as m_task

class index(ControllerPublic):
    def get(self, *args, **kwargs):
        allTasks = m_task.getAll()
        return '<!DOCTYPE html>' + t.html(
            t.head(
                t.title('Wonder Wall 2025'),
                t.link(rel='stylesheet', type='text/css', href='/static/flex.css'),
                t.link(rel='stylesheet', type='text/css', href='/static/ww.css'),
                t.link(rel='icon', type='image/ico', href='/static/favicon.ico'),

                '''
                <link
                    rel="stylesheet"
                    href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">
                ''',
                '''
                <script
                    src="https://code.jquery.com/jquery-3.7.1.min.js"
                    integrity="sha256-/JqT3SQfawRcv/BIHPThkBvs0OEvtFFmqPF/lYI/Cxo="
                    crossorigin="anonymous">
                </script>
                ''',
                t.script(src='/static/ww.js'),
                ),
            t.body(
                t.h1('Wonder Wall'),
                t.div(taskchildren.getNow(), _id='tc_null'),
                str(allTasks),
                t.pre(_id='output'),
                ),
            )
    @property
    @returnAs(t._)
    def content(self):
        return
        # yield self.getInit() if not tasks else taskchildren.getNow(parent='null')
    def getInit(self):
        return Init.getNow()
    @returnAs(t.ol)
    @returnAs(map, t.li)
    def getTasks(self, tasks):
        for task in tasks:
            yield Task.getNow(id=task.id)
    def post(self, *args, **kwargs):
        return 'Index page' + str(args) + str(kwargs)

class Init(Action):
    def get(self):
        return t.button('Init', onclick=self.getActJs())
    def validate(self, *args, **kwargs):
        pass
    def act(self):
        m_task.insert(title='Wonder Wall 2025', description='A new beginning')
        ANNOUNCER.announce('tc_null')
        return {}

class taskchildren(Action):
    def get(self, parent=None):
        parent = parent or None
        @letAs(t.ul)
        @letAs(map, t.li)
        def tasks():
            for task in m_task.getAll(parent=parent):
                print(task.id)
                yield Task.getNow(id=task.id)
        return t.div(
            t.div(
                tasks,
                t.button('New Task', onclick=self.getActJs(parent=parent)),
                _class='taskchildren',
                id=f'tc_{parent}',
                ),
            )
    def validate(self, parent):
        pass
    def act(self, parent):
        m_task.insert(title='New Task', parent=parent)
        self.updateParent(parent)
        return {}

class Task(Action):
    def get(self, id):
        task = m_task.getOne(id=id)
        timeText = 'ASAP'
        return t.div(
            t.div(
                t.span(task.title),
                t.span(timeText),
                _class='flex-col-stretch flex-grow',
                ),
            t.div(
                t.button(t.i(_class='bi bi-check-lg')),
                t.button(t.i(_class='bi bi-pencil')),
                _class='flex-row flex-gap',
                ),
            id=f't_{id}',
            _class='flex-row-stretch task',
            )

class TaskTitle(Action):
    def get(self, id):
        ids = self.Ids()
        task = m_task.getOne(id=id)
        return t.input(
            value=html_encode(task.title),
            id=ids.title,
            onchange=self.getActJs(
                id=id,
                title=self.byId(ids.title),
                ),
            )
    def validate(self, id, title):
        pass
    def act(self, id, title):
        m_task.update(id=id, title=title)
        ANNOUNCER.announce(f't_{id}:/task/{id}')
        return {}

class TaskDelete(Action):
    def get(self, id):
        return t.button('Delete', onclick=self.getActJs(id=id))
    def validate(self, id):
        pass
    def act(self, id):
        task = m_task.getOne(id=id)
        m_task.delete(id=id)
        self.updateParent(task.parent)
        return {}


ANNOUNCER = MessageAnnouncer()

class announce(ControllerPublic):
    def get(self):
        ANNOUNCER.announce('Hello World')
        return 'Announced'

class stream(ControllerPublic):
    def get(self):
        return ANNOUNCER.getStream()

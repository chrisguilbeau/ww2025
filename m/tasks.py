from m.__init__ import singleton
from m.__init__ import Table

@singleton
class Task(Table):
    name = 'task'
    columns = (
        'id integer primary key',
        'task text',
        'done integer',
        )

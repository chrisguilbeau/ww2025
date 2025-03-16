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
    def getAfter(self, time):
        return self.select(
            sql='''
            select *
            from task
            where done > ? or done = 0 or done is null
            order by done desc;
            ''',
            params=(time,),
            )

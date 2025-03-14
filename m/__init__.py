from cgpy.lets     import letAs
from collections   import namedtuple
from lib.framework import Stream
from lib.messager  import MessageAnnouncer
import sqlite3

class stream(Stream):
    announcer = MessageAnnouncer(
        id='wonderwall',
        )
    messageProcessor = 'framework.process'

def singleton(cls):
    return cls()

def cacheable(f):
    def wrapper(*args, **kwargs):
        if f.__name__ not in wrapper.cache:
            wrapper.cache[f.__name__] = f(*args, **kwargs)
        return wrapper.cache[f.__name__]
    wrapper.cache = {}
    return wrapper

class Table():
    name = ()
    columns = ()
    @property
    def cnn(self):
        return sqlite3.connect('db.sqlite')
    @property
    def columnNames(self):
        return [c.split()[0] for c in self.columns]
    @property
    def Row(self):
        return namedtuple('Row', self.columnNames)
    def __init__(self):
        self.execute(f'''
        CREATE TABLE IF NOT EXISTS {self.name} (
            {','.join(self.columns)}
        );
        ''')
    def execute(self, sql, params=()):
        print(sql)
        cnn = self.cnn
        c = cnn.cursor()
        print(sql)
        print(params)
        c.execute(sql, params)
        cnn.commit()
    def select(self, sql, params=()):
        cnn = sqlite3.connect('db.sqlite')
        c = cnn.cursor()
        print(sql)
        print(params)
        c.execute(sql, params)
        for row in c.fetchall():
            yield self.Row(*row)
    def getAll(self, **kwargs):
        params = []
        @letAs(' and '.join)
        def where():
            for k, v in kwargs.items():
                if v is None:
                    yield f'{k} is null'
                else:
                    params.append(v)
                    yield f'{k} = ?'
        if where:
            where = 'where ' + where
        sql = f'select * from {self.name} {where};'
        return self.select(sql=sql, params=params)
    def getOne(self, **kwargs):
        for row in self.getAll(**kwargs):
            return row
    def insert(self, **kwargs):
        cnn = sqlite3.connect('db.sqlite')
        c = cnn.cursor()
        params = []
        @letAs(','.join)
        def values():
            for v in kwargs.values():
                if v is None:
                    yield 'null'
                else:
                    params.append(v)
                    yield '?'
        sql = f'''
            insert into {self.name} ({','.join(kwargs.keys())})
            values ({values});
            '''
        print(sql)
        c.execute(sql, params)
        cnn.commit()

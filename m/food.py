from m.__init__  import singleton
from m.__init__  import Table

@singleton
class Food(Table):
    name = 'food'
    columns = (
        'year integer',
        'doy integer',
        'meal integer',
        'desc text',
        'status integer',
        )
    def getNextSevenDays(self):
        sql = '''
        select * from food
        where date >= date('now')
        and date < date('now', '+7 days')
        order by date, meal;
        '''
        return self.select(sql=sql)

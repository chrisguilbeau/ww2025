from lib.framework import ControllerPublic
from lib.framework import page
from lib.framework import returnAs
from lib.framework import t

class index(ControllerPublic):
    def get(self, *args, **kwargs):
        return page(
            title='Wonder Wall',
            bodyStuff=self.content(),
            )
    @returnAs(t.div, _class='flex-col-stretch flex-expand')
    def content(self):
        yield t.style('''
            iframe {
                   border: none;
                   height: 100%;
                   width: 100%;
                         }
            ''')
        yield t.div(
            t.div(t.iframe(src='/weather'),),
            t.div(t.iframe(src='/tasks'),),
            t.div(t.iframe(src='/food'), _class='flex-grow',),
            _class='flex-row-stretch flex-grow',
            )

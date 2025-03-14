from lib.framework import ControllerPublic
from lib.framework import returnAs
from lib.framework import t

class weather(ControllerPublic):
    @returnAs(t.div, id='weather', **{'data-url': '/weather/weather'})
    def get(self):
        return '''
<a class="weatherwidget-io" href="https://forecast7.com/en/43d97n73d03/ripton/?unit=us" data-theme="pure" >Ripton, VT, USA</a>
<script>
!function(d,s,id){var js,fjs=d.getElementsByTagName(s)[0];if(!d.getElementById(id)){js=d.createElement(s);js.id=id;js.src='https://weatherwidget.io/js/widget.min.js';fjs.parentNode.insertBefore(js,fjs);}}(document,'script','weatherwidget-io-js');
</script>
        '''

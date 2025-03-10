from lib.framework import ControllerPublic
from lib.framework import page as _page
from lib.framework import Stream
from lib.framework import t
from lib.messager  import MessageAnnouncer

class stream(Stream):
    announcer = MessageAnnouncer(
        id='weather',
        timeDict={'refreshInner': 600},
        )
    messageProcessor = 'weather.process'

class index(ControllerPublic):
    def get(self, *args, **kwargs):
        return _page(
            headStuff=(
                t.script(src='/static/weather.js'),
                t.script(stream.getInitJs()),
                ),
            bodyStuff=t.div(inner.getNow(), id='weather'),
            )

class inner(ControllerPublic):
    def get(self):
        from datetime import datetime
        yield '''
<script>
        (function(d, s, id) {
            if (d.getElementById(id)) {
                if (window.__TOMORROW__) {
                    window.__TOMORROW__.renderWidget();
                }
                return;
            }
            const fjs = d.getElementsByTagName(s)[0];
            const js = d.createElement(s);
            js.id = id;
            js.src = "https://www.tomorrow.io/v1/widget/sdk/sdk.bundle.min.js";

            fjs.parentNode.insertBefore(js, fjs);
        })(document, 'script', 'tomorrow-sdk');
        </script>

        <div class="tomorrow"
           data-location-id="299485"
           data-language="EN"
           data-unit-system="IMPERIAL"
           data-skin="light"
           data-widget-type="upcoming"
           style="padding-bottom:22px;position:relative;"
        >
          <a
            href="https://www.tomorrow.io/weather-api/"
            rel="nofollow noopener noreferrer"
            target="_blank"
            style="position: absolute; bottom: 0; transform: translateX(-50%); left: 50%;"
          >
            <img
              alt="Powered by the Tomorrow.io Weather API"
              src="https://weather-website-client.tomorrow.io/img/powered-by.svg"
              width="250"
              height="18"
            />
          </a>
        </div>
        '''
        yield t.p()
        yield t.i('last updated ', datetime.now().strftime('%I:%M %p'))

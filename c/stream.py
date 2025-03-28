from lib.framework import Stream
from lib.messager  import MessageAnnouncer

class stream(Stream):
    announcer = MessageAnnouncer(
        id='wonderwall',
        timeDict={
            'food': 60 * 60,
            'tasks': 60 * 60,
            'weather': 60 * 15,
            'agenda': 60 * 60,
            },
        )
    messageProcessor = 'framework.process'

from lib.framework import Stream
from lib.messager  import MessageAnnouncer

class stream(Stream):
    announcer = MessageAnnouncer(
        id='wonderwall',
        )
    messageProcessor = 'framework.process'

from lib.myflask import Response
from queue import Queue
from queue import Full

class MessageAnnouncer:

    def __init__(self):
        self.listeners = []

    def listen(self):
        q = Queue(maxsize=5)
        self.listeners.append(q)
        return q

    def announce(self, msg):
        for i in reversed(range(len(self.listeners))):
            try:
                self.listeners[i].put_nowait(self.format(msg))
            except Full:
                del self.listeners[i]

    def format(self, data: str) -> str:
        return f'data: {data}\n\n'

    def getStream(self):
        def stream():
            messages = self.listen()
            while True:
                msg = messages.get()  # blocks until a new message arrives
                yield msg
        return Response(stream(), mimetype='text/event-stream')

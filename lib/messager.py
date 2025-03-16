import time
from lib.myflask import Response
import os

def tail_f_generator(file_path, keepalive_interval=30, sleep_interval=0.5):
    """
    Tails the given file and yields new lines as SSE events.
    If no new line is available, it waits briefly, and only sends a
    keepalive comment every `keepalive_interval` seconds.
    """
    with open(file_path, 'r') as f:
        f.seek(0, os.SEEK_END)
        last_sent = time.time()
        while True:
            line = f.readline()
            if line:
                # Reset the timer when new data is sent.
                last_sent = time.time()
                yield f"data: {line.strip()}\n\n"
            else:
                # No new line; check if it's time to send a keepalive.
                current_time = time.time()
                if current_time - last_sent >= keepalive_interval:
                    yield ": keepalive\n\n"
                    last_sent = current_time
                else:
                    # Sleep briefly to avoid busy looping.
                    time.sleep(sleep_interval)

class MessageAnnouncer:
    def __init__(self, id, timeDict=None, keepAliveInterval=None):
        self.id = id
        self.file_path = f'{id}-messages.txt'
        self.timeDict = timeDict or {}
        # If a keepalive interval is provided, store it.
        if keepAliveInterval:
            self.timeDict['keepalive'] = keepAliveInterval

    def announce(self, msg):
        """
        Append a new message to the file, ensuring it ends with a newline.
        """
        with open(self.file_path, 'a') as f:
            f.write(f"{msg}\n")
            f.flush()

    def getStream(self):
        """
        Returns a Flask Response that uses the tail_f_generator to stream events.
        """
        # Use the keepalive interval from timeDict if provided.
        interval = self.timeDict.get('keepalive', 30)
        return Response(tail_f_generator(self.file_path, keepalive_interval=interval),
                        mimetype='text/event-stream')

from lib.myflask import Response

import os
import time
MAX_SEC = 60 * 60 * 24 * 7  # 1 week

def formatMessage(msg):
    return f"data: {msg}\n\n"

def getTailGen(
        filePath,
        timeDict,
        keepalive_interval=30,
        ):
    """
    Tails the given file and yields new lines as SSE events.
    If no new line is available, it waits briefly, and only sends a
    keepalive comment every `keepalive_interval` seconds.
    """
    mil = 0.1
    milCount = 0
    secCount = 0
    timeDict = timeDict or {}
    timeDict['keepalive'] = keepalive_interval
    with open(filePath, 'r') as f:
        f.seek(0, os.SEEK_END)
        while True:
            line = f.readline()
            if line:
                yield formatMessage(line.strip())
            # Sleep briefly to avoid busy looping.
            time.sleep(mil)
            milCount += 1
            if milCount == 10:
                milCount = 0
                secCount += 1
                for msg, secs in timeDict.items():
                    if secCount % secs == 0:
                        print(msg)
                        yield formatMessage(msg)
            if secCount >= MAX_SEC:
                secCount = 0

class MessageAnnouncer:
    timeLoopThread = None
    def __init__(self, id, timeDict=None, keepAliveInterval=None):
        self.id = id
        self.filePath = f'{id}-messages.txt'
        self.timeDict = timeDict or {}

    def announce(self, msg):
        """
        Append a new message to the file, ensuring it ends with a newline.
        """
        with open(self.filePath, 'a') as f:
            f.write(f"{msg}\n")
            f.flush()

    def getStream(self):
        """
        Returns a Flask Response that uses the getTailGen to stream events.
        """
        return Response(
            getTailGen(self.filePath, timeDict=self.timeDict),
            mimetype='text/event-stream',
            )

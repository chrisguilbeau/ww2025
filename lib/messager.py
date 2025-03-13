from lib.myflask import Response
import threading
import time

def tail_f_generator(file_path):
    """
    Tails the given file natively (without an external subprocess) and yields
    new lines as SSE events, including a keep-alive comment if no new line
    appears.
    """
    yield 'connected'
    with open(file_path, 'r') as f:
        # Seek to the end of the file
        f.seek(0, 2)
        while True:
            line = f.readline()
            if line:
                yield f"data: {line.strip()}\n\n"
            else:
                time.sleep(0.1)

class MessageAnnouncer:
    def __init__(self, id, timeDict=None, keepAliveInterval=None):
        self.id = id
        self.file_path = f'{id}-messages.txt'
        self.timeDict = timeDict = timeDict or {}
        # Start a background thread to send keep-alive messages
        if keepAliveInterval:
            timeDict['keepalive'] = keepAliveInterval
        if timeDict:
            self._time_thread = threading.Thread(
                target=self._time_loop, daemon=True)
            self._time_thread.start()

    def _time_loop(self):
        startTime = time.time()
        print('TIMELOOP: starting time loop for', self.id)
        while True:
            print('processing timeDict for', self.id, repr(self))
            now = time.time()
            elapsed = round(now - startTime)
            for message, interval in self.timeDict.items():
                print(elapsed, interval)
                if elapsed % interval == 0:
                    print(self.id, message)
                    self.announce(message)
            time.sleep(1)

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
        return Response(tail_f_generator(self.file_path),
                        mimetype='text/event-stream')

from lib.myflask import Response
import subprocess
import threading
import time

def tail_f_generator(file_path):
    """
    This generator spawns a subprocess that tails the given file.
    Each new line from tail is yielded as an SSE formatted message.
    """
    # Start tailing the file from its current end
    process = subprocess.Popen(
        ['/usr/bin/tail', '-n', '0', '-f', file_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
        )
    try:
        while True:
            # Read a new line from the tail process
            line = process.stdout.readline().strip()
            if line:
                # Format the message as an SSE event
                yield f"data: {line.strip()}\n\n"
            else:
                time.sleep(0.1)
    finally:
        process.terminate()

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

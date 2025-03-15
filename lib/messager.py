from lib.myflask import Response
import time
import os
import select

def tail_f_generator(file_path):
    """
    Tails the given file natively (without an external subprocess) and yields
    new lines as SSE events. If no new line is available, it yields a keep-alive
    comment to prevent client timeouts.
    """
    with open(file_path, 'r') as f:
        # Move the file pointer to the end of the file.
        f.seek(0, os.SEEK_END)
        while True:
            # Use select to wait for the file to become readable, with a timeout.
            rlist, _, _ = select.select([f], [], [], 0.1)
            if rlist:
                line = f.readline()
                if line:
                    yield f"data: {line.strip()}\n\n"
            else:
                # If select times out without the file being readable, yield keep-alive.
                yield ": keepalive\n\n"

class MessageAnnouncer:
    def __init__(self, id, timeDict=None, keepAliveInterval=None):
        self.id = id
        self.file_path = f'{id}-messages.txt'
        self.timeDict = timeDict = timeDict or {}
        # Start a background thread to send keep-alive messages
        if keepAliveInterval:
            timeDict['keepalive'] = keepAliveInterval

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

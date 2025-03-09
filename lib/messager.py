import subprocess
import time
from lib.myflask import Response

def tail_f_generator(file_path):
    """
    This generator spawns a subprocess that tails the given file.
    Each new line from tail is yielded as an SSE formatted message.
    """
    # Start tailing the file from its current end
    process = subprocess.Popen(
        ['tail', '-n', '0', '-f', file_path],
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
    def __init__(self, id):
        self.file_path = f'{id}-messages.txt'

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
        return Response(tail_f_generator(self.file_path), mimetype='text/event-stream')

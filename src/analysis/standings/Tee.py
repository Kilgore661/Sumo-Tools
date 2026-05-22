"""
Simple output-stream duplicator.

Provides a file-like object that mirrors writes to multiple streams,
typically console output and a log file.
"""

class Tee:
    def __init__(self, *streams):
        self.streams = streams

    def write(self, data: str) -> None:
        for stream in self.streams:
            stream.write(data)
            stream.flush()

    def flush(self) -> None:
        for stream in self.streams:
            stream.flush()

from __future__ import annotations

import time
from pathlib import Path
from typing import Callable, Set

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


class LocationHandler(FileSystemEventHandler):
    def __init__(self, on_file: Callable[[str], None], seen: Set[str]) -> None:
        self._on_file = on_file
        self._seen = seen

    def on_created(self, event):
        if event.is_directory:
            return
        path = str(event.src_path)
        if path in self._seen:
            return
        self._seen.add(path)
        self._on_file(path)


def watch_directory(path: str, on_file: Callable[[str], None]) -> None:
    directory = Path(path)
    seen: Set[str] = set()
    handler = LocationHandler(on_file, seen)
    observer = Observer()
    observer.schedule(handler, str(directory), recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(0.5)
    finally:
        observer.stop()
        observer.join()

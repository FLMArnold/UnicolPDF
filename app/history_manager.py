import io
from dataclasses import dataclass


@dataclass
class _Entry:
    buf: io.BytesIO
    description: str


class HistoryManager:
    def __init__(self, max_steps: int = 20):
        self._past: list[_Entry] = []
        self._future: list[_Entry] = []
        self._max_steps = max(1, max_steps)

    def add_snapshot(self, buf: io.BytesIO, description: str):
        self._past.append(_Entry(buf, description))
        self._future.clear()
        while len(self._past) > self._max_steps:
            self._past.pop(0)

    def undo(self, current_buf: io.BytesIO) -> io.BytesIO | None:
        if not self._past:
            return None
        entry = self._past.pop()
        self._future.insert(0, _Entry(current_buf, entry.description))
        return entry.buf

    def redo(self, current_buf: io.BytesIO) -> io.BytesIO | None:
        if not self._future:
            return None
        entry = self._future.pop(0)
        self._past.append(_Entry(current_buf, entry.description))
        return entry.buf

    def navigate(self, rel_index: int, current_buf: io.BytesIO) -> io.BytesIO | None:
        if rel_index == 0:
            return None
        if rel_index > 0:
            rel_index = min(rel_index, len(self._past))
            for _ in range(rel_index):
                e = self._past.pop()
                self._future.insert(0, _Entry(current_buf, e.description))
                current_buf = e.buf
            return current_buf
        else:
            rel_index = abs(rel_index)
            rel_index = min(rel_index, len(self._future))
            for _ in range(rel_index):
                e = self._future.pop(0)
                self._past.append(_Entry(current_buf, e.description))
                current_buf = e.buf
            return current_buf

    @property
    def cursor(self) -> int:
        if not self._future:
            return len(self._past)
        return -len(self._future)

    def get_display_entries(self):
        result = []
        for i, entry in enumerate(self._past):
            rel_idx = len(self._past) - i
            result.append((entry.description, rel_idx, False, False))
        result.append(("当前", 0, True, False))
        for i, entry in enumerate(self._future):
            rel_idx = -(i + 1)
            result.append((entry.description, rel_idx, False, True))
        return result

    def set_max_steps(self, n: int):
        self._max_steps = max(1, n)
        while len(self._past) > self._max_steps:
            self._past.pop(0)

    def clear(self):
        self._past.clear()
        self._future.clear()

    @property
    def entry_count(self) -> int:
        return len(self._past) + len(self._future)

    @property
    def max_steps(self) -> int:
        return self._max_steps

    def can_undo(self) -> bool:
        return len(self._past) > 0

    def can_redo(self) -> bool:
        return len(self._future) > 0

"""Shared control-flow exceptions for both imported and `python -m` workers."""


class DungLuot(Exception):
    """Stop one run with an explicit, resumable state."""

    def __init__(self, trang_thai, thong_diep):
        super().__init__(thong_diep)
        self.trang_thai, self.thong_diep = trang_thai, thong_diep

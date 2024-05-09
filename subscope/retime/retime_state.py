from subscope.shared.event import Event


class RetimeState(Event):
    def __init__(self, theme=None, folder=None, files=None, selected_files=None, offset="+2.0"):
        self.theme = theme
        self.folder = folder
        self.files = files or []
        self.selected_files = selected_files or []
        self.offset = offset

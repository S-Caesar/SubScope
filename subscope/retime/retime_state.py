from subscope.shared.event import Event


class RetimeState(Event):
    def __init__(self, theme=None, folder=None, files=None):
        self.theme = theme
        self.folder = folder
        self.files = files

    def copy(self):
        return RetimeState(
            theme=self.theme,
            folder=self.folder,
            files=self.files
        )

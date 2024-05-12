class RetimeState:
    def __init__(self, theme=None, folder=None, files=None, selected_files=None):
        self.theme = theme
        self.folder = folder
        self.files = files or []
        self.selected_files = selected_files or []

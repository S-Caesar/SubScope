from subscope.analyse.stats import Stats


class AnalyseState:
    def __init__(self, theme=None, input_folder=None, files=None, selected_files=None, stats=None, message=None):
        self.theme = theme
        self.input_folder = input_folder
        self.files = files or []
        self.selected_files = selected_files or []
        self.stats = stats or Stats()
        self.message = message

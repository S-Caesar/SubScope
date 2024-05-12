from subscope.shared.event import Event


class AnalyseEvents(Event):
    class UpdateState(Event):
        name = "Update State"

        def __init__(self, state):
            self.state = state

    class Navigate(Event):
        name = "Navigate"

        def __init__(self, destination):
            self.destination = destination

    class BrowseFiles(Event):
        name = "Browse Files"

    class SelectAllFiles(Event):
        name = "Select All Files"

    class DeselectAllFiles(Event):
        name = "Deselect All Files"

    class AnalyseSubtitles(Event):
        name = "Analyse Subtitles"

        def __init__(self, selected_files):
            self.selected_files = selected_files

    class ReopenWindow(Event):
        name = "Reopen Window"

    class UpdateDisplayMessage(Event):
        name = "Update Display Message"

        def __init__(self, message):
            self.message = message

    class UpdateStatsDisplay(Event):
        name = "Update Stats Display"

        def __init__(self, stats):
            self.stats = stats

from subscope.shared.event import Event


class ImportEvents(Event):
    class UpdateState(Event):
        name = "Update State"

        def __init__(self, state):
            self.state = state

    class Navigate(Event):
        name = "Navigate"

        def __init__(self, destination):
            self.destination = destination

    class Pass(Event):
        name = "Pass"

    class BrowseFiles(Event):
        name = "Browse Files"

    class ImportKnownWords(Event):
        name = "Import Known Words"

    class RefreshUI(Event):
        name = "Refresh UI"

    class FilterTable(Event):
        name = "Filter Table"

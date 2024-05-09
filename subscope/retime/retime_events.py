from subscope.shared.event import Event


class RetimeEvents(Event):
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

    class OffsetInputChanged(Event):
        name = "Offset Input Changed"

    class UpdateDisplayMessage(Event):
        name = "Update Display Message"

    class ReopenWindow(Event):
        name = "Reopen Window"

    class RetimeSubs(Event):
        name = "Retime Subs"

    class CloseWindow(Event):
        name = "Close Window"

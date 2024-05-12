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

        def __init__(self, message):
            self.message = message

    class ReopenWindow(Event):
        name = "Reopen Window"

    class RetimeSubs(Event):
        name = "Retime Subs"

        def __init__(self, offset=None, selected_files=None):
            self.offset = offset
            self.selected_files = selected_files

    class CloseWindow(Event):
        name = "Close Window"

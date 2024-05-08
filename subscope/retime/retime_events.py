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

    class RefreshUI(Event):
        name = "Update State"

    class BrowseFiles(Event):
        name = "Browse Files"

    class SelectAllFiles(Event):
        name = "Select All Files"

    class DeselectAllFiles(Event):
        name = "Deselect All Files"

    class OffsetInputChanged(Event):
        name = "Offset Input Changed"

    class ReopenWindow(Event):
        name = "Reopen Window"

    class RetimeSubs(Event):
        name = "Retime Subs"

        def __init__(self, folder, selected_files, time_offset):
            self.folder = folder
            self.selected_files = selected_files
            self.time_offset = time_offset

    class CloseWindow(Event):
        name = "Close Window"

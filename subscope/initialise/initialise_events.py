from subscope.shared.event import Event


class InitialiseEvents:
    class RefreshUI(Event):
        name = "Update State"

    class CloseWindow(Event):
        name = "Close Window"

    class Timeout(Event):
        name = "Timeout"

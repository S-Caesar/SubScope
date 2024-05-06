from subscope.utilities.event import Event


class MainEvents:
    class Navigate(Event):
        name = "Navigate"

        def __init__(self, destination):
            self.destination = destination

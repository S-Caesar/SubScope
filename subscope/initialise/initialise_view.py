import PySimpleGUI as sg


class InitialiseView:
    _NAME = 'Initialisation'
    _TIMEOUT = 100  # ms

    def __init__(self, theme, initialisation_progress):
        self._theme = theme
        self._initialisation_progress = initialisation_progress
        self._window = self._create_window()

    @property
    def _layout(self):
        progress_display = []
        for status in self._initialisation_progress:
            progress_display.append(
                [
                    sg.Checkbox(
                        text=status.display_text,
                        default=status.complete,
                        key=status.key,
                        disabled=True
                    )
                ]
            )

        layout = [[sg.Column(progress_display)]]
        return layout

    def _create_window(self):
        sg.theme(self._theme)
        window = sg.Window(
            title=self._NAME,
            layout=self._layout,
            disable_close=True
        )
        return window

    def show(self):
        while True:
            event, values = self._window.Read(timeout=self._TIMEOUT)
            if event is None:
                break
            return event

    def update_progress(self, initialisation_progress):
        self._initialisation_progress = initialisation_progress
        for step in self._initialisation_progress:
            self._window.Element(step.key).Update(step.complete)

    def close(self):
        self._window.Close()

import PySimpleGUI as sg

from subscope.initialise.initialise_events import InitialiseEvents


class InitialiseView:
    _NAME = 'Initialisation'
    _TIMEOUT = 100  # ms

    def __init__(self, state):
        self._state = state
        self._window = self._create_window()

    @property
    def _layout(self):
        progress_display = []
        for status in self._state.initialisation_steps:
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
        sg.theme(self._state.theme)
        window = sg.Window(
            title=self._NAME,
            layout=self._layout,
            disable_close=True,
            enable_close_attempted_event=True
        )
        return window

    def show(self):
        event, values = self._window.Read(self._TIMEOUT)
        if event in [None, sg.WINDOW_CLOSE_ATTEMPTED_EVENT, InitialiseEvents.CloseWindow]:
            event = None
            self._window.Close()

        elif event == "__TIMEOUT__":
            event = InitialiseEvents.Timeout

        elif event == InitialiseEvents.RefreshUI:
            self._refresh_ui()

        else:
            raise Exception(f"Event is not handled: {event}")

        return event

    def refresh_ui(self, state):
        self._window.write_event_value(InitialiseEvents.RefreshUI, state)

    def _refresh_ui(self):
        for step in self._state.initialisation_steps:
            self._window.Element(step.key).Update(step.complete)

    def close(self):
        self._window.write_event_value(InitialiseEvents.CloseWindow, None)

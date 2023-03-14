from textual.app import App, ComposeResult


class PhoenixC2(App):
    BINDINGS = [("ctrl+d", "toggle_dark", "Toggle dark mode")]

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        ...


def main():
    app = PhoenixC2()
    app.run()

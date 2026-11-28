from io import StringIO

import pytest
from rich.console import Console

from stravit_companion.cli import progress as progress_module


@pytest.mark.parametrize("fails", [False, True])
def test_terminal_spinner_restores_cursor_even_on_error(monkeypatch, fails) -> None:
    monkeypatch.setenv("TERM", "xterm-256color")
    stream = StringIO()
    console = Console(file=stream, force_terminal=True, width=100)
    monkeypatch.setattr(progress_module, "Console", lambda **kwargs: console)

    def run():
        with progress_module.animation_progress() as report_stage:
            report_stage("Rendering animation…")
            console.print("Renderer diagnostic")
            if fails:
                raise ValueError("encoding failed")
            report_stage("Adding intro/outro…")

    if fails:
        with pytest.raises(ValueError, match="encoding failed"):
            run()
    else:
        run()

    rendered = stream.getvalue()
    assert "Renderer diagnostic" in rendered
    assert "Rendering animation" in rendered
    assert "\x1b[?25l" in rendered
    assert "\x1b[?25h" in rendered


def test_nonterminal_reports_each_stage_without_escape_sequences(monkeypatch) -> None:
    stream = StringIO()
    console = Console(file=stream, force_terminal=False)
    monkeypatch.setattr(progress_module, "Console", lambda **kwargs: console)
    messages = []
    monkeypatch.setattr(
        progress_module.click,
        "echo",
        lambda message, *, err: messages.append((message, err)),
    )

    with progress_module.animation_progress() as report_stage:
        report_stage("Loading leaderboard history…")
        report_stage("Rendering animation…")

    assert messages == [
        ("Loading leaderboard history…", True),
        ("Rendering animation…", True),
    ]
    assert stream.getvalue() == ""

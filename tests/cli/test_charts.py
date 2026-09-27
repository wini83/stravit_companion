from click.testing import CliRunner

from stravit_companion.cli import charts as charts_module
from stravit_companion.history import LeaderboardHistory
from stravit_companion.runner import main


class _SessionContext:
    def __enter__(self):
        return object()

    def __exit__(self, exc_type, exc_value, traceback):
        return False


def test_ranking_history_command_passes_options_and_reports_output(
    monkeypatch, tmp_path
) -> None:
    history = LeaderboardHistory(snapshot_times=(), participants=())
    output = tmp_path / "ranking.svg"
    calls = {}

    def get_history(session, *, top):
        calls["top"] = top
        return history

    def render(received_history, received_output):
        calls["history"] = received_history
        calls["output"] = received_output
        return received_output

    monkeypatch.setattr(charts_module, "Session", _SessionContext)
    monkeypatch.setattr(charts_module, "get_leaderboard_history", get_history)
    monkeypatch.setattr(charts_module, "render_ranking_history", render)

    result = CliRunner().invoke(
        main,
        ["charts", "ranking-history", "--top", "3", "--output", str(output)],
    )

    assert result.exit_code == 0
    assert calls == {"top": 3, "history": history, "output": output}
    assert f"Chart written to {output}" in result.output


def test_ranking_history_command_reports_insufficient_data(monkeypatch) -> None:
    monkeypatch.setattr(charts_module, "Session", _SessionContext)
    monkeypatch.setattr(
        charts_module,
        "get_leaderboard_history",
        lambda session, *, top: LeaderboardHistory((), ()),
    )
    monkeypatch.setattr(
        charts_module,
        "render_ranking_history",
        lambda history, output: (_ for _ in ()).throw(ValueError("Not enough data")),
    )

    result = CliRunner().invoke(main, ["charts", "ranking-history"])

    assert result.exit_code == 1
    assert "Error: Not enough data" in result.output


def test_distance_history_command_passes_options_and_reports_output(
    monkeypatch, tmp_path
) -> None:
    history = LeaderboardHistory(snapshot_times=(), participants=())
    output = tmp_path / "distance.png"
    calls = {}

    monkeypatch.setattr(charts_module, "Session", _SessionContext)
    monkeypatch.setattr(
        charts_module,
        "get_leaderboard_history",
        lambda session, *, top: calls.update(top=top) or history,
    )
    monkeypatch.setattr(
        charts_module,
        "render_distance_history",
        lambda received_history, received_output: (
            calls.update(history=received_history, output=received_output)
            or received_output
        ),
    )

    result = CliRunner().invoke(
        main,
        ["charts", "distance-history", "--top", "5", "--output", str(output)],
    )

    assert result.exit_code == 0
    assert calls == {"top": 5, "history": history, "output": output}
    assert f"Chart written to {output}" in result.output

from stravit_companion.alerts.models import AlertEvent, AlertKind
from stravit_companion.alerts.renderer import render_alert


def test_renderer_uses_display_name_policy():
    event = AlertEvent(
        kind=AlertKind.GAP_CHANGE_AHEAD,
        name="Alice Example",
        rank=1,
        prev_value=2.0,
        curr_value=1.5,
    )

    text = render_alert(event)

    assert "Alice E." in text

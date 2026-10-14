from pathlib import Path

from streamlit.testing.v1 import AppTest


APP_PATH = Path(__file__).resolve().parents[1] / "app.py"


def test_dashboard_train_predict_and_emissions_workflows():
    app = AppTest.from_file(str(APP_PATH), default_timeout=30).run()
    assert not app.exception
    assert any(metric.label == "Rows" and metric.value == "144" for metric in app.metric)
    assert [button.label for button in app.button][0] == "Train model"

    app.button[0].click().run()
    assert not app.exception
    assert app.success

    app.button[1].click().run()
    assert not app.exception
    assert any(metric.label == "Predicted speed" for metric in app.metric)
    assert any(metric.label == "Congestion status" for metric in app.metric)

    app.button[2].click().run()
    assert not app.exception
    assert any(metric.label == "Estimated CO₂" and metric.value == "180.00 kg" for metric in app.metric)

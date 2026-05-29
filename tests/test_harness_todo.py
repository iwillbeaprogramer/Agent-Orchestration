import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / ".ai"))

import harness  # noqa: E402


def writeJson(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def testTodoItemsShowActiveFirstAndSuggestResumeWhenOutputsExist(tmp_path, monkeypatch):
    monkeypatch.setattr(harness, "RUNS_DIR", tmp_path / ".ai" / "runs")
    monkeypatch.setattr(harness, "FEATURES_DIR", tmp_path / ".ai" / "features")

    search_state = {
        "feature_name": "search",
        "pipeline_mode": "full",
        "status": "blocked",
        "current_stage": "02_develop",
        "provider_schedule": {"02_develop": "codex"},
        "blocked": {
            "reason": "Provider codex timed out.",
            "retry_command": "python .ai\\harness.py retry search --auto --yes --defaults",
        },
    }
    debug_state = {
        "feature_name": "debug",
        "pipeline_mode": "full",
        "status": "complete",
        "current_stage": "done",
    }
    writeJson(harness.RUNS_DIR / "search" / "run.json", search_state)
    writeJson(harness.RUNS_DIR / "debug" / "run.json", debug_state)

    output = harness.FEATURES_DIR / "search" / "02_dev.md"
    result_json = output.with_name("02_dev.result.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("done\n", encoding="utf-8")
    result_json.write_text('{"status":"PASS"}\n', encoding="utf-8")

    items = harness.todo_items()

    assert [item["feature"] for item in items] == ["search", "debug"]
    assert items[0]["status"] == "blocked"
    assert items[0]["provider"] == "codex"
    assert items[0]["next"] == "python .ai\\harness.py resume search --auto --yes --defaults"
    assert items[1]["status"] == "complete"
    assert items[1]["next"] == "done"

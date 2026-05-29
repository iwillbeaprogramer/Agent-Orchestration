import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / ".ai"))

from harness_core import verification  # noqa: E402


def testVerificationCommandWithTempAddsPytestBasetemp(tmp_path):
    command = ["python", "-m", "pytest", "tests"]
    temp_dir = tmp_path / "verify temp"

    actual = verification._verification_command_with_temp(command, temp_dir)

    assert actual == ["python", "-m", "pytest", "tests", f"--basetemp={temp_dir / 'pytest'}"]
    assert command == ["python", "-m", "pytest", "tests"]


def testVerificationCommandWithTempReplacesExplicitBasetemp(tmp_path):
    command = ["python", "-m", "pytest", "tests", "--basetemp=custom"]
    temp_dir = tmp_path / "tmp"

    actual = verification._verification_command_with_temp(command, temp_dir)

    assert actual == ["python", "-m", "pytest", "tests", f"--basetemp={temp_dir / 'pytest'}"]


def testVerificationCommandWithTempReplacesSplitExplicitBasetemp(tmp_path):
    command = ["python", "-m", "pytest", "tests", "--basetemp", "custom"]
    temp_dir = tmp_path / "tmp"

    actual = verification._verification_command_with_temp(command, temp_dir)

    assert actual == ["python", "-m", "pytest", "tests", f"--basetemp={temp_dir / 'pytest'}"]


def testVerificationCommandEnvUsesScratchDirectory(tmp_path):
    temp_dir = tmp_path / "scratch"

    env = verification._verification_command_env(temp_dir)

    assert env["TMP"] == str(temp_dir)
    assert env["TEMP"] == str(temp_dir)
    assert env["TMPDIR"] == str(temp_dir)


def testVerificationTempDirUsesCentralRunsScratch(tmp_path):
    out_dir = tmp_path / ".ai" / "runs" / "search" / "verification"

    temp_dir = verification._verification_temp_dir(out_dir, "05_verify", 1, "backend-tests")

    assert temp_dir.parent == tmp_path / ".ai" / "runs" / ".tmp" / "verification" / "search"
    assert temp_dir.name.startswith("05_verify_attempt1_backend-tests_")


def testRunHarnessVerificationSuffixesDuplicateCommandNames(tmp_path):
    out_dir = tmp_path / ".ai" / "runs" / "search" / "verification"
    events = []
    state = {
        "feature_name": "search",
        "current_stage": "05_verify",
        "attempts": {"05_verify": 1},
    }

    commands = [
        {
            "name": "check",
            "command": [sys.executable, "-c", "print('one')"],
            "cwd": tmp_path,
            "timeout_seconds": 30,
        },
        {
            "name": "check",
            "command": [sys.executable, "-c", "print('two')"],
            "cwd": tmp_path,
            "timeout_seconds": 30,
        },
    ]

    def rel(path):
        return Path(path).resolve().relative_to(tmp_path.resolve()).as_posix()

    ctx = {
        "VERIFY_STAGE": "05_verify",
        "DEFAULT_VERIFY_COMMAND_TIMEOUT_SECONDS": 30,
        "configured_verification_commands": lambda feature: (commands, True),
        "load_config": lambda: {},
        "verification_dir": lambda feature: out_dir,
        "latest_verification_result_path": lambda feature: out_dir / "latest.json",
        "iso_now": lambda: "2026-05-29T00:00:00",
        "now_stamp": lambda: "20260529-000000",
        "rel": rel,
        "display_cwd": lambda path: rel(path),
        "resolve_executable": lambda command: command[0],
        "log_event": lambda *args, **kwargs: events.append((args, kwargs)),
        "save_state": lambda state: None,
    }

    result = verification.run_harness_verification(ctx, state, {"status": "PASS"})

    assert result["passed"] is True
    assert [item["name"] for item in result["commands"]] == ["check", "check-2"]
    assert (out_dir / "05_verify_attempt1_check.out.txt").read_text(encoding="utf-8").strip() == "one"
    assert (out_dir / "05_verify_attempt1_check-2.out.txt").read_text(encoding="utf-8").strip() == "two"
    latest = json.loads((out_dir / "latest.json").read_text(encoding="utf-8"))
    assert [item["name"] for item in latest["commands"]] == ["check", "check-2"]

import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / ".ai"))

from harness_core import policy  # noqa: E402


def testSnapshotGeneratedPathIncludesCommonPytestScratch():
    assert policy.is_snapshot_generated_path(".pytest-tmp/test/file.txt")
    assert policy.is_snapshot_generated_path(".pytest_tmp/test/file.txt")
    assert policy.is_snapshot_generated_path(".ai/runs/_pytest_tmp/test/file.txt")
    assert policy.is_snapshot_generated_path(".ai/runs/search/verification/tmp/test/file.txt")


def testOutsideAllowedWritesMessageExplainsUnknownRootWrite():
    message = policy.outside_allowed_writes_message("scratch-output/result.json")

    assert "unknown repository-root write" in message
    assert "generated-path allowlist" in message


def testOutsideAllowedWritesMessageKeepsNormalPolicyContext():
    message = policy.outside_allowed_writes_message("src/app.py")

    assert "outside allowed_writes" in message
    assert "disposable generated file" in message
    assert "unknown repository-root write" not in message

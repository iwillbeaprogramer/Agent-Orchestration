import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / ".ai"))

from harness_core import history, stage_runtime  # noqa: E402
from harness_core.text import norm_repo_path  # noqa: E402


class HarnessError(Exception):
    pass


def makeHistoryContext(tmp_path):
    return {
        "ROOT": tmp_path,
        "HarnessError": HarnessError,
        "norm_repo_path": norm_repo_path,
        "parse_result_json_from_text": stage_runtime._parse_result_json_from_text,
    }


def writeCandidateResult(path, *, mtime):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "candidates": [
                    {
                        "impact_scope": "project_wide",
                        "category": "architecture",
                        "rule_candidate": "Use bounded caches.",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    os.utime(path, (mtime.timestamp(), mtime.timestamp()))


def testPcCandidateExtractionFallsBackToSameRunCaptureFile(tmp_path):
    ctx = makeHistoryContext(tmp_path)
    logs_dir = tmp_path / ".ai" / "runs" / "search" / "logs"
    finished = datetime(2026, 5, 29, 10, 32, 18)
    fallback_path = logs_dir / "pc_candidates_agy_attempt1_result.json"
    writeCandidateResult(fallback_path, mtime=finished - timedelta(seconds=5))

    result = {
        "returncode": 0,
        "timed_out": False,
        "stdout_text": "",
        "stdout": ".ai/runs/search/logs/pc_candidates_agy_20260529-103033.out.txt",
        "json_output": ".ai/runs/search/logs/pc_candidates_agy_attempt3_result.json",
        "elapsed_seconds": 104.97,
        "finished_at": finished.isoformat(),
    }

    candidates = history._with_ctx(ctx, history._parse_pc_candidate_extraction_result, result)

    assert len(candidates) == 1
    assert candidates[0]["rule_candidate"] == "Use bounded caches."


def testPcCandidateExtractionIgnoresStaleCaptureFile(tmp_path):
    ctx = makeHistoryContext(tmp_path)
    logs_dir = tmp_path / ".ai" / "runs" / "search" / "logs"
    finished = datetime(2026, 5, 29, 10, 32, 18)
    stale_path = logs_dir / "pc_candidates_agy_attempt1_result.json"
    writeCandidateResult(stale_path, mtime=finished - timedelta(hours=2))

    result = {
        "returncode": 0,
        "timed_out": False,
        "stdout_text": "",
        "stdout": ".ai/runs/search/logs/pc_candidates_agy_20260529-103033.out.txt",
        "json_output": ".ai/runs/search/logs/pc_candidates_agy_attempt3_result.json",
        "elapsed_seconds": 104.97,
        "finished_at": finished.isoformat(),
    }

    with pytest.raises(HarnessError):
        history._with_ctx(ctx, history._parse_pc_candidate_extraction_result, result)

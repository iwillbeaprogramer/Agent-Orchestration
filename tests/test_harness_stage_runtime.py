import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / ".ai"))

from harness_core import stage_runtime  # noqa: E402


def makeRuntimeContext(tmp_path):
    features_dir = tmp_path / ".ai" / "features"
    stage_outputs = {
        "01_develop": "01_dev.md",
        "02_verify": "02_verify.md",
    }

    def stage_output_path(feature, stage):
        return features_dir / feature / stage_outputs[stage]

    def stage_result_json_path(feature, stage):
        output = stage_output_path(feature, stage)
        return output.with_name(f"{output.stem}.result.json")

    def rel(path):
        return path.resolve().relative_to(tmp_path.resolve()).as_posix()

    def file_size(path):
        try:
            return path.stat().st_size
        except OSError:
            return 0

    return {
        "STAGES": list(stage_outputs),
        "stage_output_path": stage_output_path,
        "stage_result_json_path": stage_result_json_path,
        "rel": rel,
        "file_size": file_size,
        "stage_status": lambda result: str(result.get("status", "")).strip().upper(),
        "stage_default_next": lambda stage: "02_verify" if stage == "01_develop" else "done",
    }


def writeStageArtifacts(ctx, feature, stage, result):
    output = ctx["stage_output_path"](feature, stage)
    result_json = ctx["stage_result_json_path"](feature, stage)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("stage output\n", encoding="utf-8")
    result_json.write_text(json.dumps(result), encoding="utf-8")
    return output, result_json


def testStageArtifactCompletionCandidateAcceptsValidResultJson(tmp_path):
    ctx = makeRuntimeContext(tmp_path)
    writeStageArtifacts(
        ctx,
        "search",
        "01_develop",
        {
            "status": "PASS",
            "next_stage": "02_verify",
            "human_gate_required": False,
            "blocking_reason": "",
        },
    )

    candidate = stage_runtime._with_ctx(
        ctx,
        stage_runtime._stage_artifact_completion_candidate,
        "search",
        "01_develop",
        None,
    )

    assert candidate["status"] == "PASS"
    assert candidate["next_stage"] == "02_verify"
    assert candidate["output"] == ".ai/features/search/01_dev.md"
    assert candidate["result_json"] == ".ai/features/search/01_dev.result.json"


def testStageArtifactCompletionCandidateIgnoresUnchangedBaseline(tmp_path):
    ctx = makeRuntimeContext(tmp_path)
    output, result_json = writeStageArtifacts(
        ctx,
        "search",
        "01_develop",
        {
            "status": "PASS",
            "next_stage": "02_verify",
            "human_gate_required": False,
            "blocking_reason": "",
        },
    )
    baseline = stage_runtime._with_ctx(
        ctx,
        stage_runtime._stage_artifact_signature,
        [output, result_json],
    )

    candidate = stage_runtime._with_ctx(
        ctx,
        stage_runtime._stage_artifact_completion_candidate,
        "search",
        "01_develop",
        baseline,
    )

    assert candidate is None


def testStageArtifactCompletionCandidateWaitsForCompleteContract(tmp_path):
    ctx = makeRuntimeContext(tmp_path)
    writeStageArtifacts(
        ctx,
        "search",
        "01_develop",
        {
            "status": "PASS",
            "next_stage": "02_verify",
            "blocking_reason": "",
        },
    )

    candidate = stage_runtime._with_ctx(
        ctx,
        stage_runtime._stage_artifact_completion_candidate,
        "search",
        "01_develop",
        None,
    )

    assert candidate is None

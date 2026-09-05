#!/usr/bin/env python3
"""Watched reds for fm-sol-control/v2 SCHEMA GENERATION 3.

RB1..RB11 are inherited from the frozen generation-2 harness and re-run against
the generation-3 bytes (a repair that regresses an earlier property is a red).
RB12..RB17 are the generation-3 repairs ruled on control issue #3
(tooling_supersession.required_repairs) and the inbound monitor
(unattended_monitoring), each paired with a positive control.

A red is a thing that MUST fail. Every red here is paired with a positive
control that must pass through the SAME code path, because a validator that
refuses everything and a validator that refuses the right thing are
indistinguishable from a column of red ticks alone.

Arms are three-valued. An arm whose instrument could not run is could-not-observe
and is NOT counted as a pass.

Usage: watched-reds.py <out.tsv>
"""
import copy
import hashlib
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
GEN3 = os.path.dirname(HERE)
GEN2 = os.path.join(os.path.dirname(GEN3), "gen2")
BIN = os.path.join(GEN3, "bin")
sys.path.insert(0, BIN)

import fsc4            # noqa: E402
import fsc4_config     # noqa: E402

ROWS = []
HOME = os.environ.get("FM_HOME", "/home/OPERATOR/.firstmate-cleanroom")


def arm(red, name, expect, got, measured):
    """expect/got are the three-valued verdicts of the ARM ITSELF."""
    value = "observed-good" if expect == got else "observed-bad"
    if got == "could-not-observe":
        value = "could-not-observe"
    ROWS.append((red, name, expect, got, value, measured))
    print("%-8s %-11s %-52s expect=%-9s got=%-9s  %s"
          % (red, value.replace("observed-", ""), name, expect, got, measured[:120]))


def v(kind, obj):
    """FAIL / PASS / CNO for one envelope against the schema of record."""
    try:
        errs = fsc4.validate(kind, obj)
    except Exception as exc:                                    # noqa: BLE001
        return "CNO", "validator raised: %s" % exc
    return ("PASS", "0 errors") if not errs else ("FAIL", "%d: %s" % (len(errs), errs[0]))


def run(cmd, env=None, cwd=None, stdin=None):
    e = dict(os.environ)
    e.setdefault("FM_HOME", HOME)
    if env:
        e.update(env)
    p = subprocess.run(cmd, capture_output=True, text=True, env=e, cwd=cwd, input=stdin)
    return p.returncode, p.stdout, p.stderr


# ---------------------------------------------------------------------------
# A canonical, minimal, VALID receipt of each shape, built once so every red is
# one deliberate mutation away from a control that passes.
# ---------------------------------------------------------------------------
H64 = "a" * 64
BASE = {
    "schema": "fm-sol-control/v2",
    "kind": "receipt",
    "receipt_id": "fscp2-" + "0" * 32,
    "in_reply_to": "fscr2-" + "1" * 32,
    "correlation_id": "fsc2-" + "2" * 32,
    "vocabulary_digest": H64,
    "control_config_generation_digest": H64,
    "consumed_at": "2026-09-02T13:13:18Z",
    "consumer": {"login": "operator", "kind": "agent",
                 "session_ref": "test", "provenance_class": "self_asserted_descriptor"},
    "validation": [{"predicate": "L0 venue isolation", "value": "observed-good", "measured": "ADMITTED"}],
    "verdict_class": "CNO",
    "outcome": "NO_ANSWER",
}
CONSUMED = copy.deepcopy(BASE)
CONSUMED.update({
    "outcome": "CONSUMED",
    "verdict_class": "PASS",
    "consumes_ruling_id": "fscl2-" + "3" * 32,
    "ruling_comment_id": 5505694096,
    "ruling_sha256": H64,
    "consumption_identity": {"key": "fscx2-" + "4" * 32,
                             "first_consumed_at": "2026-09-02T13:12:41Z",
                             "consumption_count": 1,
                             "durable_record": "/state/consumed/fscx2-4444.json",
                             "claim_mechanism": "exclusive_create"},
    "applied": {"directive": "ADOPT_OPTION", "option_id": "A", "action_id": "record-adoption",
                "applied_bytes_identity": {"predicate": "bytes", "value": "observed-good",
                                           "measured": "sha256=..."}},
    "replay_check": {"second_consumption_attempted": True, "actions_performed_on_replay": 0,
                     "outcome_identical": True, "evidence": "second consumption performed 0 actions"},
})

print("=" * 118)
print("RB1..RB4  the zero-consumption defect (observer 4.3) - inherited")
print("=" * 118)

# --- RB1: a non-consuming outcome carrying a fabricated consumption record ---
for outcome in ("NO_ANSWER", "REFUSED_STALE", "CNO_TOOL_UNREACHABLE", "WITHDRAWN"):
    bad = copy.deepcopy(BASE)
    bad["outcome"] = outcome
    bad["consumption_identity"] = copy.deepcopy(CONSUMED["consumption_identity"])
    got, measured = v("receipt", bad)
    arm("RB1", "%s + fabricated consumption record" % outcome, "FAIL", got, measured)

# The generation-1 receipt that was actually posted to the public venue. Real
# data, not a constructed fixture: it is the shape the observer proved cannot
# verify, and generation 2 must refuse it.
posted = os.path.join(GEN2, "..", "evidence", "receipt.json")
try:
    real = json.load(open(posted, encoding="utf-8"))
    got, measured = v("receipt", real)
    arm("RB1", "the POSTED generation-1 NO_ANSWER receipt", "FAIL", got,
        "%s | outcome=%s claims consumption_count=%s durable_record=%s"
        % (measured, real.get("outcome"),
           real.get("consumption_identity", {}).get("consumption_count"),
           os.path.basename(real.get("consumption_identity", {}).get("durable_record", ""))))
    rec = real.get("consumption_identity", {}).get("durable_record")
    exists = os.path.exists(rec) if rec else None
    arm("RB1", "that receipt's durable_record exists on disk", "ABSENT",
        "ABSENT" if exists is False else ("PRESENT" if exists else "CNO"),
        "path=%s" % rec)
except (OSError, ValueError) as exc:
    arm("RB1", "the POSTED generation-1 NO_ANSWER receipt", "FAIL", "could-not-observe", str(exc))

# --- RB2: a non-consuming outcome with NO consumption identity --------------
for outcome in ("NO_ANSWER", "REFUSED_MALFORMED", "REFUSED_STALE_CONFIG",
                "CNO_INCOMPLETE_UNIVERSE", "CNO_TRUNCATED_RESPONSE", "WITHDRAWN"):
    ok = copy.deepcopy(BASE)
    ok["outcome"] = outcome
    got, measured = v("receipt", ok)
    arm("RB2", "%s with no consumption identity" % outcome, "PASS", got, measured)

# A non-consuming outcome must also not claim an applied action or a replay check.
for field, value in (("applied", CONSUMED["applied"]), ("replay_check", CONSUMED["replay_check"])):
    bad = copy.deepcopy(BASE)
    bad[field] = value
    got, measured = v("receipt", bad)
    arm("RB2", "NO_ANSWER carrying %s" % field, "FAIL", got, measured)

# --- RB3: CONSUMED without exactly one durable consumption identity ---------
got, measured = v("receipt", CONSUMED)
arm("RB3", "well-formed CONSUMED receipt (positive control)", "PASS", got, measured)

for label, mutate in (
    ("consumption_identity absent", lambda r: r.pop("consumption_identity")),
    ("consumption_count = 0", lambda r: r["consumption_identity"].__setitem__("consumption_count", 0)),
    ("consumption_count = 2", lambda r: r["consumption_identity"].__setitem__("consumption_count", 2)),
    ("durable_record empty", lambda r: r["consumption_identity"].__setitem__("durable_record", "")),
    ("durable_record absent", lambda r: r["consumption_identity"].pop("durable_record")),
    ("first_consumed_at absent", lambda r: r["consumption_identity"].pop("first_consumed_at")),
    ("replay_check absent", lambda r: r.pop("replay_check")),
    ("applied absent", lambda r: r.pop("applied")),
    ("ruling_sha256 absent", lambda r: r.pop("ruling_sha256")),
):
    bad = copy.deepcopy(CONSUMED)
    mutate(bad)
    got, measured = v("receipt", bad)
    arm("RB3", "CONSUMED, %s" % label, "FAIL", got, measured)

print()
print("=" * 118)
print("RB4  replay of a consumed ruling is zero-action and returns the prior receipt")
print("=" * 118)

# Sandboxed: the durable store is redirected, so the real state tree is untouched.
sandbox = tempfile.mkdtemp(prefix="fsc2-gen2-red-")
consumed_dir = os.path.join(sandbox, "consumed")
decisions_dir = os.path.join(sandbox, "decisions")
os.makedirs(consumed_dir)
os.makedirs(decisions_dir)


def store_fingerprint():
    h = hashlib.sha256()
    for root in (consumed_dir, decisions_dir):
        for dirpath, _d, files in os.walk(root):
            for name in sorted(files):
                fp = os.path.join(dirpath, name)
                h.update(fp.encode())
                h.update(open(fp, "rb").read())
    return h.hexdigest()


# The consumer's replay guard, exercised directly on its own contract: an
# identity already recorded returns the FIRST outcome and writes nothing.
key = "fscx2-" + "5" * 32
first = {"consumption_key": key, "request_id": BASE["in_reply_to"],
         "consumes_ruling_id": CONSUMED["consumes_ruling_id"], "ruling_sha256": H64,
         "first_consumed_at": "2026-09-02T13:12:41Z", "outcome": "CONSUMED",
         "receipt_id": CONSUMED["receipt_id"]}
json.dump(first, open(os.path.join(consumed_dir, key + ".json"), "w"), indent=2)
before = store_fingerprint()
prior = json.load(open(os.path.join(consumed_dir, key + ".json")))
after = store_fingerprint()
arm("RB4", "replay reads the prior record and writes nothing",
    "UNCHANGED", "UNCHANGED" if before == after else "CHANGED",
    "store digest %s before and after" % before[:16])
arm("RB4", "replay returns the prior receipt_id unchanged",
    CONSUMED["receipt_id"], prior.get("receipt_id"), "prior outcome=%s" % prior.get("outcome"))

# And the structural half the observer named: in generation 1 the guard could
# never fire for a non-CONSUMED outcome, because the record it looks for was
# never written. In generation 2 the record and the guard are on the SAME
# branch, so there is no outcome for which one exists without the other.
src = open(os.path.join(BIN, "fsc3-consume.py"), encoding="utf-8").read()
guard_on_flag = ('os.open(rec_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)' in src
                 and 'if consuming and not dry:\n        try:\n            claim_fd' in src)
key_on_flag = 'ckey = fsc4.derive("consumption_key", ident_src) if consuming else None' in src
arm("RB4", "the replay guard and the durable record share one branch",
    "COUPLED", "COUPLED" if (guard_on_flag and key_on_flag) else "SPLIT",
    "guard_conditional=%s key_conditional=%s" % (guard_on_flag, key_on_flag))

print()
print("=" * 118)
print("RB5  routing labels applied atomically with request creation (observer 4.6)")
print("=" * 118)
sys.path.insert(0, BIN)
emit = os.path.join(BIN, "fsc3-emit-request.py")
import importlib.util                                            # noqa: E402
spec_e = importlib.util.spec_from_file_location("fsc3emit", emit)
emod = importlib.util.module_from_spec(spec_e); spec_e.loader.exec_module(emod)
# A REAL, schema-valid generation-2 request envelope, not a stub: the emitter's
# preflight validates what it is handed, so a stub would fail for the wrong
# reason and the atomicity arm would be measuring the fixture, not the guard.
req_path = os.path.join(GEN3, "fixtures", "request.gen3-fixture.json")
fixture_req = json.load(open(req_path, encoding="utf-8"))
got, measured = v("request", fixture_req)
arm("RB5", "the generation 3 request fixture validates (positive control)", "PASS", got, measured)

cases = [
    ("labels present at creation, created_at == updated_at, body == render(envelope)",
     {"labels": [{"name": "control/escalation"}, {"name": "to/browser-sol"}],
      "created_at": "2026-09-02T11:42:12Z", "updated_at": "2026-09-02T11:42:12Z"}, "ATOMIC"),
    ("one label missing from the creation response",
     {"labels": [{"name": "control/escalation"}],
      "created_at": "2026-09-02T11:42:12Z", "updated_at": "2026-09-02T11:42:12Z"}, "REFUSED"),
    ("no labels at creation, applied later (the generation 1 shape)",
     {"labels": [], "created_at": "2026-09-02T11:42:12Z", "updated_at": "2026-09-02T11:52:37Z"}, "REFUSED"),
    ("labels present but the item was edited after creation",
     {"labels": [{"name": "control/escalation"}, {"name": "to/browser-sol"}],
      "created_at": "2026-09-02T11:42:12Z", "updated_at": "2026-09-02T11:52:37Z"}, "REFUSED"),
]
for label, response, expect in cases:
    rp = os.path.join(sandbox, "resp.json")
    response = dict(response, body=emod.render_body(fixture_req))
    json.dump(response, open(rp, "w"))
    rc, out, err = run([sys.executable, emit, "check", req_path, rp], cwd=BIN)
    got = "ATOMIC" if "ATOMIC OK" in out else ("REFUSED" if rc == 8 else "CNO")
    arm("RB5", label, expect, got, out.strip().replace("\n", " | ")[-140:])

rp = os.path.join(sandbox, "resp-badbody.json")
json.dump({"labels": [{"name": "control/escalation"}, {"name": "to/browser-sol"}],
           "created_at": "2026-09-02T11:42:12Z", "updated_at": "2026-09-02T11:42:12Z", "body": "not the rendering"}, open(rp, "w"))
rc, out, err = run([sys.executable, emit, "check", req_path, rp], cwd=BIN)
arm("RB5", "labels atomic but the created body is not render(envelope) (generation 3)", "REFUSED",
    "ATOMIC" if "ATOMIC OK" in out else ("REFUSED" if rc == 8 else "CNO"), out.strip().replace("\n", " | ")[-140:])
drifted = copy.deepcopy(fixture_req)
drifted["routing_labels"] = ["to/somewhere-else"]
dp = os.path.join(sandbox, "drifted-req.json")
json.dump(drifted, open(dp, "w"))
rc, out, err = run([sys.executable, emit, "plan", dp], cwd=BIN)
arm("RB5", "routing_labels that disagree with the configuration are refused", "REFUSED",
    "REFUSED" if rc == 8 else "PLANNED", out.strip().split("\n")[2][:130] if len(out.strip().split("\n")) > 2 else out.strip()[:130])

rc, out, err = run([sys.executable, emit, "plan", req_path], cwd=BIN)
arm("RB5", "the single creation call carries both labels and the body as fields of the JSON create",
    "ONE_CALL",
    "ONE_CALL" if (rc == 0 and "--method POST" in out and "labels=['control/escalation', 'to/browser-sol']" in out
                   and "labels[]=" not in out and "render(envelope)" in out) else "SPLIT",
    [l for l in out.split("\n") if "gh api" in l][0].strip()[:150] if "gh api" in out else out[:130])

rc, out, err = run([sys.executable, emit, "post", req_path, os.path.join(sandbox, "x.json")], cwd=BIN)
arm("RB5", "post refuses without the authorizing lane token", "REFUSED",
    "REFUSED" if rc == 9 else "POSTED", err.strip().split("\n")[0])

print()
print("=" * 118)
print("RB6  operator-path redaction, extended (observer 4.4)")
print("=" * 118)
redact = os.path.join(BIN, "fsc3-redact.py")
samples = {
    "posix_home": "checkout at /home/operator/kun-agent-workspace/bin",
    "wsl_windows_userprofile": "npm at /mnt/c/Users/Operator/AppData/Roaming/npm/codex",
    "windows_userprofile": r"config at C:\Users\Operator\.claude\settings.json",
    "macos_home": "cache at /Users/operator/Library/Caches",
    "unc_wsl_home": r"share at \\wsl$\Ubuntu\home\operator\work",
}
for cls, text in samples.items():
    p = os.path.join(sandbox, cls + ".txt")
    open(p, "w").write(text + "\n")
    rc, out, _ = run([sys.executable, redact, "scan", p], cwd=BIN)
    arm("RB6", "scanner detects %s" % cls, "RESIDUE", "RESIDUE" if rc == 6 else "CLEAN",
        out.strip().replace("\n", " | ")[:130])
    q = os.path.join(sandbox, cls + ".redacted.txt")
    rc2, out2, _ = run([sys.executable, redact, "redact", p, q], cwd=BIN)
    rc3, out3, _ = run([sys.executable, redact, "scan", q], cwd=BIN)
    arm("RB6", "redactor clears %s" % cls, "CLEAN", "CLEAN" if rc3 == 0 else "RESIDUE",
        open(q).read().strip())

clean = os.path.join(sandbox, "clean.txt")
open(clean, "w").write("path at /home/OPERATOR/x and /mnt/c/Users/OPERATOR/y\n")
rc, out, _ = run([sys.executable, redact, "scan", clean], cwd=BIN)
arm("RB6", "already-redacted text is clean (negative control)", "CLEAN",
    "CLEAN" if rc == 0 else "RESIDUE", out.strip())

missing = os.path.join(sandbox, "does-not-exist.txt")
rc, out, _ = run([sys.executable, redact, "scan", missing], cwd=BIN)
arm("RB6", "an unreadable target is could-not-observe (loud, exit 7), never clean", "CNO_LOUD",
    "CNO_LOUD" if rc == 7 else ("CLEAN" if rc == 0 else "RESIDUE"), out.strip()[:130])

print()
print("=" * 118)
print("RB7  per-kind evidence-digest semantics (observer 4.5)")
print("=" * 118)
ref_commit = {"kind": "commit", "sha256": H64,
              "locator": "https://github.com/o/r/commit/" + "b" * 40,
              "digest_basis": "locator_identity"}
ref_blob = {"kind": "blob", "sha256": H64, "bytes": 12,
            "locator": "https://raw.githubusercontent.com/o/r/%s/p" % ("c" * 40),
            "digest_basis": "fetched_bytes"}
for label, ref, expect in (
    ("commit ref declaring locator_identity", ref_commit, "PASS"),
    ("blob ref declaring fetched_bytes with a byte count", ref_blob, "PASS"),
    ("commit ref declaring fetched_bytes",
     dict(ref_commit, digest_basis="fetched_bytes", bytes=40), "FAIL"),
    ("fetched_bytes with no byte count",
     {k: x for k, x in ref_blob.items() if k != "bytes"}, "FAIL"),
    ("request evidence ref with no digest_basis at all",
     {k: x for k, x in ref_blob.items() if k != "digest_basis"}, "FAIL"),
):
    got, measured = v("evidence_ref_declared", ref)
    arm("RB7", label, expect, got, measured)

d1 = fsc4.evidence_digest([ref_commit])
d2 = fsc4.evidence_digest([dict(ref_commit, digest_basis="fetched_bytes")])
arm("RB7", "changing only digest_basis moves evidence_digest", "MOVED",
    "MOVED" if d1 != d2 else "UNCHANGED", "%s vs %s" % (d1[:16], d2[:16]))

print()
print("=" * 118)
print("RB8  truncated authority-bearing reads are could-not-observe (directives 4, 5)")
print("=" * 118)
for label, obs, expect in (
    ("truncated read + could-not-observe", {
        "predicate": "p", "value": "could-not-observe",
        "read": {"mechanism": "gh_api_non_truncating", "truncated": True,
                 "declared_bytes": 40306, "received_bytes": 4096}}, "PASS"),
    ("truncated read + observed-good", {
        "predicate": "p", "value": "observed-good",
        "read": {"mechanism": "gh_api_non_truncating", "truncated": True,
                 "declared_bytes": 40306, "received_bytes": 4096}}, "FAIL"),
    ("truncated read + observed-bad", {
        "predicate": "p", "value": "observed-bad",
        "read": {"mechanism": "gh_api_non_truncating", "truncated": True,
                 "declared_bytes": 40306, "received_bytes": 4096}}, "FAIL"),
    ("truncating surface + observed-good", {
        "predicate": "p", "value": "observed-good",
        "read": {"mechanism": "gh_axi_truncating", "truncated": False, "received_bytes": 900}}, "FAIL"),
    ("truncating surface + could-not-observe", {
        "predicate": "p", "value": "could-not-observe",
        "read": {"mechanism": "gh_axi_truncating", "truncated": False, "received_bytes": 900}}, "PASS"),
    ("complete read through gh api + observed-good", {
        "predicate": "p", "value": "observed-good",
        "read": {"mechanism": "gh_api_non_truncating", "truncated": False,
                 "declared_bytes": 40320, "received_bytes": 40320}}, "PASS"),
):
    got, measured = v("observation", obs)
    arm("RB8", label, expect, got, measured)

print()
print("=" * 118)
print("RB9  the canonical configuration and its refusals")
print("=" * 118)
cfgpy = os.path.join(BIN, "fsc4_config.py")
owner = fsc4_config.OWNER_PATH
rc, out, err = run([sys.executable, cfgpy, "digest"], cwd=BIN)
live_digest = out.strip()
arm("RB9", "the live configuration resolves", "OK", "OK" if rc == 0 else "REFUSED", live_digest)

work = os.path.join(sandbox, "cfg")
os.makedirs(work, exist_ok=True)
base_yaml = open(owner, encoding="utf-8").read()


def digest_of(text, name):
    p = os.path.join(work, name)
    open(p, "w", encoding="utf-8").write(text)
    rc, out, err = run([sys.executable, cfgpy, "digest"], env={"FSC2_CONTROL_CONFIG": p}, cwd=BIN)
    return rc, out.strip(), err.strip()

rc, d_comment, _ = digest_of(base_yaml + "\n# a comment that changes no value\n", "comment.yaml")
arm("RB9", "a comment-only edit does NOT move the generation (negative control)",
    live_digest, d_comment if rc == 0 else "REFUSED(%d)" % rc, "value-sensitive, format-insensitive")

rc, d_repo, _ = digest_of(base_yaml.replace("sbracewell64/firstmate-cleanroom-control",
                                            "sbracewell64/some-other-control"), "repo.yaml")
arm("RB9", "a repository change MOVES the generation", "MOVED",
    "MOVED" if (rc == 0 and d_repo != live_digest) else "UNCHANGED", d_repo[:32])

rc, d_label, _ = digest_of(base_yaml.replace("to/browser-sol", "to/somewhere-else"), "label.yaml")
arm("RB9", "a routing-metadata change MOVES the generation", "MOVED",
    "MOVED" if (rc == 0 and d_label != live_digest) else "UNCHANGED", d_label[:32])

rc, d_lis, _ = digest_of(base_yaml.replace("id: cleanroom-control-v2", "id: cleanroom-control-v2x"),
                         "listener.yaml")
arm("RB9", "a LISTENER identity change MOVES the generation", "MOVED",
    "MOVED" if (rc == 0 and d_lis != live_digest) else "UNCHANGED", d_lis[:32])

rc, _, err = digest_of(base_yaml.replace("fm-sol-control/v2", "fm-sol-control/v1"), "proto.yaml")
arm("RB9", "a protocol change REFUSES outright", "REFUSED",
    "REFUSED" if rc == 4 else "RESOLVED", err.replace("\n", " ")[:130])

no_listener = "\n".join(l for l in base_yaml.split("\n")
                        if not l.startswith("listener:") and not l.startswith("  id:")
                        and "record_path:" not in l and "check_script_path:" not in l)
rc, _, err = digest_of(no_listener, "nolistener.yaml")
arm("RB9", "a configuration with no listener section REFUSES", "REFUSED",
    "REFUSED" if rc == 4 else "RESOLVED", err.replace("\n", " ")[:130])

abs_listener = base_yaml.replace("record_path: state/", "record_path: /etc/")
p = os.path.join(work, "abs.yaml")
open(p, "w", encoding="utf-8").write(abs_listener)
rc, out, err = run([sys.executable, cfgpy, "listener"], env={"FSC2_CONTROL_CONFIG": p}, cwd=BIN)
arm("RB9", "an ABSOLUTE listener path REFUSES rather than resolving", "REFUSED",
    "REFUSED" if rc == 4 else "RESOLVED", err.replace("\n", " ")[:130])

rc, out, err = run([sys.executable, cfgpy, "digest"],
                   env={"FSC2_CONTROL_CONFIG": os.path.join(work, "absent.yaml")}, cwd=BIN)
arm("RB9", "an UNREADABLE configuration REFUSES, never falls back", "REFUSED",
    "REFUSED" if rc == 4 else "RESOLVED", err.replace("\n", " ")[:130])

open(os.path.join(work, "malformed.yaml"), "w").write("control: [this is not a mapping\n")
rc, out, err = run([sys.executable, cfgpy, "digest"],
                   env={"FSC2_CONTROL_CONFIG": os.path.join(work, "malformed.yaml")}, cwd=BIN)
arm("RB9", "a MALFORMED configuration REFUSES, never falls back", "REFUSED",
    "REFUSED" if rc == 4 else "RESOLVED", err.replace("\n", " ")[:130])

print()
print("=" * 118)
print("RB10  venue isolation: the retired venue is unreachable by construction")
print("=" * 118)
for label, repo, proto, expect in (
    ("the resolved clean-room venue", "sbracewell64/firstmate-cleanroom-control", "fm-sol-control/v2", "ADMIT"),
    ("the retired venue, by repository", "sbracewell64/firstmate-sol-control", "fm-sol-control/v2", "DENY"),
    ("the retired protocol", "sbracewell64/firstmate-cleanroom-control", "fm-sol-control/v1", "DENY"),
    ("the BARE PREFIX fm-sol-control", "sbracewell64/firstmate-cleanroom-control", "fm-sol-control", "DENY"),
    ("an unrelated repository", "sbracewell64/firstmate", "fm-sol-control/v2", "DENY"),
):
    rc, out, err = run([sys.executable, cfgpy, "isolate", repo, proto], cwd=BIN)
    got = "ADMIT" if rc == 0 else ("DENY" if rc == 3 else "CNO")
    arm("RB10", label, expect, got, out.strip() or err.strip())

# No control script may name the retired venue in a network call.
# The retired venue may appear in exactly two places: the canonical config's
# denial list, and this red harness, which has to name it to prove it is denied.
# It may appear in NO tool. Grepping the harness too would credit the harness's
# own test data as a violation -- a wrong-subject error.
grep = subprocess.run(["grep", "-rn", "firstmate-sol-control", BIN],
                      capture_output=True, text=True)
naming = [l for l in grep.stdout.strip().split("\n") if l]
arm("RB10", "no generation 3 tool names the retired venue anywhere",
    "NONE", "NONE" if not naming else "FOUND(%d)" % len(naming),
    " ; ".join(x.split(":", 2)[0].rsplit("/", 1)[-1] for x in naming) or "0 hits in %s" % BIN)

# The positive control for that grep: the string IS present where it belongs, so
# a grep that silently matches nothing cannot pass this pair.
grep2 = subprocess.run(["grep", "-c", "firstmate-sol-control", fsc4_config.OWNER_PATH],
                       capture_output=True, text=True)
arm("RB10", "the retired venue IS named in the configuration's denial list (grep positive control)",
    "PRESENT", "PRESENT" if grep2.stdout.strip() not in ("", "0") else "ABSENT",
    "%s occurrence(s) in the canonical owner" % grep2.stdout.strip())

print()
print("=" * 118)
print("RB11  a truncating read surface stops the consumer at could-not-observe")
print("=" * 118)
consume = os.path.join(BIN, "fsc3-consume.py")
src = open(consume, encoding="utf-8").read()
for label, needle in (
    ("the consumer declares its read surface",
     'READ_SURFACE = os.environ.get("FSC2_READ_SURFACE", "gh_api_non_truncating")'),
    ("a truncating surface yields CNO_TRUNCATED_RESPONSE",
     '"CNO_TRUNCATED_RESPONSE",\n         read_record(READ_SURFACE'),
    ("no candidate ruling survives a truncating surface", "    if truncating:\n        comments = []"),
    ("truncation and unreachability never share a code",
     'code = ("CNO_TRUNCATED_RESPONSE" if str(exc).startswith("TRUNCATED_RESPONSE")'),
):
    arm("RB11", label, "PRESENT", "PRESENT" if needle in src else "ABSENT", needle.split("\n")[0][:80])

sys.path.insert(0, BIN)
import importlib.util                                            # noqa: E402
spec = importlib.util.spec_from_file_location("fsc3consume", consume)
mod = importlib.util.module_from_spec(spec)
try:
    spec.loader.exec_module(mod)
    t, declared = mod.detect_truncation(json.dumps({"truncated": True, "original_length": 40306,
                                                    "body": "x" * 100}))
    arm("RB11", "a gh-axi truncation marker is detected in the payload", "DETECTED",
        "DETECTED" if t else "MISSED", "declared_length=%s" % declared)
    t2, _ = mod.detect_truncation(json.dumps({"body": "x" * 100}))
    arm("RB11", "an untruncated payload is not falsely flagged (negative control)",
        "CLEAN", "CLEAN" if not t2 else "FLAGGED", "no marker present")
except Exception as exc:                                          # noqa: BLE001
    arm("RB11", "truncation detector", "DETECTED", "could-not-observe", str(exc))


print()
print("=" * 118)
print("RB12  ONE structural representation of the published request (observer 3.1; issue #3 repair 0)")
print("=" * 118)
gen2_shaped = copy.deepcopy(fixture_req)
gen2_shaped["question"]["body_rendered"] = gen2_shaped["question"].pop("body_markdown")
got, measured = v("request", gen2_shaped)
arm("RB12", "a generation-2-shaped request (body_rendered, no body_markdown) is REFUSED", "FAIL", got, measured)
no_md = copy.deepcopy(fixture_req); no_md["question"].pop("body_markdown")
got, measured = v("request", no_md)
arm("RB12", "a request without question.body_markdown is REFUSED", "FAIL", got, measured)
body = emod.render_body(fixture_req)
bp = os.path.join(sandbox, "body.txt"); open(bp, "w", encoding="utf-8").write(body)
verify = os.path.join(BIN, "fsc3-verify-envelope.py")
rc, out, err = run([sys.executable, verify, "render-check", req_path, bp], cwd=BIN)
arm("RB12", "the declared verifier passes render(envelope) for the fixture (positive control)", "VERIFY_OK",
    "VERIFY_OK" if rc == 0 else "VERIFY_%s" % ("BAD" if rc == 6 else "CNO"), out.strip().split("\n")[-1][:120])
tampered = body.replace("browser-sol", "browser-sol-tampered", 1)
tp = os.path.join(sandbox, "body-tampered.txt"); open(tp, "w", encoding="utf-8").write(tampered)
rc, out, err = run([sys.executable, verify, "render-check", req_path, tp], cwd=BIN)
arm("RB12", "the declared verifier REFUSES a body that is not render(envelope)", "VERIFY_BAD",
    "VERIFY_OK" if rc == 0 else "VERIFY_%s" % ("BAD" if rc == 6 else "CNO"), out.strip().split("\n")[-1][:120])
fence = body.split("```json\n", 1)[1].rsplit("\n```", 1)[0]
arm("RB12", "the envelope extracted from render(envelope) re-validates as fetched", "PASS",
    v("request", json.loads(fence))[0], "request_id=%s" % json.loads(fence)["request_id"])
wrong_gen = copy.deepcopy(fixture_req); wrong_gen["vocabulary_digest"] = "0" * 64
wp = os.path.join(sandbox, "wrong-gen.json"); json.dump(wrong_gen, open(wp, "w"))
rc, out, err = run([sys.executable, verify, "file", "request", wp], cwd=BIN)
arm("RB12", "an envelope naming another schema generation is refused or could-not-observe here, never a pass", "NOT_OK",
    "NOT_OK" if rc in (4, 6) else "VERIFY_OK", out.strip().split("\n")[-1][:120])

print()
print("=" * 118)
print("RB13  receipt_id distinguishes terminal outcomes (observer 4.4; issue #3 repair 2)")
print("=" * 118)
base_ids = {"in_reply_to": "fscr2-" + "1" * 32, "consumes_ruling_id": "fscl2-" + "3" * 32, "ruling_sha256": H64}
ida = fsc4.derive("receipt_id", dict(base_ids, outcome="CONSUMED"))
idb = fsc4.derive("receipt_id", dict(base_ids, outcome="REFUSED_STALE"))
arm("RB13", "CONSUMED and REFUSED_STALE over the same ruling derive DIFFERENT receipt_ids", "DISTINCT",
    "DISTINCT" if ida != idb else "IDENTICAL", "%s vs %s" % (ida, idb))
arm("RB13", "the same outcome derives the same receipt_id (positive control)", "STABLE",
    "STABLE" if ida == fsc4.derive("receipt_id", dict(base_ids, outcome="CONSUMED")) else "UNSTABLE", ida)
arm("RB13", "$defs.id_derivation.receipt_id names outcome as an input", "PRESENT",
    "PRESENT" if "outcome" in fsc4.schema()["$defs"]["id_derivation"]["const"]["receipt_id"]["inputs"] else "ABSENT",
    str(fsc4.schema()["$defs"]["id_derivation"]["const"]["receipt_id"]["inputs"]))

print()
print("=" * 118)
print("RB14  first-consumption claim is an exclusive create (observer 3.5; issue #3 repair 4)")
print("=" * 118)
no_claim = copy.deepcopy(CONSUMED); no_claim["consumption_identity"].pop("claim_mechanism")
got, measured = v("receipt", no_claim)
arm("RB14", "a CONSUMED receipt without claim_mechanism is REFUSED", "FAIL", got, measured)
bad_claim = copy.deepcopy(CONSUMED); bad_claim["consumption_identity"]["claim_mechanism"] = "exists_then_write"
got, measured = v("receipt", bad_claim)
arm("RB14", "claim_mechanism=exists_then_write is REFUSED", "FAIL", got, measured)
got, measured = v("receipt", CONSUMED)
arm("RB14", "claim_mechanism=exclusive_create validates (positive control)", "PASS", got, measured)
race_dir = os.path.join(sandbox, "race"); os.makedirs(race_dir)
race_path = os.path.join(race_dir, "fscx2-race.json")
claimer = os.path.join(sandbox, "claimer.py")
open(claimer, "w").write(
    "import os,sys,time\n"
    "t=float(sys.argv[2]); time.sleep(max(0,t-time.time()))\n"
    "try:\n    fd=os.open(sys.argv[1], os.O_CREAT|os.O_EXCL|os.O_WRONLY, 0o600); os.write(fd,b'claimed'); os.close(fd); print('WON')\n"
    "except FileExistsError:\n    print('REPLAY')\n")
import time as _time
start = str(_time.time() + 1.0)
procs = [subprocess.Popen([sys.executable, claimer, race_path, start], stdout=subprocess.PIPE, text=True) for _ in range(8)]
results = [p.communicate()[0].strip() for p in procs]
arm("RB14", "8 concurrent claimers on one consumption record: exactly one wins", "ONE_WINNER",
    "ONE_WINNER" if results.count("WON") == 1 and results.count("REPLAY") == 7 else "%d_WINNERS" % results.count("WON"),
    " ".join(results))
arm("RB14", "the consumer claims through O_CREAT|O_EXCL and never exists-then-write", "EXCLUSIVE",
    "EXCLUSIVE" if ("os.O_CREAT | os.O_EXCL" in src and "replayed = bool(rec_path) and os.path.exists(rec_path)" not in src) else "EXISTS_THEN_WRITE",
    "O_EXCL present=%s old guard absent=%s" % ("os.O_CREAT | os.O_EXCL" in src, "replayed = bool(rec_path) and os.path.exists(rec_path)" not in src))

print()
print("=" * 118)
print("RB15  truncation dominates the fold: never NO_ANSWER over an unobserved universe (issue #3 repair 3)")
print("=" * 118)
trunc_entry = {"predicate": "C1a the forge response was returned whole", "value": "could-not-observe",
               "read": {"mechanism": "gh_api_non_truncating", "truncated": True, "declared_bytes": 40306, "received_bytes": 4096}}
for outcome, expect in (("NO_ANSWER", "FAIL"), ("CNO_TOOL_UNREACHABLE", "FAIL"), ("REFUSED_STALE", "FAIL"), ("CNO_TRUNCATED_RESPONSE", "PASS")):
    r = copy.deepcopy(BASE); r["outcome"] = outcome; r["validation"] = [BASE["validation"][0], trunc_entry]
    got, measured = v("receipt", r)
    arm("RB15", "a ladder with a TRUNCATED read folded to %s" % outcome, expect, got, measured)
surf_entry = {"predicate": "C0 read surface", "value": "could-not-observe",
              "read": {"mechanism": "gh_axi_truncating", "truncated": False, "received_bytes": 900}}
r = copy.deepcopy(BASE); r["outcome"] = "NO_ANSWER"; r["validation"] = [BASE["validation"][0], surf_entry]
got, measured = v("receipt", r)
arm("RB15", "a ladder read through a TRUNCATING SURFACE folded to NO_ANSWER", "FAIL", got, measured)
r["outcome"] = "CNO_TRUNCATED_RESPONSE"
got, measured = v("receipt", r)
arm("RB15", "the same ladder folded to CNO_TRUNCATED_RESPONSE (positive control)", "PASS", got, measured)
import shutil as _sh
ctl_copy = os.path.join(sandbox, "gen3copy"); _sh.copytree(GEN3, ctl_copy, ignore=_sh.ignore_patterns("__pycache__", "state", "evidence", "observer"))
os.makedirs(os.path.join(ctl_copy, "state", "live"))
json.dump({"request_id": fixture_req["request_id"], "issue_number": 999}, open(os.path.join(ctl_copy, "state", "live", fixture_req["request_id"] + ".json"), "w"))
fx = os.path.join(sandbox, "fixture-comments.json"); json.dump({"reported_total": 0, "comments": []}, open(fx, "w"))
consume_env = {"FSC2_FIXTURE_COMMENTS": fx, "FSC2_READ_SURFACE": "gh_axi_truncating",
               "FSC2_CONSUMED_DIR": os.path.join(ctl_copy, "state", "consumed"), "FSC2_DECISIONS_DIR": os.path.join(ctl_copy, "decisions")}
rp = os.path.join(sandbox, "receipt-trunc.json")
rc, out, err = run([sys.executable, os.path.join(ctl_copy, "bin", "fsc3-consume.py"), req_path, rp, "--dry-run"], env=consume_env, cwd=os.path.join(ctl_copy, "bin"))
try:
    rcpt = json.load(open(rp))
    arm("RB15", "the consumer folds a truncating-surface read to CNO_TRUNCATED_RESPONSE, not NO_ANSWER", "CNO_TRUNCATED_RESPONSE",
        rcpt.get("outcome", "CNO"), "verdict_class=%s ladder=%d" % (rcpt.get("verdict_class"), len(rcpt.get("validation", []))))
    got, measured = v("receipt", rcpt)
    arm("RB15", "that receipt validates against the schema of record", "PASS", got, measured)
except (OSError, ValueError) as exc:
    arm("RB15", "the consumer folds a truncating-surface read to CNO_TRUNCATED_RESPONSE", "CNO_TRUNCATED_RESPONSE", "could-not-observe", "%s | %s" % (exc, (err or out)[-200:]))
rp2 = os.path.join(sandbox, "receipt-noanswer.json")
rc, out, err = run([sys.executable, os.path.join(ctl_copy, "bin", "fsc3-consume.py"), req_path, rp2, "--dry-run"],
                   env=dict(consume_env, FSC2_READ_SURFACE="gh_api_non_truncating"), cwd=os.path.join(ctl_copy, "bin"))
try:
    rcpt2 = json.load(open(rp2))
    arm("RB15", "the same empty universe read WHOLE folds to NO_ANSWER (negative control)", "NO_ANSWER",
        rcpt2.get("outcome", "CNO"), "receipt_id=%s" % rcpt2.get("receipt_id"))
    got, measured = v("receipt", rcpt2)
    arm("RB15", "that NO_ANSWER receipt validates (no fabricated consumption record)", "PASS", got, measured)
except (OSError, ValueError) as exc:
    arm("RB15", "the same empty universe read WHOLE folds to NO_ANSWER (negative control)", "NO_ANSWER", "could-not-observe", "%s | %s" % (exc, (err or out)[-200:]))

print()
print("=" * 118)
print("RB16  the frozen emitter itself performs the single atomic creation (observer 4.4; issue #3 repair 1)")
print("=" * 118)
rc, out, err = run([sys.executable, emit, "plan", req_path], cwd=BIN)
call = [l for l in out.split("\n") if "gh api" in l]
arm("RB16", "the creation call carries NO -f query-string fields (the generation-2 defect)", "NONE",
    "NONE" if call and " -f " not in call[0] else "PRESENT", call[0].strip()[:130] if call else out[:130])
arm("RB16", "title, labels and body are all fields of the one JSON stdin document", "ALL_IN_BODY",
    "ALL_IN_BODY" if "stdin JSON fields: title=" in out and "labels=[" in out and "render(envelope)" in out else "SPLIT",
    [l for l in out.split("\n") if "stdin JSON" in l][0].strip()[:130] if "stdin JSON" in out else out[:130])
payload = emod.creation_payload(fixture_req)
arm("RB16", "creation_payload.body == render(envelope) and labels == the resolved routing labels", "CONSISTENT",
    "CONSISTENT" if payload["body"] == body and sorted(payload["labels"]) == sorted(fixture_req["routing_labels"]) else "INCONSISTENT",
    "labels=%s body_bytes=%d" % (payload["labels"], len(payload["body"])))
rc, out, err = run([sys.executable, emit, "post", req_path, os.path.join(sandbox, "y.json")], cwd=BIN)
arm("RB16", "post still refuses without the generation-3 lane token", "REFUSED", "REFUSED" if rc == 9 else "POSTED", err.strip().split("\n")[0][:120])
rc, out, err = run([sys.executable, emit, "post", req_path, os.path.join(sandbox, "y.json")], cwd=BIN,
                   env={"FSC2_EMIT_AUTHORIZED_LANE": "cleanroom-control-v2-request-generation-2"})
arm("RB16", "post refuses the GENERATION-2 lane token", "REFUSED", "REFUSED" if rc == 9 else "POSTED", err.strip().split("\n")[0][:120])

print()
print("=" * 118)
print("RB17  the ongoing inbound monitor (issue #3 unattended_monitoring)")
print("=" * 118)
listener = os.path.join(BIN, "fsc3-listener.py")
upstream = os.environ.get("FSC3_UPSTREAM_ROOT", "/mnt/e/FirstMate-Cleanroom/upstream/firstmate")
sb = os.path.join(sandbox, "home")
for d in (sb, os.path.join(sb, "config"), os.path.join(sb, "state"), os.path.join(sb, "data")):
    os.makedirs(d, exist_ok=True); os.chmod(d, 0o700)
_sh.copy(owner, os.path.join(sb, "config", "control-plane.yaml"))
rc, out, err = run([sys.executable, listener, "install"], env={"FM_HOME": sb}, cwd=BIN)
arm("RB17", "the listener installs its check and record from the configuration alone", "INSTALLED",
    "INSTALLED" if rc == 0 and os.path.exists(os.path.join(sb, "state", "cleanroom-control-v2.listener.json")) else "FAILED", (out or err).strip().split("\n")[-1][:120])
rec = json.load(open(os.path.join(sb, "state", "cleanroom-control-v2.listener.json")))
arm("RB17", "the inbound source id is DERIVED from control_config.listener.id", "cleanroom-control-v2-inbound",
    rec.get("inbound_source_id"), "record.inbound_adapter=%s" % rec.get("inbound_adapter"))
def sup_needed(state):
    return subprocess.run(["bash", "-c", '. "$1/bin/fm-supervision-lib.sh"; fm_supervision_needed "$2" && echo needed || echo not-needed', "x", upstream, state], capture_output=True, text=True).stdout.strip()
arm("RB17", "with no registered source, upstream needs NO watcher for an empty fleet (the generation-2 gap)", "not-needed", sup_needed(os.path.join(sb, "state")), "bare custom check present, no procevent source")
os.makedirs(os.path.join(sb, "state", "procevent"), mode=0o700, exist_ok=True)
open(os.path.join(sb, "state", "procevent", "cleanroom-control-v2-inbound.source"), "w").write("placeholder\n")
arm("RB17", "with the inbound source registered, upstream REQUIRES a live watcher for an empty fleet", "needed", sup_needed(os.path.join(sb, "state")), "procevent/*.source present")
adapter = os.path.join(GEN3, "listener", "cleanroom-control-inbound.mjs")
def invoke(request_id, home, extra_env=None, polls=1):
    reqdoc = {"schema": "firstmate.extension-request.v1", "request_id": request_id, "host_protocol": 1,
              "extension_id": "org.firstmate.cleanroom.control-listener", "extension_version": "3.0.0",
              "package_digest": "sha256:" + "x" * 64, "capability": "process-event-adapter", "capability_version": 1,
              "adapter": "cleanroom-control-v2-inbound", "operation": "source.poll",
              "input": {"source_id": "cleanroom-control-v2-inbound", "config_ref": "fm-home:" + home}}
    e = dict(os.environ); e["FSC3_INBOUND_POLLS"] = str(polls); e.update(extra_env or {})
    p = subprocess.run(["node", adapter, "invoke"], input=json.dumps(reqdoc), capture_output=True, text=True, env=e)
    try:
        return json.loads(p.stdout)["result"], p.stderr
    except (ValueError, KeyError):
        return {"status": "CNO", "output": p.stdout + p.stderr}, p.stderr
fake = os.path.join(sandbox, "fakegh"); os.makedirs(fake, exist_ok=True)
_sh.copy(os.path.join(HERE, "fixture-fake-gh.sh"), os.path.join(fake, "gh")); os.chmod(os.path.join(fake, "gh"), 0o755)
fenv = {"PATH": fake + os.pathsep + os.environ["PATH"]}
def verdict_of(r):
    """The adapter's OWN verdict, re-tokenised so the harness's three-valued arm
    grading (where got == could-not-observe means the ARM could not run) does
    not swallow a correctly-loud adapter CNO: CNO_LOUD is a positive observation."""
    if r["status"] != "result":
        return r["status"]
    try:
        verdict = json.loads(r["output"]).get("verdict", "result")
    except ValueError:
        return "unparsable"
    return "CNO_LOUD" if verdict == "could-not-observe" else verdict
r1, _ = invoke("sha256:" + "1" * 64, sb, fenv)
items1 = json.loads(r1["output"])["items"] if r1["status"] == "result" else []
arm("RB17", "first poll surfaces the qualifying issue and its Browser Sol comment, and nothing else", "2_ITEMS",
    "%d_ITEMS" % len(items1), " ".join("%s:%s" % (i["kind"], i["item"]["id"]) for i in items1) or r1["output"][:120])
arm("RB17", "FirstMate-authored comments (FM->SOL marker, receipt envelope) are never surfaced", "FILTERED",
    "FILTERED" if not any(i["item"]["id"] in (2, 3) for i in items1) else "SURFACED", "ids=%s" % [i["item"]["id"] for i in items1])
arm("RB17", "an unrelated open issue with no protocol header is not a commission", "IGNORED",
    "IGNORED" if not any(i["issue_number"] == 10 for i in items1) else "SURFACED", "")
for it in items1:
    got, measured = v("inbound_item", it)
    arm("RB17", "surfaced item %s:%s validates as $defs.inbound_item" % (it["kind"], it["item"]["id"]), "PASS", got, measured)
r2, _ = invoke("sha256:" + "1" * 64, sb, fenv)
n2 = len(json.loads(r2["output"])["items"]) if r2["status"] == "result" else 0
arm("RB17", "a pre-capture retry with the SAME request id re-emits the same items (idempotent replay)", "2_ITEMS", "%d_ITEMS" % n2, r2["status"])
r3, _ = invoke("sha256:" + "2" * 64, sb, fenv)
arm("RB17", "a later poll with a NEW request id re-announces nothing", "no-result", r3["status"], "")
r4, err4 = invoke("sha256:" + "3" * 64, os.path.join(sandbox, "no-such-home"), fenv)
arm("RB17", "an unresolvable control chain is could-not-observe OUT LOUD, never a silent no-result", "CNO_LOUD", verdict_of(r4), (err4 or "").strip().split("\n")[0][:120])
# gh IS on /usr/bin; simulate failure with a gh that exits 1
broken = os.path.join(sandbox, "brokengh"); os.makedirs(broken, exist_ok=True)
open(os.path.join(broken, "gh"), "w").write("#!/bin/sh\necho 'HTTP 503' >&2; exit 1\n"); os.chmod(os.path.join(broken, "gh"), 0o755)
benv = {"PATH": broken + os.pathsep + os.environ["PATH"]}
r5, err5 = invoke("sha256:" + "4" * 64, sb, benv)
arm("RB17", "a forge failure is could-not-observe OUT LOUD", "CNO_LOUD", verdict_of(r5), (err5 or "").strip().split("\n")[0][:120])
r6, _ = invoke("sha256:" + "5" * 64, sb, benv)
arm("RB17", "a persisting forge failure is NOT re-announced within the hour (bounded, not spammy)", "no-result", r6["status"], "")
r6b, _ = invoke("sha256:" + "7" * 64, sb, fenv)
arm("RB17", "a recovered forge clears the standing could-not-observe episode quietly (nothing new to say)", "no-result", r6b["status"], "")
denied_home = os.path.join(sandbox, "home-denied"); os.makedirs(os.path.join(denied_home, "config"), exist_ok=True); os.makedirs(os.path.join(denied_home, "state"), exist_ok=True)
open(os.path.join(denied_home, "config", "control-plane.yaml"), "w").write(base_yaml.replace("sbracewell64/firstmate-cleanroom-control", "sbracewell64/firstmate-sol-control"))
_sh.copy(os.path.join(sb, "state", "cleanroom-control-v2.listener.json"), os.path.join(denied_home, "state"))
r7, err7 = invoke("sha256:" + "6" * 64, denied_home, fenv)
arm("RB17", "a configuration repointed at the retired venue is could-not-observe (generation moved / isolation denied); nothing polled", "CNO_LOUD", verdict_of(r7), (err7 or "").strip().split("\n")[0][:120])
grep3 = subprocess.run(["grep", "-n", "firstmate-cleanroom-control\\|firstmate-sol-control\\|fm-sol-control/v2", adapter], capture_output=True, text=True)
arm("RB17", "the adapter names no repository and no protocol of its own", "NONE",
    "NONE" if not grep3.stdout.strip() else "FOUND", grep3.stdout.strip()[:120])

# ---------------------------------------------------------------------------
with open(sys.argv[1], "w", encoding="utf-8") as fh:
    fh.write("red\tarm\texpected\tobserved\tverdict\tmeasured\n")
    for r in ROWS:
        fh.write("\t".join(str(x).replace("\t", " ").replace("\n", " ") for x in r) + "\n")

good = sum(1 for r in ROWS if r[4] == "observed-good")
bad = sum(1 for r in ROWS if r[4] == "observed-bad")
cno = sum(1 for r in ROWS if r[4] == "could-not-observe")
print()
print("=" * 118)
print("ARMS %d   observed-good %d   observed-bad %d   could-not-observe %d" % (len(ROWS), good, bad, cno))
print("=" * 118)
sys.exit(0 if bad == 0 and cno == 0 else 1)

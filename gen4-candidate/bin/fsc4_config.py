#!/usr/bin/env python3
"""THE single deterministic resolver for the clean-room control-plane configuration.

SCHEMA GENERATION 4. Identical in law to generations 1 and 2 (the canonical owner
and its generation digest are UNCHANGED by generation 3); this copy differs only
in the schema of record it validates the owner against. Generation 2 note:
(a) The canonical owner now lives in the operational home (FM_HOME), which moved
to a real ext4 filesystem, so the owner path is DERIVED from FM_HOME rather than
hard-coded to one operator's drvfs mount. (b) The listener's identity and its
record and check-script paths are now owned by the configuration (captain
directive 6), so the listener record is generated from here instead of being a
second authored copy beside it.

Captain addendum, 2026-09-02. Law 1: one canonical owner. Law 2: one resolver,
consumed by the emitter, the watcher, the ruling consumer, the receipt writer,
diagnostics and the bootstrap checks alike. Law 7: a diagnostic may PROJECT what
this returns; it may never reimplement the normalization or the digest.

The config's field names are owned by the one authored schema file
(schema/fm-sol-control-v2.schema.json, $defs.control_config), so no field name
lives in two places. This module owns only the normalization and the digest.

Usage:
  fsc4_config.py show          canonical normalized projection (the digested bytes)
  fsc4_config.py digest        control_config_generation.digest
  fsc4_config.py generation    the full control_config_generation object as JSON
  fsc4_config.py get <path>    one resolved value, e.g. control.repository
  fsc4_config.py isolate <repository> <protocol>
                               venue-isolation predicate; exit 0 admit, 3 deny
  fsc4_config.py listener      the resolved listener binding as JSON (absolute paths)
  fsc4_config.py home          the resolved operational home
"""
import hashlib
import json
import os
import sys

import yaml
from jsonschema import Draft202012Validator

CONTROL_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMA_PATH = os.path.join(CONTROL_ROOT, "schema", "fm-sol-control-v2.schema.json")
DEFAULT_FM_HOME = "/home/OPERATOR/.firstmate-cleanroom"
FM_HOME = os.environ.get("FM_HOME") or DEFAULT_FM_HOME
OWNER_PATH = os.environ.get(
    "FSC2_CONTROL_CONFIG",
    os.path.join(FM_HOME, "config", "control-plane.yaml"),
)


class ConfigRefusal(Exception):
    """Fail closed. Unknown, malformed, missing or ambiguous config never resolves."""


def _read(path):
    try:
        with open(path, "rb") as fh:
            return fh.read()
    except OSError as exc:
        raise ConfigRefusal("CONFIG_UNREADABLE: %s: %s" % (path, exc))


def schema_bytes():
    return _read(SCHEMA_PATH)


def schema_digest():
    return hashlib.sha256(schema_bytes()).hexdigest()


def resolver_digest():
    """sha256 of this resolver's own bytes.

    An emitter and a watcher that resolve through different resolver bytes are
    then detectable rather than assumed identical (addendum watched red 4).
    """
    return hashlib.sha256(_read(os.path.abspath(__file__))).hexdigest()


def _config_schema():
    doc = json.loads(schema_bytes())
    sub = dict(doc["$defs"]["control_config"])
    sub["$defs"] = doc["$defs"]
    return sub


def load(path=None):
    """Parse, validate against the one authored schema file, and return the object."""
    path = path or OWNER_PATH
    raw = _read(path)
    try:
        obj = yaml.safe_load(raw.decode("utf-8"))
    except Exception as exc:
        raise ConfigRefusal("CONFIG_MALFORMED: %s: %s" % (path, exc))
    if not isinstance(obj, dict):
        raise ConfigRefusal("CONFIG_MALFORMED: %s: top level is not a mapping" % path)
    errs = sorted(
        Draft202012Validator(_config_schema()).iter_errors(obj),
        key=lambda e: list(e.absolute_path),
    )
    if errs:
        lines = ["CONFIG_INVALID: %s" % path]
        for e in errs:
            lines.append("  at %s: %s" % ("/".join(str(p) for p in e.absolute_path) or "<root>", e.message))
        raise ConfigRefusal("\n".join(lines))
    return obj


def normalize(obj):
    """Deterministic canonical bytes. Sorted keys, no insignificant whitespace,
    UTF-8, LF, one trailing newline. Comments, key order and formatting in the
    YAML owner cannot move the digest; a value change always does."""
    return (
        json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
        + b"\n"
    )


def generation(path=None, resolved_at=None):
    """The control_config_generation object every envelope carries."""
    path = path or OWNER_PATH
    obj = load(path)
    norm = normalize(obj)
    import datetime

    return {
        "owner_path": path,
        "digest": hashlib.sha256(norm).hexdigest(),
        "resolver_digest": resolver_digest(),
        "resolved_at": resolved_at
        or datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }, obj, norm


def get(dotted, path=None):
    obj = load(path)
    cur = obj
    for part in dotted.split("."):
        if not isinstance(cur, dict) or part not in cur:
            raise ConfigRefusal("CONFIG_KEY_ABSENT: %s" % dotted)
        cur = cur[part]
    return cur


def isolation_admits(repository, protocol, path=None):
    """Law 6, by EXACT STRING EQUALITY only.

    Returns (admit: bool, reason: str). Never substring, never prefix, never
    'contains': 'fm-sol-control/v2' contains 'fm-sol-control', so a word-overlap
    consumer would consume retired-venue v1 traffic.
    """
    obj = load(path)
    iso = obj["venue_isolation"]
    if iso["match_rule"] != "exact_string_equality":
        raise ConfigRefusal("CONFIG_INVALID: unsupported match_rule")
    if repository in iso["denied_repositories"]:
        return False, "DENIED_REPOSITORY: %s" % repository
    if protocol in iso["denied_protocols"]:
        return False, "DENIED_PROTOCOL: %s" % protocol
    if repository != obj["control"]["repository"]:
        return False, "NOT_THE_RESOLVED_VENUE: %s != %s" % (repository, obj["control"]["repository"])
    if protocol != obj["control"]["protocol"]:
        return False, "NOT_THE_RESOLVED_PROTOCOL: %s != %s" % (protocol, obj["control"]["protocol"])
    return True, "ADMITTED"


def listener_binding(path=None, home=None):
    """The listener's identity and absolute paths, resolved from the ONE owner.

    Captain directive 6: the listener record carries no identity or path of its
    own. Both configured paths are FM_HOME-relative and are REFUSED if absolute,
    so one configuration resolves correctly in any home and cannot be pinned to a
    single operator's filesystem. Fail closed: an absolute or escaping path
    raises rather than being normalised into something plausible.
    """
    obj = load(path)
    home = home or FM_HOME
    lis = obj["listener"]
    out = {"id": lis["id"], "home": home}
    for key in ("record_path", "check_script_path"):
        rel = lis[key]
        if os.path.isabs(rel):
            raise ConfigRefusal("CONFIG_INVALID: listener.%s must be FM_HOME-relative: %s" % (key, rel))
        absolute = os.path.normpath(os.path.join(home, rel))
        if not absolute.startswith(os.path.normpath(home) + os.sep):
            raise ConfigRefusal("CONFIG_INVALID: listener.%s escapes the home: %s" % (key, rel))
        out[key] = rel
        out[key.replace("_path", "_abspath")] = absolute
    return out


def main(argv):
    if len(argv) < 2:
        sys.stderr.write(__doc__)
        return 2
    cmd = argv[1]
    try:
        if cmd == "show":
            _, _, norm = generation()
            sys.stdout.buffer.write(norm)
            return 0
        if cmd == "digest":
            gen, _, _ = generation()
            print(gen["digest"])
            return 0
        if cmd == "generation":
            gen, _, _ = generation()
            print(json.dumps(gen, indent=2, sort_keys=True))
            return 0
        if cmd == "get":
            print(get(argv[2]))
            return 0
        if cmd == "listener":
            print(json.dumps(listener_binding(), indent=2, sort_keys=True))
            return 0
        if cmd == "home":
            print(FM_HOME)
            return 0
        if cmd == "isolate":
            admit, reason = isolation_admits(argv[2], argv[3])
            print(("ADMIT " if admit else "DENY  ") + reason)
            return 0 if admit else 3
    except ConfigRefusal as exc:
        sys.stderr.write("REFUSED: %s\n" % exc)
        return 4
    except IndexError:
        sys.stderr.write("REFUSED: missing argument\n")
        return 2
    sys.stderr.write("REFUSED: unknown command %r\n" % cmd)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))

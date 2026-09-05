#!/usr/bin/env python3
"""fm-sol-control/v2 toolkit, SCHEMA GENERATION 4: producer validation, consumer
validation, identity derivation, and the human reply-contract projection.

Every field name and every enum value comes from the one authored schema file.
Nothing below spells a protocol field name of its own: the identity inputs are
read from $defs.id_derivation and the reply contract is produced by WALKING the
schema. Fail closed: unknown, malformed, stale or ambiguous never validates.

Usage:
  fsc4.py digest                              sha256 of the schema of record
  fsc4.py validate <kind> <file.json>         validate an envelope; exit 0 pass, 5 refuse
  fsc4.py derive <id-name> <file.json>        compute a derived identity
  fsc4.py reply-contract <kind>               render the generated reply contract
  fsc4.py renderer-digest                     sha256 of this renderer
  fsc4.py evidence-digest <file.json>         sha256 over the canonical evidence quadruples (see $defs.evidence_digest_derivation)
"""
import hashlib
import json
import os
import sys

from jsonschema import Draft202012Validator

import fsc4_config

SCHEMA_PATH = fsc4_config.SCHEMA_PATH


class Refusal(Exception):
    pass


def schema():
    return json.loads(fsc4_config.schema_bytes())


def schema_digest():
    return fsc4_config.schema_digest()


def renderer_digest():
    with open(os.path.abspath(__file__), "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def _sub(kind):
    doc = schema()
    if kind not in doc["$defs"]:
        raise Refusal("UNKNOWN_KIND: %s" % kind)
    sub = dict(doc["$defs"][kind])
    sub["$defs"] = doc["$defs"]
    return sub


def validate(kind, obj):
    """Return a sorted list of refusal strings. Empty means it validated.

    Every failing predicate is reported, not only the first, and each refusal
    names the offending field.
    """
    errs = sorted(
        Draft202012Validator(_sub(kind)).iter_errors(obj),
        key=lambda e: (list(e.absolute_path), e.message),
    )
    out = []
    for e in errs:
        where = "/".join(str(p) for p in e.absolute_path) or "<root>"
        out.append("at %s: %s" % (where, e.message))
    return out


def _resolve(obj, dotted):
    cur = obj
    for part in dotted.split("."):
        if isinstance(cur, dict):
            cur = cur.get(part)
        else:
            return ""
        if cur is None:
            return ""
    return cur


def derive(name, obj):
    spec = schema()["$defs"]["id_derivation"]["const"]
    if name not in spec:
        raise Refusal("UNKNOWN_IDENTITY: %s" % name)
    rule = spec[name]
    parts = []
    for key in rule["inputs"]:
        val = _resolve(obj, key)
        parts.append("" if val is None else str(val))
    material = ("\n".join(parts) + "\n").encode("utf-8")
    return rule["prefix"] + hashlib.sha256(material).hexdigest()[:32]


def evidence_digest(refs):
    """sha256 over the canonical sorted 'kind\\tlocator\\tsha256\\tdigest_basis' rows.

    GENERATION 2 binds digest_basis into the aggregate. In generation 1 the row
    was a triple, so a reference could silently change from a real byte digest to
    a digest of its own locator string without moving evidence_digest, and the
    ruler would have been shown a different kind of binding under an unchanged
    aggregate (observer finding 4.5). An absent basis resolves to the empty
    string, which is a distinct row from either declared value rather than a
    match with one of them.
    """
    lines = sorted(
        "%s\t%s\t%s\t%s" % (r["kind"], r["locator"], r["sha256"], r.get("digest_basis", ""))
        for r in refs
    )
    return hashlib.sha256(("\n".join(lines) + "\n").encode("utf-8")).hexdigest()


# --- the generated reply contract -------------------------------------------
# Produced by WALKING the schema. No field name and no enum value below is typed
# here; every one is read out of the schema of record.

def _describe(node, defs, depth=0):
    if "$ref" in node:
        target = node["$ref"].split("/")[-1]
        resolved = defs.get(target, {})
        merged = {k: v for k, v in resolved.items()}
        for k, v in node.items():
            if k != "$ref":
                merged[k] = v
        return _describe(merged, defs, depth)
    if "const" in node:
        return "exactly %s" % json.dumps(node["const"])
    if "enum" in node:
        return "one of: " + " | ".join(json.dumps(v) for v in node["enum"])
    if "anyOf" in node and any("pattern" in b or "$ref" in b for b in node["anyOf"]):
        inner = [_describe(b, defs, depth + 1) for b in node["anyOf"]]
        return "either " + "  OR  ".join(inner)
    t = node.get("type")
    if isinstance(t, list):
        t = "|".join(t)
    if t == "object":
        req = node.get("required", [])
        props = node.get("properties", {})
        req_s = ", ".join(
            "%s=%s" % (k, _describe(props[k], defs, depth + 1)) for k in req if k in props
        )
        opt = [k for k in props if k not in req]
        s = "object{%s}" % req_s
        if opt:
            s += " optional:" + ",".join(sorted(opt))
        return s
    if t == "array":
        return "array of " + _describe(node.get("items", {}), defs, depth + 1)
    if "pattern" in node:
        return "string matching %s" % node["pattern"]
    if t == "integer":
        bits = []
        if "minimum" in node:
            bits.append(">=%s" % node["minimum"])
        if "maximum" in node:
            bits.append("<=%s" % node["maximum"])
        return "integer" + (" " + " ".join(bits) if bits else "")
    return t or "value"


def _deref(node, defs):
    if "$ref" not in node:
        return node
    target = defs.get(node["$ref"].split("/")[-1], {})
    merged = dict(target)
    for k, v in node.items():
        if k != "$ref":
            merged[k] = v
    return merged


def _render_field(name, node, defs, indent, depth=0):
    """One required field, expanded one level so a nested object does not
    arrive as a single unreadable line."""
    resolved = _deref(node, defs)
    if resolved.get("type") == "object" and resolved.get("properties") and depth < 2:
        req = resolved.get("required", [])
        props = resolved["properties"]
        opt = sorted(k for k in props if k not in req)
        out = ["%s- %s: object with %d required field%s"
               % (indent, name, len(req), "" if len(req) == 1 else "s")]
        for k in req:
            out.extend(_render_field(k, props[k], defs, indent + "    ", depth + 1))
        if opt:
            out.append("%s    - optional: %s" % (indent, ", ".join(opt)))
        return out
    if resolved.get("type") == "array" and depth < 2:
        item = _deref(resolved.get("items", {}), defs)
        if item.get("type") == "object" and item.get("properties"):
            out = ["%s- %s: array of object" % (indent, name)]
            for k in item.get("required", []):
                out.extend(_render_field(k, item["properties"][k], defs, indent + "    ", depth + 1))
            opt = sorted(k for k in item["properties"] if k not in item.get("required", []))
            if opt:
                out.append("%s    - optional: %s" % (indent, ", ".join(opt)))
            return out
    return ["%s- %s: %s" % (indent, name, _describe(node, defs))]


def reply_contract(kind):
    doc = schema()
    defs = doc["$defs"]
    node = defs[kind]
    props = node.get("properties", {})
    req = node.get("required", [])
    lines = []
    lines.append("Required fields (%d):" % len(req))
    for k in req:
        lines.extend(_render_field(k, props[k], defs, "  "))
    opt = [k for k in props if k not in req]
    # Both arms of every conditional are rendered. A contract that prints only
    # what becomes REQUIRED, and stays silent about what becomes UNSPELLABLE,
    # leaves the counterparty to discover the forbidden half by being refused.
    conds = []
    for clause in node.get("allOf", []):
        cond = clause.get("if", {}).get("properties", {})
        then = clause.get("then", {})
        then_req = then.get("required", [])
        forbidden = sorted(k for k, v in then.get("properties", {}).items() if v is False)
        for field, spec in cond.items():
            if "const" in spec:
                head = "when %s == %s:" % (field, json.dumps(spec["const"]))
            elif isinstance(spec.get("not"), dict) and "const" in spec["not"]:
                head = "when %s != %s:" % (field, json.dumps(spec["not"]["const"]))
            else:
                continue
            if then_req:
                conds.append((head, "%s is REQUIRED" % ", ".join(then_req)))
            if forbidden:
                conds.append((head, "%s MUST BE ABSENT (present is refused)" % ", ".join(forbidden)))
    if conds:
        lines.append("")
        lines.append("Conditional companion fields:")
        width = max(len(h) for h, _ in conds)
        for head, rule in conds:
            lines.append("  - %-*s  %s" % (width, head, rule))
    if opt:
        lines.append("")
        lines.append("Optional fields (%d): %s" % (len(opt), ", ".join(sorted(opt))))
    lines.append("")
    lines.append("Rules the consumer enforces mechanically (a violation is refused, never repaired):")
    lines.append("  - additionalProperties is false on every object: an unknown or misspelled field")
    lines.append("    name is REFUSED_MALFORMED and the refusal names the field.")
    for k in req:
        c = props[k].get("$comment") or defs.get(
            props[k].get("$ref", "").split("/")[-1], {}
        ).get("$comment")
        if c:
            wrapped = []
            cur = "  - %s: " % k
            for word in c.split():
                if len(cur) + len(word) + 1 > 96:
                    wrapped.append(cur)
                    cur = "      " + word
                else:
                    cur += ("" if cur.endswith(": ") else " ") + word
            wrapped.append(cur)
            lines.extend(wrapped)
    return "\n".join(lines) + "\n"


def main(argv):
    if len(argv) < 2:
        sys.stderr.write(__doc__)
        return 2
    cmd = argv[1]
    try:
        if cmd == "digest":
            print(schema_digest())
            return 0
        if cmd == "renderer-digest":
            print(renderer_digest())
            return 0
        if cmd == "reply-contract":
            sys.stdout.write(reply_contract(argv[2]))
            return 0
        if cmd == "validate":
            obj = json.load(open(argv[3], encoding="utf-8"))
            errs = validate(argv[2], obj)
            if errs:
                print("REFUSED_MALFORMED (%d)" % len(errs))
                for e in errs:
                    print("  " + e)
                return 5
            print("VALID %s" % argv[2])
            return 0
        if cmd == "derive":
            obj = json.load(open(argv[3], encoding="utf-8"))
            print(derive(argv[2], obj))
            return 0
        if cmd == "evidence-digest":
            obj = json.load(open(argv[2], encoding="utf-8"))
            refs = obj["evidence_refs"] if isinstance(obj, dict) else obj
            print(evidence_digest(refs))
            return 0
    except Refusal as exc:
        sys.stderr.write("REFUSED: %s\n" % exc)
        return 5
    except (OSError, ValueError, KeyError, IndexError) as exc:
        sys.stderr.write("REFUSED: %s: %s\n" % (type(exc).__name__, exc))
        return 5
    sys.stderr.write("REFUSED: unknown command %r\n" % cmd)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))

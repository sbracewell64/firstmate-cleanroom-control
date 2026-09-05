#!/usr/bin/env python3
"""Operator-path redaction and residue scanning for PUBLIC evidence. Generation 3 (unchanged from generation 2 apart from the module it resolves through).

Generation 1 redacted `/home/<user>` exactly and completely, and missed every
other spelling of the same fact: `/mnt/c/Users/<operator>/AppData/Roaming/npm/codex`
survived onto the public venue in three files whose declared class states that
operator-local filesystem paths are replaced (observer finding 4.4). A redaction
contract that covers only the form the operator happened to think of is not a
contract, so the classes are enumerated in the schema of record
($defs.redaction_class) and READ FROM IT here rather than typed twice.

The scanner is separate from the redactor on purpose: `scan` is the one that
produces `publication_redaction.residue_count`, and the schema pins that value to
a structural 0, so a request whose published evidence still carries an
operator-local user-profile path cannot be expressed at all.

Usage:
  fsc4-redact.py classes                       the classes this tool implements
  fsc4-redact.py scan <path> [<path> ...]      report residue; exit 0 clean, 6 residue found
  fsc4-redact.py redact <in> <out>             write the redacted copy
  fsc4-redact.py policy-digest                 the digest of this redaction policy
"""
import hashlib
import json
import os
import re
import sys

import fsc4_config

REPLACEMENT = "OPERATOR"

# One row per $defs.redaction_class value. The class name is the join key; the
# pattern is owned here because a regex is not a protocol field name.
PATTERNS = {
    # /home/OPERATOR/... and bare /home/OPERATOR
    "posix_home": re.compile(r"(?<![A-Za-z0-9_.-])/home/([A-Za-z0-9._-]+)"),
    # WSL's view of the Windows profile: /mnt/c/Users/OPERATOR/AppData/...
    "wsl_windows_userprofile": re.compile(r"(?<![A-Za-z0-9_.-])(/mnt/[a-z]/Users)/([A-Za-z0-9._ -]+)"),
    # Native Windows: C:\Users\OPERATOR\... and C:/Users/OPERATOR/...
    "windows_userprofile": re.compile(r"([A-Za-z]:[\\/]{1,2}Users[\\/]{1,2})([A-Za-z0-9._ -]+)"),
    # macOS: /Users/OPERATOR/...
    "macos_home": re.compile(r"(?<![A-Za-z0-9_.:\\-])/Users/([A-Za-z0-9._-]+)"),
    # UNC into a WSL distro: \\wsl$\Ubuntu\home\OPERATOR\...
    "unc_wsl_home": re.compile(r"(\\\\wsl[$.][^\\]*\\[^\\]+\\home\\)([A-Za-z0-9._-]+)"),
}

# Names that are not an operator identity even though they sit in that position.
BENIGN = {"OPERATOR", "runner", "root", "Public", "Default", "All Users", "ubuntu"}


def schema_classes():
    """The authoritative class list, read out of the schema of record."""
    doc = json.loads(fsc4_config.schema_bytes())
    return doc["$defs"]["redaction_class"]["enum"]


def _assert_total():
    """The implemented set and the declared set must be the same set.

    A class declared in the schema with no pattern here would silently pass
    everything; a pattern here with no declared class would redact something the
    contract never promised. Either is a refusal, not a warning.
    """
    declared, implemented = set(schema_classes()), set(PATTERNS)
    if declared != implemented:
        raise SystemExit(
            "REFUSED: redaction classes drifted. declared-only=%s implemented-only=%s"
            % (sorted(declared - implemented), sorted(implemented - declared))
        )


def hits(text):
    """Every operator-path occurrence, as (class, matched_text, identity)."""
    out = []
    for name, pat in PATTERNS.items():
        for m in pat.finditer(text):
            identity = m.group(m.lastindex)
            if identity in BENIGN:
                continue
            out.append((name, m.group(0), identity))
    return out


def redact(text):
    def sub(pat):
        def repl(m):
            groups = m.groups()
            ident = groups[-1]
            if ident in BENIGN:
                return m.group(0)
            prefix = m.group(0)[: len(m.group(0)) - len(ident)]
            return prefix + REPLACEMENT
        return lambda t: pat.sub(repl, t)
    for pat in PATTERNS.values():
        text = sub(pat)(text)
    return text


def policy_digest():
    """Digest over the policy this tool actually implements: the class names and
    their patterns, canonically ordered. Changing a pattern moves the digest, so
    a request cannot cite a policy generation it was not compiled under."""
    material = "\n".join("%s\t%s" % (k, PATTERNS[k].pattern) for k in sorted(PATTERNS))
    material += "\nreplacement\t%s\nbenign\t%s\n" % (REPLACEMENT, ",".join(sorted(BENIGN)))
    return hashlib.sha256(material.encode("utf-8")).hexdigest()


def main(argv):
    if len(argv) < 2:
        sys.stderr.write(__doc__)
        return 2
    cmd = argv[1]
    _assert_total()
    if cmd == "classes":
        for c in schema_classes():
            print("%-26s %s" % (c, PATTERNS[c].pattern))
        return 0
    if cmd == "policy-digest":
        print(policy_digest())
        return 0
    if cmd == "scan":
        total = 0
        for path in argv[2:]:
            targets = []
            if os.path.isdir(path):
                for root, _d, files in os.walk(path):
                    targets.extend(os.path.join(root, f) for f in sorted(files))
            else:
                targets.append(path)
            for t in targets:
                try:
                    text = open(t, "r", encoding="utf-8", errors="replace").read()
                except OSError as exc:
                    # Unreadable is COULD-NOT-OBSERVE, and it is reported as a
                    # scan failure rather than counted as clean.
                    print("CNO  %s: %s" % (t, exc))
                    return 7
                for name, matched, ident in hits(text):
                    print("HIT  %-26s %-40s %s" % (name, matched, t))
                    total += 1
        print("residue_count %d" % total)
        return 6 if total else 0
    if cmd == "redact":
        text = open(argv[2], "r", encoding="utf-8").read()
        out = redact(text)
        open(argv[3], "w", encoding="utf-8").write(out)
        left = hits(out)
        print("redacted %s -> %s ; residue %d" % (argv[2], argv[3], len(left)))
        return 6 if left else 0
    sys.stderr.write("REFUSED: unknown command %r\n" % cmd)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))

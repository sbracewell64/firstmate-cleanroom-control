#!/usr/bin/env python3
"""SUPERSEDED shim. The canonical owner of the live outbound record is
bin/fsc4-live-record.py (register / verify / reconcile / retire); this file only
forwards the one form that can be identity-verified, so older call sites keep
working through the canonical path.

  fsc4-register-live.py <request.json> <creation-response.json>
      -> fsc4-live-record.py register <request.json> <creation-response.json>

The former `--issue <n> --url <url>` form is REFUSED: it typed an issue number
and url by hand, which is exactly the guessed-id path the emit contract forbids.
For an issue that exists without a live record, run
  fsc4-live-record.py reconcile <issue-number>
which derives the record from the verified venue envelope.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

def main():
    args = sys.argv[1:]
    if "--issue" in args or "--url" in args or len(args) != 2:
        sys.stderr.write(__doc__)
        sys.stderr.write("REFUSED: hand-typed identities are not accepted; use `fsc4-live-record.py reconcile <n>`\n")
        return 2
    return subprocess.call([sys.executable, os.path.join(HERE, "fsc4-live-record.py"), "register", args[0], args[1]])

if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env bash
# Enforce the generation 3 write-once schema freeze by digest, the only
# enforcement this filesystem supports.
#
# Every artifact named in FREEZE.json is re-hashed. The control-config
# generation snapshot is DELIBERATELY NOT CHECKED: that value is designed to
# move, and treating a legitimate configuration change as schema drift would
# credit this verifier with a property it does not have.
#
# Exit 0 = unchanged since freeze; 6 = DRIFTED; 4 = could not observe.
set -u
GEN3="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ROOT="$(cd "$GEN3/../../.." && pwd)"
F="$GEN3/schema/FREEZE.json"
[ -r "$F" ] || { echo "CNO: freeze record unreadable: $F" >&2; exit 4; }
command -v jq >/dev/null 2>&1 || { echo "CNO: jq unavailable" >&2; exit 4; }
names=$(jq -r '.artifacts | keys[]' "$F") || { echo "CNO: freeze record unparsable" >&2; exit 4; }
[ -n "$names" ] || { echo "CNO: freeze record names no artifacts" >&2; exit 4; }
rc=0 n=0
while IFS= read -r key; do
  [ -n "$key" ] || continue
  n=$((n + 1))
  want=$(jq -r --arg k "$key" '.artifacts[$k].sha256' "$F")
  rel=$(jq -r --arg k "$key" '.artifacts[$k].path' "$F")
  path="$ROOT/$rel"
  if [ ! -r "$path" ]; then
    printf 'CNO   %-24s unreadable: %s\n' "$key" "$path"; rc=4; continue
  fi
  have=$(sha256sum "$path" | cut -d' ' -f1)
  if [ "$want" = "$have" ]; then
    printf 'ok    %-24s %s\n' "$key" "$have"
  else
    printf 'DRIFT %-24s frozen=%s now=%s\n' "$key" "$want" "$have"; rc=6
  fi
done <<< "$names"
printf 'checked %d artifact(s); exit %d\n' "$n" "$rc"
exit "$rc"

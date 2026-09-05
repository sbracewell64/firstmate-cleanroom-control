#!/bin/sh
case "$*" in
  *issues?state=open*) printf '%s' '[{"number":9,"id":900,"html_url":"u9","title":"t","state":"open","user":{"login":"op"},"created_at":"2026-09-02T00:00:00Z","updated_at":"2026-09-02T00:00:01Z","comments":3,"body":"protocol_family: fm-sol-control/v2\nkind: browser-sol-follow-on-commission\nfrom: browser-sol\nto: firstmate\n\nbody"},{"number":10,"id":1000,"html_url":"u10","title":"unrelated","state":"open","user":{"login":"op"},"created_at":"2026-09-02T00:00:00Z","updated_at":"2026-09-02T00:00:01Z","comments":0,"body":"just a note"}]' ;;
  *issues/9/comments*) printf '%s' '[{"id":1,"html_url":"c1","user":{"login":"op"},"created_at":"2026-09-02T00:00:02Z","body":"Ruling text from Browser Sol"},{"id":2,"html_url":"c2","user":{"login":"op"},"created_at":"2026-09-02T00:00:03Z","body":"[FM->SOL] report-back from firstmate"},{"id":3,"html_url":"c3","user":{"login":"op"},"created_at":"2026-09-02T00:00:04Z","body":"receipt\n```json\n{\"kind\":\"receipt\",\"schema\":\"fm-sol-control/v2\"}\n```"}]' ;;
  *) exit 1 ;;
esac

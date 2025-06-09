#!/usr/bin/env python
import sys, json, requests, concurrent.futures
from pathlib import Path
import importlib.util

# Carrega lista de sites do linkdb
linkdb = json.loads(Path("core/linkdb.json").read_text())
targets = linkdb["social_media"]

def check_site(site, url_tpl, username):
    url = url_tpl.format(username=username)
    try:
        r = requests.get(url, timeout=5, allow_redirects=True)
        return site, r.status_code < 400
    except Exception:
        return site, False

def main(username):
    results={}
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as ex:
        futs=[ex.submit(check_site,s,u,username) for s,u in targets.items()]
        for f in concurrent.futures.as_completed(futs):
            site, ok=f.result()
            results[site]=ok
    print(json.dumps({"username":username,"hits":results}, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    if len(sys.argv)<2:
        print("Uso: python username_hunt.py <username>")
        sys.exit(1)
    main(sys.argv[1])

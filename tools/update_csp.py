#!/usr/bin/env python3
"""Recompute the Content-Security-Policy in index.html.

Run this after every edit to index.html:   python3 tools/update_csp.py
It hashes each inline <script> and rewrites the CSP meta tag. If the hashes
are stale, browsers refuse to run the script and the page is blank.
"""
import base64, hashlib, re, sys, pathlib

path = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else pathlib.Path(__file__).resolve().parent.parent / 'index.html')
html = path.read_text(encoding='utf-8')
scripts = re.findall(r'<script>(.*?)</script>', html, flags=re.S)
hashes = ["'sha256-%s'" % base64.b64encode(hashlib.sha256(s.encode('utf-8')).digest()).decode() for s in scripts]
csp = ("default-src 'none'; script-src " + ' '.join(hashes) + "; style-src 'unsafe-inline'; font-src 'none'; "
       "img-src 'self' data: blob:; connect-src https://api.open-meteo.com https://geocoding-api.open-meteo.com; "
       "worker-src 'self'; manifest-src 'self'; form-action 'none'; base-uri 'none'; object-src 'none'")
new, n = re.subn(r'(<meta http-equiv="Content-Security-Policy" content=")[^"]*(")', lambda m: m.group(1) + csp + m.group(2), html)
if n != 1:
    sys.exit('CSP meta tag not found')
path.write_text(new, encoding='utf-8')
print(f'Updated CSP with {len(hashes)} script hash(es).')

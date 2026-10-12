#!/usr/bin/env python3
"""Local preview of _posts and _drafts with inline HTML/JS widgets working.

    python3 _tools/preview.py            # serves http://127.0.0.1:4000
    python3 _tools/preview.py 4010       # other port

Renders markdown on every request (edit -> refresh). Resolves {% post_url slug %} to /slug.html,
strips other liquid tags, passes raw HTML through (details/summary, inline SVG, <script>).
Not Jekyll: styling is approximate; footnotes/kramdown attribute lists are not supported.
Lives in an underscore dir so Jekyll never publishes it.
"""
import html, os, re, sys, urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
from markdown_it import MarkdownIt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POSTS, DRAFTS = os.path.join(ROOT, '_posts'), os.path.join(ROOT, '_drafts')
md = MarkdownIt('commonmark', {'html': True, 'linkify': False}).enable('table').enable('strikethrough')

CSS = """body{max-width:800px;margin:40px auto;padding:0 20px;font:17px/1.6 -apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;color:#111;background:#fff}
h1,h2,h3{line-height:1.25}h2{margin-top:2em;border-bottom:1px solid #eee;padding-bottom:.2em}
table{border-collapse:collapse;margin:1em 0;font-size:15px;display:block;overflow-x:auto}th,td{border:1px solid #ddd;padding:5px 10px}th{background:#f6f6f6}
code{background:#f4f4f4;padding:1px 4px;border-radius:3px;font-size:.9em}pre code{display:block;padding:10px;overflow-x:auto}
blockquote{border-left:4px solid #ddd;margin:1em 0;padding:.2em 1em;color:#444}details{margin:1em 0}summary{cursor:pointer}
.meta{color:#666;font-size:14px}.banner{background:#fff3cd;border:1px solid #ffe08a;padding:6px 12px;font-size:13px;border-radius:6px}
@media (prefers-color-scheme: dark){body{background:#111;color:#e8e8e8}th{background:#222}th,td{border-color:#444}code{background:#222}h2{border-color:#333}.banner{background:#3a2f00;border-color:#665500}}"""

def slug_of(fname):  # 2026-08-31-foo.md -> foo
    return re.sub(r'^\d{4}-\d{2}-\d{2}-', '', fname[:-3])

def index_files():
    files = {}
    for kind, d in (('post', POSTS), ('draft', DRAFTS)):
        if os.path.isdir(d):
            for f in sorted(os.listdir(d), reverse=True):
                if f.endswith('.md'):
                    files.setdefault(slug_of(f), (kind, os.path.join(d, f)))
    return files

def render(path, kind):
    src = open(path, encoding='utf-8').read()
    fm = {}
    m = re.match(r'^---\n(.*?)\n---\n', src, re.S)
    if m:
        for line in m.group(1).splitlines():
            if ':' in line:
                k, v = line.split(':', 1); fm[k.strip()] = v.strip().strip('"')
        src = src[m.end():]
    src = re.sub(r'\{%\s*post_url\s+([^\s%]+)\s*%\}', lambda mm: '/' + slug_of(mm.group(1) + '.md') + '.html', src)
    src = re.sub(r'\{%-?.*?-?%\}', '', src)
    body = md.render(src)
    title = html.escape(fm.get('title', slug_of(os.path.basename(path))))
    return f"""<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title><style>{CSS}</style></head><body>
<div class="banner">local preview ({kind}) — approximate styling, widgets live. <a href="/">all posts</a></div>
<h1>{title}</h1><p class="meta">{html.escape(fm.get('date',''))} · {html.escape(os.path.relpath(path, ROOT))}</p>
{body}</body></html>"""

class H(BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def send(self, code, body, ctype='text/html; charset=utf-8'):
        b = body.encode('utf-8'); self.send_response(code)
        self.send_header('Content-Type', ctype); self.send_header('Content-Length', str(len(b)))
        self.send_header('Cache-Control', 'no-store'); self.end_headers(); self.wfile.write(b)
    def do_GET(self):
        p = urllib.parse.unquote(self.path.split('?')[0])
        files = index_files()
        if p in ('/', '/index.html'):
            items = ''.join(f'<li><a href="/{s}.html">{html.escape(s)}</a> <span class="meta">({k}, {os.path.basename(f)})</span></li>'
                            for s, (k, f) in sorted(files.items(), key=lambda kv: os.path.basename(kv[1][1]), reverse=True))
            return self.send(200, f'<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body><h1>Local preview</h1><ul>{items}</ul></body></html>')
        if p.startswith('/assets/'):
            fp = os.path.normpath(os.path.join(ROOT, p.lstrip('/')))
            if fp.startswith(ROOT) and os.path.isfile(fp):
                data = open(fp, 'rb').read(); self.send_response(200); self.send_header('Content-Length', str(len(data))); self.end_headers(); return self.wfile.write(data)
        s = p.strip('/')[:-5] if p.endswith('.html') else p.strip('/')
        if s in files:
            kind, fp = files[s]
            try: return self.send(200, render(fp, kind))
            except Exception as e: return self.send(500, f'<pre>{html.escape(repr(e))}</pre>')
        self.send(404, '<p>not found. <a href="/">index</a></p>')

if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 4000
    print(f'preview at http://127.0.0.1:{port}/  (drafts + posts; ctrl-c to stop)', flush=True)
    HTTPServer(('127.0.0.1', port), H).serve_forever()

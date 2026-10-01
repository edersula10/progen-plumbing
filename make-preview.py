#!/usr/bin/env python3
"""Bundle the whole site into ONE self-contained HTML file for previewing (hash-routed)."""
import re, base64, os
os.chdir(os.path.dirname(os.path.abspath(__file__)))

css = open("css/style.css").read()
js = open("js/main.js").read()
from PIL import Image
import io
def data_uri(path, size):
    im = Image.open(path); im.thumbnail((size,size), Image.LANCZOS)
    buf = io.BytesIO(); fmt = "PNG" if path.endswith(".png") else "JPEG"
    im.save(buf, fmt, **({"quality":82} if fmt=="JPEG" else {"optimize":True}))
    return f"data:image/{fmt.lower()};base64," + base64.b64encode(buf.getvalue()).decode()
ASSETS = {"assets/logo-badge.jpg": data_uri("assets/logo-badge.jpg",720)}
for f in os.listdir("assets"):
    if f.startswith("logo-") and f.endswith(".png"): ASSETS["assets/"+f] = data_uri("assets/"+f, 112)
    elif f.startswith("work-") or f.startswith("job-"): ASSETS["assets/"+f] = data_uri("assets/"+f, 900)

PAGES = [("home","index.html"),("services","services.html"),("service-areas","service-areas.html"),
         ("about","about.html"),("contact","contact.html"),("work","work.html")] + \
        [("services/"+f[:-5], "services/"+f) for f in sorted(os.listdir("services"))]

def rewrite(html_, depth):
    root = "../" if depth else ""
    def fix(m):
        attr, url = m.group(1), m.group(2)
        u = url
        if u.startswith(root): u = u[len(root):]
        if u.startswith(("http","mailto:","tel:","data:")): return f'{attr}="{u}"'
        if u.startswith("assets/"):
            base = u.split(" ")[0]
            if base in ASSETS: return f'{attr}="{ASSETS[base]}"'
        if u.endswith(".html"):
            key = u[:-5]
            if key == "index": key = "home"
            return f'{attr}="#/{key}"'
        return f'{attr}="{u}"'
    return re.sub(r'(href|src|srcset)="([^"]+)"', fix, html_)

home = open("index.html").read()
header = re.search(r'<header class="site-header">.*?</header>', home, re.S).group(0)
footer = re.search(r'<footer class="site-footer">.*?</footer>', home, re.S).group(0)
callbar = re.search(r'<div class="call-bar">.*?</div>', home, re.S).group(0)
header = rewrite(header, 0); footer = rewrite(footer, 0); callbar = rewrite(callbar, 0)

mains = []
for key, path in PAGES:
    h = open(path).read()
    main = re.search(r'<main id="main">(.*?)</main>', h, re.S).group(1)
    main = rewrite(main, path.startswith("services/"))
    # map iframes can't load inside the preview sandbox
    main = main.replace('<script async src="https://www.instagram.com/embed.js"></script>', '')
    main = re.sub(r'<iframe[^>]*></iframe>', '<div style="display:grid;place-items:center;height:100%;color:var(--muted);font-size:15px;padding:24px;text-align:center">Google Map embed (2300 St Clair Ave W) — loads on the live site</div>', main)
    # in-page section ids would fight the hash router
    main = re.sub(r' id="(services|about|why|process|faq|book|testimonials|reviews|areas|work)"', '', main)
    title = re.search(r'<title>(.*?)</title>', h).group(1)
    mains.append(f'<div class="page" data-page="{key}" data-title="{title}" hidden>{main}</div>')

router = """
(function(){
  var pages = document.querySelectorAll('.page');
  function show(){
    var key = (location.hash.replace(/^#\\/?/, '') || 'home');
    var found = false;
    pages.forEach(function(p){ var on = p.dataset.page === key; p.hidden = !on; if (on){ found = true; document.title = p.dataset.title; } });
    if (!found) { pages[0].hidden = false; }
    document.querySelectorAll('.nav a').forEach(function(a){
      var h = a.getAttribute('href') || '';
      var cur = h === '#/' + key || (key.indexOf('services/') === 0 && h === '#/services');
      if (cur) a.setAttribute('aria-current','page'); else a.removeAttribute('aria-current');
    });
    window.scrollTo(0,0);
    document.body.classList.remove('nav-open');
    document.querySelectorAll('.reveal').forEach(function(el){ el.classList.add('is-visible'); });
    document.querySelectorAll('[data-count]').forEach(function(el){ el.textContent = el.getAttribute('data-count'); });
  }
  window.addEventListener('hashchange', show);
  show();
})();
"""

out = f"""<title>Pro Gen Plumbing</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@600;700&family=DM+Sans:wght@400;500;600&display=swap" rel="stylesheet">
<style>
{css}
/* preview-only */
.preview-bar {{ position: fixed; left: 0; right: 0; bottom: 0; z-index: 200; background: #4DA3FF; color: #070A0E; font: 600 13px/1.3 var(--font-heading); text-align: center; padding: 8px 12px; }}
.preview-bar a {{ color: inherit; text-decoration: underline; }}
@media (max-width: 767px) {{ .preview-bar {{ display: none; }} }}
.page[hidden] {{ display: none; }}
</style>
{header}
<main id="main">
{''.join(mains)}
</main>
{footer}
{callbar}
<div class="preview-bar">Preview build — all 12 pages in one file. Instagram reels play on the live site (shown here as link cards). Form is not connected yet.</div>
<script>
{js}
{router}
</script>
"""
open("../progen-preview.html","w").write(out)
print("wrote ../progen-preview.html", len(out)//1024, "KB")

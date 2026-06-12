#!/usr/bin/env python3
"""
figma_storyboard.py — turn a Figma design file into a storyboard 화면설계서 site.

Each Figma FRAME (named e.g. "SB-01 ...") becomes one page:
  LEFT  = the screen mockup, exported as an image, cropped to exclude the right
          DescriptionPanel and the bottom PolicyBox.
  RIGHT = the DescriptionPanel's TEXT nodes, rendered as REAL HTML text
          (selectable/searchable — never a screenshot).
  BOTTOM= the PolicyBox's TEXT nodes, also real HTML text.
  Crisp HTML callout circles (.sb-cue.pin) are overlaid on the screen at the
  exact Figma marker positions, so numbers stay sharp at any zoom and map 1:1
  to the numbered items on the right.
A thumbnail board (index.html) links every page. A shared top-right control
(글자 크기 + 콜아웃 진하기 slider) persists in localStorage, so a change on ONE
page applies to ALL pages (and live across open tabs via the `storage` event).

Auth: FIGMA_TOKEN + FIGMA_FILE_KEY from the environment or a `.env` beside this
skill (KEY=VALUE lines). The token needs read access to the file.

Usage:
  export FIGMA_TOKEN=figd_...   FIGMA_FILE_KEY=xxxxxxxx
  python3 figma_storyboard.py --out ./design-specs --pages 9:2,60:2 --title "My CMS"
  python3 figma_storyboard.py --out ./design-specs            # all canvas pages

Gotcha learned the hard way: the Figma image API render-times-out on batches of
large frames ("Render timeout, try requesting fewer or smaller images"); export
ONE frame id per request (this script does, with a few worker threads).
"""
import argparse, json, os, re, html, time, shutil, urllib.request, urllib.parse
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(HERE)
CIRCLED = '①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮⑯⑰⑱⑲⑳㉑㉒㉓㉔㉕㉖㉗㉘㉙㉚'
CMAP = {c: str(i + 1) for i, c in enumerate(CIRCLED)}
MARK_RE = re.compile(r'^\d{1,2}(?:-\d{1,2})?$|^\*$')
DATE_RE = re.compile(r'^\d{4}[./-]\d{2}[./-]\d{2}\.?$')
META_TEXTS = {'Date', 'Ver', 'Version', 'Writer', 'Author', 'Description', 'Policy', 'No', '1.0', '-'}
MARKER_PATH_RE = re.compile(r'(description_|/point|/marker|/callout|/pin|/annotation)', re.I)


def load_env():
    for p in (os.path.join(SKILL, '.env'), os.path.join(HERE, '.env')):
        if os.path.exists(p):
            for line in open(p):
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    os.environ.setdefault(k.strip(), v.strip())


def api(path, token):
    req = urllib.request.Request('https://api.figma.com' + path, headers={'X-Figma-Token': token})
    with urllib.request.urlopen(req, timeout=180) as r:
        return json.load(r)


# ---------- Figma structure / text / markers ----------
def clean_text(value):
    return (value or '').replace('\u2028', '\n').replace('\u00a0', ' ').strip()


def node_fill_rgb(node):
    fills = node.get('fills') or []
    if not fills:
        return None
    color = fills[0].get('color') or {}
    return tuple(round(color.get(k, 0), 3) for k in ('r', 'g', 'b'))


def cue_visual_style(value):
    length = len((value or '').strip())
    if length <= 1:
        return ''
    size = 26 if length == 2 else min(38, 24 + length * 3)
    font = 11 if length == 2 else 10
    return '--sb-cue-size:%dpx;--sb-cue-font:%dpx' % (size, font)


def cue_style_attr(value):
    style = cue_visual_style(value)
    return ' style="%s"' % style if style else ''


def collect_text(node, out):
    if node.get('type') == 'TEXT' and (node.get('characters', '') or '').strip():
        b = node.get('absoluteBoundingBox') or {}
        out.append([round(b.get('y', 0)), round(b.get('x', 0)), clean_text(node['characters'])])
    for c in node.get('children', []):
        collect_text(c, out)


def texts_sorted(node):
    o = []
    collect_text(node, o)
    o.sort()
    return [t[2] for t in o]


def text_entries(node, fx, fy):
    out = []

    def walk(n, path=''):
        if n.get('type') == 'TEXT' and (n.get('characters', '') or '').strip():
            b = n.get('absoluteBoundingBox') or {}
            st = n.get('style') or {}
            out.append({
                'x': b.get('x', 0) - fx,
                'y': b.get('y', 0) - fy,
                'w': b.get('width', 0),
                'h': b.get('height', 0),
                'name': n.get('name', '') or '',
                'text': clean_text(n.get('characters', '')),
                'path': path,
                'fill': node_fill_rgb(n),
                'font_weight': st.get('fontWeight', 0),
            })
        for c in n.get('children', []):
            walk(c, '%s/%s' % (path, n.get('name', '') or ''))

    walk(node)
    out.sort(key=lambda t: (t['y'], t['x']))
    return out


def is_meta_text(t):
    text = (t.get('text') or '').strip()
    return text in META_TEXTS or DATE_RE.match(text) is not None


def text_column_lines(frame, fx, fy, doc_x):
    lines = []
    for t in text_entries(frame, fx, fy):
        text = (t.get('text') or '').strip()
        if t['x'] < doc_x + 40 or t['y'] < 140 or not text:
            continue
        if is_meta_text(t) or MARK_RE.fullmatch(text):
            continue
        lines.append(text)
    return lines


def find_named(node, kw):
    stack = list(node.get('children', []))
    while stack:
        c = stack.pop(0)
        if c.get('type') == 'FRAME' and kw in (c.get('name', '') or '').lower():
            return c
        stack.extend(c.get('children', []))
    return None


def find_desc(frame, fx, fy, fw):
    p = find_named(frame, 'description')
    if p:
        b = p.get('absoluteBoundingBox') or {}
        return p, b.get('x', 0) - fx, 'node'
    cands = []
    for c in frame.get('children', []):
        if c.get('type') == 'FRAME':
            b = c.get('absoluteBoundingBox') or {}
            cands.append((c, b.get('x', 0) - fx, b.get('width', 0), b.get('height', 0)))
    right = [t for t in cands if t[1] > fw * 0.45 and 480 <= t[2] <= 900]
    if right:
        right.sort(key=lambda t: (-t[3], -t[1]))
        return right[0][0], right[0][1], 'node'
    labels = [t['x'] for t in text_entries(frame, fx, fy)
              if t['text'] == 'Description' or t['name'] == 'Description']
    if labels:
        return None, max(0, min(labels) - 28), 'text-column'
    right_texts = [t['x'] for t in text_entries(frame, fx, fy)
                   if t['x'] > fw * 0.62 and t['y'] > 140 and not is_meta_text(t)]
    if len(right_texts) >= 2:
        return None, max(0, min(right_texts) - 28), 'text-column'
    if any(k in (frame.get('name', '') or '').lower() for k in ('description', 'policy')):
        return frame, None, 'node'      # standalone text panel = whole frame
    return None, None, None


def find_policy(frame, fx, fy, fw, fh, desc_relx):
    p = find_named(frame, 'policy')
    if p:
        b = p.get('absoluteBoundingBox') or {}
        return p, b.get('y', 0) - fy
    best = None
    for c in frame.get('children', []):
        if c.get('type') != 'FRAME':
            continue
        nm = (c.get('name', '') or '').lower()
        if any(k in nm for k in ('header', 'lnb', 'gnb', 'description', 'modal')):
            continue
        b = c.get('absoluteBoundingBox') or {}
        relx, relY, w, h = b.get('x', 0) - fx, b.get('y', 0) - fy, b.get('width', 0), b.get('height', 0)
        if desc_relx and relx >= desc_relx - 10:
            continue
        if relY > fh * 0.5 and w > fw * 0.4 and h > 80 and (best is None or relY < best[1]):
            best = (c, relY)
    return best if best else (None, None)


def is_screen_marker_text(t):
    path = t.get('path') or ''
    fill = t.get('fill')
    weight = t.get('font_weight') or 0
    if not MARKER_PATH_RE.search(path):
        return False
    is_white_marker = fill is not None and min(fill) > 0.9 and weight >= 700
    is_red_marker = fill is not None and fill[0] > 0.7 and fill[1] < 0.25 and fill[2] < 0.35
    return is_white_marker or is_red_marker


def in_screen_region(cx, cy, lim_x, lim_y):
    return not ((lim_x and cx >= lim_x - 4) or (lim_y and cy >= lim_y - 4))


def markers(frame, fx, fy, lim_x, lim_y):
    ell, dig = [], []

    def walk(n):
        if n.get('type') == 'ELLIPSE':
            b = n.get('absoluteBoundingBox') or {}
            if 20 <= b.get('width', 0) <= 36 and 20 <= b.get('height', 0) <= 36:
                ell.append((b['x'] - fx + b['width'] / 2, b['y'] - fy + b['height'] / 2))
        if n.get('type') == 'TEXT':
            t = (n.get('characters', '') or '').strip()
            if MARK_RE.fullmatch(t):
                b = n.get('absoluteBoundingBox') or {}
                dig.append((b['x'] - fx + b['width'] / 2, b['y'] - fy + b['height'] / 2, t))
        for c in n.get('children', []):
            walk(c)
    walk(frame)
    out, seen = [], set()
    for dx, dy, t in dig:
        near = min(((abs(ex - dx) + abs(ey - dy), ex, ey) for ex, ey in ell), default=(999, 0, 0))
        if near[0] > 8:
            continue
        cx, cy = near[1], near[2]
        if not in_screen_region(cx, cy, lim_x, lim_y):
            continue
        k = (t, round(cx / 6), round(cy / 6))
        if k in seen:
            continue
        seen.add(k)
        out.append({'n': t, 'cx': round(cx), 'cy': round(cy)})
    for t in text_entries(frame, fx, fy):
        value = (t['text'] or '').strip()
        if not MARK_RE.fullmatch(value) or not is_screen_marker_text(t):
            continue
        cx, cy = t['x'] + t['w'] / 2, t['y'] + t['h'] / 2
        if not in_screen_region(cx, cy, lim_x, lim_y):
            continue
        k = (value, round(cx / 6), round(cy / 6))
        if k in seen:
            continue
        seen.add(k)
        out.append({'n': value, 'cx': round(cx), 'cy': round(cy)})
    out.sort(key=lambda m: (m['cy'], m['cx']))
    return out


# ---------- text -> HTML ----------
def classify(s):
    s = s.rstrip(); t = s.strip()
    if not t: return ('blank', '')
    if MARK_RE.fullmatch(t): return ('num', t)
    if t[0] in CIRCLED: return ('head', t)
    if t[0] in '•◦▪·*‣' or re.match(r'^-\s', t): return ('bullet', t.lstrip('•◦▪·*‣- ').strip())
    return ('text', s)


def render_desc(lines):
    flat = []
    for ln in lines:
        flat.extend(ln.split('\n'))
    intro, sections, cur, i = [], [], None, 0
    while i < len(flat):
        kind, val = classify(flat[i])
        if kind == 'blank':
            i += 1; continue
        if kind == 'num':
            j = i + 1
            while j < len(flat) and not flat[j].strip():
                j += 1
            cur = {'num': val, 'title': flat[j].strip() if j < len(flat) else '', 'items': []}
            sections.append(cur); i = j
        elif kind == 'head':
            cur = {'num': CMAP.get(val[0], ''), 'title': val[1:].strip(), 'items': []}
            sections.append(cur)
        else:
            (cur['items'] if cur else intro).append((kind, val))
        i += 1
    out = ['<div class="sb-desc">']
    if intro:
        out.append('<div class="sb-desc-intro">')
        out += ['<p%s>%s</p>' % (' class="b"' if k == 'bullet' else '', html.escape(v)) for k, v in intro]
        out.append('</div>')
    for s in sections:
        badge = '<span class="sb-num"%s>%s</span>' % (
            cue_style_attr(s['num']), html.escape(s['num'])) if s['num'] else ''
        out.append('<section class="sb-desc-item"><h4>%s<span>%s</span></h4>' % (badge, html.escape(s['title'])))
        bl = [v for k, v in s['items'] if k == 'bullet']
        if bl:
            out.append('<ul>' + ''.join('<li>%s</li>' % html.escape(b) for b in bl) + '</ul>')
        out += ['<p class="sub">%s</p>' % html.escape(v) for k, v in s['items'] if k == 'text']
        out.append('</section>')
    out.append('</div>')
    return '\n'.join(out)


# ---------- policy / rules -> structured, collapsible HTML ----------
# Figma 의 정책 박스는 보통 다중 컬럼이라 텍스트가 평탄화되어 들어온다. 무번호 짧은 줄은
# 섹션 헤더, 불릿은 항목으로 보고 카드(헤더+리스트)로 묶는다. 항목 앞부분의 "라벨: 값"/
# "라벨   값"은 라벨을 굵게, SB-/N-SEC-/M- 참조·[버튼]·API/메서드는 칩/코드로 강조한다.
P_CHIP = re.compile(r'(\[[^\]\n]{1,28}\])')
P_REF = re.compile(r'\b(SB-[0-9A-Za-z_]+|N-[A-Z]+-[0-9A-Za-z_]+|M-[0-9][0-9A-Za-z_-]*)\b')
P_CODE = re.compile(r'((?:GET|POST|PUT|DELETE|PATCH)\b|/(?:api|master)/[^\s,]+)')


def _pol_inline(s):
    s = html.escape(s)                       # escape first → brackets/slashes stay literal
    s = P_CODE.sub(r'<code>\1</code>', s)
    s = P_REF.sub(r'<span class="pref">\1</span>', s)
    s = P_CHIP.sub(r'<span class="pchip">\1</span>', s)
    return s


def _pol_item(s):
    s = s.strip()
    # 1) 콜론 라벨(가장 신뢰): "라벨: 값" — 라벨에 대괄호 없을 때만
    m = re.match(r'^([^:：\[\]\n]{1,16})[:：]\s+(.+)$', s)
    # 2) 정렬 공백: 첫 컬럼이 1~2단어(짧은 코드/구)일 때만 라벨로
    if not m:
        m = re.match(r'^(\S+(?:\s\S+)?)\s{2,}(.+)$', s)
        if m and len(m.group(1)) > 16:
            m = None
    if m:
        rest = re.sub(r'\s{2,}', ' ', m.group(2))            # 정렬용 다중 공백 정규화
        return '<span class="k">%s</span> %s' % (html.escape(m.group(1)), _pol_inline(rest))
    return _pol_inline(re.sub(r'\s{2,}', ' ', s))


def policy_html(pairs):
    """pairs: list of ('sec'|'item', text). First policy-ish 'sec' = title; empty headers merge."""
    title, secs = None, []
    for k, v in pairs:
        v = (v or '').strip()
        if not v:
            continue
        if k == 'sec':
            if title is None and not secs and re.search(r'정책|policy|rules', v, re.I):
                title = v
            elif secs and not secs[-1]['items'] and secs[-1]['h']:   # 연속 헤더 → 빈 카드 병합
                secs[-1]['h'] += ' · ' + v
            else:
                secs.append({'h': v, 'items': []})
        else:
            if not secs:
                secs.append({'h': '', 'items': []})
            secs[-1]['items'].append(v)
    out = ['<div class="sb-pol">']
    if title:
        out.append('<p class="sb-pol-title">%s</p>' % html.escape(title))
    out.append('<div class="sb-pol-cols">')
    for s in secs:
        out.append('<section class="sb-pol-card">')
        if s['h']:
            out.append('<h5>%s</h5>' % _pol_inline(s['h']))
        if s['items']:
            out.append('<ul>%s</ul>' % ''.join('<li>%s</li>' % _pol_item(it) for it in s['items']))
        out.append('</section>')
    out.append('</div></div>')
    return '\n'.join(out)


def render_policy(lines):
    flat = []
    for ln in lines:
        flat.extend(ln.split('\n'))
    pairs = []
    for ln in flat:
        kind, val = classify(ln)
        if kind == 'blank':
            continue
        if kind == 'bullet':
            pairs.append(('item', val))
        elif kind == 'head':                  # ①②③ heading
            pairs.append(('sec', val[1:].strip()))
        else:                                 # 'num' or plain 'text' = section header
            pairs.append(('sec', val if kind == 'num' else val.strip()))
    return policy_html(pairs)


# 정책 섹션 마크업(접이식, 디폴트 숨김). body() 와 산출물 후처리가 같은 형태를 쓰도록 공유.
def policy_section(policy_lines):
    return ('<section class="sb-pane sb-policy"><details class="sb-pol-det">'
            '<summary class="sb-cap">정책 · 규칙 '
            '<span class="sb-cap-en">policy / rules · Figma 텍스트 그대로</span>'
            '<span class="sb-pol-state" aria-hidden="true"></span></summary>%s</details></section>'
            ) % render_policy(policy_lines)


CTL = open(os.path.join(SKILL, 'templates', 'settings-control.html')).read()
SETTINGS_JS = open(os.path.join(SKILL, 'templates', 'settings-control.js')).read()
ZOOM_JS = open(os.path.join(SKILL, 'templates', 'zoom-control.js')).read()
LIGHTBOX_HTML = open(os.path.join(SKILL, 'templates', 'lightbox.html')).read()
LIGHTBOX_JS = open(os.path.join(SKILL, 'templates', 'lightbox.js')).read()
TOC_JS = ('<script>(function(){var c=document.querySelector(".sb-toc a.current"),'
          't=document.querySelector(".sb-toc");if(c&&t)t.scrollTop=c.offsetTop-t.clientHeight/2+40;})();</script>')


def code_of(name):
    m = re.match(r'^(SB-\S+)', name)
    return m.group(1) if m else '—'


def state_of(name):
    n = name.lower()
    if 'placeholder' in n: return '준비중'
    if '모달' in name or 'modal' in n or '팝업' in name: return '모달'
    if '알럿' in name or 'toast' in n or '안내' in name: return '알럿/안내'
    return '화면'


def short_title(name):
    t = re.sub(r'^SB-\S+\s*', '', name).replace('(Master) ', '').strip()
    return t or name


def build_toc(man, cur):
    out, g = [], None
    for m in man:
        if g != m['page_code']:
            g = m['page_code']
            out.append('<div class="g">%s</div>' % html.escape(m['page_label']))
        cls = 't current' if m['html'] == cur else 't'
        out.append('<a class="%s" href="./%s" title="%s"><span class="c">%s</span><span class="n">%s</span></a>'
                   % (cls, html.escape(m['html']), html.escape(m['frame_name']),
                      html.escape(code_of(m['frame_name'])), html.escape(short_title(m['frame_name']))))
    return '\n'.join(out)


def main():
    load_env()
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    ap.add_argument('--pages', default='', help='comma canvas-page node ids; default = all')
    ap.add_argument('--title', default='화면설계서')
    ap.add_argument('--scale', type=int, default=3)
    ap.add_argument('--max-dim', type=int, default=9800)
    args = ap.parse_args()
    token, key = os.environ['FIGMA_TOKEN'], os.environ['FIGMA_FILE_KEY']
    out = os.path.abspath(args.out)
    for d in (out, os.path.join(out, 'assets'), os.path.join(out, 'thumbs')):
        os.makedirs(d, exist_ok=True)
    shutil.copyfile(os.path.join(SKILL, 'templates', 'storyboard.css'), os.path.join(out, 'storyboard.css'))

    doc = api('/v1/files/%s?depth=2' % key, token)['document']
    file_name = api('/v1/files/%s?depth=1' % key, token).get('name', '')
    want = [x for x in args.pages.split(',') if x] or [p['id'] for p in doc['children']]
    pages = {p['id']: p for p in doc['children']}
    man, seq = [], 0
    for pid in want:
        p = pages.get(pid)
        if not p:
            continue
        code = re.sub(r'[^0-9a-z]+', '_', (p['name'].split('.')[0] or pid).lower()).strip('_') or pid.replace(':', '_')
        frames = sorted([c for c in p.get('children', []) if c.get('type') == 'FRAME'],
                        key=lambda c: (0 if (c.get('name') or '').startswith('SB') else 1, c.get('name', '')))
        for i, c in enumerate(frames, 1):
            seq += 1
            man.append({'seq': seq, 'page_id': pid, 'page_code': code, 'page_label': p['name'],
                        'frame_id': c['id'], 'frame_name': c.get('name', ''),
                        'html': '%s-%02d.html' % (code, i), 'png': 'assets/%s.png' % c['id'].replace(':', '-'),
                        'thumb': 'thumbs/%s.png' % c['id'].replace(':', '-')})
    print('frames:', len(man))

    # deep fetch -> per-frame data
    ids = [m['frame_id'] for m in man]
    nodes = {}
    for i in range(0, len(ids), 6):
        nodes.update(api('/v1/files/%s/nodes?%s' % (key, urllib.parse.urlencode(
            {'ids': ','.join(ids[i:i + 6]), 'depth': 14})), token).get('nodes', {}))
    for m in man:
        fr = nodes[m['frame_id']]['document']
        fb = fr.get('absoluteBoundingBox') or {}
        fx, fy, fw, fh = fb.get('x', 0), fb.get('y', 0), fb.get('width', 0), fb.get('height', 0)
        dn, drelx, desc_mode = find_desc(fr, fx, fy, fw)
        pn, prelY = find_policy(fr, fx, fy, fw, fh, drelx)
        desc_lines = text_column_lines(fr, fx, fy, drelx) if desc_mode == 'text-column' else (texts_sorted(dn) if dn else [])
        m.update(fw=fw, fh=fh, crop_x=drelx or fw, crop_y=prelY or fh,
                 desc=desc_lines, desc_self=bool(dn) and dn.get('id') == m['frame_id'],
                 policy=texts_sorted(pn) if pn else [], markers=markers(fr, fx, fy, drelx or fw, prelY or fh))

    # export (one id per request) + crop + thumb
    from PIL import Image

    def url_for(m):
        s = args.scale if max(m['fw'], m['fh']) * args.scale <= args.max_dim else 2
        for sc in (s, 2):
            q = urllib.parse.urlencode({'ids': m['frame_id'], 'format': 'png', 'scale': sc})
            try:
                u = (api('/v1/images/%s?%s' % (key, q), token).get('images') or {}).get(m['frame_id'])
                if u:
                    return m['frame_id'], u
            except Exception:
                time.sleep(1)
        return m['frame_id'], None
    urls = {}
    with ThreadPoolExecutor(max_workers=4) as ex:
        for fid, u in ex.map(url_for, man):
            urls[fid] = u
    for m in man:
        u = urls.get(m['frame_id'])
        if not u:
            print('  MISS', m['frame_id']); continue
        full = os.path.join(out, m['png'])
        urllib.request.urlretrieve(u, full)
        im = Image.open(full)
        W, H = im.size
        sc = W / m['fw'] if m['fw'] else args.scale
        cx, cy = min(round(m['crop_x'] * sc), W), min(round(m['crop_y'] * sc), H)
        if m['desc'] and not m['desc_self'] and cx > 80 and cy > 80:
            im.crop((0, 0, cx, cy)).save(os.path.join(out, m['png'].replace('.png', '-screen.png')))
        th = im.copy(); th.thumbnail((760, 760)); th.save(os.path.join(out, m['thumb']))

    render(out, man, key, file_name, args.title)
    print('done ->', out)


def render(out, man, key, file_name, title):
    N = len(man)

    def deeplink(fid):
        return 'https://www.figma.com/design/%s/?node-id=%s' % (key, fid.replace(':', '-'))

    def overlays(m):
        sp = []
        for mk in m['markers']:
            l, t = mk['cx'] / m['crop_x'] * 100, mk['cy'] / m['crop_y'] * 100
            if 0 <= l <= 100 and 0 <= t <= 100:
                style = 'left:%.2f%%;top:%.2f%%;%s' % (l, t, cue_visual_style(mk['n']))
                sp.append('<span class="sb-cue pin" data-cue="%s" style="%s">%s</span>' % (
                    html.escape(mk['n']), html.escape(style), html.escape(mk['n'])))
        return ''.join(sp)

    def body(m):
        sf = m['png'].replace('.png', '-screen.png')
        if m['desc'] and m['desc_self']:
            return '<div class="sb-doc-narrow"><section class="sb-pane"><div class="sb-cap">설명</div>%s</section></div>' % render_desc(m['desc'])
        if m['desc'] and os.path.exists(os.path.join(out, sf)):
            sp = ('<section class="sb-pane sb-screenpane"><div class="sb-cap">화면 <span class="sb-cap-en">번호 = 설명표 항목</span>'
                  '<span class="sb-zoomctl"><button data-z="out" aria-label="축소">−</button><span class="zlvl">100%%</span>'
                  '<button data-z="in" aria-label="확대">+</button><button class="wide" data-z="fit">맞춤</button>'
                  '<a href="#" data-lb="./%s" data-title="%s" title="원본 보기 (팝업 뷰어)">원본 보기</a></span></div>'
                  '<div class="sb-screen"><div class="sb-zoom" title="스크롤·버튼 확대 / 드래그 이동 / 더블클릭 원래대로">'
                  '<div class="sb-stage"><img class="sb-screen-img" src="./%s" alt="" draggable="false"/>%s</div></div></div></section>'
                  ) % (html.escape(m['png']), html.escape(m['frame_name']), html.escape(sf), overlays(m))
            dp = '<section class="sb-pane"><div class="sb-cap">설명 <span class="sb-cap-en">description · Figma 텍스트</span></div>%s</section>' % render_desc(m['desc'])
            # 정책 · 규칙을 화면/설명 split 앞(위)에 둔다 — 가장 중요한 계약이라 먼저 보이게.
            # 구조화 카드 + 접이식(디폴트 숨김).
            pol = policy_section(m['policy']) if m['policy'] else ''
            return '%s<div class="sb-split">%s%s</div>' % (pol, sp, dp)
        return '<figure class="sb-pane" style="padding:0"><a href="./%s" target="_blank"><img src="./%s" style="width:100%%;display:block" alt=""/></a></figure>' % (html.escape(m['png']), html.escape(m['png']))

    page = open(os.path.join(SKILL, 'templates', 'storyboard-figma-page.html')).read()
    for i, m in enumerate(man):
        prev = '<a href="./%s">‹</a>' % man[i - 1]['html'] if i else '<span class="pg">‹</span>'
        nxt = '<a href="./%s">›</a>' % man[i + 1]['html'] if i < N - 1 else '<span class="pg">›</span>'
        open(os.path.join(out, m['html']), 'w').write(page.format(
            code=html.escape(code_of(m['frame_name'])), title=html.escape(m['frame_name']),
            page_label=html.escape(m['page_label']), state=state_of(m['frame_name']),
            deeplink=deeplink(m['frame_id']), body=body(m), seq=m['seq'], N=N,
            file_name=html.escape(file_name), fid=m['frame_id'], prev=prev, next=nxt,
            toc=build_toc(man, m['html']), ctl=CTL, lightbox=LIGHTBOX_HTML,
            settings_js=SETTINGS_JS + ZOOM_JS + TOC_JS + LIGHTBOX_JS))

    groups, cur = [], None
    for m in man:
        if cur is None or cur['code'] != m['page_code']:
            cur = {'code': m['page_code'], 'label': m['page_label'], 'items': []}
            groups.append(cur)
        cur['items'].append(m)
    cards = lambda items: '\n'.join(
        '<article class="sb-card"><a class="thumb" href="./%s"><img src="./%s" loading="lazy" alt=""/></a>'
        '<div class="body"><div class="top"><span class="st">%s</span><span class="code">%s</span></div>'
        '<h3>%s</h3><p>%s</p><a class="open" href="./%s">스토리보드 열기 →</a></div></article>' % (
            html.escape(m['html']), html.escape(m['thumb']), state_of(m['frame_name']),
            html.escape(code_of(m['frame_name'])), html.escape(m['frame_name']),
            html.escape(m['page_label']), html.escape(m['html'])) for m in items)
    secs = '\n'.join('<div class="group-label"><h2>%s</h2><span>%d개 화면</span></div><main class="sb-grid">%s</main>'
                     % (html.escape(g['label']), len(g['items']), cards(g['items'])) for g in groups)
    bctl = CTL.replace('"sb-ctl"', '"sb-ctl board-ctl"').replace('"sb-fontctl"', '"sb-fontctl board-fontctl"').replace('"sb-opctl"', '"sb-opctl board-opctl"')
    idx = open(os.path.join(SKILL, 'templates', 'board-figma-index.html')).read()
    open(os.path.join(out, 'index.html'), 'w').write(idx.format(
        title=html.escape(title), N=N, file_name=html.escape(file_name), KEY=key,
        sections=secs, bctl=bctl, settings_js=SETTINGS_JS))


if __name__ == '__main__':
    main()

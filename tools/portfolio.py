#!/usr/bin/env python3
"""
포트폴리오 텍스트 왕복 도구

  python3 tools/portfolio.py export    index.html → content.md  (텍스트만 뽑기)
  python3 tools/portfolio.py apply     content.md → index.html  (고친 텍스트 되돌리기)
  python3 tools/portfolio.py check     되돌린 결과가 md와 같은지 검사

content.md 는 [키] 줄과 그 아래 본문으로 이루어진다.
키 줄은 절대 고치지 말고, 아래 본문만 고친다.
서식은 **굵게**, *강조색*, `작게` 세 가지만 쓴다. 줄바꿈은 그대로 <br> 가 된다.
"""
import sys, re, pathlib
from bs4 import BeautifulSoup, NavigableString

ROOT = pathlib.Path(__file__).resolve().parent.parent
HTML = ROOT / "index.html"
MD   = ROOT / "content.md"

# 텍스트를 담는 요소들 — 이 안의 글만 고칠 수 있다
TARGETS = "h1,h2,h3,h4,p,li,td,th,caption,span.nm,span.rl,div.lab,div.val"
SKIP_CLASS = {"toc", "lk", "id", "namecard", "chart", "out-line", "inline-figs"}
SKIP_PARENT_CLASS = {"toc", "lk"}


def to_md(el):
    """요소 안쪽 HTML → 편집용 마크다운"""
    out = []
    for node in el.children:
        if isinstance(node, NavigableString):
            out.append(str(node))
        elif node.name == "br":
            out.append("\n")
        elif node.name in ("b", "strong"):
            out.append("**" + to_md(node).strip() + "**")
        elif node.name == "em":
            out.append("*" + to_md(node).strip() + "*")
        elif node.name in ("i", "span"):
            out.append("`" + to_md(node).strip() + "`")
        elif node.name == "a":
            out.append(to_md(node))
        else:
            out.append(to_md(node))
    s = "".join(out)
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r" *\n *", "\n", s)
    return s.strip()


def from_md(s):
    """편집용 마크다운 → 요소 안쪽 HTML"""
    s = (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s, flags=re.S)
    s = re.sub(r"(?<!\*)\*([^*\n]+?)\*(?!\*)", r"<em>\1</em>", s)
    s = re.sub(r"`(.+?)`", r"<i>\1</i>", s, flags=re.S)
    return s.replace("\n", "<br>")


def collect(soup):
    """(키, 요소) 목록. 키는 섹션과 순번으로 만들어 안정적이다."""
    items, seen = [], set()
    for sec in soup.select("header.mast, section, div.closing"):
        sid = sec.get("id") or ("mast" if "mast" in (sec.get("class") or []) else "closing")
        n = 0
        for el in sec.select(TARGETS):
            if id(el) in seen:
                continue
            cls = set(el.get("class") or [])
            if cls & SKIP_CLASS:
                continue
            if any(set(p.get("class") or []) & SKIP_PARENT_CLASS for p in el.parents if p.name):
                continue
            # 자식으로 다른 대상 요소를 품은 컨테이너는 건너뛴다 (중복 방지)
            if el.select(TARGETS):
                continue
            txt = to_md(el)
            if not txt:
                continue
            for d in el.descendants:
                seen.add(id(d))
            seen.add(id(el))
            n += 1
            items.append((f"{sid}.{n:02d}", el))
    return items


def cmd_export():
    soup = BeautifulSoup(HTML.read_text(encoding="utf-8"), "html.parser")
    items = collect(soup)
    lines = [
        "# 포트폴리오 텍스트",
        "",
        "> `[키]` 줄은 고치지 마세요. 그 아래 본문만 고칩니다.",
        "> 서식은 `**굵게**` · `*강조색*` · `` `작게` `` 세 가지. 줄바꿈은 그대로 줄바꿈이 됩니다.",
        "> 다 고쳤으면: `python3 tools/portfolio.py apply`",
        "",
    ]
    cur = None
    for key, el in items:
        sec = key.split(".")[0]
        if sec != cur:
            cur = sec
            lines += ["", "---", "", f"## {sec}", ""]
        lines += [f"[{key}]", to_md(el), ""]
    MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"내보냄: {MD.relative_to(ROOT)}  ({len(items)}개 항목)")


def parse_md():
    text = MD.read_text(encoding="utf-8")
    blocks, key, buf = {}, None, []
    for line in text.split("\n"):
        m = re.fullmatch(r"\[([a-zA-Z0-9_.]+)\]", line.strip())
        if m:
            if key:
                blocks[key] = "\n".join(buf).strip()
            key, buf = m.group(1), []
        elif key is not None:
            if line.startswith(("## ", "---", "# ", "> ")):
                blocks[key] = "\n".join(buf).strip()
                key, buf = None, []
            else:
                buf.append(line)
    if key:
        blocks[key] = "\n".join(buf).strip()
    return {k: v for k, v in blocks.items() if v}


def _pattern(inner):
    """원본 HTML 안에서 이 조각을 찾기 위한 느슨한 정규식 (공백·br 표기 차이 허용)"""
    parts = re.split(r"(<[^>]+>)", inner)
    out = []
    for t in parts:
        if not t:
            continue
        if t.startswith("<"):
            tag = re.match(r"<\s*/?\s*([a-zA-Z0-9]+)", t)
            name = tag.group(1).lower() if tag else ""
            if name == "br":
                out.append(r"<\s*br\s*/?\s*>")
            else:
                out.append(re.escape(t).replace(r"\ ", r"\s+"))
        else:
            out.append(r"\s*".join(re.escape(w) for w in t.split()))
    return re.compile(r"\s*".join(x for x in out if x))


def cmd_apply():
    raw = HTML.read_text(encoding="utf-8")
    soup = BeautifulSoup(raw, "html.parser")
    items = collect(soup)
    blocks = parse_md()

    edits, cursor, notfound = [], 0, []
    for key, el in items:
        inner = el.decode_contents()
        m = _pattern(inner).search(raw, cursor)
        if not m:
            notfound.append(key)
            continue
        cursor = m.end()
        want = blocks.get(key)
        if want is not None and want != to_md(el):
            edits.append((m.start(), m.end(), from_md(want), key))

    for a, b, html, _ in reversed(edits):
        raw = raw[:a] + html + raw[b:]

    if edits:
        HTML.write_text(raw, encoding="utf-8")
    print(f"반영: {len(edits)}곳 수정 / 전체 {len(items)}개 항목")
    for _, _, _, k in edits[:20]:
        print(f"   · {k}")
    unknown = [k for k in blocks if k not in dict(items)]
    if unknown:
        print("⚠ html 에 없는 키 (무시):", ", ".join(unknown[:8]))
    if notfound:
        print("⚠ 원문에서 위치를 못 찾은 키 (건너뜀):", ", ".join(notfound[:8]))


def cmd_check():
    soup = BeautifulSoup(HTML.read_text(encoding="utf-8"), "html.parser")
    items = dict(collect(soup))
    blocks = parse_md()
    bad = [k for k, v in blocks.items() if k in items and to_md(items[k]) != v]
    print(f"검사: 전체 {len(items)} · md {len(blocks)} · 불일치 {len(bad)}")
    for k in bad[:10]:
        print(f"  ✗ {k}\n    md  : {blocks[k][:70]}\n    html: {to_md(items[k])[:70]}")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "export"
    {"export": cmd_export, "apply": cmd_apply, "check": cmd_check}[cmd]()

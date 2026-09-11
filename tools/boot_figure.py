"""Draw a boot flow as a left-to-right timeline.

Mermaid lays diagrams out automatically, which cannot place a timeline axis
underneath a row of stages. These figures are emitted as SVG instead, so the
stages sit in one row, the axis runs beneath them, and each transition label
sits under the segment of the axis it belongs to.

Sizing is driven by the text: a column is as wide as the widest thing in it,
either the stage box or the label beneath the axis. Font sizes are chosen so
the figure stays legible after GitHub scales it down to the page width.
"""

from __future__ import annotations

from xml.sax.saxutils import escape

# Rough advance width of the sans-serif stack below, as a fraction of the font
# size. Measured against the rendered output rather than derived from metrics;
# the bold figure is larger because stage names are set in semibold.
CHAR_W = 0.55
BOLD_CHAR_W = 0.63

FONT = ("-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif")
STAGE_FS = 14.0       # stage name
LABEL_FS = 11.5       # what crosses the boundary
CHIP_FS = 13.0        # entry and target chips

MIN_BOX_H = 44
ORD_Y = 18            # the stage ordinal, above its box
ROW_TOP = 26          # top of the tallest element in the stage row
AXIS_GAP = 26         # from the bottom of the stage row down to the axis
LABEL_GAP = 20        # from the axis down to the first line of label text
PAD = 16
LINE_H = 15
MIN_BOX_W = 92
GAP = 22              # clear space either side of an arrowhead
LABEL_CHARS = 18      # wrap width for the text under the axis


def text_w(s: str, fs: float, bold: bool = False) -> float:
    return len(s) * fs * (BOLD_CHAR_W if bold else CHAR_W)


def wrap(text: str, max_chars: int) -> list[str]:
    """Greedy wrap. Long single words are allowed to overflow the column."""
    lines: list[str] = []
    line = ""
    for word in text.split():
        candidate = f"{line} {word}".strip()
        if line and len(candidate) > max_chars:
            lines.append(line)
            line = word
        else:
            line = candidate
    if line:
        lines.append(line)
    return lines or [""]


def block(text: str, fs: float, max_chars: int,
          bold: bool = False) -> tuple[list[str], float]:
    lines = wrap(text, max_chars)
    return lines, max(text_w(x, fs, bold) for x in lines)


def _tspans(lines: list[str], cx: float, y: float, fs: float,
            weight: str, fill: str) -> str:
    out = []
    for i, line in enumerate(lines):
        out.append(
            f'<text x="{cx:.1f}" y="{y + i * LINE_H:.1f}" text-anchor="middle" '
            f'font-family="{FONT}" font-size="{fs}" font-weight="{weight}" '
            f'fill="{fill}">{escape(line)}</text>')
    return "".join(out)


def plain(text: str) -> str:
    """Curated prose carries Mermaid line breaks; SVG wrapping does its own."""
    return text.replace("<br/>", " ").replace("<br>", " ")


def timeline_svg(entry: str, stages: list[tuple[str, str]], target: str,
                 accent: str = "#4a6fa5") -> str:
    """`stages` is (name, what it hands to the next); the last goes to target."""
    entry, target = plain(entry), plain(target)
    stages = [(plain(n), plain(c)) for n, c in stages]
    entry_lines, entry_w = block(entry, CHIP_FS, 18)
    target_lines, target_w = block(target, CHIP_FS, 20)
    entry_w = max(entry_w + 24, 112)
    target_w = max(target_w + 24, 120)

    names, labels = [], []
    for name, carries in stages:
        nl, nw = block(name, STAGE_FS, 15, bold=True)
        names.append((nl, max(nw + 20, MIN_BOX_W)))
        labels.append(block(carries, LABEL_FS, LABEL_CHARS))

    # Column pitch: consecutive boxes must clear each other *and* leave room
    # for the label that sits under the axis segment between them.
    widths = [entry_w] + [w for _, w in names] + [target_w]
    label_w = [0.0] + [lw for _, lw in labels]
    centres = [PAD + widths[0] / 2]
    for i in range(1, len(widths)):
        need = widths[i - 1] / 2 + widths[i] / 2 + GAP
        centres.append(centres[-1] + max(need, label_w[i - 1] + 18))

    width = centres[-1] + widths[-1] / 2 + PAD
    tallest = max((len(l) for l, _ in labels), default=1)

    rows = [len(entry_lines)] + [len(l) for l, _ in names] + [len(target_lines)]
    row_h = max(MIN_BOX_H, max(rows) * LINE_H + 18)
    row_mid = ROW_TOP + row_h / 2
    axis_y = ROW_TOP + row_h + AXIS_GAP
    label_y = axis_y + LABEL_GAP

    height = label_y + tallest * LINE_H + 4

    p = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width:.0f} {height:.0f}" '
         f'width="{width:.0f}" height="{height:.0f}" role="img">',
         '<defs><marker id="a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" '
         'markerHeight="7" orient="auto-start-reverse">'
         f'<path d="M0,0 L10,5 L0,10 z" fill="{accent}"/></marker></defs>',
         f'<rect width="{width:.0f}" height="{height:.0f}" fill="#ffffff"/>']

    def chip(cx: float, w: float, lines: list[str]) -> None:
        h = max(MIN_BOX_H - 4, len(lines) * LINE_H + 14)
        y = row_mid - h / 2
        p.append(f'<rect x="{cx - w / 2:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
                 f'rx="{h / 2:.0f}" fill="#f4f4f5" stroke="#9aa0a6" '
                 f'stroke-dasharray="4 3"/>')
        ty = row_mid - (len(lines) - 1) * LINE_H / 2 + 4
        p.append(_tspans(lines, cx, ty, CHIP_FS, "normal", "#3c4043"))

    chip(centres[0], entry_w, entry_lines)
    for i, (lines, w) in enumerate(names):
        cx = centres[i + 1]
        bh = max(MIN_BOX_H, len(lines) * LINE_H + 18)
        p.append(f'<rect x="{cx - w / 2:.1f}" y="{row_mid - bh / 2:.1f}" width="{w:.1f}" '
                 f'height="{bh:.1f}" rx="5" fill="#eef3fb" stroke="{accent}"/>')
        ty = row_mid - (len(lines) - 1) * LINE_H / 2 + 4
        p.append(_tspans(lines, cx, ty, STAGE_FS, "600", "#1f2328"))
        p.append(f'<text x="{cx:.1f}" y="{ORD_Y}" text-anchor="middle" '
                 f'font-family="{FONT}" font-size="11" fill="#80868b">{i + 1}</text>')
    chip(centres[-1], target_w, target_lines)

    # The axis: one segment per transition, each ending in an arrowhead.
    for i in range(len(centres) - 1):
        x1, x2 = centres[i], centres[i + 1]
        p.append(f'<line x1="{x1:.1f}" y1="{axis_y}" x2="{x2 - 2:.1f}" y2="{axis_y}" '
                 f'stroke="{accent}" stroke-width="1.6" marker-end="url(#a)"/>')
        p.append(f'<line x1="{x1:.1f}" y1="{axis_y - 5}" x2="{x1:.1f}" y2="{axis_y + 5}" '
                 f'stroke="{accent}" stroke-width="1.2"/>')
        if i:                                     # entry -> first stage is unlabelled
            lines, _ = labels[i - 1]
            mid = (x1 + x2) / 2
            p.append(_tspans(lines, mid, label_y, LABEL_FS, "normal", "#5f6368"))
    p.append(f'<line x1="{centres[-1]:.1f}" y1="{axis_y - 5}" x2="{centres[-1]:.1f}" '
             f'y2="{axis_y + 5}" stroke="{accent}" stroke-width="1.2"/>')
    p.append("</svg>")
    return "\n".join(p)

import html
import json
import textwrap
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from models import MeetingNotes


OUTPUT_DIR = Path(__file__).parent / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)


def _safe(value: str) -> str:
    return html.escape(value or "")


def render_dashboard(notes: MeetingNotes) -> str:
    summary_html = "".join(
        f"<li>{_safe(item)}</li>" for item in notes.summary_points
    ) or "<li>No summary points found.</li>"

    decisions_html = "".join(
        f'<div class="decision">✓ {_safe(item)}</div>' for item in notes.decisions
    ) or '<div class="muted">No explicit decisions found.</div>'

    key_points_html = "".join(
        f'<div class="key-point">{_safe(item)}</div>' for item in notes.key_points
    ) or '<div class="muted">No extra key points.</div>'

    rows = []
    for item in notes.action_items:
        priority_class = item.priority.lower()
        rows.append(
            f"""
            <div class="action-row">
                <div class="task">{_safe(item.task)}</div>
                <div class="meta"><span>👤 {_safe(item.owner)}</span><span>📅 {_safe(item.due_date)}</span></div>
                <span class="priority {priority_class}">{_safe(item.priority)}</span>
            </div>
            """
        )

    actions_html = "".join(rows) or '<div class="muted">No concrete action items found.</div>'

    return f"""
    <div class="meeting-board done-pop">
        <div class="hero-row">
            <div>
                <div class="eyebrow">MEETING INTELLIGENCE</div>
                <h1>{_safe(notes.title)}</h1>
                <p class="one-line">{_safe(notes.one_line_summary)}</p>
            </div>
            <div class="score-card">
                <div class="score">{len(notes.action_items)}</div>
                <div class="score-label">ACTION ITEMS</div>
            </div>
        </div>

        <div class="stats">
            <div class="stat"><b>{len(notes.summary_points)}</b><span>Summary points</span></div>
            <div class="stat"><b>{len(notes.decisions)}</b><span>Decisions</span></div>
            <div class="stat"><b>{len(notes.key_points)}</b><span>Key points</span></div>
        </div>

        <div class="grid-two">
            <section class="panel">
                <h3>✨ Quick Summary</h3>
                <ul>{summary_html}</ul>
            </section>
            <section class="panel">
                <h3>✅ Decisions</h3>
                {decisions_html}
            </section>
        </div>

        <section class="panel actions-panel">
            <div class="panel-title-row"><h3>⚡ Action Items</h3><span>{len(notes.action_items)} total</span></div>
            {actions_html}
        </section>

        <div class="grid-two">
            <section class="panel">
                <h3>💡 Key Points</h3>
                {key_points_html}
            </section>
            <section class="panel next-panel">
                <h3>🎯 Next Meeting Focus</h3>
                <p>{_safe(notes.next_meeting_focus)}</p>
            </section>
        </div>
    </div>
    """


def render_status(stage: int, message: str) -> str:
    labels = [
        "Upload received",
        "Transcribing audio",
        "Agent extracting notes",
        "Designing visual summary",
    ]

    items = []
    for idx, label in enumerate(labels, start=1):
        if idx < stage:
            state = "complete"
            icon = "✓"
        elif idx == stage:
            state = "active"
            icon = "●"
        else:
            state = "waiting"
            icon = str(idx)

        items.append(
            f'<div class="step {state}"><span class="step-icon">{icon}</span><span>{label}</span></div>'
        )

    return f"""
    <div class="process-card">
        <div class="processing-title"><span class="pulse-dot"></span>{_safe(message)}</div>
        <div class="steps">{''.join(items)}</div>
    </div>
    """


def save_markdown(notes: MeetingNotes, transcript: str) -> str:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = OUTPUT_DIR / f"meeting_notes_{stamp}.md"

    summary = "\n".join(f"- {x}" for x in notes.summary_points)
    decisions = "\n".join(f"- {x}" for x in notes.decisions) or "- None explicitly stated"
    keys = "\n".join(f"- {x}" for x in notes.key_points) or "- None"

    if notes.action_items:
        actions = "\n".join(
            f"- **{x.task}** — Owner: {x.owner} | Due: {x.due_date} | Priority: {x.priority}"
            for x in notes.action_items
        )
    else:
        actions = "- None"

    content = f"""# {notes.title}

> {notes.one_line_summary}

## Summary
{summary}

## Decisions
{decisions}

## Action Items
{actions}

## Key Points
{keys}

## Next Meeting Focus
{notes.next_meeting_focus}

---

## Transcript
{transcript}
"""
    path.write_text(content, encoding="utf-8")
    return str(path)


def save_json(notes: MeetingNotes, transcript: str) -> str:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = OUTPUT_DIR / f"meeting_notes_{stamp}.json"
    payload = notes.model_dump()
    payload["transcript"] = transcript
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return str(path)


def _font(size: int, bold: bool = False):
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
        "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf",
    ]
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size=size)
        except OSError:
            pass
    return ImageFont.load_default()


def _wrap(draw: ImageDraw.ImageDraw, text: str, font, max_width: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    line = ""
    for word in words:
        candidate = f"{line} {word}".strip()
        box = draw.textbbox((0, 0), candidate, font=font)
        if box[2] - box[0] <= max_width:
            line = candidate
        else:
            if line:
                lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


def _rounded(draw, xy, radius, fill, outline=None, width=1):
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)


def save_png(notes: MeetingNotes) -> str:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = OUTPUT_DIR / f"meeting_summary_{stamp}.png"

    width, height = 1200, 1600
    image = Image.new("RGB", (width, height), "#F6F8FC")
    draw = ImageDraw.Draw(image)

    # soft background accents
    draw.ellipse((-180, -120, 420, 480), fill="#E8EEFF")
    draw.ellipse((900, 1200, 1450, 1750), fill="#EAFBF5")

    left = 80
    content_width = width - 160

    eyebrow = _font(28, True)
    title_font = _font(56, True)
    body_font = _font(30)
    heading_font = _font(34, True)
    small_font = _font(24)
    badge_font = _font(24, True)

    draw.text((left, 85), "AI MEETING NOTES", font=eyebrow, fill="#5A68D8")

    y = 135
    for line in _wrap(draw, notes.title, title_font, content_width - 220)[:2]:
        draw.text((left, y), line, font=title_font, fill="#172033")
        y += 68

    y += 10
    for line in _wrap(draw, notes.one_line_summary, body_font, content_width)[:3]:
        draw.text((left, y), line, font=body_font, fill="#596173")
        y += 42

    # metric pills
    y += 28
    metrics = [
        (f"{len(notes.action_items)}", "Action items"),
        (f"{len(notes.decisions)}", "Decisions"),
        (f"{len(notes.key_points)}", "Key points"),
    ]
    pill_w = 320
    gap = 20
    for i, (num, label) in enumerate(metrics):
        x = left + i * (pill_w + gap)
        _rounded(draw, (x, y, x + pill_w, y + 110), 26, "#FFFFFF", "#E4E8F2", 2)
        draw.text((x + 24, y + 16), num, font=heading_font, fill="#24304A")
        draw.text((x + 24, y + 66), label, font=small_font, fill="#727B8F")

    y += 150

    # Summary panel
    panel_top = y
    summary_height = 300
    _rounded(draw, (left, panel_top, width - left, panel_top + summary_height), 32, "#FFFFFF", "#E4E8F2", 2)
    draw.text((left + 30, panel_top + 24), "Quick Summary", font=heading_font, fill="#1E2941")
    line_y = panel_top + 80
    for item in notes.summary_points[:4]:
        draw.ellipse((left + 34, line_y + 10, left + 46, line_y + 22), fill="#6875E8")
        wrapped = _wrap(draw, item, small_font, content_width - 100)
        for part in wrapped[:2]:
            draw.text((left + 60, line_y), part, font=small_font, fill="#4E5668")
            line_y += 34
        line_y += 8

    y = panel_top + summary_height + 28

    # Action items panel
    remaining_height = height - y - 70
    _rounded(draw, (left, y, width - left, y + remaining_height), 32, "#FFFFFF", "#E4E8F2", 2)
    draw.text((left + 30, y + 24), "Action Items", font=heading_font, fill="#1E2941")

    row_y = y + 82
    for idx, item in enumerate(notes.action_items[:5], start=1):
        if row_y > height - 180:
            break
        draw.ellipse((left + 30, row_y + 2, left + 74, row_y + 46), fill="#EEF1FF")
        draw.text((left + 44, row_y + 9), str(idx), font=small_font, fill="#5968D8")

        task_lines = _wrap(draw, item.task, small_font, 650)
        draw.text((left + 92, row_y), task_lines[0], font=small_font, fill="#273149")
        meta = f"Owner: {item.owner}   •   Due: {item.due_date}"
        meta_line = textwrap.shorten(meta, width=72, placeholder="…")
        draw.text((left + 92, row_y + 40), meta_line, font=_font(20), fill="#7A8293")

        badge_x = width - left - 155
        badge_color = {
            "High": "#FFE9EA",
            "Medium": "#FFF5DE",
            "Normal": "#EAF8F2",
        }[item.priority]
        badge_text = {
            "High": "#C33C48",
            "Medium": "#A46D13",
            "Normal": "#2F7B60",
        }[item.priority]
        _rounded(draw, (badge_x, row_y + 5, badge_x + 125, row_y + 47), 20, badge_color)
        draw.text((badge_x + 18, row_y + 13), item.priority, font=_font(18, True), fill=badge_text)
        row_y += 92

    image.save(path, quality=95)
    return str(path)

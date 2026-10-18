import time

import gradio as gr

from meeting_agent import MeetingNotesService
from visualizer import (
    render_dashboard,
    render_status,
    save_json,
    save_markdown,
    save_png,
)


CSS = """
:root {
  --ink: #172033;
  --muted: #697287;
  --line: #e5e8f1;
  --violet: #6674ea;
}
.gradio-container { max-width: 1160px !important; margin: 0 auto !important; }
#hero { padding: 22px 6px 8px; }
.hero-kicker { color: #6674ea; font-weight: 800; letter-spacing: .14em; font-size: 12px; }
.hero-title { font-size: clamp(34px, 5vw, 60px); line-height: 1.02; font-weight: 900; color: #172033; margin: 10px 0; }
.hero-copy { max-width: 760px; color: #697287; font-size: 17px; }
.flow { margin-top: 20px; display:flex; flex-wrap:wrap; gap:10px; align-items:center; }
.flow-chip { background:#fff; border:1px solid #e5e8f1; border-radius:999px; padding:9px 13px; font-weight:700; color:#46506a; box-shadow:0 8px 22px rgba(34,45,90,.06); }
.flow-arrow { color:#9aa2b2; font-weight:800; }
.process-card, .meeting-board { background: linear-gradient(145deg,#ffffff,#fbfcff); border:1px solid var(--line); border-radius:28px; padding:24px; box-shadow:0 18px 60px rgba(34,45,90,.08); }
.processing-title { font-size:18px; font-weight:800; color:var(--ink); display:flex; gap:10px; align-items:center; margin-bottom:18px; }
.pulse-dot { width:12px; height:12px; border-radius:50%; background:var(--violet); display:inline-block; animation:pulse 1.1s infinite; }
@keyframes pulse { 0%,100%{transform:scale(.9);opacity:.55}50%{transform:scale(1.35);opacity:1} }
.steps { display:grid; grid-template-columns:repeat(4,1fr); gap:10px; }
.step { border-radius:18px; padding:14px; background:#f5f6fa; color:#9298a8; font-weight:700; display:flex; gap:9px; align-items:center; }
.step.active { background:#eef0ff; color:#4f5ed1; animation:glow 1.2s infinite alternate; }
.step.complete { background:#eaf8f2; color:#29755a; }
.step-icon { width:26px; height:26px; border-radius:50%; background:#fff; display:grid; place-items:center; font-size:13px; }
@keyframes glow { from{box-shadow:0 0 0 rgba(102,116,234,0)} to{box-shadow:0 10px 30px rgba(102,116,234,.18)} }
.meeting-board { overflow:hidden; position:relative; }
.meeting-board:before { content:""; position:absolute; width:360px; height:360px; border-radius:50%; background:#eef0ff; top:-220px; right:-120px; filter:blur(2px); }
.done-pop { animation:popin .55s cubic-bezier(.2,.9,.2,1); }
@keyframes popin { from{opacity:0;transform:translateY(16px) scale(.985)} to{opacity:1;transform:none} }
.hero-row { display:flex; justify-content:space-between; gap:25px; position:relative; z-index:1; }
.eyebrow { color:#6674ea; font-size:12px; letter-spacing:.16em; font-weight:900; }
.meeting-board h1 { margin:7px 0 8px; color:#172033; font-size:35px; }
.one-line { margin:0; color:#697287; font-size:16px; }
.score-card { min-width:125px; height:125px; border-radius:26px; background:#172033; color:#fff; display:flex; flex-direction:column; align-items:center; justify-content:center; box-shadow:0 16px 35px rgba(23,32,51,.18); }
.score { font-size:46px; line-height:1; font-weight:900; }.score-label{font-size:10px;letter-spacing:.12em;margin-top:7px;opacity:.68;font-weight:800}
.stats { display:grid; grid-template-columns:repeat(3,1fr); gap:12px; margin:22px 0; }
.stat { border:1px solid var(--line); border-radius:18px; padding:14px 16px; background:#fff; display:flex; flex-direction:column; }.stat b{font-size:23px;color:#273149}.stat span{font-size:12px;color:#8a91a1;margin-top:3px}
.grid-two { display:grid; grid-template-columns:1fr 1fr; gap:14px; margin-top:14px; }
.panel { background:#fff; border:1px solid var(--line); border-radius:22px; padding:19px; }.panel h3{margin:0 0 14px;color:#263049}.panel ul{padding-left:20px;color:#596173}.panel li{margin:8px 0}
.actions-panel { margin-top:14px; }.panel-title-row{display:flex;justify-content:space-between;align-items:center}.panel-title-row span{font-size:12px;color:#8c93a2}
.action-row { position:relative; border-top:1px solid #eef0f5; padding:14px 110px 14px 0; }.task{font-weight:800;color:#29334a}.meta{display:flex;gap:16px;flex-wrap:wrap;margin-top:7px;color:#808899;font-size:12px}.priority{position:absolute;right:0;top:15px;border-radius:999px;padding:5px 10px;font-size:11px;font-weight:900}.priority.high{background:#ffe9ea;color:#bd3945}.priority.medium{background:#fff4da;color:#93600f}.priority.normal{background:#e9f8f1;color:#2c7459}
.decision,.key-point{padding:8px 10px;border-radius:12px;background:#f7f8fb;margin:7px 0;color:#566071}.next-panel p{color:#596173}.muted{color:#9aa1af;font-style:italic}
@media(max-width:760px){.steps{grid-template-columns:1fr 1fr}.grid-two{grid-template-columns:1fr}.hero-row{flex-direction:column}.score-card{width:100%;height:86px}.stats{grid-template-columns:1fr}.meeting-board h1{font-size:28px}}
"""


async def process_meeting(media_path, output_style):
    empty_html = '<div class="process-card"><div class="processing-title">Upload a meeting recording to start.</div></div>'

    if not media_path:
        yield empty_html, "", "", None, None, None
        return

    try:
        yield render_status(1, "Meeting received — preparing the pipeline..."), "", "", None, None, None
        time.sleep(0.35)

        service = MeetingNotesService()

        yield render_status(2, "Listening carefully and creating the transcript..."), "", "", None, None, None
        transcript = service.transcribe(media_path)

        yield render_status(3, "Meeting Notes Agent is finding decisions and action items..."), "", transcript, None, None, None
        notes = await service.create_notes(transcript, output_style=output_style)

        yield render_status(4, "Turning the result into shareable notes and a visual card..."), "", transcript, None, None, None
        png_path = save_png(notes)
        markdown_path = save_markdown(notes, transcript)
        json_path = save_json(notes, transcript)

        final_html = render_dashboard(notes)
        done_status = render_status(5, "Done — your meeting is now organized.")
        yield done_status, final_html, transcript, png_path, markdown_path, json_path

    except Exception as exc:
        error_html = f"""
        <div class="process-card">
            <div class="processing-title">⚠️ Could not process this meeting</div>
            <div style="color:#a33b45;background:#fff2f3;border-radius:16px;padding:14px;">{str(exc)}</div>
        </div>
        """
        yield error_html, "", "", None, None, None


with gr.Blocks(title="AI Meeting Notes Agent") as demo:
    gr.HTML(
        """
        <div id="hero">
          <div class="hero-kicker">END-TO-END AI PROJECT</div>
          <div class="hero-title">AI Meeting Notes Agent</div>
          <div class="hero-copy">Drop a meeting audio or video. The app transcribes it, extracts decisions and action items, then creates a polished visual summary plus downloadable notes.</div>
          <div class="flow">
            <span class="flow-chip">🎙️ Upload</span><span class="flow-arrow">→</span>
            <span class="flow-chip">📝 Transcribe</span><span class="flow-arrow">→</span>
            <span class="flow-chip">🤖 Meeting Agent</span><span class="flow-arrow">→</span>
            <span class="flow-chip">⚡ Action Items</span><span class="flow-arrow">→</span>
            <span class="flow-chip">🖼️ Visual + Files</span>
          </div>
        </div>
        """
    )

    with gr.Row():
        with gr.Column(scale=2):
            media = gr.File(
                label="Upload meeting audio or video",
                file_types=[".mp3", ".mp4", ".wav", ".m4a", ".ogg", ".webm", ".flac", ".mpeg", ".mpga"],
                type="filepath",
            )
            style = gr.Radio(
                ["Clean English", "Simple Hinglish"],
                value="Clean English",
                label="Output style",
            )
            run_btn = gr.Button("✨ Create Meeting Notes", variant="primary", size="lg")
        with gr.Column(scale=3):
            status = gr.HTML(render_status(1, "Upload a meeting recording to start."))

    gr.Markdown("## Result")
    dashboard = gr.HTML()

    with gr.Tabs():
        with gr.Tab("Transcript"):
            transcript = gr.Textbox(
                label="Transcript",
                lines=14,
                buttons=["copy"]
            )
        with gr.Tab("Visual Card"):
            png_file = gr.File(label="Download PNG summary")
        with gr.Tab("Saved Notes"):
            md_file = gr.File(label="Download Markdown notes")
            json_file = gr.File(label="Download JSON data")

    run_btn.click(
        fn=process_meeting,
        inputs=[media, style],
        outputs=[status, dashboard, transcript, png_file, md_file, json_file],
    )

    gr.Markdown(
        """
### Reel-friendly demo flow
1. Upload a short meeting clip.  
2. Record the animated processing steps.  
3. Reveal the **Meeting Intelligence** dashboard.  
4. Open the generated **PNG summary card** and the saved **meeting_notes.md** file.
        """
    )


if __name__ == "__main__":
    demo.launch(css=CSS)

# AI Meeting Notes Agent 🎙️🤖

A simple end-to-end AI project built for a short-form coding reel.

## What it does

```text
Meeting audio/video
        ↓
OpenAI transcription
        ↓
Meeting Notes Agent
        ↓
Structured notes
        ↓
Animated Gradio dashboard
        ↓
PNG summary + Markdown + JSON
```

The user uploads an audio/video meeting file. The app:

1. Transcribes the recording.
2. Sends the transcript to an AI agent.
3. Extracts a short summary, decisions, action items, owners, due dates and key points.
4. Shows the result in an animated visual dashboard.
5. Generates a shareable PNG card.
6. Saves complete notes as Markdown and JSON.

## Why this project is reel-friendly

The demo has a visible transformation:

**raw meeting recording → animated processing → clean action items → polished visual → saved file**

That makes the result easy to understand even for someone who does not know AI coding.

## Project structure

```text
ai_meeting_notes_agent/
├── app.py                 # Gradio UI + animated pipeline
├── meeting_agent.py       # transcription + AI agent
├── models.py              # structured output schema
├── visualizer.py          # dashboard + PNG/MD/JSON exports
├── requirements.txt
├── .env.example
├── sample_data/
│   └── demo_transcript.txt
├── assets/
│   ├── demo_result.png
│   └── processing_preview.gif
└── outputs/               # generated files appear here
```

## Setup

### 1. Create a virtual environment

```bash
python -m venv .venv
```

macOS/Linux:

```bash
source .venv/bin/activate
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Add your API key

```bash
cp .env.example .env
```

Then edit `.env`:

```env
OPENAI_API_KEY=your_key_here
TRANSCRIBE_MODEL=gpt-4o-mini-transcribe
MEETING_AGENT_MODEL=gpt-4.1-mini
```

### 4. Run the app

```bash
python app.py
```

Open the local Gradio URL shown in the terminal.

## Supported upload types

The app accepts common transcription formats including:

- MP3
- MP4
- WAV
- M4A
- OGG
- WebM
- FLAC
- MPEG / MPGA

Because MP4 is accepted by the transcription API, a simple meeting video can be uploaded directly without adding a separate video-to-audio conversion step.

## Best 20-second demo recording

Say something like:

> Arman will finish the chat UI by Friday. Rahul will test the API. We agreed to deploy on Monday. The production API key is still pending, so Arman will follow up with DevOps tomorrow.

Then the result should clearly show:

- summary
- deployment decision
- action owners
- due dates
- blocker
- next-meeting focus

## Suggested reel flow

**Hook**  
“I gave my AI Agent a meeting recording… and it turned it into this.”

**Demo**

```text
Upload recording
→ animated Transcribing
→ Agent extracting action items
→ beautiful dashboard reveal
→ PNG summary
→ meeting_notes.md saved
```

**Ending**  
“Raw meeting se complete notes, action items aur shareable summary — automatically.”

## Notes

- The agent is instructed not to invent facts that are missing from the transcript.
- Owners and due dates become `Not mentioned` if they are not stated.
- Generated files are written into `outputs/`.
- For a production app, add authentication, persistent storage, file-size checks and privacy controls.

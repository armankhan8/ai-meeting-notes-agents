import os
from pathlib import Path

from agents import Agent, Runner
from dotenv import load_dotenv
from openai import OpenAI

from models import MeetingNotes

load_dotenv()

SUPPORTED_EXTENSIONS = {
    ".flac",
    ".mp3",
    ".mp4",
    ".mpeg",
    ".mpga",
    ".m4a",
    ".ogg",
    ".wav",
    ".webm",
}


class MeetingNotesService:
    def __init__(self) -> None:
        if not os.getenv("OPENAI_API_KEY"):
            raise RuntimeError(
                "OPENAI_API_KEY is missing. Copy .env.example to .env and add your key."
            )

        self.client = OpenAI()
        self.transcribe_model = os.getenv(
            "TRANSCRIBE_MODEL", "gpt-4o-mini-transcribe"
        )
        self.agent_model = os.getenv("MEETING_AGENT_MODEL", "gpt-4.1-mini")

    def transcribe(self, media_path: str) -> str:
        path = Path(media_path)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            raise ValueError(
                "Unsupported file. Use mp3, mp4, wav, m4a, ogg, webm, flac, mpeg or mpga."
            )

        with path.open("rb") as media_file:
            transcription = self.client.audio.transcriptions.create(
                model=self.transcribe_model,
                file=media_file,
            )

        text = getattr(transcription, "text", "").strip()
        if not text:
            raise RuntimeError("No speech could be transcribed from this file.")

        return text

    async def create_notes(
        self,
        transcript: str,
        output_style: str = "Clean English"
    ) -> MeetingNotes:

        language_rule = (
            "Write the final notes in simple Hinglish using natural Roman script."
            if output_style == "Simple Hinglish"
            else "Write the final notes in clear, simple English."
        )

        agent = Agent(
            name="Meeting Notes Agent",
            model=self.agent_model,
            instructions=(
                "You turn meeting transcripts into reliable structured meeting notes. "
                "Use ONLY facts stated in the transcript. Never invent names, deadlines, "
                "decisions, blockers, or tasks. If an owner or due date is missing, use "
                "'Not mentioned'. Keep bullets short and useful. "
                + language_rule
            ),
            output_type=MeetingNotes,
        )

        prompt = f"""
    Create meeting notes from the transcript below.

    TRANSCRIPT:
    {transcript}
    """.strip()

        result = await Runner.run(agent, prompt)

        notes = result.final_output

        if not isinstance(notes, MeetingNotes):
            notes = MeetingNotes.model_validate(notes)

        return notes
"""Slack bot using Bolt for Python in Socket Mode.

Responds to:
  - @mentions in channels
  - Direct messages

Usage:
    python -m src.slack.bot
"""

from __future__ import annotations

import logging

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from src.agent.answer import generate_answer
from src.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = App(token=settings.slack_bot_token)


def _format_answer(answer) -> str:
    """Format an Answer into a Slack message."""
    blocks = [answer.text]

    # Add sources footer
    source_lines = []
    seen = set()
    for r in answer.sources:
        if r.source_id not in seen:
            seen.add(r.source_id)
            icon = "📄" if r.source_type == "knowledge_base" else "🎫"
            source_lines.append(f"{icon} `{r.source_id}` — {r.source_title}")

    if source_lines:
        blocks.append("\n_Sources:_\n" + "\n".join(source_lines))

    blocks.append(f"\n_Confidence: {answer.top_score:.2f}_")

    return "\n".join(blocks)


@app.event("app_mention")
def handle_mention(event, say):
    """Handle @mentions in channels — reply in thread."""
    # Strip the bot mention from the text
    text = event.get("text", "")
    # Remove the <@BOT_ID> mention prefix
    question = _strip_mention(text)

    if not question.strip():
        say("Ask me a question! For example: _How do I rotate service account credentials?_",
            thread_ts=event.get("ts"))
        return

    logger.info(f"Mention question: {question}")
    answer = generate_answer(question)
    say(_format_answer(answer), thread_ts=event.get("ts"))


@app.event("message")
def handle_dm(event, say):
    """Handle direct messages."""
    # Ignore bot's own messages and message subtypes (edits, joins, etc.)
    if event.get("bot_id") or event.get("subtype"):
        return

    question = event.get("text", "").strip()
    if not question:
        return

    logger.info(f"DM question: {question}")
    answer = generate_answer(question)
    say(_format_answer(answer))


def _strip_mention(text: str) -> str:
    """Remove the <@BOT_ID> mention from the beginning of the message."""
    import re
    return re.sub(r"<@[A-Z0-9]+>\s*", "", text).strip()


def main():
    """Start the bot in Socket Mode."""
    handler = SocketModeHandler(app, settings.slack_app_token)
    logger.info("⚡ Atlas Support Bot is running in Socket Mode")
    handler.start()


if __name__ == "__main__":
    main()

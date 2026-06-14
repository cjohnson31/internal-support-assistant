"""FastAPI web interface for the Internal Support Assistant.

Usage:
    python -m src.web
    # Then open http://localhost:8000
"""

from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from src.agent.answer import generate_answer

app = FastAPI(title="Internal Support Assistant")


class AskRequest(BaseModel):
    question: str
    api_key: str


class SourceResponse(BaseModel):
    source_id: str
    source_title: str
    source_type: str
    score: float
    text: str


class AskResponse(BaseModel):
    answer: str
    refused: bool
    top_score: float
    sources: list[SourceResponse]


@app.post("/api/ask", response_model=AskResponse)
def ask(req: AskRequest):
    """Ask a question. Requires an Anthropic API key per request."""
    if not req.api_key.strip():
        raise HTTPException(status_code=400, detail="API key is required")
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="Question is required")

    try:
        result = generate_answer(req.question.strip(), api_key=req.api_key.strip())
    except Exception as e:
        error_msg = str(e)
        if "authentication" in error_msg.lower() or "api key" in error_msg.lower():
            raise HTTPException(status_code=401, detail="Invalid API key")
        raise HTTPException(status_code=500, detail=f"Error generating answer: {error_msg}")

    return AskResponse(
        answer=result.text,
        refused=result.refused,
        top_score=result.top_score,
        sources=[
            SourceResponse(
                source_id=s.source_id,
                source_title=s.source_title,
                source_type=s.source_type,
                score=s.score,
                text=s.text[:300],
            )
            for s in result.sources
        ],
    )


@app.get("/", response_class=HTMLResponse)
def index():
    """Serve the single-page UI."""
    return HTML_PAGE


HTML_PAGE = """\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Internal Support Assistant</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }

  body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background: #0f172a;
    color: #e2e8f0;
    min-height: 100vh;
  }

  .container {
    max-width: 800px;
    margin: 0 auto;
    padding: 2rem 1.5rem;
  }

  header {
    text-align: center;
    margin-bottom: 2.5rem;
  }

  header h1 {
    font-size: 1.75rem;
    font-weight: 700;
    color: #f8fafc;
    margin-bottom: 0.5rem;
  }

  header p {
    color: #94a3b8;
    font-size: 0.95rem;
    line-height: 1.5;
  }

  .badge {
    display: inline-block;
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 999px;
    padding: 0.25rem 0.75rem;
    font-size: 0.75rem;
    color: #94a3b8;
    margin-top: 0.75rem;
  }

  .api-key-section {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 12px;
    padding: 1.25rem;
    margin-bottom: 1.5rem;
  }

  .api-key-section label {
    display: block;
    font-size: 0.85rem;
    font-weight: 600;
    color: #cbd5e1;
    margin-bottom: 0.5rem;
  }

  .api-key-section .hint {
    font-size: 0.75rem;
    color: #64748b;
    margin-bottom: 0.75rem;
  }

  .api-key-input {
    width: 100%;
    padding: 0.65rem 1rem;
    background: #0f172a;
    border: 1px solid #334155;
    border-radius: 8px;
    color: #e2e8f0;
    font-size: 0.9rem;
    font-family: 'SF Mono', Monaco, monospace;
    outline: none;
    transition: border-color 0.2s;
  }

  .api-key-input:focus { border-color: #6366f1; }

  .ask-section {
    display: flex;
    gap: 0.75rem;
    margin-bottom: 2rem;
  }

  .question-input {
    flex: 1;
    padding: 0.75rem 1rem;
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 10px;
    color: #e2e8f0;
    font-size: 0.95rem;
    outline: none;
    transition: border-color 0.2s;
  }

  .question-input:focus { border-color: #6366f1; }

  .ask-btn {
    padding: 0.75rem 1.5rem;
    background: #6366f1;
    color: white;
    border: none;
    border-radius: 10px;
    font-size: 0.95rem;
    font-weight: 600;
    cursor: pointer;
    transition: background 0.2s;
    white-space: nowrap;
  }

  .ask-btn:hover { background: #4f46e5; }
  .ask-btn:disabled { background: #334155; cursor: not-allowed; }

  .examples {
    margin-bottom: 2rem;
  }

  .examples p {
    font-size: 0.8rem;
    color: #64748b;
    margin-bottom: 0.5rem;
  }

  .example-chips {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
  }

  .example-chip {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 8px;
    padding: 0.4rem 0.75rem;
    font-size: 0.8rem;
    color: #94a3b8;
    cursor: pointer;
    transition: all 0.2s;
  }

  .example-chip:hover {
    border-color: #6366f1;
    color: #c7d2fe;
  }

  .example-chip.oos {
    border-color: #92400e;
    color: #fbbf24;
    background: #1c1712;
  }

  .example-chip.oos:hover {
    border-color: #f59e0b;
    color: #fde68a;
  }

  .result {
    display: none;
    margin-bottom: 2rem;
  }

  .result.visible { display: block; }

  .answer-card {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1rem;
  }

  .answer-card.refused {
    border-color: #ef4444;
    background: #1c1117;
  }

  .answer-label {
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: #22c55e;
    margin-bottom: 0.75rem;
  }

  .answer-card.refused .answer-label { color: #ef4444; }

  .answer-text {
    font-size: 0.95rem;
    line-height: 1.7;
    color: #e2e8f0;
    white-space: pre-wrap;
  }

  .answer-text strong, .answer-text b { color: #f8fafc; }

  .confidence {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-top: 1rem;
    padding-top: 1rem;
    border-top: 1px solid #334155;
    font-size: 0.8rem;
    color: #64748b;
  }

  .confidence-dot {
    width: 8px; height: 8px;
    border-radius: 50%;
    background: #22c55e;
  }

  .confidence-dot.low { background: #ef4444; }
  .confidence-dot.mid { background: #eab308; }

  .sources-toggle {
    background: none;
    border: 1px solid #334155;
    border-radius: 8px;
    padding: 0.5rem 1rem;
    color: #94a3b8;
    font-size: 0.85rem;
    cursor: pointer;
    width: 100%;
    text-align: left;
    transition: all 0.2s;
  }

  .sources-toggle:hover { border-color: #6366f1; color: #c7d2fe; }

  .sources-list {
    display: none;
    margin-top: 0.75rem;
  }

  .sources-list.visible { display: block; }

  .source-item {
    background: #0f172a;
    border: 1px solid #1e293b;
    border-radius: 8px;
    padding: 0.75rem 1rem;
    margin-bottom: 0.5rem;
  }

  .source-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.35rem;
  }

  .source-name {
    font-size: 0.85rem;
    font-weight: 600;
    color: #c7d2fe;
  }

  .source-score {
    font-size: 0.75rem;
    color: #64748b;
    font-family: 'SF Mono', Monaco, monospace;
  }

  .source-type {
    font-size: 0.7rem;
    color: #64748b;
  }

  .source-preview {
    font-size: 0.8rem;
    color: #64748b;
    margin-top: 0.35rem;
    line-height: 1.4;
  }

  .loading {
    display: none;
    text-align: center;
    padding: 2rem;
    color: #94a3b8;
  }

  .loading.visible { display: block; }

  .spinner {
    display: inline-block;
    width: 20px; height: 20px;
    border: 2px solid #334155;
    border-top-color: #6366f1;
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
    margin-right: 0.5rem;
    vertical-align: middle;
  }

  @keyframes spin { to { transform: rotate(360deg); } }

  .error {
    display: none;
    background: #1c1117;
    border: 1px solid #ef4444;
    border-radius: 12px;
    padding: 1rem 1.25rem;
    color: #fca5a5;
    font-size: 0.9rem;
    margin-bottom: 1.5rem;
  }

  .error.visible { display: block; }

  footer {
    text-align: center;
    padding-top: 2rem;
    border-top: 1px solid #1e293b;
    margin-top: 2rem;
  }

  footer a {
    color: #6366f1;
    text-decoration: none;
    font-size: 0.85rem;
  }

  footer a:hover { text-decoration: underline; }

  footer p {
    color: #475569;
    font-size: 0.75rem;
    margin-top: 0.5rem;
  }
</style>
</head>
<body>
<div class="container">
  <header>
    <h1>Internal Support Assistant</h1>
    <p>A RAG-powered agent that answers questions from a knowledge base and ticket history,
       with inline citations and a confidence-based refusal gate.</p>
    <span class="badge">Retrieval-Augmented Generation &bull; Claude &bull; Chroma</span>
  </header>

  <div class="api-key-section">
    <label for="apiKey">Anthropic API Key</label>
    <div class="hint">Your key is sent directly to the Anthropic API and is never stored.
      Get one at <a href="https://console.anthropic.com/" target="_blank" style="color:#6366f1">console.anthropic.com</a></div>
    <input type="password" id="apiKey" class="api-key-input" placeholder="sk-ant-...">
  </div>

  <div class="ask-section">
    <input type="text" id="question" class="question-input"
           placeholder="Ask a question about Atlas..." autocomplete="off">
    <button id="askBtn" class="ask-btn" onclick="askQuestion()">Ask</button>
  </div>

  <div class="examples">
    <p>In-scope — answerable from the knowledge base:</p>
    <div class="example-chips">
      <span class="example-chip" onclick="fillQuestion(this)">How do I rotate service account credentials?</span>
      <span class="example-chip" onclick="fillQuestion(this)">Who can deploy to production?</span>
      <span class="example-chip" onclick="fillQuestion(this)">What's the difference between SEV-2 and SEV-3?</span>
    </div>
    <p style="margin-top: 0.75rem;">Out-of-scope — should refuse rather than hallucinate:</p>
    <div class="example-chips">
      <span class="example-chip oos" onclick="fillQuestion(this)">What is the company's parental leave policy?</span>
      <span class="example-chip oos" onclick="fillQuestion(this)">How do I book a conference room?</span>
    </div>
  </div>

  <div id="error" class="error"></div>
  <div id="loading" class="loading"><span class="spinner"></span>Thinking...</div>

  <div id="result" class="result">
    <div id="answerCard" class="answer-card">
      <div id="answerLabel" class="answer-label">Answer</div>
      <div id="answerText" class="answer-text"></div>
      <div class="confidence">
        <span id="confidenceDot" class="confidence-dot"></span>
        <span id="confidenceText"></span>
      </div>
    </div>

    <button class="sources-toggle" onclick="toggleSources()">
      &#9662; Show retrieved sources
    </button>
    <div id="sourcesList" class="sources-list"></div>
  </div>

  <footer>
    <a href="https://github.com/cjohnson31/internal-support-assistant" target="_blank">
      View on GitHub
    </a>
    <p>Built with Claude &bull; Chroma &bull; FastAPI</p>
  </footer>
</div>

<script>
const questionInput = document.getElementById('question');
questionInput.addEventListener('keydown', (e) => {
  if (e.key === 'Enter') askQuestion();
});

function fillQuestion(el) {
  questionInput.value = el.textContent;
  questionInput.focus();
}

function toggleSources() {
  document.getElementById('sourcesList').classList.toggle('visible');
}

async function askQuestion() {
  const apiKey = document.getElementById('apiKey').value.trim();
  const question = questionInput.value.trim();

  if (!apiKey) { showError('Please enter your Anthropic API key.'); return; }
  if (!question) { showError('Please enter a question.'); return; }

  hideError();
  document.getElementById('result').classList.remove('visible');
  document.getElementById('loading').classList.add('visible');
  document.getElementById('askBtn').disabled = true;

  try {
    const res = await fetch('/api/ask', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question, api_key: apiKey }),
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Request failed');
    }

    const data = await res.json();
    displayResult(data);
  } catch (e) {
    showError(e.message);
  } finally {
    document.getElementById('loading').classList.remove('visible');
    document.getElementById('askBtn').disabled = false;
  }
}

function displayResult(data) {
  const card = document.getElementById('answerCard');
  const label = document.getElementById('answerLabel');
  const text = document.getElementById('answerText');
  const dot = document.getElementById('confidenceDot');
  const conf = document.getElementById('confidenceText');

  card.className = data.refused ? 'answer-card refused' : 'answer-card';
  label.textContent = data.refused ? 'Refused — Low Confidence' : 'Answer';

  // Basic markdown-like formatting
  let formatted = data.answer
    .replace(/\\*\\*(.+?)\\*\\*/g, '<strong>$1</strong>')
    .replace(/`(.+?)`/g, '<code style="background:#334155;padding:0.1em 0.3em;border-radius:3px;font-size:0.85em">$1</code>');
  text.innerHTML = formatted;

  const score = data.top_score;
  dot.className = 'confidence-dot' + (score < 0.3 ? ' low' : score < 0.5 ? ' mid' : '');
  conf.textContent = 'Confidence: ' + score.toFixed(3);

  // Sources
  const sourcesList = document.getElementById('sourcesList');
  sourcesList.classList.remove('visible');
  sourcesList.innerHTML = data.sources.map(s => {
    const icon = s.source_type === 'knowledge_base' ? '📄' : '🎫';
    return '<div class="source-item">' +
      '<div class="source-header">' +
        '<span class="source-name">' + icon + ' ' + s.source_title + '</span>' +
        '<span class="source-score">' + s.score.toFixed(3) + '</span>' +
      '</div>' +
      '<div class="source-type">[' + s.source_id + '] &bull; ' + s.source_type + '</div>' +
      '<div class="source-preview">' + escapeHtml(s.text.substring(0, 200)) + '...</div>' +
    '</div>';
  }).join('');

  document.getElementById('result').classList.add('visible');
}

function showError(msg) {
  const el = document.getElementById('error');
  el.textContent = msg;
  el.classList.add('visible');
}

function hideError() {
  document.getElementById('error').classList.remove('visible');
}

function escapeHtml(str) {
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}
</script>
</body>
</html>
"""

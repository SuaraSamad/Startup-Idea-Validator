"""Gradio application for startup idea validation."""

from __future__ import annotations

import time
from concurrent.futures import ThreadPoolExecutor

import gradio as gr

from crew import run_crew


APP_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

* {
  font-family: 'Inter', system-ui, sans-serif;
  box-sizing: border-box;
}

body, .gradio-container {
  background-color: #0D1117 !important;
  color: #E6EDF3 !important;
}

/* Header */
.app-header {
  text-align: center;
  padding: 48px 24px 32px;
  border-bottom: 1px solid #30363D;
  margin-bottom: 32px;
}

.app-title {
  font-size: 36px;
  font-weight: 700;
  color: #E6EDF3;
  margin-bottom: 10px;
  letter-spacing: -0.5px;
}

.app-title span {
  color: #00C896;
}

.app-subtitle {
  font-size: 15px;
  color: #8B949E;
  max-width: 520px;
  margin: 0 auto;
  line-height: 1.6;
}

/* Input area */
.input-card {
  background: #161B22 !important;
  border: 1px solid #30363D !important;
  border-radius: 16px;
  padding: 32px;
  width: min(90vw, 980px);
  min-width: 700px;
  margin: 0 auto 32px;
}

.input-card, .input-card > div, .input-card .gr-group {
  background: #161B22 !important;
  border: none !important;
  box-shadow: none !important;
  padding: 0 !important;
}

.input-label {
  font-size: 11px;
  font-weight: 600;
  color: #8B949E;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  margin-bottom: 12px;
  background: transparent !important;
}

/* Textbox */
textarea, input[type="text"] {
  background: #0D1117 !important;
  border: 1px solid #30363D !important;
  border-radius: 10px !important;
  color: #E6EDF3 !important;
  width: 100% !important;
  font-size: 15px !important;
  padding: 16px !important;
  transition: border-color 0.2s;
  resize: vertical;
  box-shadow: none !important;
}

textarea:focus, input[type="text"]:focus {
  border-color: #00C896 !important;
  outline: none !important;
  box-shadow: 0 0 0 3px rgba(0, 200, 150, 0.1) !important;
}

textarea::placeholder {
  color: #8B949E !important;
}

/* Validate button */
.validate-btn {
  background: #00C896 !important;
  color: #0D1117 !important;
  font-weight: 700 !important;
  font-size: 15px !important;
  border: none !important;
  border-radius: 10px !important;
  padding: 14px 32px !important;
  width: 100% !important;
  cursor: pointer !important;
  transition: background 0.2s, transform 0.1s !important;
  margin-top: 16px !important;
  letter-spacing: 0.02em !important;
}

.validate-btn:hover {
  background: #00A87E !important;
  transform: translateY(-1px) !important;
}

.validate-btn:active {
  transform: translateY(0px) !important;
}

.validate-btn:disabled {
  background: #30363D !important;
  color: #8B949E !important;
  cursor: not-allowed !important;
  transform: none !important;
}

/* Tabs */
.tab-nav {
  border-bottom: 1px solid #30363D !important;
  margin-bottom: 0 !important;
}

.tab-nav button {
  background: transparent !important;
  color: #8B949E !important;
  border: none !important;
  border-bottom: 2px solid transparent !important;
  padding: 12px 20px !important;
  font-size: 13px !important;
  font-weight: 500 !important;
  cursor: pointer !important;
  transition: color 0.2s, border-color 0.2s !important;
}

.tab-nav button:hover {
  color: #E6EDF3 !important;
}

.tab-nav button.selected {
  color: #00C896 !important;
  border-bottom-color: #00C896 !important;
}

/* Output cards */
.output-card {
  background: #161B22 !important;
  border: 1px solid #30363D !important;
  border-radius: 12px !important;
  padding: 28px !important;
  color: #E6EDF3 !important;
  font-size: 14px !important;
  line-height: 1.8 !important;
  min-height: 320px !important;
}

/* Status / loading message */
.status-msg {
  background: #161B22;
  border: 1px solid #00C89640;
  border-radius: 10px;
  padding: 14px 20px;
  color: #00C896;
  font-size: 13px;
  text-align: center;
  margin-bottom: 16px;
}

/* Footer */
.app-footer {
  text-align: center;
  padding: 32px 24px;
  border-top: 1px solid #30363D;
  margin-top: 48px;
  color: #8B949E;
  font-size: 12px;
  letter-spacing: 0.05em;
}

/* Scrollbar */
::-webkit-scrollbar {
  width: 6px;
}
::-webkit-scrollbar-track {
  background: #0D1117;
}
::-webkit-scrollbar-thumb {
  background: #30363D;
  border-radius: 3px;
}
::-webkit-scrollbar-thumb:hover {
  background: #00C896;
}
"""


def validate_idea(idea: str, progress=gr.Progress()):
    """Validate user idea and split crew output into tab-ready sections."""
    if not idea or not idea.strip():
        return "Please enter a startup idea.", "", "", ""

    try:
        progress_value = 0.05
        progress(progress_value, desc="Agents are working... 5%")
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(run_crew, idea.strip())
            while not future.done():
                time.sleep(1.5)
                progress_value = min(0.95, progress_value + 0.03)
                progress(
                    progress_value,
                    desc=f"Agents are working. This may take 30 to 60 seconds... {int(progress_value * 100)}%",
                )
            result = future.result()
        progress(1.0, desc="Validation report generated.")
        return (
            result["market_output"],
            result["competitor_output"],
            result["validation_output"],
            result["raw_output"],
        )
    except Exception as error:
        # Keep UI stable and informative if any external service fails.
        return f"Error: {str(error)}", "", "", ""


def disable_button():
    """Disable submit button while crew execution is running."""
    return gr.update(interactive=False)


def enable_button():
    """Re-enable submit button after crew execution finishes."""
    return gr.update(interactive=True)


def build_ui() -> gr.Blocks:
    """Create and return the Gradio UI."""
    with gr.Blocks(title="Startup Idea Validator") as demo:
        gr.HTML(
            """
            <div class="app-header">
                <div class="app-title">Startup Idea <span>Validator</span></div>
                <div class="app-subtitle">
                    Powered by CrewAI and OpenAI. Drop your idea and get a full AI-generated
                    validation report in seconds.
                </div>
            </div>
            """
        )

        with gr.Group(elem_classes=["input-card"]):
            gr.HTML('<div class="input-label">Your Startup Idea</div>')
            idea_input = gr.Textbox(
                placeholder="e.g. An app that connects freelance chefs with busy households in Lagos",
                lines=4,
                show_label=False,
                elem_classes=["idea-input"],
            )
            validate_button = gr.Button(
                "Validate My Idea",
                variant="primary",
                elem_classes=["validate-btn"],
            )

        with gr.Tabs(elem_classes=["tab-nav"]):
            with gr.Tab("Market Research"):
                market_output = gr.Markdown(elem_classes=["output-card"])
            with gr.Tab("Competitor Analysis"):
                competitor_output = gr.Markdown(elem_classes=["output-card"])
            with gr.Tab("Full Validation Report"):
                validation_output = gr.Markdown(elem_classes=["output-card"])
            with gr.Tab("Raw Output"):
                raw_output = gr.Textbox(lines=18, show_label=False, elem_classes=["output-card"])

        gr.HTML(
            """
            <div class="app-footer">
                Built with CrewAI · OpenAI · Gradio
            </div>
            """
        )

        validate_event = validate_button.click(
            fn=disable_button,
            inputs=None,
            outputs=[validate_button],
            queue=False,
        ).then(
            fn=validate_idea,
            inputs=[idea_input],
            outputs=[market_output, competitor_output, validation_output, raw_output],
            show_progress="full",
        )
        validate_event.then(
            fn=enable_button,
            inputs=None,
            outputs=[validate_button],
            queue=False,
        )

    return demo


if __name__ == "__main__":
    app = build_ui()
    app.queue(default_concurrency_limit=1)
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        show_error=True,
        theme=gr.themes.Base(),
        css=APP_CSS,
    )

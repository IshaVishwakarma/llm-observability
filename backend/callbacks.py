# backend/callbacks.py
import time
from langchain_core.callbacks import BaseCallbackHandler



class MetricsCallback(BaseCallbackHandler):
    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.prompt = None
        self.response_text = None
        self.tokens_in = 0
        self.tokens_out = 0
        self.error = None

    # LANGCHAIN 1.x — signature changed
    def on_llm_start(self, serialized, prompts, run_id, parent_run_id=None, tags=None, metadata=None, **kwargs):
        self.start_time = time.time()
        self.prompt = prompts[0] if prompts else None

    def on_llm_end(self, response, run_id, parent_run_id=None, tags=None, metadata=None, **kwargs):
        self.end_time = time.time()

        # extract text
        try:
            self.response_text = response.generations[0][0].text
        except Exception:
            self.response_text = getattr(response, "text", None) or str(response)

        # token usage extraction
        llm_output = getattr(response, "llm_output", {}) or {}
        token_usage = llm_output.get("token_usage", {}) if llm_output else {}

        self.tokens_in = token_usage.get("prompt_tokens", 0)
        self.tokens_out = token_usage.get("completion_tokens", 0)

    def on_llm_error(self, error, run_id, parent_run_id=None, tags=None, metadata=None, **kwargs):
        self.error = str(error)

    @property
    def latency(self):
        if self.start_time and self.end_time:
            return round((self.end_time - self.start_time) * 1000, 3)  # ms
        return None

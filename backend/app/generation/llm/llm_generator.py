from openai import OpenAI
import json
from app.core.config import settings


class LLMGenerator:

    def __init__(self) -> None:
        # Explicit timeout to prevent local Ollama calls from hanging indefinitely
        self.client = OpenAI(
            api_key=settings.LLM_API_KEY,
            base_url=settings.LLM_BASE_URL,
            timeout=35.0,
        )

    def _get_models_to_try(self) -> list[str]:
        models = [settings.LLM_MODEL]
        # Only fallback to openrouter/auto if using openrouter host
        if "openrouter.ai" in settings.LLM_BASE_URL:
            models.append("openrouter/auto")
        return models

    def generate_text(
        self,
        prompt: str,
    ) -> str:
        models_to_try = self._get_models_to_try()

        for model in models_to_try:
            try:
                response = self.client.chat.completions.create(
                    model=model,
                    messages=[
                        {
                            "role": "user",
                            "content": prompt,
                        }
                    ],
                    temperature=0.7,
                )
                if response and hasattr(response, "choices") and response.choices and len(response.choices) > 0:
                    choice = response.choices[0]
                    if hasattr(choice, "message") and choice.message and choice.message.content:
                        return choice.message.content.strip()
            except Exception as e:
                print(f"LLMGenerator model {model} failed: {e}")
                continue

        raise ValueError("LLM returned an empty or invalid response.")

    def generate_batch_text(
        self,
        prompt: str,
        count: int,
    ) -> list[str]:
        """Generate a batch of text values in a single LLM request to avoid per-row network overhead."""
        models_to_try = self._get_models_to_try()
        batch_prompt = (
            f"{prompt}\n\n"
            f"Generate EXACTLY {count} distinct realistic values. "
            f"Return ONLY a JSON array of strings without markdown formatting. Example: [\"value1\", \"value2\"]"
        )

        for model in models_to_try:
            try:
                response = self.client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": batch_prompt}],
                    temperature=0.7,
                )
                if response and response.choices and response.choices[0].message and response.choices[0].message.content:
                    raw = response.choices[0].message.content.strip()
                    if raw.startswith("```"):
                        raw = raw.split("\n", 1)[1].rsplit("```", 1)[0].strip()
                    parsed = json.loads(raw)
                    if isinstance(parsed, list):
                        return [str(item) for item in parsed]
            except Exception as e:
                print(f"Batch generation failed for model {model}: {e}")
                continue

        # Fall back to single generation calls if batch fails
        results = []
        for _ in range(count):
            try:
                results.append(self.generate_text(prompt))
            except Exception:
                break
        return results
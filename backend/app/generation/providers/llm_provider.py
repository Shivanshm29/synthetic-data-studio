from openai import OpenAI

from app.core.config import settings, get_reliable_models


class LLMGenerator:

    def __init__(self) -> None:
        self.client = OpenAI(
            api_key=settings.LLM_API_KEY,
            base_url=settings.LLM_BASE_URL,
            timeout=35.0,
        )

    def generate_text(
        self,
        prompt: str,
    ) -> str:
        models = get_reliable_models()
        for model in models:
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

                if response and hasattr(response, "choices") and response.choices:
                    content = response.choices[0].message.content
                    if content:
                        return content.strip()
            except Exception as err:
                print(f"Provider model {model} failed: {err}")
                continue

        raise ValueError("LLM returned no content or all candidate models failed.")

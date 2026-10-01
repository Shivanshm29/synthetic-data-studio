from openai import OpenAI

from app.core.config import settings


class LLMGenerator:

    def __init__(self) -> None:
        self.client = OpenAI(
            api_key=settings.LLM_API_KEY,
            base_url=settings.LLM_BASE_URL,
        )

    def generate_text(
        self,
        prompt: str,
    ) -> str:

        response = self.client.chat.completions.create(
            model=settings.LLM_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            temperature=0.7,
        )

        content = response.choices[0].message.content

        if content is None:
            raise ValueError("LLM returned no content.")

        return content.strip()
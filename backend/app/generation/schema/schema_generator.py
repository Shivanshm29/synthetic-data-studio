from openai import OpenAI

from app.core.config import settings
from app.domain.dataset import DatasetSpecification
from app.generation.schema.schema_prompt import SchemaPromptBuilder
from app.generation.schema.schema_response import SchemaResponse


import json


def _repair_json(content: str) -> str:
    content = content.strip()
    if content.startswith("```"):
        content = content.split("\n", 1)[1]
        content = content.rsplit("```", 1)[0]
        content = content.strip()

    try:
        json.loads(content)
        return content
    except Exception:
        pass

    idx = content.rfind("}")
    while idx != -1:
        candidate = content[: idx + 1]
        closing_variants = [
            '\n], "relationships": [], "metadata": {}}}',
            '\n], "metadata": {}}}',
            "\n]}}",
            "\n}",
        ]
        for closing in closing_variants:
            test_json = candidate + closing
            try:
                json.loads(test_json)
                return test_json
            except Exception:
                continue
        idx = content.rfind("}", 0, idx)

    return content


from app.rag.rag_engine import RAGEngine


class SchemaGenerator:
    def __init__(self):
        self.client = OpenAI(
            api_key=settings.LLM_API_KEY,
            base_url=settings.LLM_BASE_URL,
            timeout=45.0,
        )

        self.prompt_builder = SchemaPromptBuilder()
        self.rag_engine = RAGEngine.get_instance()

    def generate(
        self,
        prompt: str,
        rows: int | None = None,
    ) -> DatasetSpecification:

        print("[RAG] Retrieving production dataset templates from knowledge base...")
        rag_context = self.rag_engine.format_rag_context(prompt, top_k=2)
        if rag_context:
            print("[RAG] Injected production reference context into prompt.")

        print("1. Building prompt with RAG context")

        messages = self.prompt_builder.build(
            prompt=prompt,
            rows=rows,
            rag_context=rag_context,
        )

        models_to_try = [settings.LLM_MODEL]
        if "openrouter.ai" in settings.LLM_BASE_URL:
            models_to_try.append("openrouter/auto")

        schema_obj = None
        for model in models_to_try:
            try:
                print(f"Calling LLM ({model})")
                kwargs = {
                    "model": model,
                    "messages": messages,
                    "temperature": 0,
                    "max_tokens": 4000,
                }
                # Only pass response_format if not using local Ollama or if model supports it
                if "11434" not in settings.LLM_BASE_URL:
                    kwargs["response_format"] = {"type": "json_object"}

                try:
                    response = self.client.chat.completions.create(**kwargs)
                except Exception as rf_err:
                    # Retry without response_format if API endpoint rejected it
                    if "response_format" in kwargs:
                        del kwargs["response_format"]
                        response = self.client.chat.completions.create(**kwargs)
                    else:
                        raise rf_err

                if response and hasattr(response, "choices") and response.choices and response.choices[0].message and response.choices[0].message.content:
                    content = response.choices[0].message.content.strip()
                    content = _repair_json(content)

                    print("=" * 80)
                    print(f"RAW RESPONSE ({model})")
                    print(content[:500] + ("..." if len(content) > 500 else ""))
                    print("=" * 80)

                    schema_obj = SchemaResponse.model_validate_json(content)
                    if schema_obj:
                        print("Schema validated successfully!")
                        break
            except Exception as e:
                print(f"Model {model} failed: {e}")
                continue

        if not schema_obj:
            raise ValueError("All schema generation LLM models failed or returned incomplete JSON.")

        return schema_obj.dataset
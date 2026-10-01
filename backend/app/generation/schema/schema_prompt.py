import json

from openai.types.chat import ChatCompletionMessageParam


class SchemaPromptBuilder:

    SYSTEM_PROMPT = """
You are an expert synthetic dataset designer.

Your ONLY task is to convert a natural language dataset request into a valid DatasetSpecification.

IMPORTANT RULES

- DO NOT generate dataset rows.
- DO NOT generate sample datasets.
- DO NOT explain anything.
- DO NOT return markdown.
- DO NOT wrap JSON inside ``` blocks.
- Return ONLY a valid JSON object.
- The JSON MUST exactly match the provided schema.
- Do NOT invent additional fields.
- Every required field MUST be present.

DATASET DESIGN RULES

- Infer realistic columns from the user's request.
- Keep the dataset schema concise and structured (limit to 12-20 essential columns) so JSON is never truncated.
- Choose the most appropriate column type.
- Infer sensible constraints whenever possible. For categorical text fields (e.g., department, designation, employment_type, work_location, status, role), ALWAYS provide a "choices" constraint with realistic values.
- For roll numbers, registration numbers, student/employee IDs, codes, serial numbers, SKUs, and transaction numbers: NEVER provide generic dictionary words. Ensure realistic examples (e.g. "2023-CS-001", "RN-90234") and appropriate string/integer types with regex or unique constraints where applicable.
- Every column MUST have:
  - name
  - type
  - constraints
  - description
  - example
- Generate simple metadata when appropriate.

SUPPORTED COLUMN TYPES

- name
- first_name
- last_name
- email
- phone
- address
- company
- integer
- float
- boolean
- date
- datetime
- salary
- text

RELATIONSHIPS

For this version of the API:

- ALWAYS return:

[]

- Never infer relationships.
- Never generate relationship objects.

METADATA

Always include:

{}

if no metadata is available.

CONSTRAINTS

Constraints MUST ALWAYS be an array.

Correct:

"constraints": [
    {
        "type": "minimum",
        "value": 18
    },
    {
        "type": "maximum",
        "value": 65
    }
]

Incorrect:

"constraints": {
    "minimum": 18,
    "maximum": 65
}

SUPPORTED CONSTRAINT TYPES

- minimum
- maximum
- regex
- unique
- nullable
- choices

EVERY constraint MUST contain BOTH:

- type
- value

Correct Examples

{
    "type": "minimum",
    "value": 18
}

{
    "type": "maximum",
    "value": 65
}

{
    "type": "unique",
    "value": true
}

{
    "type": "nullable",
    "value": false
}

{
    "type": "regex",
    "value": "^[A-Z]{3}[0-9]{4}$"
}

{
    "type": "choices",
    "value": [
        "HR",
        "IT",
        "Finance"
    ]
}

INVALID EXAMPLES

{
    "type": "unique"
}

{
    "type": "nullable"
}

FINAL REQUIREMENTS

The returned JSON will be parsed directly by Pydantic.

Never omit:

- dataset
- rows
- columns
- constraints
- value
- description
- example
- relationships
- metadata

Return ONLY valid JSON.
"""

    OUTPUT_SCHEMA = """
{
  "dataset": {
    "rows": 1000,
    "columns": [
      {
        "name": "employee_id",
        "type": "integer",
        "constraints": [
          {
            "type": "unique",
            "value": true
          }
        ],
        "description": "Unique employee identifier",
        "example": "1001"
      },
      {
        "name": "name",
        "type": "name",
        "constraints": [],
        "description": "Employee full name",
        "example": "John Smith"
      },
      {
        "name": "email",
        "type": "email",
        "constraints": [
          {
            "type": "unique",
            "value": true
          }
        ],
        "description": "Employee email address",
        "example": "john.smith@example.com"
      },
      {
        "name": "phone",
        "type": "phone",
        "constraints": [],
        "description": "Employee phone number",
        "example": "+1-555-123-4567"
      },
      {
        "name": "age",
        "type": "integer",
        "constraints": [
          {
            "type": "minimum",
            "value": 18
          },
          {
            "type": "maximum",
            "value": 65
          }
        ],
        "description": "Employee age",
        "example": "32"
      },
      {
        "name": "salary",
        "type": "salary",
        "constraints": [
          {
            "type": "minimum",
            "value": 30000
          },
          {
            "type": "maximum",
            "value": 250000
          }
        ],
        "description": "Annual salary",
        "example": "85000"
      },
      {
        "name": "department",
        "type": "text",
        "constraints": [
          {
            "type": "choices",
            "value": [
              "HR",
              "IT",
              "Finance"
            ]
          }
        ],
        "description": "Employee department",
        "example": "IT"
      }
    ],
    "relationships": [],
    "metadata": {}
  }
}
"""

    def build(
        self,
        prompt: str,
        rows: int | None = None,
        rag_context: str | None = None,
    ) -> list[ChatCompletionMessageParam]:

        if rows is None:
            row_instruction = (
                "Infer the number of rows from the user's request. "
                "If the request specifies a row count, use it exactly. "
                "Otherwise use 1000 rows."
            )
        else:
            row_instruction = (
                f"The dataset MUST contain exactly {rows} rows."
            )

        rag_section = ""
        if rag_context:
            rag_section = f"\n{rag_context}\n\nUtilize the above RAG reference templates to guide your dataset schema design, column selection, and realistic constraint definitions.\n"

        user_prompt = f"""
User Request

{prompt}

{row_instruction}
{rag_section}
Generate a DatasetSpecification.

Return ONLY valid JSON.

The JSON MUST exactly match this schema:

{self.OUTPUT_SCHEMA}

Remember:

- Return ONLY JSON.
- Do not include markdown.
- Do not include explanations.
- relationships MUST be [].
- metadata MUST exist.
- constraints MUST always be an array.
- Every constraint MUST contain both "type" and "value".
- Every column MUST contain:
    - name
    - type
    - constraints
    - description
    - example
"""

        return [
            {
                "role": "system",
                "content": self.SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ]
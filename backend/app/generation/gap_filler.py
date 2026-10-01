from app.generation.orchestrator import GenerationOrchestrator


class GapFiller:
    """Fills missing columns in fetched datasets using synthetic generation."""

    def __init__(self, orchestrator: GenerationOrchestrator, schema_generator):
        self._orchestrator = orchestrator
        self._schema_generator = schema_generator

    def fill_gaps(
        self,
        prompt: str,
        existing_rows: list[dict],
        missing_columns: list[str],
    ) -> list[dict]:
        """Generate ONLY missing columns for existing rows."""
        if not missing_columns or not existing_rows:
            return existing_rows

        # 1. Generate full schema from prompt
        spec = self._schema_generator.generate(prompt)
        # Override row count to match existing data
        spec.rows = len(existing_rows)

        # 2. Use orchestrator to generate only missing columns
        return self._orchestrator.generate_missing(spec, existing_rows, missing_columns)

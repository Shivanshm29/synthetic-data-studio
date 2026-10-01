import csv
import io
import json
from pydantic import BaseModel, Field


class ColumnProfile(BaseModel):
    name: str
    dtype: str
    missing_count: int
    missing_percentage: float
    unique_count: int
    sample_values: list[str]
    is_primary_key_candidate: bool


class DatasetProfileReport(BaseModel):
    file_name: str
    total_rows: int
    total_columns: int
    column_profiles: list[ColumnProfile]
    data_quality_score: float = Field(..., ge=0.0, le=1.0)
    primary_keys: list[str]
    summary: str


class DatasetProfiler:

    @staticmethod
    def profile_file(filename: str, content: bytes) -> DatasetProfileReport:
        lines: list[dict[str, str]] = []
        text = content.decode("utf-8", errors="ignore")

        if filename.endswith(".json") or filename.endswith(".jsonl"):
            try:
                parsed = json.loads(text)
                if isinstance(parsed, list):
                    lines = [dict(item) for item in parsed if isinstance(item, dict)]
            except Exception:
                for l in text.splitlines():
                    if l.strip():
                        try:
                            item = json.loads(l)
                            if isinstance(item, dict):
                                lines.append(item)
                        except Exception:
                            continue
        else:
            # Default CSV / TSV parser
            reader = csv.DictReader(io.StringIO(text))
            for i, row in enumerate(reader):
                if i >= 5000:
                    break
                lines.append(row)

        total_rows = len(lines)
        if total_rows == 0:
            return DatasetProfileReport(
                file_name=filename,
                total_rows=0,
                total_columns=0,
                column_profiles=[],
                data_quality_score=0.0,
                primary_keys=[],
                summary="Empty dataset file provided.",
            )

        headers = list(lines[0].keys())
        total_cols = len(headers)
        col_profiles: list[ColumnProfile] = []
        pk_candidates: list[str] = []
        total_missing = 0

        for col in headers:
            vals = [str(row.get(col, "")).strip() for row in lines]
            missing_c = sum(1 for v in vals if v in ("", "null", "none", "nan", "undefined", "n/a"))
            total_missing += missing_c
            missing_pct = round((missing_c / max(1, total_rows)) * 100, 2)
            unique_set = {v for v in vals if v not in ("", "null", "none", "nan")}
            unique_c = len(unique_set)

            # Check data type
            sample_non_empty = [v for v in vals if v not in ("", "null", "none")][:20]
            dtype = "string"
            if sample_non_empty:
                if all(v.isdigit() or (v.startswith("-") and v[1:].isdigit()) for v in sample_non_empty):
                    dtype = "integer"
                elif all(v.replace(".", "", 1).isdigit() for v in sample_non_empty):
                    dtype = "float"
                elif all(v.lower() in ("true", "false", "0", "1") for v in sample_non_empty):
                    dtype = "boolean"

            is_pk = (unique_c == total_rows) and (missing_c == 0) and (total_rows > 0)
            if is_pk:
                pk_candidates.append(col)

            samples = list(unique_set)[:4]

            col_profiles.append(
                ColumnProfile(
                    name=col,
                    dtype=dtype,
                    missing_count=missing_c,
                    missing_percentage=missing_pct,
                    unique_count=unique_c,
                    sample_values=samples,
                    is_primary_key_candidate=is_pk,
                )
            )

        total_cells = total_rows * total_cols
        completeness = 1.0 - (total_missing / max(1, total_cells))
        quality_score = round(max(0.0, min(1.0, completeness * 0.95 + 0.05)), 2)

        return DatasetProfileReport(
            file_name=filename,
            total_rows=total_rows,
            total_columns=total_cols,
            column_profiles=col_profiles,
            data_quality_score=quality_score,
            primary_keys=pk_candidates,
            summary=f"Profiled {total_rows:,} rows across {total_cols} columns. Data completeness: {round(completeness*100, 1)}%.",
        )

import urllib.parse
import httpx
from app.core.config import settings
from app.datascout.datascout_schema import ExistingDataset


def search_huggingface_datasets(query: str, limit: int = 4) -> list[ExistingDataset]:
    """Search Hugging Face Hub Datasets API live in real-time."""
    if not query.strip():
        return []

    encoded_query = urllib.parse.quote(query.strip())
    url = f"https://huggingface.co/api/datasets?search={encoded_query}&limit={limit}&full=true"

    headers = {"User-Agent": "SyntheticDataStudio/1.0"}
    if settings.HF_TOKEN:
        headers["Authorization"] = f"Bearer {settings.HF_TOKEN}"

    results: list[ExistingDataset] = []
    try:
        with httpx.Client(timeout=8.0) as client:
            resp = client.get(url, headers=headers)
            if resp.status_code == 200:
                data = resp.json()
                for item in data:
                    ds_id = item.get("id") or item.get("_id")
                    if not ds_id:
                        continue
                    name = item.get("id", ds_id)
                    description = item.get("description") or f"Hugging Face public dataset: {name}"
                    downloads = item.get("downloads", 0)
                    likes = item.get("likes", 0)
                    tags = item.get("tags", [])
                    license_str = "Open / Community"
                    for tag in tags:
                        if tag.startswith("license:"):
                            license_str = tag.split("license:", 1)[1].upper()
                            break

                    dataset_url = f"https://huggingface.co/datasets/{name}"
                    quality_score = min(0.99, max(0.70, 0.80 + (downloads / 50000.0) * 0.15))
                    similarity_score = 0.90

                    results.append(
                        ExistingDataset(
                            name=f"HF: {name}",
                            description=description[:250] + ("..." if len(description) > 250 else ""),
                            estimated_rows=downloads if downloads > 1000 else 10000,
                            estimated_columns=len(tags) if len(tags) > 3 else 8,
                            license=license_str,
                            format="Parquet / Arrow / JSON",
                            download_source=dataset_url,
                            quality_score=round(quality_score, 2),
                            similarity_score=similarity_score,
                            advantages=[f"{downloads:,} downloads", f"{likes} likes on HF Hub"],
                            limitations=["Requires datasets library or HF API loading"],
                            source_platform="huggingface",
                            dataset_id=name,
                        )
                    )
    except Exception as err:
        print(f"Hugging Face search API error: {err}")

    return results

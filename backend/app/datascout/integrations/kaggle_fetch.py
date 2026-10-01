import io
import csv
import zipfile
import httpx
from typing import Any
from app.core.config import settings
from app.datascout.datascout_schema import FetchResult

def fetch_kaggle_preview(dataset_ref: str) -> FetchResult:
    if not settings.KAGGLE_API_TOKEN:
        return FetchResult(
            requires_auth=True,
            dataset_name=dataset_ref,
            source_platform="kaggle"
        )
        
    headers = {
        "User-Agent": "SyntheticDataStudio/1.0",
        "Authorization": f"Bearer {settings.KAGGLE_API_TOKEN}"
    }
    
    url = f"https://www.kaggle.com/api/v1/datasets/download/{dataset_ref}"
    
    try:
        with httpx.Client(timeout=30.0, headers=headers, follow_redirects=True) as client:
            resp = client.get(url)
            if resp.status_code != 200:
                return FetchResult(source_platform="kaggle", dataset_name=dataset_ref)
                
            # It's a zip file
            zip_content = io.BytesIO(resp.content)
            
            with zipfile.ZipFile(zip_content) as z:
                # Find first CSV
                csv_filename = next((name for name in z.namelist() if name.lower().endswith(".csv")), None)
                if not csv_filename:
                    return FetchResult(source_platform="kaggle", dataset_name=dataset_ref)
                    
                with z.open(csv_filename) as f:
                    content = f.read().decode("utf-8", errors="replace")
                    
                # Parse CSV
                csv_file = io.StringIO(content)
                reader = csv.DictReader(csv_file)
                
                rows = []
                for idx, row in enumerate(reader):
                    if idx >= 100:
                        break
                    rows.append(dict(row))
                    
                columns = []
                if rows:
                    columns = list(rows[0].keys())
                    
                return FetchResult(
                    rows=rows,
                    count=len(rows),
                    columns=columns,
                    source_platform="kaggle",
                    dataset_name=dataset_ref,
                    truncated=True
                )
                
    except Exception as e:
        print(f"Error fetching Kaggle preview: {e}")
        return FetchResult(source_platform="kaggle", dataset_name=dataset_ref)


def fetch_kaggle_full(dataset_ref: str, max_rows: int = 1000) -> FetchResult:
    if not settings.KAGGLE_API_TOKEN:
        return FetchResult(
            requires_auth=True,
            dataset_name=dataset_ref,
            source_platform="kaggle"
        )
        
    headers = {
        "User-Agent": "SyntheticDataStudio/1.0",
        "Authorization": f"Bearer {settings.KAGGLE_API_TOKEN}"
    }
    
    url = f"https://www.kaggle.com/api/v1/datasets/download/{dataset_ref}"
    
    try:
        with httpx.Client(timeout=60.0, headers=headers, follow_redirects=True) as client:
            resp = client.get(url)
            if resp.status_code != 200:
                return FetchResult(source_platform="kaggle", dataset_name=dataset_ref)
                
            zip_content = io.BytesIO(resp.content)
            
            with zipfile.ZipFile(zip_content) as z:
                csv_filename = next((name for name in z.namelist() if name.lower().endswith(".csv")), None)
                if not csv_filename:
                    return FetchResult(source_platform="kaggle", dataset_name=dataset_ref)
                    
                with z.open(csv_filename) as f:
                    content = f.read().decode("utf-8", errors="replace")
                    
                csv_file = io.StringIO(content)
                reader = csv.DictReader(csv_file)
                
                rows = []
                total_lines = 0
                for row in reader:
                    if total_lines < max_rows:
                        rows.append(dict(row))
                    total_lines += 1
                    
                columns = []
                if rows:
                    columns = list(rows[0].keys())
                    
                return FetchResult(
                    rows=rows,
                    count=len(rows),
                    columns=columns,
                    source_platform="kaggle",
                    dataset_name=dataset_ref,
                    truncated=total_lines > max_rows,
                    total_available=total_lines
                )
                
    except Exception as e:
        print(f"Error fetching Kaggle full: {e}")
        return FetchResult(source_platform="kaggle", dataset_name=dataset_ref)

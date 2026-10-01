import httpx
from typing import Any
from app.core.config import settings
from app.datascout.datascout_schema import FetchResult

def fetch_hf_preview(dataset_id: str) -> FetchResult:
    headers = {"User-Agent": "SyntheticDataStudio/1.0"}
    if settings.HF_TOKEN:
        headers["Authorization"] = f"Bearer {settings.HF_TOKEN}"
        
    try:
        with httpx.Client(timeout=10.0, headers=headers) as client:
            # 1. Get splits
            splits_url = f"https://datasets-server.huggingface.co/splits?dataset={dataset_id}"
            splits_resp = client.get(splits_url)
            if splits_resp.status_code != 200:
                return FetchResult()
                
            splits_data = splits_resp.json()
            if "splits" not in splits_data or not splits_data["splits"]:
                return FetchResult()
                
            first_split = splits_data["splits"][0]
            config = first_split.get("config", "default")
            split = first_split.get("split", "train")
            
            # 2. Get first rows
            rows_url = f"https://datasets-server.huggingface.co/first-rows?dataset={dataset_id}&config={config}&split={split}"
            rows_resp = client.get(rows_url)
            
            if rows_resp.status_code != 200:
                return FetchResult()
                
            rows_data = rows_resp.json()
            raw_rows = rows_data.get("rows", [])
            
            parsed_rows = []
            columns = []
            
            if raw_rows:
                for row_item in raw_rows:
                    parsed_rows.append(row_item.get("row", {}))
                
                if parsed_rows:
                    columns = list(parsed_rows[0].keys())
                    
            return FetchResult(
                rows=parsed_rows,
                count=len(parsed_rows),
                columns=columns,
                source_platform="huggingface",
                dataset_name=dataset_id,
                truncated=True
            )
            
    except Exception as e:
        print(f"Error fetching HF preview: {e}")
        return FetchResult()

def fetch_hf_full(dataset_id: str, max_rows: int = 1000) -> FetchResult:
    headers = {"User-Agent": "SyntheticDataStudio/1.0"}
    if settings.HF_TOKEN:
        headers["Authorization"] = f"Bearer {settings.HF_TOKEN}"
        
    try:
        with httpx.Client(timeout=30.0, headers=headers) as client:
            # 1. Get splits
            splits_url = f"https://datasets-server.huggingface.co/splits?dataset={dataset_id}"
            splits_resp = client.get(splits_url)
            if splits_resp.status_code != 200:
                return FetchResult()
                
            splits_data = splits_resp.json()
            if "splits" not in splits_data or not splits_data["splits"]:
                return FetchResult()
                
            first_split = splits_data["splits"][0]
            config = first_split.get("config", "default")
            split = first_split.get("split", "train")
            
            # 2. Get size
            size_url = f"https://datasets-server.huggingface.co/size?dataset={dataset_id}"
            size_resp = client.get(size_url)
            total_available = 0
            if size_resp.status_code == 200:
                size_data = size_resp.json()
                size_info = size_data.get("size", {})
                split_info = size_info.get("splits", [])
                for sp in split_info:
                    if sp.get("config") == config and sp.get("split") == split:
                        total_available = sp.get("num_rows", 0)
                        break
                        
            # 3. Paginate rows
            parsed_rows = []
            columns = []
            offset = 0
            
            while offset < max_rows:
                limit = min(100, max_rows - offset)
                rows_url = f"https://datasets-server.huggingface.co/rows?dataset={dataset_id}&config={config}&split={split}&offset={offset}&length={limit}"
                rows_resp = client.get(rows_url)
                
                if rows_resp.status_code != 200:
                    break
                    
                rows_data = rows_resp.json()
                raw_rows = rows_data.get("rows", [])
                
                if not raw_rows:
                    break
                    
                for row_item in raw_rows:
                    parsed_rows.append(row_item.get("row", {}))
                    
                if not columns and parsed_rows:
                    columns = list(parsed_rows[0].keys())
                    
                offset += len(raw_rows)
                
                if len(raw_rows) < limit:
                    break
                    
            return FetchResult(
                rows=parsed_rows,
                count=len(parsed_rows),
                columns=columns,
                source_platform="huggingface",
                dataset_name=dataset_id,
                truncated=(total_available > len(parsed_rows)) if total_available else False,
                total_available=total_available
            )
            
    except Exception as e:
        print(f"Error fetching HF full: {e}")
        return FetchResult()

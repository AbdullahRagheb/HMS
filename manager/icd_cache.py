from pathlib import Path
import pandas as pd # type: ignore

_ICD_PATH = (
    Path(__file__).resolve().parent.parent          # project root
    / "core" / "static" / "icd" / "icd11.xlsx"
)   # adjust if csv
_df = pd.read_excel(_ICD_PATH, engine="openpyxl", dtype=str).fillna("")

# keep only what you need for the UI
_df = _df.rename(columns={
    "Code":    "code",
    "Title":   "title",
    "Arabic":  "title_ar",
})
# For quick “starts‑with” look‑ups make an all‑caps helper column
_df["code_upper"]  = _df["code"].str.upper()
_df["title_upper"] = _df["title"].str.upper()

def search(q: str, limit: int = 12) -> list[dict]:
    """Return at most *limit* dicts {code, title} whose code OR title starts with *q*"""
    q = q.strip().upper()
    if not q:
        return []
    mask = (_df["code_upper"].str.startswith(q)) | (_df["title_upper"].str.startswith(q))
    hits = _df[mask].head(limit)
    return hits[["code", "title"]].to_dict(orient="records")
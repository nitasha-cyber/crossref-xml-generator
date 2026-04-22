from io import BytesIO
import pandas as pd


REQUIRED_COLUMNS = ["content_type", "title", "doi", "publication_year"]


def parse_excel_file(content: bytes) -> list[dict]:
    df = pd.read_excel(BytesIO(content), engine="openpyxl")
    df.columns = [str(c).strip() for c in df.columns]

    if df.empty:
        return []

    for col in REQUIRED_COLUMNS:
        if col not in df.columns:
            df[col] = None

    records = []
    for row in df.fillna("").to_dict(orient="records"):
        normalized = {k: (v.strip() if isinstance(v, str) else v) for k, v in row.items()}
        records.append(normalized)
    return records

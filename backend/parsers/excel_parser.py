from io import BytesIO
import pandas as pd


REQUIRED_COLUMNS = ["content_type", "title", "doi", "publication_year"]
ALLOWED_CONTENT_TYPES = {"book", "journal", "report", "proceeding", "posted_content"}
COLUMN_ALIASES = {
    "abstract": "abstract",
    "license": "license_url",
    "license_url": "license_url",
}
CONTENT_TYPE_ALIASES = {
    "journal article": "journal",
    "journal_article": "journal",
    "report / working paper": "report",
    "report/working paper": "report",
    "conference proceeding": "proceeding",
    "posted content": "posted_content",
}


def _normalize_column_name(name: str) -> str:
    key = str(name).strip()
    lowered = key.lower()
    return COLUMN_ALIASES.get(lowered, lowered)


def _normalize_content_type(value: str) -> str:
    normalized = str(value).strip().lower().replace("-", "_")
    normalized = CONTENT_TYPE_ALIASES.get(normalized, normalized)
    return normalized


def parse_excel_file(content: bytes) -> list[dict]:
    df = pd.read_excel(BytesIO(content), engine="openpyxl")
    df.columns = [_normalize_column_name(c) for c in df.columns]

    if df.empty:
        return []

    missing_columns = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing_columns:
        missing = ", ".join(missing_columns)
        raise ValueError(f"Missing required Excel column(s): {missing}")

    records = []
    errors = []
    for index, row in enumerate(df.fillna("").to_dict(orient="records"), start=2):
        normalized = {k: (v.strip() if isinstance(v, str) else v) for k, v in row.items()}
        if not any(str(v).strip() for v in normalized.values()):
            continue

        missing_fields = [field for field in REQUIRED_COLUMNS if str(normalized.get(field, "")).strip() == ""]
        if missing_fields:
            errors.append(f"Row {index}: missing required value(s): {', '.join(missing_fields)}")
            continue

        normalized["content_type"] = _normalize_content_type(normalized["content_type"])
        if normalized["content_type"] not in ALLOWED_CONTENT_TYPES:
            allowed = ", ".join(sorted(ALLOWED_CONTENT_TYPES))
            errors.append(
                f"Row {index}: invalid content_type '{row.get('content_type')}'. "
                f"Use one of: {allowed}"
            )
            continue

        year = str(normalized["publication_year"]).strip()
        if year.endswith(".0"):
            year = year[:-2]
        if not year.isdigit():
            errors.append(f"Row {index}: publication_year must be a 4-digit year")
            continue
        normalized["publication_year"] = int(year)

        records.append(normalized)

    if errors:
        raise ValueError("; ".join(errors))
    return records

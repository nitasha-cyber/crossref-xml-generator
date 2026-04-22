import re

DOI_REGEX = re.compile(r"^10\.\d{4,9}/[-._;()/:A-Z0-9]+$", re.IGNORECASE)
ORCID_REGEX = re.compile(r"^\d{4}-\d{4}-\d{4}-\d{3}[\dX]$")


def is_valid_doi(value: str) -> bool:
    return bool(value and DOI_REGEX.match(value.strip()))


def is_valid_orcid(value: str) -> bool:
    return bool(value and ORCID_REGEX.match(value.strip()))

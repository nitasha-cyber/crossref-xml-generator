# CrossRef XML Generator

Waikato University Library web application for generating CrossRef XML from Excel metadata or manual data entry.

## Features

- Upload and parse Excel (`.xlsx`/`.xls`) files
- Preview parsed rows in a selectable table
- Add metadata manually for all supported content types
- Generate CrossRef XML preview in real time
- Download XML for one entry or ZIP batch for multiple entries

## Supported Content Types

Primary:
- Book
- Journal article
- Report / working paper

Secondary:
- Conference proceeding
- Posted content

## Project Structure

```text
crossref-xml-generator/
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   ├── config.py
│   ├── models/
│   ├── generators/
│   ├── parsers/
│   └── utils/
├── frontend/
│   ├── index.html
│   ├── css/style.css
│   └── js/app.js
├── templates/
│   └── sample_template.xlsx
├── README.md
└── .gitignore
```

## Run Locally

```bash
cd /home/runner/work/crossref-xml-generator/crossref-xml-generator
pip install -r backend/requirements.txt
cd backend
python main.py
```

Open: `http://localhost:8000`

## Excel Template Columns

Required columns:
- `content_type`
- `title`
- `doi`
- `publication_year`

Optional columns include: `author`, `orcid`, `abstract`, `license_url`, `publisher`, `isbn`, `journal_title`, `issn`, `volume`, `issue`, `first_page`, `last_page`, `institution`, `report_number`, `conference_name`, `conference_location`, `posted_content_type`.

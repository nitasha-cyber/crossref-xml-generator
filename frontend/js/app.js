const uploadBtn = document.getElementById('uploadBtn');
const generateBtn = document.getElementById('generateBtn');
const downloadBtn = document.getElementById('downloadBtn');
const fileInput = document.getElementById('excelFile');
const uploadStatus = document.getElementById('uploadStatus');
const genStatus = document.getElementById('genStatus');
const xmlPreview = document.getElementById('xmlPreview');
const previewTable = document.getElementById('previewTable');
const manualForm = document.getElementById('manualForm');

let parsedRows = [];
let latestPayload = null;
const REQUIRED_FIELDS = ['content_type', 'title', 'doi', 'publication_year'];
const ALLOWED_CONTENT_TYPES = ['book', 'journal', 'report', 'proceeding', 'posted_content'];
const MANUAL_DATA_FIELDS = ['title', 'doi', 'publication_year', 'author', 'orcid', 'license_url', 'abstract'];

function formatApiError(detail, fallback) {
  if (!detail) return fallback;
  if (typeof detail === 'string') return detail;
  if (Array.isArray(detail)) {
    return detail.map((item) => item?.msg || JSON.stringify(item)).join('; ');
  }
  if (typeof detail === 'object') return detail.message || JSON.stringify(detail);
  return String(detail);
}

function cleanRecord(record) {
  const output = {};
  Object.entries(record).forEach(([k, v]) => {
    if (v !== undefined && v !== null && String(v).trim() !== '') output[k] = typeof v === 'string' ? v.trim() : v;
  });
  return output;
}

function renderTable(rows) {
  const thead = previewTable.querySelector('thead');
  const tbody = previewTable.querySelector('tbody');
  thead.innerHTML = '';
  tbody.innerHTML = '';

  if (!rows.length) {
    thead.innerHTML = '<tr><th>No data</th></tr>';
    return;
  }

  const columns = Array.from(new Set(rows.flatMap(r => Object.keys(r))));
  const headerCells = ['<th>Select</th>', ...columns.map(c => `<th>${c}</th>`)].join('');
  thead.innerHTML = `<tr>${headerCells}</tr>`;

  rows.forEach((row, idx) => {
    const cells = columns.map(c => `<td>${row[c] ?? ''}</td>`).join('');
    tbody.innerHTML += `<tr><td><input type="checkbox" data-row-index="${idx}" /></td>${cells}</tr>`;
  });
}

uploadBtn.addEventListener('click', async () => {
  const file = fileInput.files?.[0];
  if (!file) {
    uploadStatus.textContent = 'Please choose an Excel file.';
    return;
  }

  const formData = new FormData();
  formData.append('file', file);
  uploadStatus.textContent = 'Uploading...';

  try {
    const res = await fetch('/api/upload-excel', { method: 'POST', body: formData });
    const data = await res.json();
    if (!res.ok) throw new Error(formatApiError(data.detail, 'Upload failed'));
    parsedRows = data.rows || [];
    renderTable(parsedRows);
    uploadStatus.textContent = `Loaded ${data.count} rows.`;
  } catch (err) {
    uploadStatus.textContent = err.message;
  }
});

function validateEntry(entry, rowLabel) {
  const maxYear = new Date().getUTCFullYear() + 1;
  const missing = REQUIRED_FIELDS.filter((field) => String(entry[field] ?? '').trim() === '');
  if (missing.length) return `${rowLabel}: missing required fields (${missing.join(', ')})`;

  if (!ALLOWED_CONTENT_TYPES.includes(String(entry.content_type))) {
    return `${rowLabel}: invalid content_type "${entry.content_type}". Use one of: ${ALLOWED_CONTENT_TYPES.join(', ')}`;
  }

  const year = String(entry.publication_year);
  if (!/^\d{4}$/.test(year)) {
    return `${rowLabel}: publication_year must be a 4-digit year`;
  }
  const yearValue = Number(year);
  if (yearValue < 1000 || yearValue > maxYear) {
    return `${rowLabel}: publication_year must be between 1000 and ${maxYear}`;
  }

  return null;
}

function collectEntries() {
  const errors = [];
  const selected = Array.from(document.querySelectorAll('input[data-row-index]:checked'))
    .map((cb) => ({ rowIndex: Number(cb.dataset.rowIndex), row: cleanRecord(parsedRows[Number(cb.dataset.rowIndex)]) }))
    .map(({ rowIndex, row }) => {
      const issue = validateEntry(row, `Excel row ${rowIndex + 2}`);
      if (issue) {
        errors.push(issue);
        return null;
      }
      row.publication_year = Number(row.publication_year);
      return row;
    })
    .filter(Boolean);

  const formData = Object.fromEntries(new FormData(manualForm).entries());
  const manual = cleanRecord(formData);
  const hasManualContent = MANUAL_DATA_FIELDS.some((field) => String(manual[field] ?? '').trim() !== '');
  if (hasManualContent) {
    const manualIssue = validateEntry(manual, 'Manual entry');
    if (manualIssue) {
      errors.push(manualIssue);
    } else {
      manual.publication_year = Number(manual.publication_year);
      selected.push(manual);
    }
  }

  return { entries: selected, errors };
}

generateBtn.addEventListener('click', async () => {
  const { entries, errors } = collectEntries();
  if (errors.length) {
    genStatus.textContent = errors.join(' | ');
    downloadBtn.disabled = true;
    return;
  }
  if (!entries.length) {
    genStatus.textContent = 'Select Excel rows and/or fill one manual entry first.';
    return;
  }

  latestPayload = { entries };
  genStatus.textContent = 'Generating XML...';

  try {
    const res = await fetch('/api/generate-xml', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(latestPayload),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(formatApiError(data.detail, 'XML generation failed'));

    xmlPreview.textContent = data.xml;
    genStatus.textContent = `Generated XML for ${data.count} entr${data.count === 1 ? 'y' : 'ies'}.`;
    downloadBtn.disabled = false;
  } catch (err) {
    genStatus.textContent = err.message;
    downloadBtn.disabled = true;
  }
});

downloadBtn.addEventListener('click', async () => {
  if (!latestPayload) return;

  try {
    const res = await fetch('/api/download-xml', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(latestPayload),
    });

    if (!res.ok) {
      const data = await res.json();
      throw new Error(formatApiError(data.detail, 'Download failed'));
    }

    const disposition = res.headers.get('Content-Disposition') || '';
    const match = disposition.match(/filename=([^;]+)/i);
    const filename = match ? match[1] : 'crossref.xml';
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);

    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
  } catch (err) {
    genStatus.textContent = err.message;
  }
});

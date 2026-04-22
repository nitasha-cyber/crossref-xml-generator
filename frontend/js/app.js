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
    if (!res.ok) throw new Error(data.detail || 'Upload failed');
    parsedRows = data.rows || [];
    renderTable(parsedRows);
    uploadStatus.textContent = `Loaded ${data.count} rows.`;
  } catch (err) {
    uploadStatus.textContent = err.message;
  }
});

function collectEntries() {
  const selected = Array.from(document.querySelectorAll('input[data-row-index]:checked'))
    .map(cb => parsedRows[Number(cb.dataset.rowIndex)])
    .map(cleanRecord)
    .filter(r => r.title && r.doi && r.publication_year);

  const formData = Object.fromEntries(new FormData(manualForm).entries());
  const manual = cleanRecord(formData);
  if (manual.title && manual.doi && manual.publication_year) {
    manual.publication_year = Number(manual.publication_year);
    selected.push(manual);
  }

  return selected;
}

generateBtn.addEventListener('click', async () => {
  const entries = collectEntries();
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
    if (!res.ok) throw new Error(data.detail || 'XML generation failed');

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
      throw new Error(data.detail || 'Download failed');
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

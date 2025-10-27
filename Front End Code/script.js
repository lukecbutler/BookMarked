// Wayback Library — Vanilla JS rewrite (no jQuery)
zipEl.addEventListener('input', () => {
    let v = zipEl.value.replace(/[^\d-]/g, '').slice(0, 10);
    zipEl.value = v;
});


// ------ Form submit
const form = $('#patronForm');
form.addEventListener('submit', async (e) => {
    e.preventDefault();


    // simple check for identityConfirmed
    if ($('#identityConfirmed').value !== 'yes') {
        alert('Please confirm identity with "Yes" to submit the form.');
        return;
    }


    try {
        const body = new URLSearchParams(new FormData(form));
        const res = await fetch('process_patron_form.php', { method: 'POST', body });
        if (!res.ok) throw new Error('Network error');


        // refresh table after success
        await loadPatrons();
        form.reset();
        alert('Patron saved successfully.');
    } catch (err) {
        console.error(err);
        alert('Failed to save patron.');
    }
});


// ------ Table + Pagination + Search
const tbody = $('#patronTableBody');
const pager = $('#patronPager');
const search = $('#patronSearch');
const pageSize = 10;
let rows = []; // raw HTML rows from backend turned into DOM
let filtered = []; // after search
let page = 1;


async function loadPatrons() {
    // `fetch_patron_data.php` should return <tr>...</tr> markup; we inject then parse into rows
    const html = await (await fetch('fetch_patron_data.php', { cache: 'no-store' })).text();
    // put into a temporary table body to convert to nodes
    const tmp = document.createElement('tbody');
    tmp.innerHTML = html.trim();
    rows = $$('#patronTableBody tr', tmp);
    applyFilterAndRender();
}


function applyFilterAndRender() {
    const q = (search.value || '').toLowerCase().trim();
    filtered = !q ? rows : rows.filter(tr => tr.innerText.toLowerCase().includes(q));
    page = 1;
    renderPage();
    renderPager();
}


function renderPage() {
    tbody.innerHTML = '';
    const start = (page - 1) * pageSize;
    const slice = filtered.slice(start, start + pageSize);
    slice.forEach(tr => tbody.appendChild(tr.cloneNode(true)));
}


function renderPager() {
    pager.innerHTML = '';
    const pages = Math.max(1, Math.ceil(filtered.length / pageSize));
    for (let i = 1; i <= pages; i++) {
        const btn = document.createElement('button');
        btn.className = 'wl-page';
        btn.type = 'button';
        btn.textContent = i;
        if (i === page) btn.setAttribute('aria-current', 'page');
        btn.addEventListener('click', () => { page = i; renderPage(); renderPager(); });
        pager.appendChild(btn);
    }
}


search.addEventListener('input', () => applyFilterAndRender());


// initial load
loadPatrons();
}) ();
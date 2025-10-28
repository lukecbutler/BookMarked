// Wait for the document to be ready before running any jQuery
$(document).ready(function () {
    
    // --- Element Definitions ---
    // Note: 'zipEl' is for the '#zipcode' input on index.html
    const zipEl = $('#zipcode'); 
    const form = $('#patronForm');
    const tbody = $('#patronTableBody');
    const search = $('#patronSearch'); // Note: This element doesn't exist in index.html
    const pager = $('#patronPager');   // Note: This element doesn't exist in index.html

    const pageSize = 10;
    let rows = [];
    let filtered = [];
    let page = 1;

    // --- Event Listeners ---

    // Zip code formatting
    if (zipEl.length) { // Check if the zip element exists on this page
        zipEl.on('input', function () {
            let v = $(this).val().replace(/[^\d-]/g, '').slice(0, 10);
            $(this).val(v);
        });
    }

    // Form submission
    if (form.length) { // Check if the form exists
        form.on('submit', async function (e) {
            e.preventDefault();

            // Use .val() to get the value from a jQuery object
            if ($('#identityConfirmed').val() !== 'yes') {
                alert('Please confirm identity with "Yes" to submit the form.');
                return;
            }

            try {
                // Use form[0] to get the raw HTML element for FormData
                const body = new URLSearchParams(new FormData(form[0]));
                const res = await fetch('process_patron_form.php', { method: 'POST', body });
                
                if (!res.ok) throw new Error('Network error');

                await loadPatrons();
                form[0].reset(); // Use form[0] to call the vanilla JS reset method
                alert('Patron saved successfully.');

            } catch (err) {
                console.error(err);
                alert('Failed to save patron.');
            }
        });
    }

    // --- Table + Pagination + Search Functions ---
    // Note: This logic is different from what's in index.html
    
    async function loadPatrons() {
        try {
            const html = await (await fetch('fetch_patron_data.php', { cache: 'no-store' })).text();
            
            // Use jQuery to parse the HTML
            const tmp = $('<tbody></tbody>').html(html.trim());
            rows = tmp.find('tr').toArray(); // Convert jQuery find result to an array
            
            applyFilterAndRender();
        } catch (err) {
            console.error("Error loading patrons:", err);
            tbody.html('<tr><td colspan="11">Error loading patrons.</td></tr>');
        }
    }

    function applyFilterAndRender() {
        const q = (search.val() || '').toLowerCase().trim();
        filtered = !q ? rows : rows.filter(tr => $(tr).text().toLowerCase().includes(q));
        page = 1;
        renderPage();
        renderPager();
    }

    function renderPage() {
        tbody.html(''); // Clear the table body
        const start = (page - 1) * pageSize;
        const slice = filtered.slice(start, start + pageSize);
        
        // Use jQuery's .append()
        slice.forEach(tr => tbody.append($(tr).clone()));
    }

    function renderPager() {
        pager.html(''); // Clear pager
        const pages = Math.max(1, Math.ceil(filtered.length / pageSize));
        
        for (let i = 1; i <= pages; i++) {
            const btn = $('<button type="button" class="wl-page"></button>');
            btn.text(i);
            if (i === page) {
                btn.attr('aria-current', 'page');
            }
            
            // Add click event using jQuery
            btn.on('click', function() {
                page = i;
                renderPage();
                renderPager();
            });
            
            pager.append(btn);
        }
    }

    // Add search listener
    if (search.length) {
        search.on('input', applyFilterAndRender);
    }

    // Initial load (if the table exists)
    if (tbody.length) {
        loadPatrons();
    }

}); // Closes the $(document).ready() wrapper
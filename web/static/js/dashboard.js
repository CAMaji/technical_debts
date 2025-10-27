const branch_select = document.getElementById("branch_select");
const period_select = document.getElementById("period_select");
const include_fixme_input = document.getElementById("include_fixme_input");
const include_complexity_input = document.getElementById("include_complexity_input");


// once doc is ready
document.addEventListener("DOMContentLoaded", () => {
    init_period_select();
    // react to changes
    if (branch_select) branch_select.addEventListener('change', () => safe_display_or_calculate());
    if (period_select) period_select.addEventListener('change', () => safe_display_or_calculate());
    if (include_fixme_input) include_fixme_input.addEventListener('change', () => display_metrics());
    if (include_complexity_input) include_complexity_input.addEventListener('change', () => display_metrics());

    display_metrics();
});

function calculate_and_display_metrics() {
    // Prefer displaying existing metrics; if not present, calculate then display
    return safe_display_or_calculate();
}

function safe_display_or_calculate() {
    return display_metrics().catch(err => {
        if (err && err.status === 404) {
            return calculate_metrics().then(() => display_metrics());
        }
        throw err;
    });
}

// Replace init_period_select with datetime-local support
function init_period_select() {
    // Set default value to now, converted to local datetime-local format
    const now = new Date();
    const pad = (n) => n.toString().padStart(2, '0');
    const yyyy = now.getFullYear();
    const MM = pad(now.getMonth() + 1);
    const dd = pad(now.getDate());
    const hh = pad(now.getHours());
    const mm = pad(now.getMinutes());
    const value = `${yyyy}-${MM}-${dd}T${hh}:${mm}`;
    period_select.value = value;
}

function get_period_value_for_backend() {
    // Convert datetime-local (yyyy-mm-ddThh:mm) to backend format dd/mm/yyyy hh:mm
    const raw = period_select.value; // e.g., 2025-10-10T14:30
    if (!raw) return '';
    const [datePart, timePart] = raw.split('T');
    if (!datePart || !timePart) return '';
    const [y, m, d] = datePart.split('-');
    return `${d}/${m}/${y} ${timePart}`;
}

// Update calculate/display to use the formatter
function calculate_metrics() {
    const selected_branch_option = branch_select.options[branch_select.selectedIndex];
    const branch_id = selected_branch_option.getAttribute("data-id");

    const time_period = get_period_value_for_backend();

    const include_fixme = include_fixme_input.checked;
    const include_complexity = include_complexity_input.checked;

    return fetch('/calculate_metrics', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            repository_id: repository_id,
            branch_id: branch_id,
            time_period: time_period,
            include_fixme: include_fixme,
            include_complexity: include_complexity,
        })
    })
    .then(async response => {
        if (!response.ok) {
            const err = new Error(`HTTP error! Status: ${response.status}`);
            err.status = response.status;
            throw err;
        }
        return response.json();
    })
    .then(data => {
        console.log("Calculated Metrics:", data);
        renderCommitInfo(data);
        return data;
    });
}

function display_metrics() {
    const selected_branch_option = branch_select.options[branch_select.selectedIndex];
    const branch_id = selected_branch_option.getAttribute("data-id");

    const time_period = get_period_value_for_backend();

    const include_fixme = include_fixme_input.checked;
    const include_complexity = include_complexity_input.checked;

    return fetch('/display_metrics', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            repository_id: repository_id,
            branch_id: branch_id,
            time_period: time_period,
            include_fixme: include_fixme,
            include_complexity: include_complexity,
        })
    })
    .then(async response => {
        if (!response.ok) {
            const err = new Error(`HTTP error! Status: ${response.status}`);
            err.status = response.status;
            throw err;
        }
        return response.json();
    })
    .then(data => {
        console.log("Displayed Metrics (from DB):", data);
        renderCommitInfo(data);
        console.log("Fixme data test: ", data.fixme_analysis);
        //const findings = data.fixme_analysis || [];
        //const todoFixmeMap = aggregateTodoFixme(data.fixme_analysis || []);

        renderMetrics((data.cyclomatic_complexity_analysis || [])/*, todoFixmeMap*/);
        return data;
    });
}

function renderCommitInfo(data) {
    try {
        const shaEl = document.getElementById("commit-sha");
        const dateEl = document.getElementById("commit-date");
        const msgEl = document.getElementById("commit-message");

        if (shaEl) shaEl.textContent = data.commit_sha || "-";
        if (dateEl) dateEl.textContent = data.commit_date || "-";
        if (msgEl) msgEl.textContent = data.commit_message || "";
    } catch {  }
}

function renderMetrics(metrics) {
    const tbody = document.querySelector("#metrics-container tbody");
    const template = document.getElementById("metric-template");

    // Remove all rows except template
    tbody.querySelectorAll("tr").forEach(row => {
        if (row !== template) row.remove();
    });

    if (!metrics || metrics.length === 0) return;

    // Helper: create a chevron SVG icon
    const createChevronIcon = () => {
        const svgNS = 'http://www.w3.org/2000/svg';
        const svg = document.createElementNS(svgNS, 'svg');
        svg.setAttribute('width', '14');
        svg.setAttribute('height', '14');
        svg.setAttribute('viewBox', '0 0 16 16');
        svg.style.transition = 'transform 120ms ease';
        const path = document.createElementNS(svgNS, 'path');
        path.setAttribute('d', 'M6 12l4-4-4-4');
        path.setAttribute('fill', 'none');
        path.setAttribute('stroke', 'currentColor');
        path.setAttribute('stroke-width', '2');
        path.setAttribute('stroke-linecap', 'round');
        path.setAttribute('stroke-linejoin', 'round');
        svg.appendChild(path);
        return svg;
    };

    // Group by file
    const groups = new Map();
    metrics.forEach(item => {
        const key = item.file || "(unknown file)";
        if (!groups.has(key)) groups.set(key, []);
        groups.get(key).push(item);
    });

    const COLSPAN = 5;

    groups.forEach((items, file) => {
        // Parent file row
        const parent = document.createElement("tr");
        parent.classList.add("file-row", "table-active");
        const parentTd = document.createElement("td");
        parentTd.colSpan = COLSPAN;

        const toggleBtn = document.createElement("button");
        toggleBtn.type = "button";
        toggleBtn.className = "btn btn-sm btn-link p-0 me-2 toggle-btn";
        toggleBtn.setAttribute("aria-expanded", "true");
        toggleBtn.setAttribute("aria-label", "Toggle file functions");
        const icon = createChevronIcon();
        toggleBtn.appendChild(icon);

        const nameSpan = document.createElement("span");
        nameSpan.className = "fw-semibold";
        nameSpan.textContent = file;

        const countSmall = document.createElement("small");
        countSmall.className = "text-muted ms-2";
        countSmall.textContent = `(${items.length} function${items.length !== 1 ? 's' : ''})`;

        parentTd.appendChild(toggleBtn);
        parentTd.appendChild(nameSpan);
        parentTd.appendChild(countSmall);
        parent.appendChild(parentTd);
        tbody.appendChild(parent);

        // Child function rows
        const childRows = [];
        items.forEach(item => {
            const clone = template.cloneNode(true);
            clone.classList.remove("d-none");
            clone.id = "";
            clone.classList.add("function-row");

            const firstTd = clone.querySelector("td");
            if (firstTd) firstTd.classList.add("ps-4");

            // Fill cells
            const fileNameEl = clone.querySelector(".file-name");
            if (fileNameEl) fileNameEl.textContent = "";

            const functionInfoEl = clone.querySelector(".function-info");
            if (functionInfoEl) functionInfoEl.textContent = `Function: ${item.function} (Line: ${item.start_line})`;

            const debtEl = clone.querySelector(".debt-value");
            if (debtEl) debtEl.textContent = item.debt ?? "-";
            
            const bugsEl = clone.querySelector(".bugs-value");
            if (bugsEl) bugsEl.textContent = item.bugs ?? "-";
            
            const complexityEl = clone.querySelector(".complexity-value");
            if (complexityEl) complexityEl.textContent = item.cyclomatic_complexity ?? "-";
            
            const bar = clone.querySelector(".progress-bar");
            const complexity = parseInt(item.cyclomatic_complexity || 0, 10);
            const progress = Math.min((complexity / 10) * 100, 100);
            if (bar) {
                bar.style.width = `${progress}%`;
                bar.setAttribute("aria-valuenow", progress);
            }

            tbody.appendChild(clone);
            childRows.push(clone);
        });

        // Toggle behavior
        let expanded = true;
        const setExpanded = (exp) => {
            expanded = exp;
            icon.style.transform = expanded ? 'rotate(90deg)' : 'rotate(0deg)';
            childRows.forEach(r => r.classList.toggle("d-none", !expanded));
            toggleBtn.setAttribute("aria-expanded", expanded ? "true" : "false");
        };
        toggleBtn.addEventListener("click", () => setExpanded(!expanded));
        // default expanded
        setExpanded(true);
    });
}
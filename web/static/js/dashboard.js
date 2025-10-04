const branch_select = document.getElementById("branch_select");
const period_select = document.getElementById("period_select");
const include_fixme_input = document.getElementById("include_fixme_input");
const include_complexity_input = document.getElementById("include_complexity_input");

// once doc is ready
document.addEventListener("DOMContentLoaded", () => {
    init_period_select();
    display_metrics();
});

function calculate_and_display_metrics() {
    calculate_metrics()
        .then(() => display_metrics())
        .catch(err => console.error("Error in calculate+display:", err));
}

function calculate_metrics() {
    const selected_branch_option = branch_select.options[branch_select.selectedIndex];
    const branch_id = selected_branch_option.getAttribute("data-id");

    const selected_period = period_select.options[period_select.selectedIndex];
    const time_period = selected_period.value;

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
    .then(response => {
        if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
        return response.json();
    })
    .then(data => {
        console.log("Calculated Metrics:", data);
    });
}

function display_metrics() {
    const selected_branch_option = branch_select.options[branch_select.selectedIndex];
    const branch_id = selected_branch_option.getAttribute("data-id");

    const selected_period = period_select.options[period_select.selectedIndex];
    const time_period = selected_period.value;

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
    .then(response => {
        if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
        return response.json();
    })
    .then(data => {
        console.log("Displayed Metrics (from DB):", data);
        renderMetrics(data.cyclomatic_complexity_analysis);
    });
}

function renderMetrics(metrics) {
    const tbody = document.querySelector("#metrics-container tbody");
    const template = document.getElementById("metric-template");

    // Remove all rows except template
    tbody.querySelectorAll("tr").forEach(row => {
        if (row !== template) row.remove();
    });

    metrics.forEach(item => {
        const clone = template.cloneNode(true);
        clone.classList.remove("d-none");
        clone.id = "";

        clone.querySelector(".file-name").textContent = item.file;
        clone.querySelector(".function-info").textContent = `Function: ${item.function} (Line: ${item.start_line})`;
        clone.querySelector(".debt-value").textContent = item.debt ?? "-";
        clone.querySelector(".bugs-value").textContent = item.bugs ?? "-";
        clone.querySelector(".complexity-value").textContent = item.cyclomatic_complexity ?? "-";

        const complexity = parseInt(item.complexity || 0, 10);
        const progress = Math.min((complexity / 10) * 100, 100);
        clone.querySelector(".progress-bar").style.width = `${progress}%`;
        clone.querySelector(".progress-bar").setAttribute("aria-valuenow", progress);

        tbody.appendChild(clone);
    });
}


function init_period_select() {
    period_select.appendChild(build_option("Latest", generate_date(0), true));
    period_select.appendChild(build_option("30 days", generate_date(30)));
    period_select.appendChild(build_option("60 days", generate_date(60)));
    period_select.appendChild(build_option("90 days", generate_date(90)));
}

function build_option(innerHTML, value, is_selected = false) {
    const option = document.createElement("option");
    option.innerHTML = innerHTML;
    option.value = value;
    option.selected = is_selected;
    return option;
}
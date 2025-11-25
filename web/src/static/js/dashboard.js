// search container elements
const branch_select = document.getElementById("branch_select");
const period_select = document.getElementById("period_select");
const commit_select = document.getElementById("commit_select");

const include_identifiable_identities_label = document.getElementById("include_identifiable_identities_label");
const include_identifiable_identities_input = document.getElementById("include_identifiable_identities_input");
const include_complexity_input = document.getElementById("include_complexity_input");
const include_duplication_input = document.getElementById("include_duplication_input");

// commit selected for metrics display
const commit_sha_display = document.getElementById("commit-sha");
const commit_date_display = document.getElementById("commit-date");
const commit_message_display = document.getElementById("commit-message");

// once doc is ready
document.addEventListener("DOMContentLoaded", () => {
    init_period_select();

    // init the commits select
    const branch_id = get_selected_branch_id();
    get_commits_by_branch_id(branch_id).then((commits) => {
        set_commit_select_options(commits);
    });

    // refresh the list of commits when the user selects a new branch
    branch_select.addEventListener("change", () => {
        const branch_id = get_selected_branch_id();
        get_commits_by_branch_id(branch_id).then((commits) => {
            set_commit_select_options(commits);
        });
    });

    // init the identifiable identities list to show the users the ones he can select/deselect
    
    const identifiable_identities_list_tippy = tippy(include_identifiable_identities_label, {
        allowHTML: true,
        arrow: false,
        interactive: true,
        placement: "bottom",
        content: `
            
        `,
    });
    include_identifiable_identities_label.addEventListener("click", () => {
        identifiable_identities_list_tippy.show();
    });
});

function set_commit_select_options(commits) {
    commit_select.innerHTML = "";
    commits.forEach((commit) => {
        const { id, message } = commit;

        const container = document.createElement("option");
        container.setAttribute("data-id", id);
        const truncated = message.length > 150 ? message.slice(0, 150) + "..." : message;
        container.innerHTML = truncated;

        commit_select.appendChild(container);
    });
}

function display_metrics() {
    const branch_id = get_selected_branch_id();
    const commit_id = get_selected_commit_id();
    const include_identifiable_identities = include_identifiable_identities_input.checked;
    const include_complexity = include_complexity_input.checked;
    const include_duplication = include_duplication_input.checked;

    display_metrics_by_commit_id(repository_id, branch_id, commit_id, include_identifiable_identities, include_complexity, include_duplication).then((metrics) => {
        console.log(metrics);
        const { commit_date, commit_message, commit_sha, cyclomatic_complexity_analysis, identifiable_identities_analysis, duplicated_code_analysis } = metrics;
        render_commit_info(commit_sha, commit_date, commit_message);
        render_calculated_metrics(cyclomatic_complexity_analysis, identifiable_identities_analysis, duplicated_code_analysis)
    });
}

function get_selected_branch_id() {
    return branch_select.options[branch_select.selectedIndex].getAttribute("data-id");
}

function get_selected_commit_id() {
    return commit_select.options[commit_select.selectedIndex].getAttribute("data-id");
}

// show the commit sha, date and message under the repo information selection
function render_commit_info(commit_sha, commit_date, commit_message) {
    commit_sha_display.textContent = commit_sha || "-";
    commit_date_display.textContent = commit_date || "-";
    commit_message_display.textContent = commit_message || "";
}

function render_calculated_metrics(cyclomatic_complexity_analysis, identifiable_identities_analysis, duplicated_code_analysis) {
    // Process the data to group by file
    const fileMetrics = processMetricsData(
        cyclomatic_complexity_analysis, 
        identifiable_identities_analysis, 
        duplicated_code_analysis
    );

    // Initialize or refresh the table
    const $table = $('#metrics-table');
    
    // Destroy existing table if it exists
    if ($table.bootstrapTable('getOptions')) {
        $table.bootstrapTable('destroy');
    }

    // Initialize the table with data
    $table.bootstrapTable({
        columns: [
            {
                field: 'fileName',
                title: 'File Name',
                sortable: true,
                width: '40%'
            },
            {
                field: 'avgComplexity',
                title: 'Avg Complexity',
                sortable: true,
                align: 'center',
                width: '20%',
                formatter: (value) => value !== null ? value.toFixed(2) : '-'
            },
            {
                field: 'identifiableIdentitiesCount',
                title: 'Identifiable Identities',
                sortable: true,
                align: 'center',
                width: '20%'
            },
            {
                field: 'duplicateCodeCount',
                title: 'Duplicate Code',
                sortable: true,
                align: 'center',
                width: '20%'
            }
        ],
        data: fileMetrics,
        detailView: true,
        detailFormatter: detailFormatter,
        detailViewIcon: true,
        detailViewByClick: false,
        showColumns: false,
        onPostBody: function() {
            // Force visibility of detail icons
            $table.find('.detail-icon').css({
                'color': '#495057',
                'font-weight': 'bold',
                'font-size': '1.2rem'
            });
        }
    });
}

// Process metrics data to group by file
function processMetricsData(cyclomatic_complexity_analysis, identifiable_identities_analysis, duplicated_code_analysis) {
    const fileMap = new Map();

    // Process cyclomatic complexity data
    if (cyclomatic_complexity_analysis && Array.isArray(cyclomatic_complexity_analysis)) {
        cyclomatic_complexity_analysis.forEach(fileArray => {
            if (Array.isArray(fileArray) && fileArray.length > 0) {
                const fileName = fileArray[0].file;
                
                if (!fileMap.has(fileName)) {
                    fileMap.set(fileName, {
                        fileName: fileName,
                        functions: [],
                        avgComplexity: 0,
                        identifiableIdentitiesCount: 0,
                        duplicateCodeCount: 0
                    });
                }

                const fileData = fileMap.get(fileName);
                fileData.functions = fileArray.map(func => ({
                    name: func.function,
                    line: func.start_line,
                    complexity: func.cyclomatic_complexity
                }));

                // Calculate average complexity
                const totalComplexity = fileArray.reduce((sum, func) => sum + func.cyclomatic_complexity, 0);
                fileData.avgComplexity = totalComplexity / fileArray.length;
            }
        });
    }

    // Process identifiable identities data
    if (identifiable_identities_analysis && Array.isArray(identifiable_identities_analysis)) {
        identifiable_identities_analysis.forEach(entity => {
            const fileName = entity.file_name;
            
            if (!fileMap.has(fileName)) {
                fileMap.set(fileName, {
                    fileName: fileName,
                    functions: [],
                    avgComplexity: null,
                    identifiableIdentitiesCount: 0,
                    duplicateCodeCount: 0
                });
            }

            const fileData = fileMap.get(fileName);
            fileData.identifiableIdentitiesCount++;
        });
    }

    // Process duplicate code data
    if (duplicated_code_analysis && Array.isArray(duplicated_code_analysis)) {
        duplicated_code_analysis.forEach(duplicate => {
            const fileName = duplicate.file_name || duplicate.file;
            
            if (!fileMap.has(fileName)) {
                fileMap.set(fileName, {
                    fileName: fileName,
                    functions: [],
                    avgComplexity: null,
                    identifiableIdentitiesCount: 0,
                    duplicateCodeCount: 0
                });
            }

            const fileData = fileMap.get(fileName);
            fileData.duplicateCodeCount++;
        });
    }

    return Array.from(fileMap.values());
}

// Detail formatter for expandable rows
function detailFormatter(index, row) {
    if (!row.functions || row.functions.length === 0) {
        return '<div class="p-3 text-muted">No function data available</div>';
    }

    let html = '<div class="p-3"><table class="table table-sm table-striped">';
    html += '<thead><tr>';
    html += '<th style="width: 60%">Function Name</th>';
    html += '<th style="width: 20%" class="text-center">Line</th>';
    html += '<th style="width: 20%" class="text-center">Complexity</th>';
    html += '</tr></thead>';
    html += '<tbody>';

    row.functions.forEach(func => {
        html += '<tr>';
        html += `<td><code>${func.name}</code></td>`;
        html += `<td class="text-center">${func.line}</td>`;
        html += `<td class="text-center"><span class="badge ${getComplexityBadgeClass(func.complexity)}">${func.complexity}</span></td>`;
        html += '</tr>';
    });

    html += '</tbody></table></div>';
    return html;
}

// Helper function to get badge color based on complexity
function getComplexityBadgeClass(complexity) {
    if (complexity <= 5) return 'bg-success';
    if (complexity <= 10) return 'bg-warning';
    return 'bg-danger';
}


// code duplication analysis
function display_code_duplication() {

}
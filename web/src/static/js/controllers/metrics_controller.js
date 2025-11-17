function display_metrics_by_commit_id(repository_id, branch_id, commit_id, include_complexity, include_identifiable_identities, include_code_duplication) {
    return fetch(DISPLAY_METRICS_BY_COMMIT_ID, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            repository_id: repository_id,
            branch_id: branch_id,
            commit_id: commit_id,
            include_complexity: include_complexity,
            include_identifiable_identities: include_identifiable_identities,
            include_code_duplication: include_code_duplication,
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
        return data;
    });
}
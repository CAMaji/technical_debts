function generate_date(previousDays = 0) {
    const now = new Date();
    
    // Subtract previousDays
    now.setDate(now.getDate() - previousDays);

    const pad = (n) => n.toString().padStart(2, "0");

    const day = pad(now.getDate());
    const month = pad(now.getMonth() + 1);
    const year = now.getFullYear();
    const hours = pad(now.getHours());
    const minutes = pad(now.getMinutes());

    return `${day}/${month}/${year} ${hours}:${minutes}`;
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
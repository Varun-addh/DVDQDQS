function toggleMetricScores(metric) {
    const checkBox = document.getElementById('checkbox-' + metric);
    const allCells = document.querySelectorAll(`[id^="score-${metric}-"]`);
    const headerCell = document.getElementById('header-' + metric);
    const table = document.getElementById('scores-table');
    const tableHeader = document.getElementById('table-header');
    const overallScoreSection = document.getElementById('overall-quality-score');
    const overallScoreValue = document.getElementById('overall-score-value');

    const isAnyChecked = Array.from(document.querySelectorAll('input[type="checkbox"]'))
                              .some(checkbox => checkbox.checked);

    table.style.display = isAnyChecked ? "table" : "none";
    tableHeader.style.display = isAnyChecked ? "table-row-group" : "none";

    const displayStyle = checkBox.checked ? "table-cell" : "none";
    headerCell.style.display = displayStyle;

    allCells.forEach(cell => {
        cell.style.display = displayStyle;
    });

    const selectedMetrics = Array.from(document.querySelectorAll('input[type="checkbox"]:checked'))
                                 .map(checkbox => checkbox.name);

    if (selectedMetrics.length > 0) {
        let totalScore = 0;
        let count = 0;

        const rows = document.querySelectorAll('#table-body tr');
        rows.forEach(row => {
            const rowCells = selectedMetrics.map(metric => {
                const cell = row.querySelector(`[id^="score-${metric}-"]`);
                return parseFloat(cell?.innerText.replace('%', '') || 0);
            });

            const rowTotal = rowCells.reduce((sum, score) => sum + score, 0);
            totalScore += rowTotal;
            count += rowCells.length;
        });

        const overallScore = count > 0 ? (totalScore / count).toFixed(2) : 0.00;
        overallScoreValue.innerText = `${overallScore}%`;
        overallScoreSection.style.display = "block";
    } else {
        overallScoreSection.style.display = "none";
    }
}

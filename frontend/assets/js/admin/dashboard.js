const STATS_API = "http://127.0.0.1:8000/reports/admin/stats";

fetch(STATS_API)
  .then(res => res.json())
  .then(stats => {
    document.getElementById("totalReports").innerText = stats.total_reports;
    document.getElementById("pendingReview").innerText = stats.pending_review;
    document.getElementById("resolved").innerText = stats.resolved;
  });

const API = "http://127.0.0.1:8000/reports/admin/analytics/categories";

fetch(API)
  .then(res => res.json())
  .then(data => {
    const ctx = document.getElementById("categoryChart");

    new Chart(ctx, {
      type: "bar",
      data: {
        labels: data.labels,
        datasets: [{
          label: "Number of Reports",
          data: data.counts,
          backgroundColor: "#4f46e5"
        }]
      },
      options: {
        responsive: true,
        plugins: {
          legend: { display: false }
        }
      }
    });
  });

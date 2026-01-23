const API = "http://127.0.0.1:8000/reports/admin/all";

fetch(API)
  .then(res => res.json())
  .then(data => {
    const tbody = document.querySelector("#reportsTable tbody");

    data.forEach(r => {
      const row = document.createElement("tr");

      const needsReview = r.needs_review === true;
      const confidence = r.text_confidence ?? 0;

      const badge = needsReview
        ? `<span class="badge badge-review">Needs Review</span>`
        : `<span class="badge badge-confirmed">Confirmed</span>`;

      const confidenceClass =
        confidence >= 0.5 ? "confidence-high" : "confidence-low";

      row.innerHTML = `
        <td>${r.title}</td>

        <td>
          ${r.text_category ?? "N/A"} <br/>
          ${badge}
        </td>

        <td class="${confidenceClass}">
          ${(confidence * 100).toFixed(1)}%
        </td>

        <td>
          <select id="cat-${r.id}" ${!needsReview ? "disabled" : ""}>
            <option value="infrastructure_defect">Infrastructure Defect</option>
            <option value="natural_hazard">Natural Hazard</option>
            <option value="traffic_accident">Traffic Accident</option>
            <option value="public_safety_issue">Public Safety Issue</option>
            <option value="environmental_issue">Environmental Issue</option>
            <option value="other">Other</option>
          </select>
        </td>

        <td>
          <button onclick="confirmCategory(${r.id})"
            ${!needsReview ? "disabled" : ""}>
            Confirm
          </button>
          <button onclick="deleteReport(${r.id})">Delete</button>
        </td>
      `;

      tbody.appendChild(row);
    });
  });


function confirmCategory(id) {
  const category = document.getElementById(`cat-${id}`).value;

  fetch(`${API}/${id}/category`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ final_category: category })
  })
  .then(() => {
    alert("Category updated");
  });
}

function deleteReport(id) {
  if (!confirm("Delete this report?")) return;

  fetch(`${API}/${id}`, {
    method: "DELETE"
  })
  .then(() => location.reload());
}

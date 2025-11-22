// app/static/app.js

async function scoreTranscript() {
  const textarea = document.getElementById("transcript");
  const durationInput = document.getElementById("duration-sec");
  const status = document.getElementById("status");
  const btn = document.getElementById("score-btn");
  const resultsDiv = document.getElementById("results");
  const overallScoreEl = document.getElementById("overall-score");
  const wordCountEl = document.getElementById("word-count");
  const durationEl = document.getElementById("duration");
  const wpmEl = document.getElementById("wpm");
  const baseRubricEl = document.getElementById("base-rubric-score");
  const semanticEl = document.getElementById("semantic-score");
  const criteriaBody = document.getElementById("criteria-body");

  const text = textarea.value.trim();
  const durationSec = parseFloat(durationInput.value);

  if (!text) {
    alert("Please paste a transcript first.");
    return;
  }
  if (isNaN(durationSec) || durationSec <= 0) {
    alert("Please enter a valid duration in seconds.");
    return;
  }

  btn.disabled = true;
  status.textContent = "Scoring...";
  resultsDiv.classList.add("hidden");

  try {
    const res = await fetch("/api/score", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ transcript: text, duration_sec: durationSec }),
    });

    if (!res.ok) {
      throw new Error("Server error while scoring.");
    }

    const data = await res.json();

    overallScoreEl.textContent = data.overall_score.toFixed(1);
    wordCountEl.textContent = data.words;
    durationEl.textContent = data.duration_sec;
    wpmEl.textContent = data.wpm;
    baseRubricEl.textContent = data.base_rubric_score.toFixed(1);
    semanticEl.textContent = data.semantic_score_0_10.toFixed(1);

    criteriaBody.innerHTML = "";
    data.criteria.forEach((c) => {
      const tr = document.createElement("tr");
      tr.className = "border-t";

      tr.innerHTML = `
        <td class="px-3 py-2 align-top font-medium text-gray-900">
          ${c.criterion}
        </td>
        <td class="px-3 py-2 align-top">
          ${c.score} / ${c.max_score}
        </td>
        <td class="px-3 py-2 align-top text-xs text-gray-700">
          ${c.detail}
        </td>
      `;
      criteriaBody.appendChild(tr);
    });

    resultsDiv.classList.remove("hidden");
    status.textContent = "Done.";
  } catch (err) {
    console.error(err);
    status.textContent = "Error scoring transcript.";
    alert("Error: " + err.message);
  } finally {
    btn.disabled = false;
  }
}

document.addEventListener("DOMContentLoaded", () => {
  document.getElementById("score-btn").addEventListener("click", scoreTranscript);
});

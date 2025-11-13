document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("lipidForm");
    const resultsBox = document.getElementById("results");
    const loading = document.getElementById("loading");

    const riskLevelEl = document.getElementById("riskLevel");
    const interpretationEl = document.getElementById("interpretation");
    const managementEl = document.getElementById("management");
    const lifestyleEl = document.getElementById("lifestyle");
    const scheduleEl = document.getElementById("schedule");

    form.addEventListener("submit", async (e) => {
        e.preventDefault();

        resultsBox.classList.add("hidden");
        loading.classList.remove("hidden");

        const data = {
            patient_id: form.patient_id.value,
            age: Number(form.age.value),
            gender: form.gender.value,
            bmi: Number(form.bmi.value),
            total_cholesterol: Number(form.total_cholesterol.value),
            ldl: Number(form.ldl.value),
            hdl: Number(form.hdl.value),
            triglycerides: Number(form.triglycerides.value),
            blood_glucose: Number(form.blood_glucose.value),
            smoking: document.getElementById("smoking").checked,
            family_history: document.getElementById("family_history").checked,
            hypertension: document.getElementById("hypertension").checked,
            diabetes: document.getElementById("diabetes").checked,
            chest_pain: document.getElementById("chest_pain").checked
        };

        console.log("Sending request:", data);

        try {
            const res = await fetch("/api/analyze-lipid-profile", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(data),
            });

            const result = await res.json();
            console.log("Result:", result);

            loading.classList.add("hidden");

            if (!result.success) {
                alert("Error: " + result.error);
                return;
            }

            const risk = result.risk_analysis?.risk_level || "Unknown";

            // ✅ Risk Badge Color
            const riskColors = {
                "Low": "green",
                "Medium": "orange",
                "High": "red",
                "Urgent": "darkred"
            };
            riskLevelEl.style.background = riskColors[risk] || "gray";
            riskLevelEl.textContent = `Risk Level: ${risk}`;

            // ✅ Heart Interpretation
            interpretationEl.innerHTML = `
                <p>Your current lipid profile suggests <strong>${risk}</strong> cardiovascular risk.</p>
                <p>Please continue checking your profile every 6-12 months.</p>
            `;

            // ✅ Management
            managementEl.innerHTML = `
                <h3>Medical Management Guidance</h3>
                <p><strong>${result.management_type ?? "Monitoring"}</strong> recommended</p>
            `;

            // ✅ Lifestyle Plan
            let daily = result.lifestyle_plan?.daily_reminders || [];
            lifestyleEl.innerHTML = `
                <h3>✅ Daily Healthy Routine</h3>
                <ul>
                    ${daily.map(d => `<li>${d.time} — ${d.message}</li>`).join("")}
                </ul>
            `;

            // ✅ Follow-Up Schedule
            let followUps = result.lifestyle_plan?.checkup_schedule?.follow_ups || [];
            scheduleEl.innerHTML = `
                <h3>📅 Next Checkup Plan</h3>
                <ul>
                    ${followUps.map(f => `<li>${f.date} — ${f.type}</li>`).join("")}
                </ul>
            `;

            resultsBox.classList.remove("hidden");

        } catch (err) {
            loading.classList.add("hidden");
            alert("Request failed: " + err.message);
            console.error(err);
        }
    });
});

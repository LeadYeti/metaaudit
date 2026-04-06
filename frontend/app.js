(function () {
    "use strict";

    var views = document.querySelectorAll(".view");

    function showView(name) {
        views.forEach(function (v) { v.classList.remove("active"); });
        var target = document.getElementById("view-" + name);
        if (target) target.classList.add("active");
    }

    var params = new URLSearchParams(window.location.search);
    var initialView = params.get("view");
    if (initialView === "accounts") {
        showView("accounts");
        loadAccounts();
    }

    var accountSelect = document.getElementById("account-select");
    var daysSelect = document.getElementById("days-select");
    var statusSelect = document.getElementById("status-select");
    var runBtn = document.getElementById("run-audit-btn");

    async function loadAccounts() {
        try {
            var res = await fetch("/api/accounts");
            if (!res.ok) {
                showView("landing");
                return;
            }
            var data = await res.json();
            accountSelect.innerHTML = "";

            if (data.accounts.length === 0) {
                accountSelect.innerHTML = '<option value="">No ad accounts found</option>';
                return;
            }

            data.accounts.forEach(function (acc) {
                var opt = document.createElement("option");
                opt.value = acc.id;
                opt.textContent = acc.name || acc.id;
                accountSelect.appendChild(opt);
            });

            runBtn.disabled = false;
        } catch (err) {
            accountSelect.innerHTML = '<option value="">Error loading accounts</option>';
        }
    }

    runBtn.addEventListener("click", function () {
        var accountId = accountSelect.value;
        var days = daysSelect.value;
        var status = statusSelect.value;
        if (!accountId) return;
        runAudit(accountId, days, status);
    });

    async function runAudit(accountId, days, status) {
        showView("loading");
        animateLoadingSteps();

        try {
            var res = await fetch(
                "/api/audit?account_id=" +
                    encodeURIComponent(accountId) +
                    "&days=" +
                    encodeURIComponent(days) +
                    "&status_filter=" +
                    encodeURIComponent(status)
            );

            if (!res.ok) {
                alert("Audit failed. Please try again.");
                showView("accounts");
                return;
            }

            var data = await res.json();
            renderDashboard(data);
            showView("dashboard");
        } catch (err) {
            alert("Something went wrong. Please try again.");
            showView("accounts");
        }
    }

    function animateLoadingSteps() {
        var steps = ["step-fetch", "step-analyze", "step-score"];
        var i = 0;

        function advance() {
            if (i > 0) {
                document.getElementById(steps[i - 1]).classList.remove("active");
                document.getElementById(steps[i - 1]).classList.add("done");
            }
            if (i < steps.length) {
                document.getElementById(steps[i]).classList.add("active");
                i++;
                setTimeout(advance, 2000);
            }
        }

        steps.forEach(function (id) {
            var el = document.getElementById(id);
            el.classList.remove("active", "done");
        });
        advance();
    }

    var SEVERITY_ICONS = {
        good: "\u2713",
        warning: "\u26A0",
        critical: "\u2717",
        info: "\u2139",
    };

    function gradeColor(grade) {
        var map = { A: "#22C55E", B: "#86EFAC", C: "#EAB308", D: "#F97316", F: "#EF4444" };
        return map[grade] || "#A1A1AA";
    }

    function renderDashboard(data) {
        var circle = document.getElementById("overall-score");
        circle.querySelector(".score-number").textContent = data.overall_score;
        circle.querySelector(".score-grade").textContent = data.overall_grade;
        circle.className = "score-circle grade-" + data.overall_grade.toLowerCase();

        document.getElementById("account-name-display").textContent = data.account_name || "";

        // Data summary for verification
        if (data.data_summary) {
            var ds = data.data_summary;
            var summaryEl = document.getElementById("data-summary");
            var campaignList = ds.campaign_names.map(function (n) { return n; }).join(", ");
            summaryEl.innerHTML =
                '<div class="summary-item"><span class="summary-value">' + ds.campaigns_found + '</span><span class="summary-label">Campaigns</span></div>' +
                '<div class="summary-item"><span class="summary-value">' + ds.ad_sets_found + '</span><span class="summary-label">Ad Sets</span></div>' +
                '<div class="summary-item"><span class="summary-value">' + ds.ads_found + '</span><span class="summary-label">Ads</span></div>' +
                '<div class="summary-item"><span class="summary-value">$' + ds.total_spend.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2}) + '</span><span class="summary-label">Total Spend</span></div>' +
                '<div class="summary-item"><span class="summary-value">' + ds.total_impressions.toLocaleString() + '</span><span class="summary-label">Impressions</span></div>' +
                '<div class="summary-item"><span class="summary-value">' + ds.total_clicks.toLocaleString() + '</span><span class="summary-label">Clicks</span></div>' +
                '<div class="summary-campaigns"><strong>' + ds.status_filter + '</strong> &middot; Last ' + ds.days_analyzed + ' days &middot; Campaigns: ' + campaignList + '</div>';
        }

        var wastedBanner = document.getElementById("wasted-banner");
        var spendArea = data.areas.find(function (a) { return a.area === "Spend Efficiency"; });
        if (spendArea) {
            var wastedFinding = spendArea.findings.find(function (f) {
                return f.severity === "critical" && f.text.toLowerCase().indexOf("wasted") !== -1;
            });
            if (wastedFinding) {
                document.getElementById("wasted-text").textContent = wastedFinding.text;
                wastedBanner.style.display = "flex";
            } else {
                wastedBanner.style.display = "none";
            }
        }

        var grid = document.getElementById("category-grid");
        grid.innerHTML = "";

        data.areas.forEach(function (area) {
            var card = document.createElement("div");
            card.className = "category-card";

            var color = gradeColor(area.grade);
            var findingsHtml = area.findings
                .slice(0, 3)
                .map(function (f) {
                    return '<div class="finding severity-' +
                        f.severity +
                        '"><span class="finding-icon">' +
                        (SEVERITY_ICONS[f.severity] || "") +
                        "</span><span>" +
                        f.text +
                        "</span></div>";
                })
                .join("");

            card.innerHTML =
                '<div class="category-header">' +
                '<span class="category-name">' + area.area + "</span>" +
                '<span class="category-grade" style="color:' + color + '">' + area.grade + "</span>" +
                "</div>" +
                '<div class="score-bar"><div class="score-bar-fill" style="width:' +
                area.score + "%;background:" + color + '"></div></div>' +
                findingsHtml;

            grid.appendChild(card);
        });

        renderTrendChart(spendArea);
        renderBudgetChart(data);

        if (data.calendar_url) {
            document.getElementById("cta-link").href = data.calendar_url;
            document.getElementById("cta-card").style.display = "block";
        }
    }

    var trendChartInstance = null;
    var budgetChartInstance = null;

    function renderTrendChart(spendArea) {
        if (!spendArea || !spendArea.trends) return;

        var ctx = document.getElementById("trend-chart").getContext("2d");
        if (trendChartInstance) trendChartInstance.destroy();

        var trends = spendArea.trends;

        trendChartInstance = new Chart(ctx, {
            type: "line",
            data: {
                labels: trends.dates,
                datasets: [
                    {
                        label: "CPM ($)",
                        data: trends.cpm,
                        borderColor: "#8B5CF6",
                        backgroundColor: "rgba(139,92,246,0.1)",
                        tension: 0.3,
                        fill: true,
                    },
                    {
                        label: "CPC ($)",
                        data: trends.cpc,
                        borderColor: "#22C55E",
                        backgroundColor: "transparent",
                        tension: 0.3,
                    },
                    {
                        label: "CPA ($)",
                        data: trends.cpa,
                        borderColor: "#EAB308",
                        backgroundColor: "transparent",
                        tension: 0.3,
                    },
                ],
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { labels: { color: "#A1A1AA" } },
                },
                scales: {
                    x: { ticks: { color: "#71717A" }, grid: { color: "#27272A" } },
                    y: { ticks: { color: "#71717A" }, grid: { color: "#27272A" } },
                },
            },
        });
    }

    function renderBudgetChart(data) {
        var ctx = document.getElementById("budget-chart").getContext("2d");
        if (budgetChartInstance) budgetChartInstance.destroy();

        var spendArea = data.areas.find(function (a) { return a.area === "Spend Efficiency"; });
        if (!spendArea || !spendArea.trends) return;

        var labels = data.areas.map(function (a) { return a.area; });
        var scores = data.areas.map(function (a) { return a.score; });
        var colors = data.areas.map(function (a) { return gradeColor(a.grade); });

        budgetChartInstance = new Chart(ctx, {
            type: "doughnut",
            data: {
                labels: labels,
                datasets: [
                    {
                        data: scores,
                        backgroundColor: colors,
                        borderColor: "#0A0A0F",
                        borderWidth: 2,
                    },
                ],
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: "bottom",
                        labels: { color: "#A1A1AA", padding: 12, font: { size: 11 } },
                    },
                },
            },
        });
    }
})();

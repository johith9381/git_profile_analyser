/* ============================================================
   GitInsight — script.js
   All original functionality preserved + new analytics features
   ============================================================ */

$(function () {
    const path = window.location.pathname;

    /* ── Search History ── */
    const getHistory = () => JSON.parse(localStorage.getItem('gitHistory') || '[]');
    const saveHistory = (username) => {
        let history = getHistory();
        if (!history.includes(username)) {
            history.unshift(username);
            localStorage.setItem('gitHistory', JSON.stringify(history.slice(0, 5)));
        }
    };

    const renderHistory = () => {
        const history = getHistory();
        const container = $('#searchHistory');
        if (!container.length) return;
        container.empty();
        history.forEach(user => {
            const badge = $(`<span class="badge bg-light text-muted border px-3 py-2 rounded-pill small" style="cursor:pointer;">${user}</span>`);
            badge.on('click', () => {
                $('#usernameInput').val(user);
                $('#analyzerForm').submit();
            });
            container.append(badge);
        });
    };

    if (path === '/' || path === '/analyzer') {
        renderHistory();
        buildHeroAnimation();
    }

    /* ── Hero Commit Grid & Growth Bars ── */
    function buildHeroAnimation() {
        // Commit grid — 26 columns × 7 rows
        const grid = document.getElementById('heroCommitGrid');
        if (!grid) return;

        const cols = 26, rows = 7;
        // Pre-defined "active" pattern (simulated git activity)
        const activeSet = new Set([
            2, 8, 15, 16, 22, 28, 29, 35,
            41, 47, 48, 54, 60, 61, 67, 73,
            74, 80, 86, 87, 93, 99, 105, 111,
            112, 118, 124, 130, 136, 137, 143,
            20, 34, 55, 76, 97, 118, 139, 160,
            11, 25, 46, 68, 89, 110, 131, 152
        ]);

        for (let c = 0; c < cols; c++) {
            const col = document.createElement('div');
            col.className = 'commit-col';
            for (let r = 0; r < rows; r++) {
                const dot = document.createElement('div');
                const idx = c * rows + r;
                const rnd = Math.random();
                if (activeSet.has(idx) || rnd > 0.72) {
                    dot.className = rnd > 0.9 ? 'commit-dot semi' : 'commit-dot active';
                } else {
                    dot.className = 'commit-dot';
                }
                dot.style.animationDelay = `${(c * rows + r) * 0.012}s`;
                col.appendChild(dot);
            }
            grid.appendChild(col);
        }

        // Growth bars
        const barsWrap = document.getElementById('heroGrowthBars');
        if (!barsWrap) return;

        const years = [
            { year: '2019', pct: 22 },
            { year: '2020', pct: 38 },
            { year: '2021', pct: 55 },
            { year: '2022', pct: 72 },
            { year: '2023', pct: 85 },
            { year: '2024', pct: 100 },
        ];

        years.forEach((y, i) => {
            const row = document.createElement('div');
            row.className = 'growth-bar-row';
            row.innerHTML = `
                <span class="growth-bar-label">${y.year}</span>
                <div class="growth-bar-track">
                    <div class="growth-bar-fill" style="width:${y.pct}%;animation-delay:${i * 0.15}s;"></div>
                </div>
            `;
            barsWrap.appendChild(row);
        });
    }

    /* ── Form Submission ── */
    $('#analyzerForm').on('submit', function (e) {
        e.preventDefault();
        const btn      = $('#analyzeBtn');
        const spinner  = $('#loadingSpinner');
        const errorBox = $('#errorMsg');
        const username = $("input[name='github_username']").val().trim();

        if (!username) return;

        errorBox.addClass('d-none').text('');
        btn.prop('disabled', true).addClass('opacity-50');
        spinner.removeClass('d-none');

        $.post('/analyze', { github_username: username })
            .done(function (resp) {
                if (resp && resp.redirect) {
                    saveHistory(username);
                    window.location.href = resp.redirect;
                } else {
                    errorBox.removeClass('d-none').text('Unexpected response from server.');
                }
            })
            .fail(function (xhr) {
                const msg = xhr.responseJSON && xhr.responseJSON.error
                    ? xhr.responseJSON.error
                    : 'User not found or GitHub API limit reached.';
                errorBox.removeClass('d-none').text(msg);
            })
            .always(function () {
                btn.prop('disabled', false).removeClass('opacity-50');
                spinner.addClass('d-none');
            });
    });

    /* ══════════════════════════════════
       DASHBOARD LOGIC
       ══════════════════════════════════ */
    if (!path.includes('/dashboard') || !window.dashboardData) return;

    const data = window.dashboardData;

    /* ── Section Switching (sidebar + mobile pills) ── */
    function switchSection(sectionId) {
        // Sidebar links
        $('.nav-link-modern').removeClass('active');
        $(`.nav-link-modern[data-section="${sectionId}"]`).addClass('active');

        // Mobile pills
        $('.mobile-nav-pill').removeClass('active');
        $(`.mobile-nav-pill[data-section="${sectionId}"]`).addClass('active');

        // Sections
        $('.section-scope').addClass('d-none');
        $(`#section-${sectionId}`).removeClass('d-none');

        // Trigger section-specific initializations
        initSectionCharts(sectionId);
    }

    $('.nav-link-modern').on('click', function (e) {
        e.preventDefault();
        switchSection($(this).data('section'));
    });

    $('.mobile-nav-pill').on('click', function () {
        switchSection($(this).data('section'));
    });

    /* ── Track which charts have been initialized ── */
    const initialized = {};

    function initSectionCharts(sectionId) {
        if (initialized[sectionId]) return;
        initialized[sectionId] = true;

        if (sectionId === 'overview') {
            initOverview();
        } else if (sectionId === 'activity') {
            initActivity();
        } else if (sectionId === 'technology') {
            initTechnology();
        }
    }

    /* ── Overview Init ── */
    function initOverview() {
        // Activity progress bar
        const activityVal = data.activity_score || 0;
        const pct = Math.min(100, Math.round(activityVal / 200 * 100));
        setTimeout(() => {
            $('#activityProgress').css('width', pct + '%');
        }, 300);

        // Consistency gauge
        const consistencyVal = data.metrics.consistency_score || 0;
        const rotation = -90 + (consistencyVal * 1.8);
        setTimeout(() => {
            $('#consistencyGauge').css('transform', `rotate(${rotation}deg)`);
        }, 350);
    }

    /* ── Activity Init ── */
    function initActivity() {
        // Heatmap
        const heat = document.getElementById('heatmap');
        if (heat && heat.children.length === 0) {
            const values = data.heatmap || [];
            values.forEach((v, i) => {
                const cell = document.createElement('div');
                cell.className = `heat-cell intensity-${v || 0}`;
                cell.style.animationDelay = `${i * 0.012}s`;
                heat.appendChild(cell);
            });
        }

        // DNA Radar Chart
        const ctxDna = document.getElementById('dnaRadar');
        if (ctxDna && !ctxDna._chartInitialized) {
            ctxDna._chartInitialized = true;
            new Chart(ctxDna, {
                type: 'radar',
                data: {
                    labels: ['Builder', 'Collaborator', 'Innovator', 'Consistency'],
                    datasets: [{
                        label: 'Developer Persona',
                        data: [data.dna.Builder, data.dna.Collaborator, data.dna.Innovator, data.dna.Consistency],
                        backgroundColor: 'rgba(99,102,241,0.18)',
                        borderColor: '#6366f1',
                        pointBackgroundColor: '#6366f1',
                        pointBorderColor: '#fff',
                        pointHoverBackgroundColor: '#fff',
                        pointHoverBorderColor: '#6366f1',
                        borderWidth: 2,
                    }]
                },
                options: {
                    scales: {
                        r: {
                            beginAtZero: true,
                            max: 100,
                            ticks: { display: false, stepSize: 25 },
                            grid: { color: 'rgba(0,0,0,0.06)' },
                            pointLabels: { font: { size: 12, weight: '600' } }
                        }
                    },
                    plugins: { legend: { display: false } },
                    animation: { duration: 1000, easing: 'easeInOutQuart' }
                }
            });
        }
    }

    /* ── Technology Init ── */
    function initTechnology() {
        // Language Pie
        const ctxLang = document.getElementById('langPie');
        if (ctxLang && !ctxLang._chartInitialized) {
            ctxLang._chartInitialized = true;
            const labels = Object.keys(data.language_distribution);
            const values = labels.map(k => data.language_distribution[k]);
            const colors = ['#6366f1','#a855f7','#f43f5e','#10b981','#f59e0b','#3b82f6','#ec4899','#14b8a6'];
            new Chart(ctxLang, {
                type: 'doughnut',
                data: {
                    labels: labels,
                    datasets: [{
                        data: values,
                        backgroundColor: colors.slice(0, labels.length),
                        borderWidth: 0,
                        hoverOffset: 8
                    }]
                },
                options: {
                    cutout: '70%',
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: { usePointStyle: true, padding: 16, font: { size: 11 } }
                        }
                    },
                    animation: { animateRotate: true, duration: 1000 }
                }
            });
        }

        // Skill Radar
        const ctxSkill = document.getElementById('skillRadar');
        if (ctxSkill && !ctxSkill._chartInitialized) {
            ctxSkill._chartInitialized = true;
            new Chart(ctxSkill, {
                type: 'radar',
                data: {
                    labels: data.skill_radar.labels,
                    datasets: [{
                        label: 'Language Proficiency',
                        data: data.skill_radar.values,
                        backgroundColor: 'rgba(168,85,247,0.18)',
                        borderColor: '#a855f7',
                        pointBackgroundColor: '#a855f7',
                        borderWidth: 2,
                    }]
                },
                options: {
                    scales: {
                        r: {
                            beginAtZero: true,
                            ticks: { display: false },
                            grid: { color: 'rgba(0,0,0,0.06)' },
                            pointLabels: { font: { size: 11, weight: '600' } }
                        }
                    },
                    plugins: { legend: { display: false } },
                    animation: { duration: 1000, easing: 'easeInOutQuart' }
                }
            });
        }
    }

    /* ── Initialize default section (Overview) ── */
    initOverview();

});

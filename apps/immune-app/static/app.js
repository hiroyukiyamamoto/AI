// Immune Cell Learning App JS

let cellsData = [];
let scenariosData = [];
let quizQuestions = [];

// Simulator State
let currentScenario = null;
let currentStepIndex = 0;

// Quiz State
let quizCurrentIndex = 0;
let quizScore = 0;
let quizAnswers = [];

document.addEventListener('DOMContentLoaded', async () => {
    lucide.createIcons();
    await loadInitialData();
});

// Load data from FastAPI Backend
async function loadInitialData() {
    try {
        const [cellsRes, scenariosRes, quizRes] = await Promise.all([
            fetch('/api/cells'),
            fetch('/api/scenarios'),
            fetch('/api/quiz')
        ]);

        if (cellsRes.ok) {
            const data = await cellsRes.json();
            cellsData = data.cells;
            renderCells(cellsData);
        }

        if (scenariosRes.ok) {
            const data = await scenariosRes.json();
            scenariosData = data.scenarios;
            renderScenarioList();
        }

        if (quizRes.ok) {
            const data = await quizRes.json();
            quizQuestions = data.questions;
        }
    } catch (err) {
        console.error('Error fetching data from API:', err);
    }
}

// Tab Switching
function switchTab(tabId) {
    document.querySelectorAll('.tab-content').forEach(el => el.classList.add('hidden'));
    document.querySelectorAll('.nav-btn').forEach(btn => btn.classList.remove('active-tab'));

    const targetTab = document.getElementById(`tab-${tabId}`);
    const targetBtn = document.getElementById(`tab-btn-${tabId}`);

    if (targetTab) targetTab.classList.remove('hidden');
    if (targetBtn) targetBtn.classList.add('active-tab');

    lucide.createIcons();
}

// Render Cell Cards
function renderCells(cells) {
    const grid = document.getElementById('cell-grid');
    if (!grid) return;

    grid.innerHTML = cells.map(cell => `
        <div class="cell-card bg-slate-800/80 border border-slate-700/80 hover:border-slate-500 rounded-2xl p-6 flex flex-col justify-between cursor-pointer" onclick="openCellModal('${cell.id}')">
            <div>
                <div class="flex items-center justify-between mb-4">
                    <span class="text-xs font-bold px-3 py-1 rounded-full text-white" style="background-color: ${cell.color}25; color: ${cell.color}; border: 1px solid ${cell.color}50;">
                        ${cell.badge}
                    </span>
                    <span class="text-3xl">${cell.icon}</span>
                </div>
                <h3 class="text-xl font-bold text-white mb-1 flex items-baseline gap-2">
                    ${cell.name}
                    <span class="text-xs font-normal text-slate-400 font-mono">${cell.englishName}</span>
                </h3>
                <p class="text-xs font-medium text-amber-400 mb-3">「${cell.catchphrase}」</p>
                <p class="text-xs text-slate-300 leading-relaxed line-clamp-3 mb-4">
                    ${cell.description}
                </p>
            </div>

            <div>
                <div class="space-y-1.5 mb-4">
                    ${Object.entries(cell.stats).map(([stat, val]) => `
                        <div class="flex items-center justify-between text-[11px]">
                            <span class="text-slate-400">${stat}</span>
                            <div class="flex items-center gap-2">
                                <div class="w-20 bg-slate-900 rounded-full h-1.5 overflow-hidden">
                                    <div class="h-full rounded-full" style="width: ${val}%; background-color: ${cell.color}"></div>
                                </div>
                                <span class="font-bold text-slate-300 font-mono w-6 text-right">${val}</span>
                            </div>
                        </div>
                    `).join('')}
                </div>

                <button class="w-full py-2 rounded-xl text-xs font-bold text-slate-200 bg-slate-700/50 hover:bg-slate-700 transition-all flex items-center justify-center gap-1">
                    <span>詳細データを見る</span>
                    <i data-lucide="arrow-right" class="w-3.5 h-3.5"></i>
                </button>
            </div>
        </div>
    `).join('');

    lucide.createIcons();
}

// Filter Cells
function filterCells(category) {
    document.querySelectorAll('.filter-btn').forEach(btn => btn.classList.remove('active-filter'));
    const btn = document.getElementById(`filter-${category}`);
    if (btn) btn.classList.add('active-filter');

    if (category === 'all') {
        renderCells(cellsData);
    } else {
        const filtered = cellsData.filter(c => c.category === category);
        renderCells(filtered);
    }
}

// Open Cell Modal
function openCellModal(cellId) {
    const cell = cellsData.find(c => c.id === cellId);
    if (!cell) return;

    const modal = document.getElementById('cell-modal');
    const content = document.getElementById('modal-content');

    content.innerHTML = `
        <div class="text-center mb-6">
            <div class="w-20 h-20 mx-auto rounded-3xl flex items-center justify-center text-4xl mb-3 shadow-lg" style="background-color: ${cell.color}20; border: 2px solid ${cell.color}60;">
                ${cell.icon}
            </div>
            <span class="text-xs font-bold px-3 py-1 rounded-full text-white inline-block mb-2" style="background-color: ${cell.color}30; color: ${cell.color}; border: 1px solid ${cell.color}60;">
                ${cell.badge}
            </span>
            <h3 class="text-2xl font-extrabold text-white">${cell.name}</h3>
            <p class="text-xs text-slate-400 font-mono">${cell.englishName}</p>
            <p class="text-sm font-semibold text-amber-400 mt-2">「${cell.catchphrase}」</p>
        </div>

        <div class="space-y-4 text-xs sm:text-sm text-slate-300">
            <div class="bg-slate-900/80 p-4 rounded-2xl border border-slate-700">
                <h4 class="font-bold text-white mb-2 flex items-center gap-1.5">
                    <i data-lucide="info" class="w-4 h-4 text-indigo-400"></i> 細胞の役割・解説
                </h4>
                <p class="leading-relaxed text-slate-300">${cell.description}</p>
            </div>

            <div class="bg-slate-900/80 p-4 rounded-2xl border border-slate-700">
                <h4 class="font-bold text-white mb-2 flex items-center gap-1.5">
                    <i data-lucide="sparkles" class="w-4 h-4 text-amber-400"></i> 主な特徴・能力
                </h4>
                <ul class="space-y-2">
                    ${cell.features.map(f => `
                        <li class="flex items-start gap-2">
                            <i data-lucide="check-circle-2" class="w-4 h-4 text-emerald-400 shrink-0 mt-0.5"></i>
                            <span>${f}</span>
                        </li>
                    `).join('')}
                </ul>
            </div>

            <div class="bg-slate-900/80 p-4 rounded-2xl border border-slate-700">
                <h4 class="font-bold text-white mb-3 flex items-center gap-1.5">
                    <i data-lucide="bar-chart-2" class="w-4 h-4 text-rose-400"></i> ステータス解析
                </h4>
                <div class="space-y-2">
                    ${Object.entries(cell.stats).map(([stat, val]) => `
                        <div class="flex items-center justify-between">
                            <span class="text-slate-400">${stat}</span>
                            <div class="flex items-center gap-3">
                                <div class="w-36 bg-slate-800 rounded-full h-2 overflow-hidden">
                                    <div class="h-full rounded-full" style="width: ${val}%; background-color: ${cell.color}"></div>
                                </div>
                                <span class="font-bold text-white font-mono text-xs w-6 text-right">${val}</span>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        </div>
    `;

    modal.classList.remove('hidden');
    lucide.createIcons();
}

function closeCellModal() {
    document.getElementById('cell-modal').classList.add('hidden');
}

// -------------------------------------------------------------
// SIMULATOR LOGIC
// -------------------------------------------------------------
function renderScenarioList() {
    const container = document.getElementById('scenario-selector');
    if (!container) return;

    container.innerHTML = scenariosData.map(sc => `
        <div class="bg-slate-900 border border-slate-700 hover:border-rose-500/60 rounded-2xl p-5 cursor-pointer transition-all flex flex-col justify-between space-y-4" onclick="selectScenario('${sc.id}')">
            <div>
                <div class="flex items-center justify-between mb-2">
                    <span class="text-xs font-bold px-2.5 py-0.5 rounded bg-rose-500/20 text-rose-300 border border-rose-500/30">
                        難易度: ${sc.difficulty}
                    </span>
                    <span class="text-xs text-slate-400">全 ${sc.steps.length} ステップ</span>
                </div>
                <h4 class="text-base font-bold text-white">${sc.title}</h4>
                <p class="text-xs text-slate-400 mt-2 line-clamp-2">${sc.description}</p>
            </div>
            <button class="w-full py-2 rounded-xl text-xs font-bold text-white bg-gradient-to-r from-rose-500 to-indigo-600 hover:from-rose-600 hover:to-indigo-700 transition-all flex items-center justify-center gap-2">
                <i data-lucide="play" class="w-3.5 h-3.5"></i> この作戦を開始
            </button>
        </div>
    `).join('');

    lucide.createIcons();
}

function selectScenario(scenarioId) {
    currentScenario = scenariosData.find(s => s.id === scenarioId);
    if (!currentScenario) return;

    currentStepIndex = 0;
    document.getElementById('scenario-selector').classList.add('hidden');
    document.getElementById('sim-active-area').classList.remove('hidden');

    document.getElementById('sim-stage-title').innerText = currentScenario.title;
    document.getElementById('sim-stage-desc').innerText = currentScenario.description;

    renderSimStep();
}

function renderSimStep() {
    const step = currentScenario.steps[currentStepIndex];
    const totalSteps = currentScenario.steps.length;

    // Update Progress
    const pct = Math.round(((currentStepIndex) / totalSteps) * 100);
    document.getElementById('sim-progress-bar').style.width = `${pct}%`;
    document.getElementById('sim-stage-num').innerText = `STEP ${step.stepNumber} / ${totalSteps}`;

    // Question
    document.getElementById('sim-question-text').innerText = step.question;

    // Feedback & Next Button Reset
    const feedbackBox = document.getElementById('sim-feedback-box');
    feedbackBox.classList.add('hidden');
    document.getElementById('sim-next-btn').classList.add('hidden');

    // Options
    const container = document.getElementById('sim-options-container');
    container.innerHTML = step.options.map((opt, idx) => `
        <button onclick="chooseSimOption(${idx})" class="sim-opt-btn w-full text-left p-4 rounded-xl bg-slate-800 hover:bg-slate-700 border border-slate-700/80 transition-all font-medium text-xs sm:text-sm text-slate-200 flex items-center justify-between">
            <span>${opt.text}</span>
            <i data-lucide="chevron-right" class="w-4 h-4 text-slate-400"></i>
        </button>
    `).join('');

    lucide.createIcons();
}

function chooseSimOption(optionIndex) {
    const step = currentScenario.steps[currentStepIndex];
    const selected = step.options[optionIndex];

    const feedbackBox = document.getElementById('sim-feedback-box');
    feedbackBox.classList.remove('hidden');

    // Disable option buttons
    document.querySelectorAll('.sim-opt-btn').forEach(btn => {
        btn.disabled = true;
        btn.classList.add('opacity-50', 'cursor-not-allowed');
    });

    if (selected.correct) {
        feedbackBox.className = "p-4 rounded-xl text-xs sm:text-sm leading-relaxed border bg-emerald-950/60 border-emerald-500/50 text-emerald-200 shadow-lg";
        feedbackBox.innerHTML = `
            <div class="flex items-center gap-2 font-bold mb-1 text-emerald-300">
                <i data-lucide="check-circle-2" class="w-5 h-5 text-emerald-400"></i>
                作戦成功！ (ミッション達成)
            </div>
            <div>${selected.reason}</div>
        `;
        document.getElementById('sim-next-btn').classList.remove('hidden');
    } else {
        feedbackBox.className = "p-4 rounded-xl text-xs sm:text-sm leading-relaxed border bg-rose-950/60 border-rose-500/50 text-rose-200 shadow-lg";
        feedbackBox.innerHTML = `
            <div class="flex items-center gap-2 font-bold mb-1 text-rose-300">
                <i data-lucide="x-circle" class="w-5 h-5 text-rose-400"></i>
                作戦失敗... 別の選択肢を試してください！
            </div>
            <div>${selected.reason}</div>
            <button onclick="renderSimStep()" class="mt-3 px-4 py-1.5 rounded-lg bg-rose-600 text-white font-bold text-xs hover:bg-rose-500 transition-all">
                再試行する
            </button>
        `;
    }

    lucide.createIcons();
}

function nextSimStep() {
    currentStepIndex++;
    if (currentStepIndex < currentScenario.steps.length) {
        renderSimStep();
    } else {
        // Complete Scenario!
        document.getElementById('sim-progress-bar').style.width = '100%';
        const feedbackBox = document.getElementById('sim-feedback-box');
        feedbackBox.className = "p-6 rounded-2xl text-center bg-gradient-to-r from-emerald-900/80 to-teal-900/80 border border-emerald-400 text-emerald-100 shadow-2xl";
        feedbackBox.innerHTML = `
            <div class="text-3xl mb-2">🎉</div>
            <h4 class="text-xl font-bold mb-2">ミッション完了！病原体の完全撃退に成功しました！</h4>
            <p class="text-xs sm:text-sm text-emerald-200 mb-4">自然免疫と獲得免疫の見事な連携攻撃により、体内の健康が維持されました。</p>
            <button onclick="resetSimulator()" class="px-6 py-2 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-xs shadow-lg">
                他のステージに挑戦する
            </button>
        `;
        document.getElementById('sim-next-btn').classList.add('hidden');
        document.getElementById('sim-options-container').innerHTML = '';
        document.getElementById('sim-question-text').innerText = '作戦成功！全ステップ完了！';
    }
}

function resetSimulator() {
    currentScenario = null;
    currentStepIndex = 0;
    document.getElementById('sim-active-area').classList.add('hidden');
    document.getElementById('scenario-selector').classList.remove('hidden');
}

// -------------------------------------------------------------
// QUIZ LOGIC
// -------------------------------------------------------------
function startQuiz() {
    quizCurrentIndex = 0;
    quizScore = 0;
    quizAnswers = [];

    document.getElementById('quiz-start-btn').classList.add('hidden');
    document.getElementById('quiz-result-card').classList.add('hidden');
    document.getElementById('quiz-container').classList.remove('hidden');

    renderQuizQuestion();
}

function renderQuizQuestion() {
    const q = quizQuestions[quizCurrentIndex];
    if (!q) return;

    document.getElementById('quiz-progress-text').innerText = `第 ${quizCurrentIndex + 1} / ${quizQuestions.length} 問`;
    document.getElementById('quiz-score-badge').innerText = `${quizScore} 点`;
    document.getElementById('quiz-question-title').innerText = q.question;

    const explanation = document.getElementById('quiz-explanation');
    explanation.classList.add('hidden');
    document.getElementById('quiz-next-btn').classList.add('hidden');

    const choicesContainer = document.getElementById('quiz-choices');
    choicesContainer.innerHTML = q.options.map((opt, idx) => `
        <button onclick="submitQuizAnswer(${idx})" class="quiz-choice-btn w-full text-left p-4 rounded-xl bg-slate-800 hover:bg-slate-700 border border-slate-700 transition-all text-xs sm:text-sm text-slate-200 font-medium flex items-center justify-between">
            <span>${idx + 1}. ${opt}</span>
            <i data-lucide="circle" class="w-4 h-4 text-slate-500"></i>
        </button>
    `).join('');

    lucide.createIcons();
}

function submitQuizAnswer(choiceIndex) {
    const q = quizQuestions[quizCurrentIndex];
    const isCorrect = choiceIndex === q.answerIndex;

    if (isCorrect) {
        quizScore += 10;
    }
    quizAnswers.push({ questionId: q.id, choiceIndex, isCorrect });

    // Disable all choice buttons
    document.querySelectorAll('.quiz-choice-btn').forEach((btn, idx) => {
        btn.disabled = true;
        btn.classList.add('cursor-not-allowed');
        if (idx === q.answerIndex) {
            btn.className = "w-full text-left p-4 rounded-xl bg-emerald-950/80 border-2 border-emerald-500 text-emerald-200 font-bold flex items-center justify-between";
        } else if (idx === choiceIndex && !isCorrect) {
            btn.className = "w-full text-left p-4 rounded-xl bg-rose-950/80 border-2 border-rose-500 text-rose-200 font-bold flex items-center justify-between opacity-80";
        } else {
            btn.classList.add('opacity-40');
        }
    });

    // Explanation Box
    const expBox = document.getElementById('quiz-explanation');
    expBox.classList.remove('hidden');

    if (isCorrect) {
        expBox.className = "p-4 rounded-xl text-xs sm:text-sm border bg-emerald-950/60 border-emerald-500/50 text-emerald-200 leading-relaxed";
        expBox.innerHTML = `
            <div class="font-bold flex items-center gap-1.5 mb-1 text-emerald-300">
                <i data-lucide="check-circle" class="w-4 h-4"></i> 正解！
            </div>
            <div>${q.explanation}</div>
        `;
    } else {
        expBox.className = "p-4 rounded-xl text-xs sm:text-sm border bg-rose-950/60 border-rose-500/50 text-rose-200 leading-relaxed";
        expBox.innerHTML = `
            <div class="font-bold flex items-center gap-1.5 mb-1 text-rose-300">
                <i data-lucide="x-circle" class="w-4 h-4"></i> 不正解... （正解: ${q.options[q.answerIndex]}）
            </div>
            <div>${q.explanation}</div>
        `;
    }

    document.getElementById('quiz-score-badge').innerText = `${quizScore} 点`;
    document.getElementById('quiz-next-btn').classList.remove('hidden');

    lucide.createIcons();
}

function nextQuizQuestion() {
    quizCurrentIndex++;
    if (quizCurrentIndex < quizQuestions.length) {
        renderQuizQuestion();
    } else {
        showQuizResults();
    }
}

function showQuizResults() {
    document.getElementById('quiz-container').classList.add('hidden');
    const resultCard = document.getElementById('quiz-result-card');
    resultCard.classList.remove('hidden');

    document.getElementById('quiz-final-score').innerText = `${quizScore} / 100 点`;

    let rankTitle = "";
    let rankComment = "";

    if (quizScore === 100) {
        rankTitle = "ランク: 免疫無双の最高司令官 (100点)";
        rankComment = "パーフェクト！自然免疫から獲得免疫まで、完璧にマスターしています！";
    } else if (quizScore >= 80) {
        rankTitle = "ランク: 頼れる司令塔ヘルパーT級";
        rankComment = "素晴らしい！免疫システムの基本から応用まで深く理解できています。";
    } else if (quizScore >= 50) {
        rankTitle = "ランク: 先陣切る熱血好中球級";
        rankComment = "グッジョブ！主要な免疫細胞の働きをしっかり抑えています。もう少しで司令官になれます！";
    } else {
        rankTitle = "ランク: 見習い白血球";
        rankComment = "図鑑やシミュレーターをもう一度チェックして、免疫細胞のチームワークをおさらいしてみましょう！";
    }

    document.getElementById('quiz-rank-badge').innerText = rankTitle;
    document.getElementById('quiz-rank-comment').innerText = rankComment;

    document.getElementById('quiz-start-btn').classList.remove('hidden');
}

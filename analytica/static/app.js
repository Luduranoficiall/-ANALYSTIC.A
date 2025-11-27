const themes = ["light", "dark", "neon", "gold", "extra", "matrix", "night"];
let currentThemeIndex = 0;

// Aplica tema
function setTheme(theme) {
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem("theme", theme);
}

// Detecção de tema salvo
function loadSavedTheme() {
    const saved = localStorage.getItem("theme");
    if (saved) {
        setTheme(saved);
        currentThemeIndex = themes.indexOf(saved);
        return;
    }

    // tema automático por horário
    const hour = new Date().getHours();
    if (hour >= 19 || hour < 7) setTheme("dark");
    else setTheme("light");
}

// Troca manual de tema
function nextTheme() {
    currentThemeIndex = (currentThemeIndex + 1) % themes.length;
    setTheme(themes[currentThemeIndex]);
}

// Inicializa
document.addEventListener("DOMContentLoaded", () => {
    loadSavedTheme();
    const btn = document.getElementById("theme-toggle");
    if (btn) btn.onclick = nextTheme;

    // Carregar KPIs
    if (typeof loadKPIs === "function") {
        loadKPIs();
    }

        // WebSocket para gráficos em tempo real
        const ws = new WebSocket("wss://analystic.a/ws");
        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            if (typeof updateRealtimeChart === "function") {
                updateRealtimeChart(data);
            }
        };
});

// Função IA
async function askAI() {
    const q = document.getElementById("ai-question")?.value;
    if (!q) return;
    const res = await fetch(`/insights?question=${encodeURIComponent(q)}`);
    const json = await res.json();
    document.getElementById("ai-response").innerHTML = json.insights;
}

// Carregar KPIs
async function loadKPIs() {
    const res = await fetch("/api/kpis");
    const data = await res.json();

    if (document.getElementById("kpi-members"))
        document.getElementById("kpi-members").innerText = data.members;
    if (document.getElementById("kpi-cashback"))
        document.getElementById("kpi-cashback").innerText = "R$ " + data.cashback;
    if (document.getElementById("kpi-partners"))
        document.getElementById("kpi-partners").innerText = data.partners;
    if (document.getElementById("kpi-revenue"))
        document.getElementById("kpi-revenue").innerText = "R$ " + data.revenue;
}

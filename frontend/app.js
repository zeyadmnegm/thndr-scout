const statusEl = document.getElementById("status");
const refreshBtn = document.getElementById("refresh-btn");
const rankingsEl = document.getElementById("rankings");

function fmtPct(n) {
  const sign = n >= 0 ? "+" : "";
  return `${sign}${n.toFixed(1)}%`;
}

function fmtTimeAgo(iso) {
  if (!iso) return "never scanned";
  const diffMs = Date.now() - new Date(iso).getTime();
  const mins = Math.round(diffMs / 60000);
  if (mins < 1) return "just now";
  if (mins < 60) return `${mins}m ago`;
  const hours = Math.round(mins / 60);
  if (hours < 24) return `${hours}h ago`;
  return `${Math.round(hours / 24)}d ago`;
}

function renderCard(row, index) {
  const li = document.createElement("li");
  li.className = "card";

  const changeClass = row.momentum_1m >= 0 ? "change-up" : "change-down";
  const peText = row.trailing_pe ? row.trailing_pe.toFixed(1) : "—";

  li.innerHTML = `
    <div class="card-top">
      <span class="rank">${index + 1}</span>
      <span class="score">${Math.round(row.score)}</span>
      <div class="name-block">
        <div class="ticker">${row.ticker.replace(".CA", "")}</div>
        <div class="company">${row.name}</div>
      </div>
      <div class="price-block">
        <div>${row.price.toFixed(2)} EGP</div>
        <div class="${changeClass}">${fmtPct(row.momentum_1m)} (1m)</div>
      </div>
    </div>
    <p class="blurb">${row.blurb}</p>
    <div class="details">
      <div class="detail-grid">
        <span>3-month momentum</span><span>${fmtPct(row.momentum_3m)}</span>
        <span>Dividend yield</span><span>${row.dividend_yield.toFixed(1)}%</span>
        <span>Trailing P/E</span><span>${peText}</span>
        <span>Volatility (annualized)</span><span>${row.volatility.toFixed(1)}%</span>
        <span>Sector</span><span>${row.sector}</span>
        <span>News sentiment</span><span>${row.article_count} articles scored</span>
      </div>
    </div>
  `;

  li.addEventListener("click", () => {
    li.querySelector(".details").classList.toggle("open");
  });

  return li;
}

async function loadRankings() {
  const res = await fetch("/api/rankings");
  const data = await res.json();

  statusEl.textContent = data.is_scanning
    ? "Scanning…"
    : `Last scanned ${fmtTimeAgo(data.generated_at)}`;
  refreshBtn.disabled = data.is_scanning;

  rankingsEl.innerHTML = "";
  if (!data.results.length) {
    rankingsEl.innerHTML = `<li class="empty">No results yet — the first scan takes a minute or two.</li>`;
    return;
  }
  data.results.forEach((row, i) => rankingsEl.appendChild(renderCard(row, i)));
}

refreshBtn.addEventListener("click", async () => {
  refreshBtn.disabled = true;
  statusEl.textContent = "Scanning…";
  await fetch("/api/refresh", { method: "POST" });
  poll();
});

function poll() {
  loadRankings();
  const interval = setInterval(async () => {
    const res = await fetch("/api/status");
    const status = await res.json();
    if (!status.is_scanning) {
      clearInterval(interval);
      loadRankings();
    }
  }, 4000);
}

loadRankings();
setInterval(loadRankings, 60000);

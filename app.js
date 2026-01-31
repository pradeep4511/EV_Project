document.addEventListener('DOMContentLoaded', function(){
  const select = document.getElementById('manufacturer');
  const card = document.getElementById('card');
  const nameEl = document.getElementById('c-name');
  const mAvg = document.getElementById('m-avg');
  const mPred = document.getElementById('m-pred');
  const mChange = document.getElementById('m-change');
  const mChangePct = document.getElementById('m-change-pct');
  const navOverview = document.getElementById('view-overview');
  const navInsights = document.getElementById('view-insights');
  const navVisuals = document.getElementById('view-visuals');
  const panelInsights = document.getElementById('insights');
  const panelVisuals = document.getElementById('visuals');
  const insightsList = document.getElementById('insights-list');
  const brandsBarCanvas = document.getElementById('brands-bar');
  const visualYearly = document.getElementById('visual-yearly');
  const visualTopManufacturers = document.getElementById('visual-top-manufacturers');
  const brandYearlyEl = document.getElementById('brand-yearly');

  let brandsBarChart = null;
  let yearlyChart = null;
  let topManChart = null;
  let brandYearlyChart = null;

  async function loadMetrics(){
    try{
      const res = await fetch('/api/metrics');
      const data = await res.json();
      return data;
    }catch(e){
      console.error('Failed to fetch metrics', e);
      return [];
    }
  }

  function formatNumber(n){
    if(n===null||n===undefined) return '-';
    return Intl.NumberFormat().format(Math.round(n));
  }

  function formatPct(n){
    if(n===null||n===undefined) return '-';
    return n.toFixed(2) + '%';
  }

  select.addEventListener('change', async function(){
    const val = select.value;
    if(!val){ card.classList.add('hidden'); return; }
    const metrics = await loadMetrics();
    const row = metrics.find(r => r.Manufacturer === val);
    if(!row){ card.classList.add('hidden'); return; }
    nameEl.textContent = row.Manufacturer;
    mAvg.textContent = formatNumber(row.Avg_2015_25);
    mPred.textContent = formatNumber(row.Predicted_2026);
    mChange.textContent = formatNumber(row.Change);
    mChangePct.textContent = formatPct(row.Change_pct);
    card.classList.remove('hidden');
    // render brand-specific yearly sales chart
    await renderBrandYearly(val);
  });

  // If server rendered with a selected result, trigger display
  const initial = select.value;
  if(initial){ select.dispatchEvent(new Event('change')); }

  // Navigation helpers
  function showPanel(panel){
    // hide all
    card.classList.add('hidden');
    panelInsights.classList.add('hidden');
    panelVisuals.classList.add('hidden');
    // clear active classes
    document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
    // show requested
    if(panel === 'overview') card.classList.remove('hidden');
    if(panel === 'insights') panelInsights.classList.remove('hidden');
    if(panel === 'visuals') panelVisuals.classList.remove('hidden');
  }

  navOverview.addEventListener('click', function(){ navOverview.classList.add('active'); showPanel('overview'); });
  navInsights.addEventListener('click', async function(){ navInsights.classList.add('active'); showPanel('insights'); await renderInsights(); });
  navVisuals.addEventListener('click', async function(){ navVisuals.classList.add('active'); showPanel('visuals'); await renderVisuals(); });

  async function renderInsights(){
    const metrics = await loadMetrics();
    if(!metrics || metrics.length===0){ insightsList.innerHTML = '<p>No data</p>'; return; }
    // top 5 gainers and top 5 losers by Change_pct
    const sortedDesc = [...metrics].sort((a,b) => b.Change_pct - a.Change_pct);
    const top = sortedDesc.slice(0,5);
    const bottom = sortedDesc.slice(-5).reverse();
    let html = '<div class="insight-block"><h3>Top 5 Gainers</h3><ul>';
    top.forEach(r=>{ html += `<li>${r.Manufacturer}: ${r.Change_pct.toFixed(2)}% (${Intl.NumberFormat().format(Math.round(r.Change))})</li>` });
    html += '</ul></div>';
    html += '<div class="insight-block"><h3>Top 5 Losers</h3><ul>';
    bottom.forEach(r=>{ html += `<li>${r.Manufacturer}: ${r.Change_pct.toFixed(2)}% (${Intl.NumberFormat().format(Math.round(r.Change))})</li>` });
    html += '</ul></div>';
    insightsList.innerHTML = html;
    // render the bar chart that shows raw change (Predicted_2026 - Avg_2015_25)
    await renderBrandsBar(metrics);
  }

  // Renders a horizontal bar chart of raw change per brand (can show positives and negatives)
  async function renderBrandsBar(metrics){
    if(!metrics || metrics.length===0) return;
    // sort by Change descending for clear ordering
    const sorted = [...metrics].sort((a,b) => b.Change - a.Change);
    const labels = sorted.map(r => r.Manufacturer);
    const values = sorted.map(r => Math.round(r.Change));
    const bg = values.map(v => v >= 0 ? 'rgba(45,212,191,0.9)' : 'rgba(255,99,132,0.9)');
    // destroy previous
    if(brandsBarChart){ brandsBarChart.destroy(); brandsBarChart = null; }
    const ctx = brandsBarCanvas.getContext('2d');
    brandsBarChart = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [{ label: 'Change (Units)', data: values, backgroundColor: bg }]
      },
      options: {
        indexAxis: 'y',
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: function(ctx){
                return Intl.NumberFormat().format(ctx.raw) + ' units';
              }
            }
          }
        },
        scales: {
          x: { ticks: { callback: v => Intl.NumberFormat().format(v) } }
        }
      }
    });
  }

  // Render year-wise sales for selected brand
  async function renderBrandYearly(manufacturer){
    try{
      const res = await fetch(`/api/brand/${encodeURIComponent(manufacturer)}`);
      const data = await res.json();
      if(data.error){ console.error(data.error); return; }

      if(brandYearlyChart){ brandYearlyChart.destroy(); brandYearlyChart = null; }
      if(!brandYearlyEl) return;
      brandYearlyChart = new Chart(brandYearlyEl.getContext('2d'), {
        type: 'line',
        data: { labels: data.years, datasets: [{ label: manufacturer + ' - Units Sold', data: data.units, borderColor: 'rgba(34,197,94,0.9)', backgroundColor: 'rgba(34,197,94,0.12)', fill:true, tension:0.25, pointRadius:3 }] },
        options: { responsive:true, maintainAspectRatio:false, plugins:{legend:{display:true}}, scales:{y:{ticks:{callback: v => Intl.NumberFormat().format(v)}}} }
      });
    }catch(e){ console.error('Failed to load brand yearly data', e); }
  }

  // Render multiple visuals based on /api/insights
  async function renderVisuals(){
    try{
      const res = await fetch('/api/insights');
      const data = await res.json();
      if(data.error){ console.error(data.error); return; }

      // Yearly sales line
      if(yearlyChart){ yearlyChart.destroy(); yearlyChart = null; }
      yearlyChart = new Chart(visualYearly.getContext('2d'), {
        type: 'line',
        data: { labels: data.yearly_sales.years, datasets: [{ label: 'Avg Units Sold', data: data.yearly_sales.avg_units, borderColor: 'rgba(96,165,250,0.9)', backgroundColor: 'rgba(96,165,250,0.12)', fill: true, tension: 0.2, pointRadius:4 }] },
        options: { responsive:true, maintainAspectRatio:false, plugins:{legend:{display:false}} }
      });

      // Top manufacturers bar
      if(topManChart){ topManChart.destroy(); topManChart = null; }
      topManChart = new Chart(visualTopManufacturers.getContext('2d'), {
        type: 'bar',
        data: { labels: data.top_manufacturers.labels, datasets: [{ label: 'Units Sold (2024)', data: data.top_manufacturers.values, backgroundColor: 'rgba(45,212,191,0.9)' }] },
        options: { responsive:true, maintainAspectRatio:false, plugins:{legend:{display:false}}, scales:{y:{ticks:{callback: v => Intl.NumberFormat().format(v)}}} }
      });

    }catch(e){ console.error('Failed to load visuals', e); }
  }
});

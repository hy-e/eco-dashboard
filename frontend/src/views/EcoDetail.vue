<template>
  <div class="page">
    <!-- Top bar -->
    <header class="topbar">
      <div class="topbar-inner">
        <button class="back-btn" @click="$router.back()">← 뒤로</button>
        <div class="eco-info" v-if="ecoMeta">
          <span class="eco-no">{{ ecoMeta.eco_no }}</span>
          <span class="eco-desc">{{ ecoMeta.eco_desc }}</span>
          <span class="badge process">{{ ecoMeta.process_id }}</span>
          <span class="badge step">{{ ecoMeta.step_seq }}</span>
          <span class="status-chip" :class="ecoMeta.status === 'DONE' ? 'done' : 'progress'">
            {{ ecoMeta.status === 'DONE' ? '완료' : '진행중' }}
          </span>
        </div>
        <div class="topbar-right">상세 변경점 분석</div>
      </div>
    </header>

    <main class="main" v-if="analysis">
      <!-- Summary strip -->
      <div class="strip">
        <div class="strip-item">
          <span class="strip-label">분석 파라미터</span>
          <span class="strip-value">{{ analysis.total_params }}</span>
        </div>
        <div class="strip-divider"></div>
        <div class="strip-item highlight">
          <span class="strip-label">유의차 검출</span>
          <span class="strip-value">{{ analysis.detected_params }}</span>
        </div>
        <div class="strip-divider"></div>
        <div class="strip-item">
          <span class="strip-label">검출률</span>
          <span class="strip-value">{{ analysis.detection_rate }}%</span>
        </div>
        <div class="strip-spacer"></div>
        <div class="toggle-wrap">
          <button :class="['toggle-btn', { active: !showAll }]" @click="showAll = false">유의차만</button>
          <button :class="['toggle-btn', { active: showAll }]"  @click="showAll = true">전체 보기</button>
        </div>
      </div>

      <!-- Significant items table -->
      <div class="card">
        <div class="card-title">유의차 분석 결과</div>
        <div class="tbl-wrap">
          <table class="tbl">
            <thead>
              <tr>
                <th>Parameter</th>
                <th>Category</th>
                <th>Unit</th>
                <th>Ref Avg</th>
                <th>ECO Avg</th>
                <th>Ref Std</th>
                <th>ECO Std</th>
                <th>Δ (avg)</th>
                <th>Δ%</th>
                <th>유의 지표</th>
                <th>유의도</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="item in visibleItems"
                :key="item.parameter"
                :class="{ selected: selectedParam === item.parameter }"
                @click="selectParam(item)"
              >
                <td class="mono">{{ item.parameter }}</td>
                <td>{{ item.category }}</td>
                <td class="unit">{{ item.unit }}</td>
                <td class="num">{{ item.ref_stats.avg }}</td>
                <td class="num eco-val">{{ item.eco_stats.avg }}</td>
                <td class="num muted">{{ item.ref_stats.std }}</td>
                <td class="num muted">{{ item.eco_stats.std }}</td>
                <td class="num" :class="deltaClass(item.delta_avg)">
                  {{ item.delta_avg > 0 ? '+' : '' }}{{ item.delta_avg }}
                </td>
                <td class="num" :class="deltaClass(item.delta_pct)">
                  {{ item.delta_pct > 0 ? '+' : '' }}{{ item.delta_pct }}%
                </td>
                <td>
                  <span v-for="m in item.sig_metrics" :key="m" class="metric-badge">{{ m }}</span>
                  <span v-if="!item.sig_metrics.length" class="muted">-</span>
                </td>
                <td>
                  <span class="sig-chip" :class="item.significance.toLowerCase()">
                    {{ item.significance }}
                  </span>
                </td>
              </tr>
              <tr v-if="visibleItems.length === 0">
                <td colspan="11" class="empty">검출된 유의차 항목이 없습니다.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Chart panel -->
      <div class="card chart-panel" v-if="selectedParam && itemData">
        <div class="chart-panel-header">
          <div class="chart-panel-title">
            <span class="chart-param">{{ selectedParam }}</span>
            <span class="chart-unit">({{ itemData.unit }})</span>
            <span class="sig-chip" :class="itemData.significance.toLowerCase()">
              {{ itemData.significance }}
            </span>
          </div>
          <button class="close-btn" @click="selectedParam = null; itemData = null">✕</button>
        </div>

        <div v-if="loadingChart" class="chart-loading">차트 데이터 로딩 중...</div>

        <div v-else class="chart-grid">
          <!-- Time Series -->
          <div class="chart-wrap">
            <div class="chart-label">Time Series — ECO vs Ref</div>
            <e-chart :option="timeSeriesOpt" height="280px" />
          </div>
          <!-- Box Plot -->
          <div class="chart-wrap">
            <div class="chart-label">Box Plot</div>
            <e-chart :option="boxPlotOpt" height="280px" />
          </div>
          <!-- CDF -->
          <div class="chart-wrap">
            <div class="chart-label">CDF</div>
            <e-chart :option="cdfOpt" height="280px" />
          </div>
        </div>
      </div>
    </main>

    <div v-else class="loading-page">데이터 로딩 중...</div>
  </div>
</template>

<script>
import EChart from '@/components/EChart.vue';
import { fetchEcos, fetchEcoAnalysis, fetchItemData } from '@/api';

const CHART_COLORS = {
  ref:    '#8890a4',
  eco:    '#4f8ef7',
  grid:   '#2d3448',
  text:   '#8890a4',
  legend: '#c8ccd8',
};

function cdf(values) {
  const s = [...values].sort((a, b) => a - b);
  return s.map((v, i) => [v, parseFloat(((i + 1) / s.length).toFixed(4))]);
}

function baseAxis(name) {
  return {
    name, nameTextStyle: { color: CHART_COLORS.text, fontSize: 10 },
    axisLabel: { color: CHART_COLORS.text, fontSize: 10 },
    splitLine: { lineStyle: { color: CHART_COLORS.grid } },
    axisLine: { lineStyle: { color: CHART_COLORS.grid } },
  };
}

export default {
  name: 'EcoDetail',
  components: { EChart },
  data() {
    return {
      ecoMeta: null,
      analysis: null,
      showAll: false,
      selectedParam: null,
      itemData: null,
      loadingChart: false,
    };
  },
  computed: {
    visibleItems() {
      if (!this.analysis) return [];
      return this.showAll
        ? this.analysis.items
        : this.analysis.items.filter(i => i.significance !== 'NONE');
    },

    timeSeriesOpt() {
      if (!this.itemData) return {};
      const { ref_data, eco_data, ref_stats, eco_stats, unit } = this.itemData;
      const fmt = (v) => parseFloat(v).toFixed(4);
      return {
        backgroundColor: 'transparent',
        legend: { data: ['Ref', 'ECO'], textStyle: { color: CHART_COLORS.legend }, top: 4, right: 8 },
        tooltip: {
          trigger: 'item',
          backgroundColor: '#1e2433',
          borderColor: '#2d3448',
          textStyle: { color: '#c8ccd8', fontSize: 12 },
          formatter: (p) => {
            const d = new Date(p.value[0]);
            const dt = `${d.getMonth()+1}/${d.getDate()} ${d.getHours()}:${String(d.getMinutes()).padStart(2,'0')}`;
            return `<b>${p.seriesName}</b><br/>${dt}<br/>${fmt(p.value[1])} ${unit}`;
          },
        },
        grid: { top: 40, right: 20, bottom: 44, left: 64 },
        xAxis: { type: 'time', ...baseAxis(''),
          axisLabel: {
            color: CHART_COLORS.text, fontSize: 10,
            formatter: (v) => { const d = new Date(v); return `${d.getMonth()+1}/${d.getDate()}`; },
          },
        },
        yAxis: { type: 'value', ...baseAxis(unit) },
        series: [
          {
            name: 'Ref', type: 'scatter', symbolSize: 6,
            data: ref_data.map(d => [d.time, d.value]),
            itemStyle: { color: CHART_COLORS.ref, opacity: 0.75 },
            markLine: {
              silent: true, symbol: 'none',
              lineStyle: { color: CHART_COLORS.ref, type: 'dashed', width: 1.5 },
              label: { color: CHART_COLORS.ref, fontSize: 10, formatter: `μ=${fmt(ref_stats.avg)}` },
              data: [{ yAxis: ref_stats.avg }],
            },
          },
          {
            name: 'ECO', type: 'scatter', symbolSize: 6,
            data: eco_data.map(d => [d.time, d.value]),
            itemStyle: { color: CHART_COLORS.eco, opacity: 0.85 },
            markLine: {
              silent: true, symbol: 'none',
              lineStyle: { color: CHART_COLORS.eco, type: 'dashed', width: 1.5 },
              label: { color: CHART_COLORS.eco, fontSize: 10, formatter: `μ=${fmt(eco_stats.avg)}` },
              data: [{ yAxis: eco_stats.avg }],
            },
          },
        ],
      };
    },

    boxPlotOpt() {
      if (!this.itemData) return {};
      const { ref_stats: r, eco_stats: e, unit } = this.itemData;
      const mkBox = (s) => [s.min, s.q1, s.med, s.q3, s.max];
      return {
        backgroundColor: 'transparent',
        legend: { data: ['Ref', 'ECO'], textStyle: { color: CHART_COLORS.legend }, top: 4, right: 8 },
        tooltip: {
          trigger: 'item',
          backgroundColor: '#1e2433',
          borderColor: '#2d3448',
          textStyle: { color: '#c8ccd8', fontSize: 11 },
          formatter: (p) => {
            const [, min, q1, med, q3, max] = p.value;
            return `<b>${p.seriesName}</b><br/>Max: ${max}<br/>Q3: ${q3}<br/>Med: ${med}<br/>Q1: ${q1}<br/>Min: ${min}`;
          },
        },
        grid: { top: 40, right: 20, bottom: 44, left: 64 },
        xAxis: {
          type: 'category', data: ['Ref', 'ECO'],
          axisLabel: { color: CHART_COLORS.legend, fontSize: 12 },
          axisLine: { lineStyle: { color: CHART_COLORS.grid } },
        },
        yAxis: { type: 'value', ...baseAxis(unit) },
        series: [
          {
            name: 'Ref', type: 'boxplot',
            data: [mkBox(r)],
            itemStyle: { borderColor: CHART_COLORS.ref, borderWidth: 2, color: 'rgba(136,144,164,0.15)' },
            encode: { x: 0, y: [1,2,3,4,5] },
          },
          {
            name: 'ECO', type: 'boxplot',
            data: [mkBox(e)],
            itemStyle: { borderColor: CHART_COLORS.eco, borderWidth: 2, color: 'rgba(79,142,247,0.15)' },
            encode: { x: 0, y: [1,2,3,4,5] },
          },
        ],
      };
    },

    cdfOpt() {
      if (!this.itemData) return {};
      const { ref_data, eco_data, unit } = this.itemData;
      const refCdf = cdf(ref_data.map(d => d.value));
      const ecoCdf = cdf(eco_data.map(d => d.value));
      return {
        backgroundColor: 'transparent',
        legend: { data: ['Ref', 'ECO'], textStyle: { color: CHART_COLORS.legend }, top: 4, right: 8 },
        tooltip: {
          trigger: 'axis',
          backgroundColor: '#1e2433',
          borderColor: '#2d3448',
          textStyle: { color: '#c8ccd8', fontSize: 11 },
          formatter: (params) =>
            params.map(p => `${p.marker}${p.seriesName}: ${p.value[0]} ${unit} → ${(p.value[1]*100).toFixed(1)}%`).join('<br/>'),
        },
        grid: { top: 40, right: 20, bottom: 44, left: 64 },
        xAxis: { type: 'value', ...baseAxis(unit) },
        yAxis: {
          type: 'value', min: 0, max: 1, ...baseAxis('누적확률'),
          axisLabel: {
            color: CHART_COLORS.text, fontSize: 10,
            formatter: (v) => `${(v * 100).toFixed(0)}%`,
          },
        },
        series: [
          {
            name: 'Ref', type: 'line', step: 'end', symbol: 'none',
            data: refCdf,
            lineStyle: { color: CHART_COLORS.ref, width: 2 },
            areaStyle: { color: 'rgba(136,144,164,0.06)' },
          },
          {
            name: 'ECO', type: 'line', step: 'end', symbol: 'none',
            data: ecoCdf,
            lineStyle: { color: CHART_COLORS.eco, width: 2 },
            areaStyle: { color: 'rgba(79,142,247,0.06)' },
          },
        ],
      };
    },
  },
  created() { this.init(); },
  methods: {
    async init() {
      const ecoNo = this.$route.params.ecoNo;
      const [ecoRes, analRes] = await Promise.all([
        fetchEcos({ eco_no: ecoNo }),
        fetchEcoAnalysis(ecoNo),
      ]);
      this.ecoMeta  = ecoRes.data.items[0] || null;
      this.analysis = analRes.data;
    },
    async selectParam(item) {
      if (this.selectedParam === item.parameter) {
        this.selectedParam = null;
        this.itemData = null;
        return;
      }
      this.selectedParam = item.parameter;
      this.itemData = null;
      this.loadingChart = true;
      try {
        const { data } = await fetchItemData(this.$route.params.ecoNo, item.parameter);
        this.itemData = data;
      } finally {
        this.loadingChart = false;
      }
      this.$nextTick(() => {
        const el = this.$el.querySelector('.chart-panel');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
      });
    },
    deltaClass(v) { return v > 0 ? 'delta-up' : v < 0 ? 'delta-down' : ''; },
  },
};
</script>

<style scoped>
.page { min-height: 100vh; background: #111520; }
.topbar { background: #161b27; border-bottom: 1px solid #2d3448; position: sticky; top: 0; z-index: 100; }
.topbar-inner { max-width: 1400px; margin: 0 auto; padding: 0 20px; height: 52px; display: flex; align-items: center; gap: 16px; }
.back-btn { background: #2d3448; border: none; border-radius: 6px; color: #c8ccd8; padding: 5px 12px; font-size: 13px; cursor: pointer; white-space: nowrap; }
.back-btn:hover { background: #3a4260; }
.eco-info { display: flex; align-items: center; gap: 8px; flex: 1; flex-wrap: wrap; }
.eco-no { font-family: monospace; color: #4f8ef7; font-size: 14px; font-weight: 700; }
.eco-desc { color: #8890a4; font-size: 12px; }
.topbar-right { font-size: 12px; color: #55607a; margin-left: auto; white-space: nowrap; }

.badge { display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 600; }
.badge.process { background: #1e3260; color: #7eb3ff; }
.badge.step    { background: #1e3040; color: #5ecfb0; }
.status-chip   { display: inline-block; padding: 3px 10px; border-radius: 12px; font-size: 11px; font-weight: 600; }
.status-chip.done     { background: #0d3326; color: #3ecf8e; }
.status-chip.progress { background: #2e2810; color: #f7c948; }

.main { max-width: 1400px; margin: 0 auto; padding: 20px 24px; display: flex; flex-direction: column; gap: 16px; }
.loading-page { display: flex; align-items: center; justify-content: center; height: 60vh; color: #8890a4; }

.strip { background: #1e2433; border: 1px solid #2d3448; border-radius: 8px; padding: 14px 24px; display: flex; align-items: center; gap: 24px; flex-wrap: wrap; }
.strip-item { display: flex; flex-direction: column; gap: 2px; }
.strip-item.highlight .strip-value { color: #4f8ef7; }
.strip-label { font-size: 11px; color: #8890a4; text-transform: uppercase; letter-spacing: 0.05em; }
.strip-value { font-size: 24px; font-weight: 700; color: #e8eaf0; }
.strip-divider { width: 1px; height: 40px; background: #2d3448; }
.strip-spacer { flex: 1; }
.toggle-wrap { display: flex; border: 1px solid #2d3448; border-radius: 6px; overflow: hidden; }
.toggle-btn { background: transparent; border: none; color: #8890a4; padding: 6px 14px; font-size: 12px; cursor: pointer; transition: background 0.15s, color 0.15s; }
.toggle-btn.active { background: #2d3448; color: #e8eaf0; }

.card { background: #1e2433; border: 1px solid #2d3448; border-radius: 8px; padding: 16px 20px; }
.card-title { font-size: 13px; font-weight: 600; color: #8890a4; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 14px; }

.tbl-wrap { overflow-x: auto; }
.tbl { width: 100%; border-collapse: collapse; font-size: 12px; }
.tbl th { background: #161b27; color: #8890a4; font-weight: 600; text-align: left; padding: 8px 12px; border-bottom: 1px solid #2d3448; white-space: nowrap; }
.tbl td { padding: 8px 12px; border-bottom: 1px solid #1e2433; color: #c8ccd8; vertical-align: middle; }
.tbl tbody tr { cursor: pointer; transition: background 0.15s; }
.tbl tbody tr:hover { background: #1a2033; }
.tbl tbody tr.selected { background: #1a2540; }
.mono { font-family: monospace; color: #4f8ef7; }
.unit { color: #8890a4; }
.num { text-align: right; font-variant-numeric: tabular-nums; }
.muted { color: #55607a; }
.eco-val { color: #7eb3ff; }
.delta-up { color: #f76060; font-weight: 600; }
.delta-down { color: #3ecf8e; font-weight: 600; }
.metric-badge { display: inline-block; background: #1a2a50; color: #7eb3ff; border-radius: 3px; padding: 1px 5px; font-size: 10px; margin-right: 3px; }
.sig-chip { display: inline-block; padding: 3px 8px; border-radius: 4px; font-size: 11px; font-weight: 600; }
.sig-chip.high   { background: #3a1010; color: #f76060; }
.sig-chip.medium { background: #2e2810; color: #f7c948; }
.sig-chip.low    { background: #102040; color: #4f8ef7; }
.sig-chip.none   { background: #0d3326; color: #3ecf8e; }
.empty { text-align: center; color: #55607a; padding: 32px; }

.chart-panel { }
.chart-panel-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 14px; padding-bottom: 12px; border-bottom: 1px solid #2d3448; }
.chart-panel-title { display: flex; align-items: center; gap: 8px; }
.chart-param { font-family: monospace; font-size: 15px; font-weight: 700; color: #e8eaf0; }
.chart-unit { font-size: 12px; color: #8890a4; }
.close-btn { background: none; border: 1px solid #2d3448; border-radius: 6px; color: #8890a4; padding: 4px 10px; cursor: pointer; font-size: 13px; }
.close-btn:hover { background: #2d3448; color: #e8eaf0; }
.chart-loading { text-align: center; color: #8890a4; padding: 60px 0; }
.chart-grid { display: grid; grid-template-columns: 2fr 1fr 1fr; gap: 16px; }
.chart-wrap { background: #161b27; border: 1px solid #2d3448; border-radius: 6px; padding: 12px 8px 8px; }
.chart-label { font-size: 11px; color: #8890a4; text-align: center; margin-bottom: 6px; letter-spacing: 0.04em; }

@media (max-width: 900px) { .chart-grid { grid-template-columns: 1fr; } }
</style>

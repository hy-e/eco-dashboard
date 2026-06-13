<template>
  <div id="app">
    <header class="topbar">
      <div class="topbar-inner">
        <div class="logo"><span class="logo-mark">◈</span> ECO Change Analysis Dashboard</div>
        <div class="topbar-right">반도체 공정 ECO 변경점 분석</div>
      </div>
    </header>

    <main class="main">
      <section class="stats-row">
        <stat-card label="전체 ECO" :value="stats.total_ecos" variant="primary" />
        <stat-card label="분석 완료" :value="stats.done_ecos" :sub="`전체 대비 ${doneRate}%`" variant="success" />
        <stat-card label="진행 중" :value="stats.in_progress" variant="warning" />
        <div class="progress-bar-wrap">
          <div class="progress-label">완료율</div>
          <div class="progress-track">
            <div class="progress-fill" :style="{ width: doneRate + '%' }"></div>
          </div>
          <div class="progress-pct">{{ doneRate }}%</div>
        </div>
      </section>

      <section class="filter-row">
        <div class="filter-group">
          <label>ECO No.</label>
          <input v-model="filterEcoNo" placeholder="예) ECO-2024-0001" @input="onFilter" />
        </div>
        <div class="filter-group">
          <label>Step Seq</label>
          <select v-model="filterStepSeq" @change="onFilter">
            <option value="">전체</option>
            <option v-for="s in stepSeqs" :key="s" :value="s">{{ s }}</option>
          </select>
        </div>
        <button class="reset-btn" @click="resetFilter">초기화</button>
        <div class="filter-result">{{ ecoList.length }}건</div>
      </section>

      <section class="content-row">
        <div class="table-section">
          <div class="section-title">ECO 분석 목록</div>
          <eco-table :items="ecoList" :selected-eco="selectedEco" @select="onSelectEco" />
        </div>
        <div class="summary-section">
          <div class="section-title">분석 Summary</div>
          <eco-summary :eco="selectedEco" />
        </div>
      </section>
    </main>
  </div>
</template>

<script>
import StatCard from '@/components/StatCard.vue';
import EcoTable from '@/components/EcoTable.vue';
import EcoSummary from '@/components/EcoSummary.vue';
import { fetchStats, fetchStepSeqs, fetchEcos } from '@/api';

export default {
  name: 'Dashboard',
  components: { StatCard, EcoTable, EcoSummary },
  data() {
    return {
      stats: { total_ecos: 0, done_ecos: 0, in_progress: 0 },
      stepSeqs: [], ecoList: [], selectedEco: null,
      filterEcoNo: '', filterStepSeq: '', _timer: null,
    };
  },
  computed: {
    doneRate() {
      return this.stats.total_ecos
        ? Math.round((this.stats.done_ecos / this.stats.total_ecos) * 100)
        : 0;
    },
  },
  created() { this.init(); },
  methods: {
    async init() {
      const [s, q] = await Promise.all([fetchStats(), fetchStepSeqs()]);
      this.stats = s.data;
      this.stepSeqs = q.data;
      await this.loadEcos();
    },
    async loadEcos() {
      const params = {};
      if (this.filterEcoNo)   params.eco_no   = this.filterEcoNo;
      if (this.filterStepSeq) params.step_seq = this.filterStepSeq;
      const { data } = await fetchEcos(params);
      this.ecoList = data.items;
      if (this.selectedEco && !this.ecoList.find(e => e.eco_no === this.selectedEco.eco_no))
        this.selectedEco = null;
    },
    onFilter() {
      clearTimeout(this._timer);
      this._timer = setTimeout(this.loadEcos, 300);
    },
    resetFilter() { this.filterEcoNo = ''; this.filterStepSeq = ''; this.loadEcos(); },
    onSelectEco(eco) {
      this.selectedEco = this.selectedEco?.eco_no === eco.eco_no ? null : eco;
    },
  },
};
</script>

<style scoped>
#app { min-height: 100vh; }
.topbar { background: #161b27; border-bottom: 1px solid #2d3448; position: sticky; top: 0; z-index: 100; }
.topbar-inner { max-width: 1400px; margin: 0 auto; padding: 0 24px; height: 52px; display: flex; align-items: center; justify-content: space-between; }
.logo { font-size: 16px; font-weight: 700; color: #e8eaf0; display: flex; align-items: center; gap: 8px; }
.logo-mark { color: #4f8ef7; font-size: 18px; }
.topbar-right { font-size: 12px; color: #55607a; }
.main { max-width: 1400px; margin: 0 auto; padding: 24px; display: flex; flex-direction: column; gap: 20px; }
.stats-row { display: flex; gap: 16px; align-items: center; flex-wrap: wrap; }
.progress-bar-wrap { flex: 1; min-width: 180px; display: flex; align-items: center; gap: 10px; }
.progress-label { font-size: 12px; color: #8890a4; white-space: nowrap; }
.progress-track { flex: 1; height: 8px; background: #2d3448; border-radius: 4px; overflow: hidden; }
.progress-fill { height: 100%; background: linear-gradient(90deg, #3ecf8e, #4f8ef7); border-radius: 4px; transition: width 0.6s ease; }
.progress-pct { font-size: 13px; color: #3ecf8e; font-weight: 600; white-space: nowrap; }
.filter-row { background: #1e2433; border: 1px solid #2d3448; border-radius: 8px; padding: 14px 20px; display: flex; align-items: center; gap: 16px; flex-wrap: wrap; }
.filter-group { display: flex; align-items: center; gap: 8px; }
.filter-group label { font-size: 12px; color: #8890a4; white-space: nowrap; }
.filter-group input, .filter-group select { background: #161b27; border: 1px solid #2d3448; border-radius: 6px; color: #e8eaf0; padding: 6px 10px; font-size: 13px; outline: none; transition: border-color 0.2s; }
.filter-group input:focus, .filter-group select:focus { border-color: #4f8ef7; }
.filter-group input { width: 200px; }
.reset-btn { background: #2d3448; border: none; border-radius: 6px; color: #c8ccd8; padding: 6px 14px; font-size: 13px; cursor: pointer; transition: background 0.2s; }
.reset-btn:hover { background: #3a4260; }
.filter-result { margin-left: auto; font-size: 13px; color: #8890a4; }
.content-row { display: grid; grid-template-columns: 1fr 340px; gap: 20px; align-items: start; }
.table-section, .summary-section { background: #1e2433; border: 1px solid #2d3448; border-radius: 8px; padding: 16px 20px; }
.section-title { font-size: 13px; font-weight: 600; color: #8890a4; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 14px; }
@media (max-width: 900px) { .content-row { grid-template-columns: 1fr; } }
</style>

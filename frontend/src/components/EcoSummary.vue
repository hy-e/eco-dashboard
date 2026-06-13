<template>
  <div class="summary-panel">
    <div v-if="!eco" class="summary-empty">
      <div class="empty-icon">📋</div>
      <p>ECO를 선택하면 분석 summary가 표시됩니다.</p>
    </div>

    <template v-else>
      <div class="summary-header">
        <span class="eco-label">{{ eco.eco_no }}</span>
        <span class="summary-title">분석 Summary</span>
      </div>

      <div v-if="loading" class="loading">로딩 중...</div>

      <template v-else-if="summary">
        <div class="summary-stats">
          <div class="sstat">
            <div class="sstat-label">분석 항목</div>
            <div class="sstat-value">{{ summary.total_items }}</div>
          </div>
          <div class="sstat highlight">
            <div class="sstat-label">검출 항목</div>
            <div class="sstat-value">{{ summary.detected_items }}</div>
          </div>
          <div class="sstat">
            <div class="sstat-label">검출률</div>
            <div class="sstat-value">{{ summary.detection_rate }}%</div>
          </div>
        </div>

        <div class="donut-wrap">
          <svg viewBox="0 0 120 120" class="donut">
            <circle cx="60" cy="60" r="48" fill="none" stroke="#2d3448" stroke-width="14"/>
            <circle
              cx="60" cy="60" r="48" fill="none"
              stroke="#4f8ef7" stroke-width="14"
              stroke-dasharray="301.6"
              :stroke-dashoffset="301.6 * (1 - summary.detection_rate / 100)"
              stroke-linecap="round"
              transform="rotate(-90 60 60)"
              style="transition: stroke-dashoffset 0.6s ease"
            />
            <text x="60" y="56" text-anchor="middle" font-size="18" font-weight="700" fill="#e8eaf0">
              {{ summary.detection_rate }}%
            </text>
            <text x="60" y="72" text-anchor="middle" font-size="9" fill="#8890a4">검출률</text>
          </svg>
        </div>

        <div class="items-title">카테고리별 분석 결과</div>
        <div class="item-list">
          <div
            v-for="item in summary.items"
            :key="item.category"
            class="item-row"
          >
            <div class="item-cat">{{ item.category }}</div>
            <div class="item-bar-wrap">
              <div
                class="item-bar"
                :style="{ width: (item.detected / item.total * 100) + '%', background: barColor(item.significance) }"
              ></div>
            </div>
            <div class="item-counts">{{ item.detected }}/{{ item.total }}</div>
            <div class="item-rate" :class="rateClass(item.change_rate)">
              {{ item.change_rate > 0 ? '+' : '' }}{{ item.change_rate }}%
            </div>
            <div class="sig-chip" :class="item.significance.toLowerCase()">{{ item.significance }}</div>
          </div>
        </div>
      </template>
    </template>
  </div>
</template>

<script>
import { fetchEcoSummary } from '@/api';

export default {
  name: 'EcoSummary',
  props: {
    eco: { type: Object, default: null },
  },
  data() {
    return { summary: null, loading: false };
  },
  watch: {
    eco(val) {
      if (val) this.load(val.eco_no);
      else this.summary = null;
    },
  },
  methods: {
    async load(ecoNo) {
      this.loading = true;
      this.summary = null;
      try {
        const { data } = await fetchEcoSummary(ecoNo);
        this.summary = data;
      } finally {
        this.loading = false;
      }
    },
    barColor(sig) {
      return { HIGH: '#f76060', MEDIUM: '#f7c948', LOW: '#4f8ef7', NONE: '#3ecf8e' }[sig] || '#4f8ef7';
    },
    rateClass(rate) {
      if (rate > 0) return 'up';
      if (rate < 0) return 'down';
      return '';
    },
  },
};
</script>

<style scoped>
.summary-panel {
  background: #1e2433;
  border: 1px solid #2d3448;
  border-radius: 8px;
  padding: 20px;
  height: 100%;
  min-height: 400px;
}
.summary-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #55607a;
  font-size: 13px;
  gap: 12px;
  min-height: 300px;
}
.empty-icon { font-size: 36px; }
.summary-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #2d3448;
}
.eco-label { font-family: monospace; color: #4f8ef7; font-size: 13px; font-weight: 600; }
.summary-title { color: #e8eaf0; font-size: 14px; font-weight: 600; }
.loading { color: #8890a4; font-size: 13px; padding: 20px 0; }
.summary-stats {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
}
.sstat {
  flex: 1;
  background: #161b27;
  border-radius: 6px;
  padding: 12px;
  text-align: center;
}
.sstat.highlight { background: #1a2540; border: 1px solid #2d4080; }
.sstat-label { font-size: 11px; color: #8890a4; margin-bottom: 4px; }
.sstat-value { font-size: 22px; font-weight: 700; color: #e8eaf0; }
.donut-wrap { display: flex; justify-content: center; margin: 8px 0 16px; }
.donut { width: 110px; height: 110px; }
.items-title { font-size: 12px; color: #8890a4; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 10px; }
.item-list { display: flex; flex-direction: column; gap: 7px; }
.item-row {
  display: grid;
  grid-template-columns: 60px 1fr 44px 48px 54px;
  align-items: center;
  gap: 8px;
}
.item-cat { font-size: 12px; color: #c8ccd8; }
.item-bar-wrap { background: #161b27; border-radius: 4px; height: 6px; overflow: hidden; }
.item-bar { height: 100%; border-radius: 4px; transition: width 0.4s ease; }
.item-counts { font-size: 11px; color: #8890a4; text-align: right; }
.item-rate { font-size: 11px; font-weight: 600; text-align: right; }
.item-rate.up { color: #f76060; }
.item-rate.down { color: #3ecf8e; }
.sig-chip {
  font-size: 10px;
  font-weight: 600;
  padding: 2px 6px;
  border-radius: 4px;
  text-align: center;
}
.sig-chip.high { background: #3a1010; color: #f76060; }
.sig-chip.medium { background: #2e2810; color: #f7c948; }
.sig-chip.low { background: #102040; color: #4f8ef7; }
.sig-chip.none { background: #0d3326; color: #3ecf8e; }
</style>

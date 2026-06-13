<template>
  <div class="stat-card" :class="variant">
    <div class="stat-label">{{ label }}</div>
    <div class="stat-value">{{ value }}</div>
    <div v-if="sub" class="stat-sub">{{ sub }}</div>
  </div>
</template>

<script>
export default {
  name: 'StatCard',
  props: {
    label: String,
    value: [String, Number],
    sub: String,
    variant: { type: String, default: 'default' },
  },
};
</script>

<style scoped>
.stat-card {
  background: #1e2433;
  border: 1px solid #2d3448;
  border-radius: 8px;
  padding: 20px 24px;
  min-width: 140px;
}
.stat-card.primary { border-left: 3px solid #4f8ef7; }
.stat-card.success { border-left: 3px solid #3ecf8e; }
.stat-card.warning { border-left: 3px solid #f7c948; }
.stat-label { font-size: 12px; color: #8890a4; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 8px; }
.stat-value { font-size: 28px; font-weight: 700; color: #e8eaf0; }
.stat-sub { font-size: 12px; color: #8890a4; margin-top: 4px; }
</style>

<template>
  <div ref="el" :style="{ width: '100%', height: height }"></div>
</template>

<script>
import * as echarts from 'echarts';

export default {
  name: 'EChart',
  props: {
    option: { type: Object, required: true },
    height: { type: String, default: '280px' },
  },
  data() {
    return { _chart: null };
  },
  mounted() {
    this._chart = echarts.init(this.$refs.el);
    this._chart.setOption(this.option);
    this._onResize = () => this._chart && this._chart.resize();
    window.addEventListener('resize', this._onResize);
  },
  beforeDestroy() {
    window.removeEventListener('resize', this._onResize);
    if (this._chart) { this._chart.dispose(); this._chart = null; }
  },
  watch: {
    option(val) {
      if (this._chart) this._chart.setOption(val, { notMerge: true });
    },
  },
};
</script>

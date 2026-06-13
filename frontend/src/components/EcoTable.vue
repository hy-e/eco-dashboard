<template>
  <div class="eco-table-wrap">
    <table class="eco-table">
      <thead>
        <tr>
          <th>ECO No.</th>
          <th>Process</th>
          <th>Step Seq</th>
          <th>Description</th>
          <th>진행 Lot</th>
          <th>EDS Lot</th>
          <th>상태</th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="eco in items"
          :key="eco.eco_no"
          :class="{ selected: selectedEco && selectedEco.eco_no === eco.eco_no }"
          @click="$emit('select', eco)"
        >
          <td class="mono">{{ eco.eco_no }}</td>
          <td><span class="badge process">{{ eco.process_id }}</span></td>
          <td><span class="badge step">{{ eco.step_seq }}</span></td>
          <td class="desc">{{ eco.eco_desc }}</td>
          <td class="num">{{ eco.lot_count }}</td>
          <td class="num">{{ eco.eds_lot_count }}</td>
          <td>
            <span class="status-chip" :class="eco.status === 'DONE' ? 'done' : 'progress'">
              {{ eco.status === 'DONE' ? '완료' : '진행중' }}
            </span>
          </td>
        </tr>
        <tr v-if="items.length === 0">
          <td colspan="7" class="empty">검색 결과가 없습니다.</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
export default {
  name: 'EcoTable',
  props: {
    items: { type: Array, default: () => [] },
    selectedEco: { type: Object, default: null },
  },
};
</script>

<style scoped>
.eco-table-wrap { overflow-x: auto; }
.eco-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}
.eco-table th {
  background: #161b27;
  color: #8890a4;
  font-weight: 600;
  text-align: left;
  padding: 10px 14px;
  border-bottom: 1px solid #2d3448;
  white-space: nowrap;
}
.eco-table td {
  padding: 10px 14px;
  border-bottom: 1px solid #1e2433;
  color: #c8ccd8;
  vertical-align: middle;
}
.eco-table tbody tr { cursor: pointer; transition: background 0.15s; }
.eco-table tbody tr:hover { background: #1e2433; }
.eco-table tbody tr.selected { background: #1a2540; }
.mono { font-family: 'Courier New', monospace; color: #4f8ef7; }
.desc { max-width: 260px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.num { text-align: right; font-variant-numeric: tabular-nums; }
.badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 600;
}
.badge.process { background: #1e3260; color: #7eb3ff; }
.badge.step { background: #1e3040; color: #5ecfb0; }
.status-chip {
  display: inline-block;
  padding: 3px 10px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 600;
}
.status-chip.done { background: #0d3326; color: #3ecf8e; }
.status-chip.progress { background: #2e2810; color: #f7c948; }
.empty { text-align: center; color: #55607a; padding: 32px; }
</style>

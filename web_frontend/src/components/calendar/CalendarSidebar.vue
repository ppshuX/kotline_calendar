<template>
  <div class="right-sidebar">
    <SidebarTabs :tabs="tabs" v-model="currentTab" />

    <div v-show="currentTab === 'events'" class="tab-content">
      <EventListPanel
        :events="events"
        :format-event-time="formatEventTime"
        :selected-date="selectedDate"
        @select="event => $emit('select-event', event)"
        @add="$emit('add-event')"
      />
    </div>

    <div v-show="currentTab === 'fortune'" class="tab-content">
      <FortunePanel />
    </div>

    <div v-show="currentTab === 'holiday'" class="tab-content">
      <HolidayPanel 
        :today-holidays="todayHolidays" 
        :selected-date-label="selectedDate"
      />
    </div>

    <div v-show="currentTab === 'ai'" class="tab-content">
      <AIAssistantPanel />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import SidebarTabs from './SidebarTabs.vue'
import EventListPanel from './EventListPanel.vue'
import HolidayPanel from './HolidayPanel.vue'
import FortunePanel from './FortunePanel.vue'
import AIAssistantPanel from './AIAssistantPanel.vue'

const props = defineProps({
  tabs: {
    type: Array,
    default: () => []
  },
  activeTab: {
    type: String,
    default: 'events'
  },
  events: {
    type: Array,
    default: () => []
  },
  formatEventTime: {
    type: Function,
    default: (dateTime) => dateTime
  },
  todayHolidays: {
    type: Object,
    default: () => null
  },
  selectedDate: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['update:activeTab', 'select-event', 'add-event'])

const currentTab = computed({
  get: () => props.activeTab,
  set: (value) => emit('update:activeTab', value)
})
</script>

<style scoped>
.right-sidebar {
  background: white;
  padding: 20px;
  border-radius: 16px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
  height: 650px;
  max-height: 650px;
  min-height: 650px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.tab-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 16px;
  background: #f8f9fc;
  border-radius: 12px;
  margin-top: 12px;
  box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.06);
  border: 1px solid rgba(102, 126, 234, 0.1);
  overflow-y: auto;  /* 内部可滚动 */
  overflow-x: hidden;
}

@media (max-width: 992px) {
  .right-sidebar {
    height: 500px;
    max-height: 500px;
    min-height: 500px;
    margin-top: 16px;
  }
}

@media (max-width: 768px) {
  .right-sidebar {
    height: 600px;
    max-height: 600px;
    min-height: 600px;
    padding: 14px;
    margin-top: 16px;
  }
  
  .tab-content {
    padding: 12px;
    font-size: 13px;
  }
}

@media (max-width: 576px) {
  .right-sidebar {
    height: calc(100vh - 120px);
    max-height: calc(100vh - 120px);
    min-height: 600px;
    padding: 10px;
    margin-top: 12px;
  }
  
  .tab-content {
    padding: 8px;
    font-size: 11px;
    margin-top: 8px;
  }
}
</style>

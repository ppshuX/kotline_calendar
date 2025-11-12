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

    <div v-show="currentTab === 'weather'" class="tab-content">
      <WeatherPanel />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import SidebarTabs from './SidebarTabs.vue'
import EventListPanel from './EventListPanel.vue'
import HolidayPanel from './HolidayPanel.vue'
import FortunePanel from './FortunePanel.vue'
import WeatherPanel from './WeatherPanel.vue'

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
  min-height: 600px;
  display: flex;
  flex-direction: column;
}

.tab-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 16px;
  background: var(--bg-soft);
  border-radius: 12px;
  margin-top: 8px;
}

@media (max-width: 992px) {
  .right-sidebar {
    min-height: 400px;
    margin-top: 16px;
  }
}

@media (max-width: 768px) {
  .right-sidebar {
    padding: 16px;
    margin-top: 20px;
  }
}

@media (max-width: 576px) {
  .right-sidebar {
    padding: 12px;
    min-height: 300px;
  }
}
</style>

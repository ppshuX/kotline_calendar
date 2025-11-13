<template>
  <div class="main-view">
    <!-- 根据路由状态切换视图 -->
    <CalendarGrid v-if="$store.state.router.router_name === 'calendar'" />
    <EventList v-else-if="$store.state.router.router_name === 'event_list'" />
    <EventDetail v-else-if="$store.state.router.router_name === 'event_detail'" />
    <AddEventForm v-else-if="$store.state.router.router_name === 'add_event'" />
    <EditEventForm v-else-if="$store.state.router.router_name === 'edit_event'" />
    <FortunePanel v-else-if="$store.state.router.router_name === 'fortune'" />
    <WeatherPanel v-else-if="$store.state.router.router_name === 'weather'" />
    <AIAssistantPanel v-else-if="$store.state.router.router_name === 'ai_assistant'" />
  </div>
</template>

<script>
// 导入组件
import CalendarGrid from '../components/CalendarGrid.vue'
import EventList from '../components/EventList.vue'
import EventDetail from '../components/EventDetail.vue'
import AddEventForm from '../components/AddEventForm.vue'
import EditEventForm from '../components/EditEventForm.vue'
import FortunePanel from '../components/FortunePanel.vue'
import WeatherPanel from '../components/WeatherPanel.vue'
import AIAssistantPanel from '../components/AIAssistantPanel.vue'

export default {
  name: 'MainView',
  components: {
    CalendarGrid,
    EventList,
    EventDetail,
    AddEventForm,
    EditEventForm,
    FortunePanel,
    WeatherPanel,
    AIAssistantPanel,
  },
}
</script>

<style scoped>
.main-view {
  width: 100%;
  height: 100vh;
  overflow: hidden;
}
</style>


<template>
  <div class="event-list-view">
    <div class="header">
      <button class="back-btn" @click="goBack">◀ 返回</button>
      <h2>事件列表</h2>
      <button class="add-btn" @click="goToAdd">➕</button>
    </div>

    <div v-if="loading" class="loading">⏳ 加载中...</div>
    
    <div v-else-if="events.length === 0" class="empty">
      📭 暂无事件
    </div>
    
    <div v-else class="event-list">
      <div 
        v-for="event in events" 
        :key="event.id"
        class="event-item"
        @click="viewDetail(event.id)"
      >
        <div class="event-content">
          <h3>{{ event.title }}</h3>
          <p class="time">🕐 {{ formatTime(event.start_time) }}</p>
          <p v-if="event.location" class="location">📍 {{ event.location }}</p>
        </div>
        <button 
          class="delete-btn" 
          @click.stop="confirmDelete(event.id)"
        >
          🗑️
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { mapState, mapActions } from 'vuex'

export default {
  name: 'EventList',
  
  computed: {
    ...mapState({
      allEvents: state => state.events.events,
      loading: state => state.events.loading
    }),
    
    // 只显示用户创建的日程，不包括订阅的节日（subscription_id不为null的是订阅的节日）
    events() {
      return this.allEvents.filter(event => !event.subscription_id)
    },
  },
  
  methods: {
    ...mapActions(['fetchEvents', 'deleteEvent']),
    
    goBack() {
      this.$store.commit('updateRouterName', 'calendar')
    },
    
    goToAdd() {
      this.$store.commit('updateRouterName', 'add_event')
    },
    
    viewDetail(id) {
      this.$store.commit('updateRouterName', 'event_detail')
      this.$store.commit('updateRouterParams', { id })
    },
    
    formatTime(dateTimeStr) {
      if (!dateTimeStr) return ''
      const date = new Date(dateTimeStr)
      return `${date.getMonth() + 1}/${date.getDate()} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`
    },
    
    async confirmDelete(id) {
      if (!confirm('确定删除这个事件吗？')) return
      
      const success = await this.$store.dispatch('deleteEvent', id)
      if (success) {
        alert('删除成功！')
      } else {
        alert('删除失败！')
      }
    },
  },
  
  mounted() {
    this.fetchEvents()
  },
}
</script>

<style scoped>
.event-list-view {
  width: 100%;
  height: 100%;
  padding: 8px;
  background: #f8f9fa;
  overflow-y: auto;
  font-size: 12px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
  padding: 8px 10px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 6px;
  color: white;
}

.header h2 {
  flex: 1;
  text-align: center;
  margin: 0;
  font-size: 14px;
  font-weight: 600;
}

.back-btn,
.add-btn {
  padding: 4px 8px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 11px;
  transition: all 0.2s;
  background: rgba(255, 255, 255, 0.2);
  color: white;
}

.back-btn:hover,
.add-btn:hover {
  background: rgba(255, 255, 255, 0.3);
}

.loading,
.empty {
  text-align: center;
  padding: 30px 15px;
  background: white;
  border-radius: 6px;
  color: #999;
  font-size: 13px;
}

.event-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.event-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px;
  background: white;
  border-radius: 6px;
  border-left: 3px solid #667eea;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.event-item:hover {
  background: #f8f9ff;
  transform: translateX(2px);
  box-shadow: 0 3px 6px rgba(102, 126, 234, 0.15);
}

.event-content {
  flex: 1;
  min-width: 0;
}

.event-content h3 {
  margin: 0 0 3px 0;
  color: #303133;
  font-size: 13px;
  font-weight: 600;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.event-content p {
  margin: 2px 0;
  color: #606266;
  font-size: 10px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.delete-btn {
  padding: 4px 6px;
  background: #f56c6c;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 13px;
  transition: all 0.2s;
  flex-shrink: 0;
  margin-left: 6px;
}

.delete-btn:hover {
  background: #f78989;
}
</style>


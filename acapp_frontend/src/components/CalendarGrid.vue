<template>
  <div class="calendar-container">
    <!-- 顶部信息栏（月份 + 今日信息 + 操作按钮） -->
    <div class="header-bar">
      <button class="nav-btn" @click="prevMonth">◀</button>
      <div class="header-info">
        <div class="month-text">{{ monthText }}</div>
        <div class="today-info">{{ todayText }} · {{ todayLunar }}</div>
      </div>
      <button class="nav-btn" @click="nextMonth">▶</button>
    </div>

    <!-- 操作按钮栏 -->
    <Toolbar 
      :event-count="eventCount"
      @show-list="goToList"
      @show-fortune="goToFortune"
      @show-weather="goToWeather"
      @show-ai="goToAI"
    />

    <!-- 日历网格 -->
    <CalendarGridView 
      :days="calendarDays" 
      @select="selectDate" 
    />

    <!-- 日期操作弹窗 -->
    <div v-if="showDateMenu" class="date-menu" @click.self="closeDateMenu">
      <div class="menu-content">
        <div class="menu-header">
          {{ selectedDateText }}
          <button class="close-btn" @click="closeDateMenu">✕</button>
        </div>
        <div class="menu-body">
          <div v-if="selectedDateEvents.length > 0" class="event-list">
            <div 
              v-for="event in selectedDateEvents" 
              :key="event.id"
              class="event-item"
              @click="viewEvent(event)"
            >
              <span class="event-title">{{ event.title }}</span>
              <span class="event-time">{{ formatTime(event.start_time) }}</span>
            </div>
          </div>
          <div v-else class="no-events">
            该日期暂无日程
          </div>
        </div>
        <div class="menu-actions">
          <button class="menu-btn primary" @click="addEvent">➕ 添加日程</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapState, mapGetters, mapActions } from 'vuex'
import CalendarGridView from './CalendarGridView.vue'
import Toolbar from './Toolbar.vue'

export default {
  name: 'CalendarGrid',
  
  components: {
    CalendarGridView,
    Toolbar,
  },

  data() {
    return {
      // 节日数据 Map<日期字符串, 节日名称>
      datesWithFestivals: {},
      // 日期菜单
      showDateMenu: false,
      selectedDate: null,
      selectedDateStr: '',
    }
  },

  computed: {
    ...mapState({
      events: state => state.events.events,
      loading: state => state.events.loading,
      currentDate: state => state.events.currentDate
    }),
    ...mapGetters(['eventCount', 'isCalendarView']),

    monthText() {
      return `${this.currentDate.getFullYear()}年${this.currentDate.getMonth() + 1}月`
    },

    todayText() {
      const today = new Date()
      return `${today.getMonth() + 1}/${today.getDate()}`
    },

    todayLunar() {
      return '农历十月初七'
    },

    selectedDateText() {
      if (!this.selectedDate) return ''
      const weekDays = ['日', '一', '二', '三', '四', '五', '六']
      const date = this.selectedDate
      return `${date.getMonth() + 1}月${date.getDate()}日 星期${weekDays[date.getDay()]}`
    },

    selectedDateEvents() {
      if (!this.selectedDateStr) return []
      // 只显示用户创建的日程，不包括订阅的节日（subscription_id不为null的是订阅的节日）
      return this.events.filter(event => {
        if (!event.start_time || !event.start_time.startsWith(this.selectedDateStr)) {
          return false
        }
        // 排除订阅的节日事件
        return !event.subscription_id
      })
    },

    calendarDays() {
      const year = this.currentDate.getFullYear()
      const month = this.currentDate.getMonth()
      const firstDay = new Date(year, month, 1)
      const lastDay = new Date(year, month + 1, 0)
      const firstDayWeek = firstDay.getDay()

      const days = []

      // 上月日期
      const prevMonthLastDay = new Date(year, month, 0).getDate()
      for (let i = firstDayWeek - 1; i >= 0; i--) {
        days.push({
          date: prevMonthLastDay - i,
          isOtherMonth: true,
          isToday: false,
          isWeekend: false,
          isHoliday: false,
          holiday: null,
          eventCount: 0,
        })
      }

      // 当月日期
      for (let i = 1; i <= lastDay.getDate(); i++) {
        const date = new Date(year, month, i)
        const dateStr = this.formatDate(date)
        const weekDay = date.getDay()

        // 获取该日期的节日名称（优先显示法定节假日，然后是传统节日）
        const festivalName = this.datesWithFestivals[dateStr] || null
        
        days.push({
          date: i,
          isOtherMonth: false,
          isToday: this.isToday(year, month, i),
          isWeekend: weekDay === 0 || weekDay === 6,
          isHoliday: !!festivalName,
          holiday: festivalName,
          eventCount: this.getEventCountByDate(dateStr),
        })
      }

      // 下月日期（填充到 42 格）
      const remainingDays = 42 - days.length
      for (let i = 1; i <= remainingDays; i++) {
        days.push({
          date: i,
          isOtherMonth: true,
          isToday: false,
          isWeekend: false,
          isHoliday: false,
          holiday: null,
          eventCount: 0,
        })
      }

      return days
    },
  },

  methods: {
    ...mapActions(['fetchEvents']),

    isToday(year, month, date) {
      const today = new Date()
      return (
        today.getFullYear() === year &&
        today.getMonth() === month &&
        today.getDate() === date
      )
    },

    formatDate(date) {
      const year = date.getFullYear()
      const month = String(date.getMonth() + 1).padStart(2, '0')
      const day = String(date.getDate()).padStart(2, '0')
      return `${year}-${month}-${day}`
    },

    getEventCountByDate(dateStr) {
      // 只统计用户创建的日程，不包括订阅的节日
      return this.events.filter(event => {
        if (!event.start_time || !event.start_time.startsWith(dateStr)) {
          return false
        }
        // 排除订阅的节日事件
        return !event.is_public_calendar
      }).length
    },

    // 加载当前月份的节日信息
    async loadFestivalsForMonth() {
      const year = this.currentDate.getFullYear()
      const month = this.currentDate.getMonth()
      const lastDay = new Date(year, month + 1, 0)
      
      // 清空当前月份的节日数据
      const newDatesWithFestivals = {}
      
      // 遍历当前月份的所有日期
      for (let day = 1; day <= lastDay.getDate(); day++) {
        const date = new Date(year, month, day)
        const dateStr = this.formatDate(date)
        
        try {
          // 调用API获取节日信息
          const response = await fetch(`https://app7626.acapp.acwing.com.cn/api/holidays/check/?date=${dateStr}`)
          const data = await response.json()
          
          // 优先显示法定节假日
          if (data.is_holiday && data.holiday) {
            newDatesWithFestivals[dateStr] = data.holiday
          } 
          // 然后显示传统节日（取第一个）
          else if (data.festivals && data.festivals.length > 0) {
            const traditionalFestival = data.festivals.find(f => f.type === 'traditional')
            if (traditionalFestival) {
              newDatesWithFestivals[dateStr] = traditionalFestival.name
            } else if (data.festivals[0]) {
              newDatesWithFestivals[dateStr] = data.festivals[0].name
            }
          }
        } catch (error) {
          console.error(`加载${dateStr}的节日信息失败:`, error)
        }
      }
      
      // 更新节日数据
      this.datesWithFestivals = newDatesWithFestivals
    },

    prevMonth() {
      const newDate = new Date(this.currentDate)
      newDate.setMonth(newDate.getMonth() - 1)
      this.$store.commit('SET_CURRENT_DATE', newDate)
    },

    nextMonth() {
      const newDate = new Date(this.currentDate)
      newDate.setMonth(newDate.getMonth() + 1)
      this.$store.commit('SET_CURRENT_DATE', newDate)
    },

    goToToday() {
      this.$store.commit('SET_CURRENT_DATE', new Date())
    },

    selectDate(day) {
      if (day.isOtherMonth) return
      
      const year = this.currentDate.getFullYear()
      const month = this.currentDate.getMonth()
      this.selectedDate = new Date(year, month, day.date)
      this.selectedDateStr = this.formatDate(this.selectedDate)
      this.showDateMenu = true
      
      console.log('选中日期:', day.date)
    },

    closeDateMenu() {
      this.showDateMenu = false
      this.selectedDate = null
      this.selectedDateStr = ''
    },

    viewEvent(event) {
      this.$store.dispatch('changeView', {
        name: 'event_detail',
        params: { eventId: event.id }
      })
    },

    addEvent() {
      this.$store.dispatch('changeView', {
        name: 'add_event',
        params: { date: this.selectedDateStr }
      })
    },

    goToList() {
      this.$store.commit('updateRouterName', 'event_list')
    },

    goToFortune() {
      this.$store.commit('updateRouterName', 'fortune')
    },

    goToWeather() {
      this.$store.commit('updateRouterName', 'weather')
    },

    goToAI() {
      this.$store.commit('updateRouterName', 'ai_assistant')
    },

    async loadEvents() {
      await this.fetchEvents()
    },

    formatTime(dateTimeStr) {
      if (!dateTimeStr) return ''
      const date = new Date(dateTimeStr)
      return `${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`
    },
  },

  watch: {
    currentDate: {
      handler() {
        this.loadFestivalsForMonth()
      },
      immediate: true
    }
  },

  mounted() {
    this.fetchEvents()
    this.loadFestivalsForMonth()
  },
}
</script>

<style scoped>
.calendar-container {
  width: 100%;
  height: 100%;
  padding: 10px;
  background: #f8f9fa;
  font-size: 13px;
  overflow-y: auto;
}

/* 顶部信息栏 */
.header-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 8px;
  margin-bottom: 8px;
  color: white;
}

.nav-btn {
  padding: 6px 12px;
  background: rgba(255, 255, 255, 0.2);
  border: none;
  color: white;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  margin: 0 6px;
  transition: all 0.2s;
}

.nav-btn:hover {
  background: rgba(255, 255, 255, 0.3);
}

.header-info {
  flex: 1;
  text-align: center;
}

.month-text {
  font-size: 16px;
  font-weight: bold;
  margin-bottom: 2px;
}

.today-info {
  font-size: 11px;
  opacity: 0.9;
}

/* 日期操作弹窗 */
.date-menu {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.menu-content {
  background: white;
  border-radius: 12px;
  width: 90%;
  max-width: 400px;
  max-height: 80%;
  display: flex;
  flex-direction: column;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}

.menu-header {
  padding: 15px;
  border-bottom: 1px solid #e0e0e0;
  font-weight: bold;
  font-size: 15px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 12px 12px 0 0;
}

.close-btn {
  background: transparent;
  border: none;
  color: white;
  font-size: 20px;
  cursor: pointer;
  padding: 0;
  width: 30px;
  height: 30px;
  border-radius: 50%;
  transition: all 0.2s;
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.2);
}

.menu-body {
  flex: 1;
  overflow-y: auto;
  padding: 15px;
  min-height: 120px;
}

.event-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.event-item {
  padding: 10px;
  background: #f8f9fa;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.event-item:hover {
  background: #e9ecef;
  transform: translateX(4px);
}

.event-title {
  font-weight: 500;
  color: #333;
}

.event-time {
  font-size: 12px;
  color: #666;
}

.no-events {
  text-align: center;
  color: #999;
  padding: 30px 0;
  font-size: 13px;
}

.menu-actions {
  padding: 15px;
  border-top: 1px solid #e0e0e0;
}

.menu-btn {
  width: 100%;
  padding: 10px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.menu-btn.primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.menu-btn.primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}
</style>

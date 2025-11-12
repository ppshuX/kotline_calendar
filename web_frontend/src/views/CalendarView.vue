<template>
  <div class="calendar-page">
    <NavBar 
      @login="handleLogin"
      @register="handleRegister"
      @logout="handleLogout"
      @subscribe="handleSubscribe"
    />
    
    <ContentField>
      <!-- 天气横条：始终显示 -->
      <WeatherBar />
      
      <div class="row g-3 justify-content-center">
        <!-- 日历：桌面端左侧，移动端上方全宽 -->
        <div class="col-lg-6 col-md-6 col-12">
          <div class="calendar-wrapper">
            <FullCalendar ref="fullCalendarRef" :options="calendarOptions" />
          </div>
        </div>
        
        <!-- 侧边栏：桌面端右侧，移动端下方全宽 -->
        <div class="col-lg-6 col-md-6 col-12">
          <CalendarSidebar
            :tabs="tabs"
            v-model:activeTab="activeTab"
            :events="filteredEvents"
            :selected-date="selectedDateLabel"
            :format-event-time="formatEventTime"
            :today-holidays="todayHolidays"
            @select-event="handleEventCardSelect"
            @add-event="openAddDialogForSelectedDate"
          />
        </div>
      </div>
      
      <!-- 浮动添加按钮：仅登录后显示 -->
      <button v-if="isLoggedIn" class="floating-add-btn" @click="openAddDialog">
        <i class="bi bi-plus-lg"></i>
      </button>
      
      <!-- 未登录引导按钮 -->
      <button v-else class="floating-login-btn" @click="router.push('/login')">
        <i class="bi bi-box-arrow-in-right"></i>
        <span class="login-text">登录</span>
      </button>
    </ContentField>

    <EventDialog
      v-model:visible="showAddDialog"
      :event="editingEvent"
      @save="saveEvent"
    />

    <EventDetail
      v-model:visible="showDetailDialog"
      :event="selectedEvent"
      :lunar-date="lunarDateText"
      @edit="editEvent"
      @delete="deleteEvent"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import FullCalendar from '@fullcalendar/vue3'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import NavBar from '../components/NavBar.vue'
import ContentField from '../components/ContentField.vue'
import WeatherBar from '../components/calendar/WeatherBar.vue'
import EventDialog from '../components/calendar/EventDialog.vue'
import EventDetail from '../components/calendar/EventDetail.vue'
import CalendarSidebar from '../components/calendar/CalendarSidebar.vue'
import { useCalendarEvents } from '../composables/useCalendarEvents'
import { useHolidayData } from '../composables/useHolidayData'
import { useSidebarTabs } from '../composables/useSidebarTabs'

const router = useRouter()

// FullCalendar 组件引用
const fullCalendarRef = ref(null)

// 检查登录状态
const isLoggedIn = ref(false)
const checkLoginStatus = () => {
  const token = localStorage.getItem('access_token')
  isLoggedIn.value = !!token
  return isLoggedIn.value
}

// 未登录提示并跳转登录
const requireLogin = (action = '该操作') => {
  ElMessage.warning({
    message: `${action}需要登录，请先登录`,
    duration: 3000
  })
  setTimeout(() => {
    router.push({ name: 'login', query: { redirect: '/calendar' } })
  }, 500)
  return false
}

const {
  holidaysMap,
  todayHolidays,
  loadHolidays,
  loadTodayHolidays,
  getHolidaysForDate,
  applyHolidayEvents
} = useHolidayData()

// 日期选择回调
const handleDateSelected = (dateStr) => {
  selectedDateForFilter.value = dateStr
  selectedDateLabel.value = new Date(dateStr).toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    weekday: 'long'
  })
  
  // 立即加载选中日期的节假日（不管当前在哪个标签页）⭐
  loadHolidaysForSelectedDate(dateStr)
  
  // 只有登录后才自动切换到日程列表标签
  if (checkLoginStatus()) {
    activeTab.value = 'events'
  }
}

// 加载指定日期的节假日数据
const loadHolidaysForSelectedDate = async (dateStr) => {
  if (!dateStr) {
    await loadTodayHolidays()
    return
  }
  
  const holidays = await getHolidaysForDate(dateStr)
  todayHolidays.value = holidays
}

const {
  calendarOptions,
  showAddDialog,
  showDetailDialog,
  selectedEvent,
  editingEvent,
  lunarDateText,
  eventsList,
  selectedDate,
  openAddDialog,
  handleDateClick,
  handleEventClick,
  formatEventTime,
  loadEvents,
  saveEvent,
  editEvent,
  deleteEvent,
  testLunar,
  updateCalendarEvents,
  getEventsCountForDate
} = useCalendarEvents({ 
  applyHolidayEvents,
  onDateSelect: handleDateSelected
})

const { activeTab, tabs } = useSidebarTabs('fortune', isLoggedIn)

// 选中的日期（用于过滤日程列表）
const selectedDateForFilter = ref('')
const selectedDateLabel = ref('')

// 过滤后的日程列表（根据选中日期）
const filteredEvents = computed(() => {
  if (!selectedDateForFilter.value) {
    return eventsList.value
  }
  
  return eventsList.value.filter(event => {
    const eventDate = event.start_time.split('T')[0]
    return eventDate === selectedDateForFilter.value
  })
})

// 配置日期点击事件
calendarOptions.value.dateClick = handleDateClick

// 配置事件点击事件
calendarOptions.value.eventClick = handleEventClick

// 定义"今天"按钮的处理函数
const handleTodayClick = async () => {
  // 获取 FullCalendar API
  if (fullCalendarRef.value) {
    const calendarApi = fullCalendarRef.value.getApi()
    calendarApi.today()  // 跳转到今天
    calendarApi.unselect()  // 取消选中状态
  }
  
  // 重置为今天的日期（而不是清空）
  const today = new Date()
  const todayStr = today.toISOString().split('T')[0]
  
  selectedDateForFilter.value = ''  // 清空过滤（显示所有日程）
  selectedDateLabel.value = today.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    weekday: 'long'
  })
  selectedDate.value = todayStr  // 设为今天的日期字符串
  
  // 重新加载今天的节假日
  await loadTodayHolidays()
}

// 配置自定义"回到今天"按钮（始终可点击）
calendarOptions.value.customButtons = {
  myToday: {
    text: '今天',
    click: handleTodayClick
  }
}

// 替换工具栏中的 today 按钮为自定义按钮
calendarOptions.value.headerToolbar = {
  left: 'prev,next myToday',  // 使用自定义的 myToday 按钮
  center: 'title',
  right: 'dayGridMonth,dayGridWeek,timeGridDay'
}

// 配置日期单元格渲染（添加圆点指示器）
calendarOptions.value.dayCellDidMount = (arg) => {
  // 使用本地日期，避免时区问题
  const year = arg.date.getFullYear()
  const month = String(arg.date.getMonth() + 1).padStart(2, '0')
  const day = String(arg.date.getDate()).padStart(2, '0')
  const dateStr = `${year}-${month}-${day}`
  
  const count = getEventsCountForDate(dateStr)
  
  if (count > 0) {
    // 创建圆点元素
    const dot = document.createElement('div')
    dot.className = 'event-dot'
    
    // 根据事件数量设置颜色深浅（GitHub 热力图风格）
    let bgColor
    if (count === 1) {
      bgColor = 'rgba(102, 126, 234, 0.3)'  // 浅色 - 1 个事件
    } else if (count === 2) {
      bgColor = 'rgba(102, 126, 234, 0.5)'  // 中浅 - 2 个事件
    } else if (count <= 4) {
      bgColor = 'rgba(102, 126, 234, 0.7)'  // 中深 - 3-4 个事件
    } else {
      bgColor = 'rgba(102, 126, 234, 0.9)'  // 深色 - 5+ 个事件
    }
    
    dot.style.cssText = `
      position: absolute;
      bottom: 4px;
      right: 4px;
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: ${bgColor};
      z-index: 10;
      transition: transform 0.2s ease;
      cursor: pointer;
    `
    
    // 创建 GitHub 风格的 tooltip
    const tooltip = document.createElement('div')
    tooltip.className = 'event-dot-tooltip'
    tooltip.textContent = `${count} 个日程`
    tooltip.style.cssText = `
      position: absolute;
      bottom: 100%;
      right: 0;
      margin-bottom: 8px;
      padding: 6px 10px;
      background: rgba(0, 0, 0, 0.8);
      color: white;
      font-size: 12px;
      border-radius: 4px;
      white-space: nowrap;
      pointer-events: none;
      opacity: 0;
      transform: translateY(4px);
      transition: opacity 0.2s ease, transform 0.2s ease;
      z-index: 1000;
    `
    
    // 添加三角箭头
    const arrow = document.createElement('div')
    arrow.style.cssText = `
      position: absolute;
      top: 100%;
      right: 4px;
      width: 0;
      height: 0;
      border-left: 4px solid transparent;
      border-right: 4px solid transparent;
      border-top: 4px solid rgba(0, 0, 0, 0.8);
    `
    tooltip.appendChild(arrow)
    dot.appendChild(tooltip)
    
    // 悬停显示 tooltip（GitHub 风格）
    dot.addEventListener('mouseenter', () => {
      dot.style.transform = 'scale(1.3)'
      tooltip.style.opacity = '1'
      tooltip.style.transform = 'translateY(0)'
    })
    dot.addEventListener('mouseleave', () => {
      dot.style.transform = 'scale(1)'
      tooltip.style.opacity = '0'
      tooltip.style.transform = 'translateY(4px)'
    })
    
    // 添加到日期单元格
    arg.el.style.position = 'relative'
    arg.el.appendChild(dot)
  }
}

const handleEventCardSelect = (event) => {
  // 事件卡片只在登录后才显示，所以这里不需要检查
  handleEventClick({
    event: {
      extendedProps: event,
      start: event.start_time
    }
  })
}

// 为选中的日期添加日程
const openAddDialogForSelectedDate = () => {
  if (!checkLoginStatus()) {
    requireLogin('创建事件')
    return
  }
  if (selectedDate.value) {
    editingEvent.value = {
      start_time: selectedDate.value
    }
  } else {
    editingEvent.value = null
  }
  showAddDialog.value = true
}

// 刷新圆点的函数（提取出来，避免重复代码）
const refreshEventDots = () => {
  setTimeout(() => {
    const dayCells = document.querySelectorAll('.fc-daygrid-day')
    dayCells.forEach(cell => {
      // 移除旧圆点
      const oldDot = cell.querySelector('.event-dot')
      if (oldDot) oldDot.remove()
      
      // 重新创建圆点
      const dateAttr = cell.getAttribute('data-date')
      if (dateAttr) {
        const count = getEventsCountForDate(dateAttr)
        if (count > 0) {
          const dot = document.createElement('div')
          dot.className = 'event-dot'
          
          let bgColor
          if (count === 1) bgColor = 'rgba(102, 126, 234, 0.3)'
          else if (count === 2) bgColor = 'rgba(102, 126, 234, 0.5)'
          else if (count <= 4) bgColor = 'rgba(102, 126, 234, 0.7)'
          else bgColor = 'rgba(102, 126, 234, 0.9)'
          
          dot.style.cssText = `
            position: absolute; bottom: 4px; right: 4px;
            width: 8px; height: 8px; border-radius: 50%;
            background: ${bgColor}; z-index: 10;
            transition: transform 0.2s ease; cursor: pointer;
          `
          
          const tooltip = document.createElement('div')
          tooltip.textContent = `${count} 个日程`
          tooltip.style.cssText = `
            position: absolute; bottom: 100%; right: 0; margin-bottom: 8px;
            padding: 6px 10px; background: rgba(0, 0, 0, 0.8); color: white;
            font-size: 12px; border-radius: 4px; white-space: nowrap;
            pointer-events: none; opacity: 0; transform: translateY(4px);
            transition: opacity 0.2s ease, transform 0.2s ease; z-index: 1000;
          `
          dot.appendChild(tooltip)
          
          dot.addEventListener('mouseenter', () => {
            dot.style.transform = 'scale(1.3)'
            tooltip.style.opacity = '1'
            tooltip.style.transform = 'translateY(0)'
          })
          dot.addEventListener('mouseleave', () => {
            dot.style.transform = 'scale(1)'
            tooltip.style.opacity = '0'
            tooltip.style.transform = 'translateY(4px)'
          })
          
          cell.style.position = 'relative'
          cell.appendChild(dot)
        }
      }
    })
  }, 100)
}

// 监听事件列表变化（只在变化时触发一次，不会频繁刷新）
watch(eventsList, () => {
  updateCalendarEvents()
  refreshEventDots()
})

// 监听节假日数据变化，自动更新日历
watch(holidaysMap, () => {
  updateCalendarEvents()
})

// 监听标签页切换，当切换到节假日标签时加载对应日期的数据
watch(activeTab, async (newTab) => {
  if (newTab === 'holiday') {
    // 如果有选中的日期，加载该日期的节假日；否则加载今天的
    if (selectedDateForFilter.value) {
      await loadHolidaysForSelectedDate(selectedDateForFilter.value)
    } else {
      await loadTodayHolidays()
    }
  }
})

onMounted(async () => {
  checkLoginStatus()
  await loadHolidays()
  await loadTodayHolidays()
  
  // 节假日加载后更新日历
  updateCalendarEvents()
  
  // 只有登录后才加载用户事件
  if (isLoggedIn.value) {
    await loadEvents()
  }
})

function handleLogin() {
  console.info('login action placeholder')
}

function handleRegister() {
  console.info('register action placeholder')
}

function handleLogout() {
  console.info('logout action placeholder')
}

function handleSubscribe() {
  console.info('subscribe action placeholder')
}
</script>

<style>
/* 导入日历样式（已优化，移除大量 !important） */
@import '@/styles/calendar.css';
</style>

<style scoped>
/* ==================== 组件特有样式 ==================== */

/* 日历页面容器 */
.calendar-page {
  min-height: 100vh;
  background: var(--color-background-soft);
}

/* 桌面端日历完全自适应容器大小 */
.calendar-wrapper :deep(.fc) {
  height: 100%;
  width: 100%;
}

/* 月视图 - 自适应，不固定高度 */
.calendar-wrapper :deep(.fc-dayGridMonth-view) {
  height: 100%;
}

/* 日历内容自适应缩放 */
.calendar-wrapper :deep(.fc-view-harness) {
  height: 100% !important;
}

/* 周/日时间轴视图 - 自适应高度 */
.calendar-wrapper :deep(.fc-timeGridWeek-view),
.calendar-wrapper :deep(.fc-timeGridDay-view) {
  height: 100%;
  max-height: none;
}

/* 时间轴滚动区域 */
.calendar-wrapper :deep(.fc-timegrid-body) {
  max-height: 500px;
  overflow-y: auto;
}

/* PC端容器 */
.row {
  max-width: 1400px;
  margin: 0 auto;
}

/* 确保两列完全等宽等高 */
.row > div {
  display: flex;
}

/* 桌面端：左侧日历占 60%，右侧 40% */
@media (min-width: 768px) {
  .row > div:first-child {
    flex: 0 0 60%;
    max-width: 60%;
  }

  .row > div:last-child {
    flex: 0 0 40%;
    max-width: 40%;
  }
}

/* 移动端：上下布局，日历和侧边栏都全宽 */
@media (max-width: 767px) {
  .row > div {
    flex: 0 0 100%;
    max-width: 100%;
  }
  
  /* 日历高度减小 */
  .calendar-wrapper {
    height: 380px;  /* 移动端日历更小 */
  }
  
  /* 整体缩小间距 */
  .calendar-page :deep(.fc) {
    font-size: 13px;
  }
  
  /* 日期单元格缩小 */
  .calendar-page :deep(.fc-daygrid-day) {
    min-height: 50px !important;
  }
  
  /* 周标题缩小 */
  .calendar-page :deep(.fc-col-header-cell) {
    padding: 6px 2px;
    font-size: 12px;
  }
}

.calendar-wrapper,
.right-sidebar {
  flex: 1;
  width: 100%;
  max-width: 100%;
  overflow: hidden;
}

/* 浮动添加按钮 */
.floating-add-btn {
  position: fixed;
  right: 24px;
  bottom: 24px;
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  border: none;
  font-size: 26px;
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
  cursor: pointer;
  transition: all 0.3s ease;
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
}

.floating-add-btn:hover {
  transform: scale(1.1) rotate(90deg);
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.5);
}

.floating-add-btn:active {
  transform: scale(0.95);
}

/* 未登录引导按钮 */
.floating-login-btn {
  position: fixed;
  right: 24px;
  bottom: 24px;
  height: 60px;
  padding: 0 24px;
  border-radius: 30px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  border: none;
  font-size: 16px;
  font-weight: 500;
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
  cursor: pointer;
  transition: all 0.3s ease;
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.floating-login-btn:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.5);
}

.floating-login-btn:active {
  transform: translateY(-2px);
}

.floating-login-btn i {
  font-size: 18px;
}

.login-text {
  white-space: nowrap;
}

/* ==================== 移动端适配 ==================== */
@media (max-width: 768px) {
  /* 确保移动端日历居中 */
  .calendar-wrapper {
    max-width: 100%;
    margin-left: auto;
    margin-right: auto;
  }
  
  .floating-add-btn {
    right: 16px;
    bottom: 16px;
    width: 50px;
    height: 50px;
    font-size: 22px;
  }
  
  .floating-login-btn {
    right: 16px;
    bottom: 16px;
    height: 50px;
    padding: 0 20px;
    font-size: 15px;
  }
  
  .floating-login-btn i {
    font-size: 16px;
  }
}

/* ==================== PC 端完美对称布局 ==================== */
@media (min-width: 992px) {
  .row {
    display: flex;
    align-items: stretch;
  }
  
  .row > div {
    flex: 1 1 0;  /* 完全等宽 */
    max-width: 50%;
  }
  
  .calendar-wrapper,
  .right-sidebar {
    min-height: 650px;
    height: 100%;
  }
}
</style>


import { ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useRouter } from 'vue-router'
import dayGridPlugin from '@fullcalendar/daygrid'
import timeGridPlugin from '@fullcalendar/timegrid'
import scrollGridPlugin from '@fullcalendar/scrollgrid'
import interactionPlugin from '@fullcalendar/interaction'
import { eventAPI, lunarAPI } from '../api'

export function useCalendarEvents({ applyHolidayEvents, onDateSelect } = {}) {
  const router = useRouter()
  const showAddDialog = ref(false)
  const showDetailDialog = ref(false)
  const selectedEvent = ref(null)
  const editingEvent = ref(null)
  const lunarDateText = ref('')
  const eventsList = ref([])
  const selectedDate = ref(null)  // 当前选中的日期

  const calendarOptions = ref({
    plugins: [dayGridPlugin, timeGridPlugin, scrollGridPlugin, interactionPlugin],
    initialView: 'dayGridMonth',
    locale: 'zh-cn',
    headerToolbar: {
      left: 'prev,next today',
      center: 'title',  // 显示标题
      right: 'dayGridMonth,dayGridWeek,timeGridDay'
    },
    buttonText: {
      today: '今天',
      month: '月',
      week: '周',
      day: '日'
    },
    slotMinTime: '06:00:00',  // 时间轴开始时间
    slotMaxTime: '23:00:00',  // 时间轴结束时间
    slotDuration: '00:30:00',  // 时间格子间隔（30分钟）
    slotLabelFormat: {
      hour: '2-digit',
      minute: '2-digit',
      hour12: false  // 24小时制
    },
    allDaySlot: true,  // 显示"全天"行（周视图和日视图需要）
    allDayText: '全天',  // 全天槽的文本
    titleFormat: (date) => {
      // 使用不间断空格防止换行
      return `${date.date.year}年\u00A0${date.date.month + 1}月`
    },
    dayHeaderFormat: { weekday: 'narrow' },
    dayCellContent: (arg) => arg.dayNumberText.replace('日', ''),
    moreLinkText: (num) => num,
    events: [],
    editable: true,
    selectable: true,
    selectMirror: true,
    unselectAuto: false,  // 不自动取消选择，保持选中状态
    dayMaxEvents: false,
    weekends: true,
    // 使用 FullCalendar 原生的 select 回调
    select: (selectInfo) => {
      // 只选择单个日期（点击）
      selectedDate.value = selectInfo.startStr
      if (onDateSelect) {
        onDateSelect(selectInfo.startStr)
      }
    },
    // FullCalendar 官方推荐的响应式配置
    aspectRatio: window.innerWidth < 768 ? 1 : 1.8,  // 移动端 1:1，桌面端 1.8:1
    handleWindowResize: true,  // 自动处理窗口 resize
    windowResizeDelay: 100,  // resize 防抖
    views: {
      dayGridWeek: {
        dayHeaderFormat: { weekday: 'short' }
      },
      timeGridWeek: {
        dayHeaderFormat: { weekday: 'short', day: 'numeric' },
        slotEventOverlap: false  // 时间冲突的事件并排显示
      },
      timeGridDay: {
        dayHeaderFormat: { weekday: 'long', month: 'long', day: 'numeric' },
        slotEventOverlap: false
      }
    },
    eventDisplay: 'block',  // 事件显示为块状
    displayEventTime: true,  // 显示事件时间
    displayEventEnd: true,  // 显示事件结束时间
    eventTimeFormat: {  // 事件时间格式
      hour: '2-digit',
      minute: '2-digit',
      hour12: false
    }
  })

  const checkLogin = () => {
    const token = localStorage.getItem('access_token')
    return !!token
  }

  const requireLogin = (action = '该操作') => {
    ElMessage.warning({
      message: `${action}需要登录，请先登录`,
      duration: 3000
    })
    setTimeout(() => {
      router.push({ name: 'login', query: { redirect: '/calendar' } })
    }, 500)
  }

  const openAddDialog = () => {
    if (!checkLogin()) {
      requireLogin('创建事件')
      return
    }
    editingEvent.value = null
    showAddDialog.value = true
  }

  const handleDateClick = (arg) => {
    // 保留这个函数以兼容旧代码，但现在主要使用 select 回调
    // 点击事件时不做任何操作，让 select 回调处理
  }

  const formatDate = (date) => {
    if (!date) return ''
    const d = new Date(date)
    const year = d.getFullYear()
    const month = String(d.getMonth() + 1).padStart(2, '0')
    const day = String(d.getDate()).padStart(2, '0')
    return `${year}-${month}-${day}`
  }

  const handleEventClick = async (clickInfo) => {
    if (!checkLogin()) {
      requireLogin('查看事件详情')
      return
    }

    selectedEvent.value = clickInfo.event.extendedProps

    try {
      const dateStr = formatDate(clickInfo.event.start)
      if (dateStr) {
        const lunar = await lunarAPI.getLunarDate(dateStr)
        lunarDateText.value = `${lunar.lunar_date} ${lunar.zodiac}年`
      } else {
        lunarDateText.value = ''
      }
    } catch (error) {
      lunarDateText.value = ''
    }

    showDetailDialog.value = true
  }

  const formatEventTime = (dateTime) => {
    if (!dateTime) return ''
    const d = new Date(dateTime)
    const month = d.getMonth() + 1
    const day = d.getDate()
    const hour = String(d.getHours()).padStart(2, '0')
    const minute = String(d.getMinutes()).padStart(2, '0')
    const weekdays = ['日', '一', '二', '三', '四', '五', '六']
    const weekday = weekdays[d.getDay()]
    return `${month}月${day}日 周${weekday} ${hour}:${minute}`
  }

  const updateCalendarEvents = () => {
    // 将用户事件转换为 FullCalendar 格式
    const userEvents = eventsList.value.map(event => ({
      id: event.id,
      title: event.title,
      start: event.start_time,
      end: event.end_time || null,
      allDay: event.all_day || false,
      backgroundColor: '#667eea',
      borderColor: '#5568d3',
      textColor: '#ffffff',
      extendedProps: {
        ...event,
        description: event.description || '',
        location: event.location || '',
        reminder_minutes: event.reminder_minutes || 15
      }
    }))

    // 合并节假日事件（如果提供了 applyHolidayEvents 函数）
    let events = [...userEvents]
    if (applyHolidayEvents) {
      events = applyHolidayEvents(events)
    }

    calendarOptions.value.events = events
  }

  const loadEvents = async () => {
    try {
      const events = await eventAPI.getAll()
      eventsList.value = events.sort((a, b) => new Date(a.start_time) - new Date(b.start_time))
      updateCalendarEvents()
      ElMessage.success(`✅ 加载了 ${events.length} 个日程`)
    } catch (error) {
      ElMessage.error('❌ 加载失败: ' + error.message)
    }
  }

  const saveEvent = async (data) => {
    try {
      if (data.id) {
        await eventAPI.update(data.id, data)
        ElMessage.success('✅ 更新成功')
      } else {
        await eventAPI.create(data)
        ElMessage.success('✅ 添加成功')
      }
      loadEvents()
    } catch (error) {
      ElMessage.error('❌ 保存失败: ' + error.message)
    }
  }

  const editEvent = (event) => {
    if (!checkLogin()) {
      requireLogin('编辑事件')
      return
    }
    editingEvent.value = event
    showAddDialog.value = true
  }

  const deleteEvent = async (event) => {
    if (!checkLogin()) {
      requireLogin('删除事件')
      return
    }
    try {
      await eventAPI.delete(event.id)
      ElMessage.success('🗑️ 删除成功')
      loadEvents()
    } catch (error) {
      ElMessage.error('❌ 删除失败: ' + error.message)
    }
  }

  const testLunar = async () => {
    try {
      const today = formatDate(new Date())
      const lunar = await lunarAPI.getLunarDate(today)
      ElMessage.success(`🏮 今天是${lunar.lunar_date} ${lunar.zodiac}年`)
    } catch (error) {
      ElMessage.error('❌ 测试失败: ' + error.message)
    }
  }

  // 获取某一天的事件数量
  const getEventsCountForDate = (dateStr) => {
    return eventsList.value.filter(event => {
      const eventDate = formatDate(event.start_time)
      return eventDate === dateStr
    }).length
  }

  return {
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
  }
}

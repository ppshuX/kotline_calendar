import { ref, computed } from 'vue'

export function useSidebarTabs(initialTab = 'events', isLoggedIn = false) {
  const activeTab = ref(initialTab)

  // 根据登录状态动态生成标签页
  const tabs = computed(() => {
    const baseTabs = [
      { id: 'fortune', label: '今日运势', icon: 'bi-stars' },
      { id: 'holiday', label: '今日节日', icon: 'bi-calendar-heart' },
      { id: 'ai', label: 'AI助手', icon: 'bi-robot' }
    ]
    
    // 只有登录后才显示日程列表
    if (isLoggedIn) {
      return [
        { id: 'events', label: '日程列表', icon: 'bi-calendar-check' },
        ...baseTabs
      ]
    }
    
    return baseTabs
  })

  const setActiveTab = (tabId) => {
    activeTab.value = tabId
  }

  return {
    activeTab,
    tabs,
    setActiveTab
  }
}


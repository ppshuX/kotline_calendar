package com.ncu.kotlincalendar

import android.Manifest
import android.app.TimePickerDialog
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Build
import android.os.Bundle
import android.util.Log
import android.view.View
import android.widget.ArrayAdapter
import android.widget.Button
import android.widget.ImageButton
import android.widget.LinearLayout
import android.widget.Spinner
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AlertDialog
import com.google.android.material.textfield.TextInputEditText
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import androidx.lifecycle.lifecycleScope
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.kizitonwose.calendar.core.CalendarDay
import com.kizitonwose.calendar.core.CalendarMonth
import com.kizitonwose.calendar.core.DayPosition
import com.kizitonwose.calendar.core.daysOfWeek
import com.kizitonwose.calendar.view.CalendarView
import com.kizitonwose.calendar.view.MonthDayBinder
import com.kizitonwose.calendar.view.MonthScrollListener
import com.kizitonwose.calendar.view.ViewContainer
import com.kizitonwose.calendar.view.WeekCalendarView
import com.kizitonwose.calendar.view.WeekDayBinder
import com.ncu.kotlincalendar.api.client.RetrofitClient
import com.ncu.kotlincalendar.data.database.AppDatabase
import com.ncu.kotlincalendar.data.database.EventDao
import com.ncu.kotlincalendar.data.database.SubscriptionDao
import com.ncu.kotlincalendar.data.models.Event
import com.ncu.kotlincalendar.data.models.Subscription
import com.ncu.kotlincalendar.data.managers.ReminderManager
import com.ncu.kotlincalendar.data.managers.SubscriptionManager
import com.ncu.kotlincalendar.data.repository.EventRepository
import com.ncu.kotlincalendar.ui.managers.WeatherManager
import com.ncu.kotlincalendar.ui.managers.HolidayManager
import com.ncu.kotlincalendar.ui.managers.FortuneManager
import com.ncu.kotlincalendar.utils.PreferenceManager
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import java.text.SimpleDateFormat
import java.time.Instant
import java.time.LocalDate
import java.time.YearMonth
import java.time.ZoneId
import java.time.format.DateTimeFormatter
import java.util.*

class MainActivity : AppCompatActivity() {
    
    private lateinit var calendarView: CalendarView
    private lateinit var weekCalendarView: WeekCalendarView
    private lateinit var weekTimelineRecycler: RecyclerView
    private lateinit var weekTimelineAdapter: TimeSlotAdapter
    private lateinit var dayViewRecycler: RecyclerView
    private lateinit var dayViewAdapter: TimeSlotAdapter
    private lateinit var monthViewCard: com.google.android.material.card.MaterialCardView
    private lateinit var weekViewContainer: android.widget.LinearLayout
    private lateinit var dayViewCard: com.google.android.material.card.MaterialCardView
    private lateinit var bottomContentCard: com.google.android.material.card.MaterialCardView
    private lateinit var tvSelectedDate: TextView
    private lateinit var tvMonthYear: TextView
    private lateinit var btnPreviousMonth: ImageButton
    private lateinit var btnNextMonth: ImageButton
    private lateinit var btnViewSwitch: Button
    private lateinit var btnAddEvent: Button
    private lateinit var btnAICreate: Button
    private lateinit var btnSubscribe: Button
    private lateinit var btnCloudMode: Button
    private lateinit var recyclerView: RecyclerView
    private lateinit var adapter: EventAdapter
    
    // Tab 和内容视图
    private lateinit var tabLayout: com.google.android.material.tabs.TabLayout
    private lateinit var weatherCard: com.google.android.material.card.MaterialCardView
    private lateinit var tvWeatherLocation: TextView
    private lateinit var tvTemperature: TextView
    private lateinit var tvWeatherDesc: TextView
    private lateinit var tvFeelsLike: TextView
    private lateinit var tvHumidity: TextView
    private lateinit var tvWind: TextView
    private lateinit var scrollViewHoliday: android.widget.LinearLayout
    private lateinit var scrollViewFortune: android.widget.LinearLayout
    private lateinit var festivalCardsContainer: LinearLayout
    private lateinit var tvHolidayHint: TextView
    private lateinit var tvFortuneContent: TextView
    
    // 数据库
    private lateinit var database: AppDatabase
    private lateinit var eventDao: EventDao
    private lateinit var subscriptionDao: SubscriptionDao
    
    // Repository（统一本地/云端数据访问）
    private lateinit var eventRepository: EventRepository
    private lateinit var reminderManager: ReminderManager
    private lateinit var subscriptionManager: SubscriptionManager
    private val eventsList = mutableListOf<Event>()
    
    // UI管理器
    private lateinit var weatherManager: WeatherManager
    private lateinit var holidayManager: HolidayManager
    private lateinit var fortuneManager: FortuneManager
    
    // 日历相关
    private var selectedDate: LocalDate? = LocalDate.now()
    private var currentMonth: YearMonth = YearMonth.now()
    private val datesWithEvents = mutableSetOf<LocalDate>()  // 有日程的日期集合（用户创建）
    private val datesWithFestivals = mutableMapOf<LocalDate, String>()  // 有节日的日期集合 -> 节日名称
    private var currentTab: Int = 0  // 0=日程 1=节日 2=运势
    private var viewMode: Int = 0  // 0=月视图（默认） 1=周视图 2=日视图
    
    // 地点选择回调
    private var onLocationSelectedCallback: ((String, String, Double, Double) -> Unit)? = null
    
    // 月视图 DayViewContainer
    inner class DayViewContainer(view: View) : ViewContainer(view) {
        val textView: TextView = view.findViewById(R.id.calendarDayText)
        val dotView: View = view.findViewById(R.id.calendarDayDot)
        val festivalLabel: TextView = view.findViewById(R.id.calendarDayFestivalLabel)
        
        lateinit var day: CalendarDay
        
        init {
            view.setOnClickListener {
                if (day.position == DayPosition.MonthDate) {
                    selectDate(day.date)
                }
            }
        }
    }
    
    // 周视图 DayViewContainer
    inner class WeekDayViewContainer(view: View) : ViewContainer(view) {
        val dayText: TextView = view.findViewById(R.id.weekDayText)
        val numberText: TextView = view.findViewById(R.id.weekDayNumber)
        val dotView: View = view.findViewById(R.id.weekDayDot)
        val festivalLabel: TextView = view.findViewById(R.id.weekDayFestivalLabel)
        
        lateinit var day: com.kizitonwose.calendar.core.WeekDay
        
        init {
            view.setOnClickListener {
                selectDate(day.date)
            }
        }
    }
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        
        // Toolbar已使用自定义布局（包含logo和标题），无需设置ActionBar
        
        // 初始化数据库和提醒管理器
        database = AppDatabase.getDatabase(this)
        eventDao = database.eventDao()
        subscriptionDao = database.subscriptionDao()
        
        // 初始化Repository
        eventRepository = EventRepository(this)
        reminderManager = ReminderManager(this)
        subscriptionManager = SubscriptionManager(
            subscriptionDao,
            eventDao,
            RetrofitClient.api
        )
        
        // 初始化视图
        calendarView = findViewById(R.id.calendarView)
        weekCalendarView = findViewById(R.id.weekCalendarView)
        weekTimelineRecycler = findViewById(R.id.weekTimelineRecycler)
        dayViewRecycler = findViewById(R.id.dayViewRecycler)
        monthViewCard = findViewById(R.id.monthViewCard)
        weekViewContainer = findViewById(R.id.weekViewContainer)
        dayViewCard = findViewById(R.id.dayViewCard)
        bottomContentCard = findViewById(R.id.bottomContentCard)
        tvSelectedDate = findViewById(R.id.tvSelectedDate)
        tvMonthYear = findViewById(R.id.tvMonthYear)
        btnPreviousMonth = findViewById(R.id.btnPreviousMonth)
        btnNextMonth = findViewById(R.id.btnNextMonth)
        btnViewSwitch = findViewById(R.id.btnViewSwitch)
        btnAddEvent = findViewById(R.id.btnAddEvent)
        btnAICreate = findViewById(R.id.btnAICreate)
        btnSubscribe = findViewById(R.id.btnSubscribe)
        btnCloudMode = findViewById(R.id.btnCloudMode)
        recyclerView = findViewById(R.id.recyclerView)
        tabLayout = findViewById(R.id.tabLayout)
        weatherCard = findViewById(R.id.weatherCard)
        tvWeatherLocation = findViewById(R.id.tvWeatherLocation)
        tvTemperature = findViewById(R.id.tvTemperature)
        tvWeatherDesc = findViewById(R.id.tvWeatherDesc)
        tvFeelsLike = findViewById(R.id.tvFeelsLike)
        tvHumidity = findViewById(R.id.tvHumidity)
        tvWind = findViewById(R.id.tvWind)
        scrollViewHoliday = findViewById(R.id.scrollViewHoliday)
        scrollViewFortune = findViewById(R.id.scrollViewFortune)
        festivalCardsContainer = findViewById(R.id.festivalCardsContainer)
        tvHolidayHint = findViewById(R.id.tvHolidayHint)
        tvFortuneContent = findViewById(R.id.tvFortuneContent)
        
        // 初始化WeatherManager
        weatherManager = WeatherManager(
            this, weatherCard, tvWeatherLocation, tvTemperature,
            tvWeatherDesc, tvFeelsLike, tvHumidity, tvWind
        )
        
        // 初始化HolidayManager
        holidayManager = HolidayManager(
            festivalCardsContainer, tvHolidayHint, this
        )
        
        // 初始化FortuneManager
        fortuneManager = FortuneManager(this, tvFortuneContent)
        
        // 设置日程列表 RecyclerView
        adapter = EventAdapter(
            events = emptyList(),
            onItemClick = { event ->
                // 点击日程 - 显示详情
                showEventDetails(event)
            },
            onItemLongClick = { event ->
                // 长按日程 - 删除
                showDeleteConfirmDialog(event)
            }
        )
        recyclerView.layoutManager = LinearLayoutManager(this)
        recyclerView.adapter = adapter
        
        // 设置周视图时间线 RecyclerView
        weekTimelineAdapter = TimeSlotAdapter(
            events = emptyList(),
            onEventClick = { event ->
                showEventDetails(event)
            }
        )
        weekTimelineRecycler.layoutManager = LinearLayoutManager(this)
        weekTimelineRecycler.adapter = weekTimelineAdapter
        
        // 设置日视图时间线 RecyclerView
        dayViewAdapter = TimeSlotAdapter(
            events = emptyList(),
            onEventClick = { event ->
                showEventDetails(event)
            }
        )
        dayViewRecycler.layoutManager = LinearLayoutManager(this)
        dayViewRecycler.adapter = dayViewAdapter
        
        // 初始化 Tab
        tabLayout.addTab(tabLayout.newTab().setText("📅 日程安排"))
        tabLayout.addTab(tabLayout.newTab().setText("🎊 今日节日"))
        tabLayout.addTab(tabLayout.newTab().setText("🔮 今日运势"))
        
        // Tab 切换监听
        tabLayout.addOnTabSelectedListener(object : com.google.android.material.tabs.TabLayout.OnTabSelectedListener {
            override fun onTabSelected(tab: com.google.android.material.tabs.TabLayout.Tab?) {
                currentTab = tab?.position ?: 0
                switchContent(currentTab)
                // 注意：节日数据已在selectDate()中预加载，这里主要处理日程数据
                // 但为了确保数据一致性，仍然调用loadDataForDate()
                selectedDate?.let { loadDataForDate(it) }
            }
            
            override fun onTabUnselected(tab: com.google.android.material.tabs.TabLayout.Tab?) {}
            override fun onTabReselected(tab: com.google.android.material.tabs.TabLayout.Tab?) {}
        })
        
        // 设置日历
        setupCalendar()
        setupWeekCalendar()
        
        // 默认显示今天的日期
        updateDateDisplay(selectedDate!!)
        
        // 初始化列表
        updateEventsList()
        
        // 加载数据库中的日程
        loadAllEvents()
        
        // 初始化加载当前日期的节日信息（修复首次不显示问题）
        selectedDate?.let { date ->
            val millis = date.atStartOfDay(ZoneId.systemDefault()).toInstant().toEpochMilli()
            loadHolidayInfo(millis)
        }
        
        // 月份导航按钮（仅在月视图展开时使用）
        btnPreviousMonth.setOnClickListener {
            currentMonth = currentMonth.minusMonths(1)
            calendarView.scrollToMonth(currentMonth)
        }
        
        btnNextMonth.setOnClickListener {
            currentMonth = currentMonth.plusMonths(1)
            calendarView.scrollToMonth(currentMonth)
        }
        
        // 三视图切换按钮
        btnViewSwitch.setOnClickListener {
            viewMode = (viewMode + 1) % 3
            switchViewMode(viewMode)
        }
        
        // 初始化为月视图
        switchViewMode(0)
        
        // 点击"添加日程"按钮
        btnAddEvent.setOnClickListener {
            showAddEventDialog()
        }
        
        // 点击"AI创建日程"按钮
        btnAICreate.setOnClickListener {
            showAIEventDialog()
        }
        
        // 点击"订阅网络日历"按钮 - 打开订阅管理界面
        btnSubscribe.setOnClickListener {
            val intent = android.content.Intent(this, SubscriptionsActivity::class.java)
            startActivity(intent)
        }
        
        // 点击"云端模式"按钮
        btnCloudMode.setOnClickListener {
            toggleCloudMode()
        }
        
        // 初始化云端模式按钮状态
        updateCloudModeButton()
        
        Toast.makeText(this, "📅 日历已加载，数据会自动保存", Toast.LENGTH_SHORT).show()
        
        // 加载天气信息（使用WeatherManager）- 延迟加载确保UI已初始化
        lifecycleScope.launch {
            delay(200) // 等待UI完全初始化
            weatherManager.loadWeather(lifecycleScope)
        }
        
        // 请求通知权限（Android 13+）
        requestNotificationPermission()
    }
    
    /**
     * 当Activity恢复时刷新数据（从订阅页面返回时）
     */
    override fun onResume() {
        super.onResume()
        // 重新加载所有事件（包括新订阅的）
        loadAllEvents()
        // 刷新日历显示
        updateCalendarDots()
        // 刷新当前日期的节日信息
        selectedDate?.let { date ->
            val millis = date.atStartOfDay(ZoneId.systemDefault()).toInstant().toEpochMilli()
            loadHolidayInfo(millis)
        }
        // 刷新天气信息（使用WeatherManager）
        weatherManager.loadWeather(lifecycleScope)
    }
    
    // 请求通知权限
    private fun requestNotificationPermission() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            if (ContextCompat.checkSelfPermission(
                    this,
                    Manifest.permission.POST_NOTIFICATIONS
                ) != PackageManager.PERMISSION_GRANTED
            ) {
                ActivityCompat.requestPermissions(
                    this,
                    arrayOf(Manifest.permission.POST_NOTIFICATIONS),
                    1001
                )
            }
        }
    }
    
    private fun showDate(timeInMillis: Long) {
        val dateFormat = SimpleDateFormat("yyyy年MM月dd日 EEEE", Locale.CHINESE)
        val dateStr = dateFormat.format(Date(timeInMillis))
        tvSelectedDate.text = "选中日期：$dateStr"
    }
    
    // 处理Activity返回结果
    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        super.onActivityResult(requestCode, resultCode, data)
        
        if (requestCode == MapPickerActivity.REQUEST_CODE_MAP_PICKER && resultCode == RESULT_OK && data != null) {
            val locationName = data.getStringExtra("location_name") ?: ""
            val locationAddress = data.getStringExtra("location_address") ?: ""
            val latitude = data.getDoubleExtra("latitude", 0.0)
            val longitude = data.getDoubleExtra("longitude", 0.0)
            
            // 调用回调函数更新对话框
            onLocationSelectedCallback?.invoke(locationName, locationAddress, latitude, longitude)
        } else if (requestCode == REQUEST_SETTINGS && resultCode == RESULT_OK) {
            // 从设置页或登录页返回，重新加载所有事件（可能切换了模式）
            updateCloudModeButton()
            
            // 如果登录成功，自动切换到云端模式
            if (PreferenceManager.isLoggedIn(this) && !PreferenceManager.isCloudMode(this)) {
                PreferenceManager.setCloudMode(this, true)
                Toast.makeText(this, "已自动切换到云端模式", Toast.LENGTH_SHORT).show()
            }
            
            loadAllEvents()
            updateCloudModeButton()
        }
    }
    
    companion object {
        private const val REQUEST_SETTINGS = 1002
    }
    
    // 弹出添加日程的对话框
    private fun showAddEventDialog(eventToEdit: Event? = null) {
        // 加载自定义布局
        val dialogView = layoutInflater.inflate(R.layout.dialog_add_event, null)
        val etTitle = dialogView.findViewById<com.google.android.material.textfield.TextInputEditText>(R.id.etTitle)
        val etTime = dialogView.findViewById<com.google.android.material.textfield.TextInputEditText>(R.id.etTime)
        val etDesc = dialogView.findViewById<com.google.android.material.textfield.TextInputEditText>(R.id.etDescription)
        val spinnerReminder = dialogView.findViewById<Spinner>(R.id.spinnerReminder)
        val tvLocationDisplay = dialogView.findViewById<TextView>(R.id.tvLocationDisplay)
        val btnSelectLocation = dialogView.findViewById<Button>(R.id.btnSelectLocation)
        
        // 确保地点选择功能在所有视图模式下都可见
        tvLocationDisplay?.visibility = View.VISIBLE
        btnSelectLocation?.visibility = View.VISIBLE
        
        // 设置提醒选项
        val reminderOptions = arrayOf("不提醒", "提前5分钟", "提前15分钟", "提前30分钟", "提前1小时", "提前1天")
        val reminderMinutes = arrayOf(0, 5, 15, 30, 60, 24 * 60)
        spinnerReminder?.adapter = ArrayAdapter(this, android.R.layout.simple_spinner_dropdown_item, reminderOptions)
        
        // 用于存储选择的日期时间
        val calendar = Calendar.getInstance()
        
        // 用于存储选择的地点信息
        var selectedLocationName = ""
        var selectedAddress = ""
        var selectedLatitude = 0.0
        var selectedLongitude = 0.0
        
        // 如果是编辑模式，填充现有数据
        if (eventToEdit != null) {
            // 检查是否是订阅的事件
            if (eventToEdit.subscriptionId != null) {
                Toast.makeText(this, "不能编辑订阅的日程，请在订阅管理中管理", Toast.LENGTH_LONG).show()
                return
            }
            
            etTitle?.setText(eventToEdit.title)
            etDesc?.setText(eventToEdit.description)
            calendar.timeInMillis = eventToEdit.dateTime
            
            // 填充地点信息
            if (eventToEdit.locationName.isNotEmpty()) {
                selectedLocationName = eventToEdit.locationName
                selectedAddress = "" // Event没有存储详细地址，只有名称
                selectedLatitude = eventToEdit.latitude
                selectedLongitude = eventToEdit.longitude
                tvLocationDisplay?.text = "📍 $selectedLocationName"
            }
            
            // 设置提醒选项
            val reminderIndex = reminderMinutes.indexOf(eventToEdit.reminderMinutes)
            if (reminderIndex >= 0) {
                spinnerReminder?.setSelection(reminderIndex)
            }
        } else {
            // 新增模式，使用选中的日期
            val selected = selectedDate ?: LocalDate.now()
            calendar.timeInMillis = selected.atStartOfDay(ZoneId.systemDefault()).toInstant().toEpochMilli()
        }
        
        // 显示初始时间
        updateTimeDisplay(etTime, calendar)
        
        // 点击时间输入框，弹出时间选择器
        etTime?.setOnClickListener {
            showTimePicker(calendar) { hour, minute ->
                calendar.set(Calendar.HOUR_OF_DAY, hour)
                calendar.set(Calendar.MINUTE, minute)
                updateTimeDisplay(etTime, calendar)
            }
        }
        
        // 点击地点选择按钮，打开地图选择器
        btnSelectLocation?.setOnClickListener {
            // 设置回调函数，当从地图返回时更新对话框
            onLocationSelectedCallback = { name, address, lat, lng ->
                selectedLocationName = name
                selectedAddress = address
                selectedLatitude = lat
                selectedLongitude = lng
                tvLocationDisplay?.text = if (name.isNotEmpty()) {
                    "📍 $name"
                } else {
                    "点击按钮在地图上选择地点"
                }
            }
            
            val intent = Intent(this, MapPickerActivity::class.java)
            startActivityForResult(intent, MapPickerActivity.REQUEST_CODE_MAP_PICKER)
        }
        
        // 创建对话框
        val title = if (eventToEdit != null) "✏️ 编辑日程" else "📝 添加日程"
        AlertDialog.Builder(this)
            .setTitle(title)
            .setView(dialogView)
            .setPositiveButton("保存") { dialog, _ ->
                val titleText = etTitle?.text.toString().trim()
                val descText = etDesc?.text.toString().trim()
                val selectedReminderMinutes = reminderMinutes[spinnerReminder?.selectedItemPosition ?: 0]
                
                if (titleText.isNotEmpty()) {
                    if (eventToEdit != null) {
                        // 编辑模式：更新现有日程
                        updateEvent(
                            eventToEdit.id,
                            titleText,
                            descText,
                            calendar.timeInMillis,
                            selectedReminderMinutes,
                            selectedLocationName,
                            selectedLatitude,
                            selectedLongitude
                        )
                    } else {
                        // 新增模式：添加新日程
                        addEvent(
                            titleText,
                            descText,
                            calendar.timeInMillis,
                            selectedReminderMinutes,
                            selectedLocationName,
                            selectedLatitude,
                            selectedLongitude
                        )
                    }
                } else {
                    Toast.makeText(this, "标题不能为空", Toast.LENGTH_SHORT).show()
                }
            }
            .setNegativeButton("取消", null)
            .show()
    }
    
    // 显示时间选择器
    private fun showTimePicker(calendar: Calendar, onTimeSelected: (Int, Int) -> Unit) {
        val hour = calendar.get(Calendar.HOUR_OF_DAY)
        val minute = calendar.get(Calendar.MINUTE)
        
        TimePickerDialog(
            this,
            { _, selectedHour, selectedMinute ->
                onTimeSelected(selectedHour, selectedMinute)
            },
            hour,
            minute,
            true  // 24小时制
        ).show()
    }
    
    // 更新时间显示
    private fun updateTimeDisplay(editText: com.google.android.material.textfield.TextInputEditText?, calendar: Calendar) {
        val timeFormat = SimpleDateFormat("yyyy-MM-dd HH:mm", Locale.getDefault())
        editText?.setText(timeFormat.format(calendar.time))
    }
    
    // 从数据库/云端加载所有日程（根据模式自动切换）
    private fun loadAllEvents() {
        lifecycleScope.launch(Dispatchers.IO) {
            try {
                val userEvents: List<Event>
                
                // 根据模式获取用户自己的事件
                if (PreferenceManager.isCloudMode(this@MainActivity) && PreferenceManager.isLoggedIn(this@MainActivity)) {
                    // 云端模式：从API获取
                    val result = eventRepository.getAllEvents()
                    userEvents = result.getOrElse { emptyList() }
                } else {
                    // 本地模式：从数据库获取
                    userEvents = eventDao.getUserEvents()
                }
                
                // 获取订阅的日历事件（订阅始终是本地存储的）
                val subscriptionEvents = subscriptionManager.getVisibleEvents()
                    .filter { it.subscriptionId != null } // 只要订阅的事件
                
                // 合并用户事件和订阅事件
                val allEvents = userEvents + subscriptionEvents
                
                withContext(Dispatchers.Main) {
                    eventsList.clear()
                    eventsList.addAll(allEvents)
                    updateCalendarDots()  // 更新日历标记
                    
                    // 根据当前视图模式更新显示
                    when (viewMode) {
                        0 -> {
                            // 月视图：更新事件列表
                            updateEventsList()
                        }
                        1 -> {
                            // 周视图：更新时间线
                            updateWeekView()
                        }
                        2 -> {
                            // 日视图：更新时间线
                            updateDayView()
                        }
                    }
                    
                    // 刷新周视图日历
                    weekCalendarView.notifyCalendarChanged()
                }
            } catch (e: Exception) {
                Log.e("MainActivity", "加载日程失败", e)
                withContext(Dispatchers.Main) {
                    Toast.makeText(this@MainActivity, "加载失败: ${e.message}", Toast.LENGTH_SHORT).show()
                }
            }
        }
    }
    
    // 加载指定日期的日程（根据模式自动切换）
    private fun loadEventsForSelectedDate(date: Long) {
        lifecycleScope.launch(Dispatchers.IO) {
            try {
                val userEvents: List<Event>
                
                // 根据模式获取用户自己的事件
                if (PreferenceManager.isCloudMode(this@MainActivity) && PreferenceManager.isLoggedIn(this@MainActivity)) {
                    // 云端模式：从API获取
                    val result = eventRepository.getEventsForDate(date)
                    userEvents = result.getOrElse { emptyList() }
                } else {
                    // 本地模式：从数据库获取
                    userEvents = eventDao.getEventsForDate(date)
                        .filter { it.subscriptionId == null } // 只要用户创建的
                }
                
                // 获取订阅的日历事件（订阅始终是本地存储的）
                val subscriptionEvents = subscriptionManager.getVisibleEvents(date)
                    .filter { it.subscriptionId != null } // 只要订阅的事件
                
                // 合并用户事件和订阅事件
                val allEvents = userEvents + subscriptionEvents
                
                withContext(Dispatchers.Main) {
                    eventsList.clear()
                    eventsList.addAll(allEvents)
                    updateEventsList()
                }
            } catch (e: Exception) {
                Log.e("MainActivity", "加载日程失败", e)
            }
        }
    }
    
    // 添加日程（根据模式自动切换本地/云端）
    private fun addEvent(
        title: String,
        description: String = "",
        dateTime: Long,
        reminderMinutes: Int = 0,
        locationName: String = "",
        latitude: Double = 0.0,
        longitude: Double = 0.0
    ) {
        lifecycleScope.launch(Dispatchers.IO) {
            try {
                val event = Event(
                    title = title,
                    description = description,
                    dateTime = dateTime,
                    reminderMinutes = reminderMinutes,
                    subscriptionId = null,  // 用户创建的日程
                    locationName = locationName,
                    latitude = latitude,
                    longitude = longitude
                )
                
                // 根据模式创建事件
                val result = eventRepository.createEvent(event)
                val savedEvent = result.getOrElse {
                    withContext(Dispatchers.Main) {
                        Toast.makeText(this@MainActivity, "保存失败: ${it.message}", Toast.LENGTH_SHORT).show()
                    }
                    return@launch
                }
                
                // 设置提醒
                if (reminderMinutes > 0) {
                    withContext(Dispatchers.Main) {
                        reminderManager.setReminder(savedEvent)
                        
                        // 计算提醒时间并显示
                        val reminderTime = dateTime - (reminderMinutes * 60 * 1000)
                        val df = SimpleDateFormat("HH:mm", Locale.getDefault())
                        Toast.makeText(
                            this@MainActivity,
                            "⏰ 将在 ${df.format(Date(reminderTime))} 提醒您",
                            Toast.LENGTH_LONG
                        ).show()
                    }
                }
                
                // 重新加载数据
                selectedDate?.let { 
                    val millis = it.atStartOfDay(ZoneId.systemDefault()).toInstant().toEpochMilli()
                    loadEventsForSelectedDate(millis)
                }
                updateCalendarDots()  // 更新日历标记
                
                withContext(Dispatchers.Main) {
                    // 刷新周视图
                    weekCalendarView.notifyCalendarChanged()
                    Toast.makeText(this@MainActivity, "✅ 添加成功！", Toast.LENGTH_SHORT).show()
                }
            } catch (e: Exception) {
                withContext(Dispatchers.Main) {
                    Toast.makeText(this@MainActivity, "保存失败: ${e.message}", Toast.LENGTH_SHORT).show()
                }
            }
        }
    }
    
    // 更新日程（只能更新用户创建的，根据模式自动切换本地/云端）
    private fun updateEvent(
        id: Long,
        title: String,
        description: String,
        dateTime: Long,
        reminderMinutes: Int = 0,
        locationName: String = "",
        latitude: Double = 0.0,
        longitude: Double = 0.0
    ) {
        lifecycleScope.launch(Dispatchers.IO) {
            try {
                // 根据模式获取现有事件
                val existingEvent: Event? = if (PreferenceManager.isCloudMode(this@MainActivity) && PreferenceManager.isLoggedIn(this@MainActivity)) {
                    // 云端模式：从API获取
                    val result = eventRepository.getAllEvents()
                    result.getOrNull()?.find { it.id == id }
                } else {
                    // 本地模式：从数据库获取
                    eventDao.getAllEvents().find { it.id == id }
                }
                
                if (existingEvent == null) {
                    withContext(Dispatchers.Main) {
                        Toast.makeText(this@MainActivity, "日程不存在", Toast.LENGTH_SHORT).show()
                    }
                    return@launch
                }
                
                if (existingEvent.subscriptionId != null) {
                    withContext(Dispatchers.Main) {
                        Toast.makeText(this@MainActivity, "不能编辑订阅的日程", Toast.LENGTH_SHORT).show()
                    }
                    return@launch
                }
                
                // 先取消旧提醒
                withContext(Dispatchers.Main) {
                    reminderManager.cancelReminder(id)
                }
                
                val event = Event(
                    id = id,
                    title = title,
                    description = description,
                    dateTime = dateTime,
                    reminderMinutes = reminderMinutes,
                    subscriptionId = null,  // 保持为null
                    locationName = locationName,
                    latitude = latitude,
                    longitude = longitude
                )
                
                // 根据模式更新事件
                val result = eventRepository.updateEvent(event)
                if (result.isFailure) {
                    withContext(Dispatchers.Main) {
                        Toast.makeText(this@MainActivity, "更新失败: ${result.exceptionOrNull()?.message}", Toast.LENGTH_SHORT).show()
                    }
                    return@launch
                }
                
                // 设置新提醒
                if (reminderMinutes > 0) {
                    withContext(Dispatchers.Main) {
                        reminderManager.setReminder(event)
                    }
                }
                
                // 重新加载数据
                selectedDate?.let { 
                    val millis = it.atStartOfDay(ZoneId.systemDefault()).toInstant().toEpochMilli()
                    loadEventsForSelectedDate(millis)
                }
                updateCalendarDots()  // 更新日历标记
                
                withContext(Dispatchers.Main) {
                    // 刷新周视图
                    weekCalendarView.notifyCalendarChanged()
                    Toast.makeText(this@MainActivity, "✅ 更新成功！", Toast.LENGTH_SHORT).show()
                }
            } catch (e: Exception) {
                withContext(Dispatchers.Main) {
                    Toast.makeText(this@MainActivity, "更新失败: ${e.message}", Toast.LENGTH_SHORT).show()
                }
            }
        }
    }
    
    // 更新日程列表显示（只显示选中日期的事件）
    private fun updateEventsList() {
        // 过滤出选中日期的事件，且只显示用户创建的事件（排除订阅的）
        val selected = selectedDate ?: return
        
        val filteredEvents = eventsList.filter { event ->
            val eventDate = Instant.ofEpochMilli(event.dateTime)
                .atZone(ZoneId.systemDefault())
                .toLocalDate()
            // 只显示用户创建的日程（subscriptionId == null）
            eventDate == selected && event.subscriptionId == null
        }
        
        adapter.updateEvents(filteredEvents)
    }
    
    // 显示日程详情
    private fun showEventDetails(event: Event) {
        val dateFormat = SimpleDateFormat("yyyy年MM月dd日 EEEE HH:mm", Locale.CHINESE)
        val dateStr = dateFormat.format(Date(event.dateTime))
        
        // 获取订阅信息（同步获取）
        var subscriptionName: String? = null
        if (event.subscriptionId != null) {
            lifecycleScope.launch(Dispatchers.IO) {
                try {
                    val subscription = subscriptionDao.getAllSubscriptions().find { it.id == event.subscriptionId }
                    subscriptionName = subscription?.name
                    
                    // 获取农历信息
                    getLunarDate(event.dateTime) { lunar ->
                        val message = buildString {
                            append("📅 日期：$dateStr\n\n")
                            append("📝 标题：${event.title}\n\n")
                            if (event.description.isNotEmpty()) {
                                append("💬 描述：${event.description}\n\n")
                            }
                            if (subscriptionName != null) {
                                append("📡 来源：$subscriptionName\n\n")
                            }
                            if (lunar.isNotEmpty()) {
                                append("🏮 农历：$lunar")
                            }
                        }
                        
                        val builder = AlertDialog.Builder(this@MainActivity)
                            .setTitle("📋 日程详情")
                            .setMessage(message)
                            .setNeutralButton("关闭", null)
                        
                        // 只有用户创建的日程才能编辑和删除
                        if (event.subscriptionId == null) {
                            builder.setPositiveButton("编辑") { _, _ ->
                                showAddEventDialog(event)
                            }
                            builder.setNegativeButton("删除") { _, _ ->
                                deleteEvent(event)
                            }
                        }
                        
                        builder.show()
                    }
                } catch (e: Exception) {
                    // 如果获取订阅信息失败，直接显示
                    showEventDetailsWithoutSubscription(event, dateStr)
                }
            }
        } else {
            // 用户创建的日程，直接显示
            getLunarDate(event.dateTime) { lunar ->
                val message = buildString {
                    append("📅 日期：$dateStr\n\n")
                    append("📝 标题：${event.title}\n\n")
                    if (event.description.isNotEmpty()) {
                        append("💬 描述：${event.description}\n\n")
                    }
                    if (lunar.isNotEmpty()) {
                        append("🏮 农历：$lunar")
                    }
                }
                
                AlertDialog.Builder(this)
                    .setTitle("📋 日程详情")
                    .setMessage(message)
                    .setPositiveButton("编辑") { _, _ ->
                        showAddEventDialog(event)
                    }
                    .setNegativeButton("删除") { _, _ ->
                        deleteEvent(event)
                    }
                    .setNeutralButton("关闭", null)
                    .show()
            }
        }
    }
    
    // 显示日程详情（无订阅信息版本）
    private fun showEventDetailsWithoutSubscription(event: Event, dateStr: String) {
        val message = buildString {
            append("📅 日期：$dateStr\n\n")
            append("📝 标题：${event.title}\n\n")
            if (event.description.isNotEmpty()) {
                append("💬 描述：${event.description}\n\n")
            }
        }
        
        val builder = AlertDialog.Builder(this)
            .setTitle("📋 日程详情")
            .setMessage(message)
            .setNeutralButton("关闭", null)
        
        if (event.subscriptionId == null) {
            builder.setPositiveButton("编辑") { _, _ ->
                showAddEventDialog(event)
            }
            builder.setNegativeButton("删除") { _, _ ->
                deleteEvent(event)
            }
        }
        
        builder.show()
    }
    
    // 显示删除确认对话框
    private fun showDeleteConfirmDialog(event: Event) {
        AlertDialog.Builder(this)
            .setTitle("🗑️ 删除日程")
            .setMessage("确定要删除「${event.title}」吗？")
            .setPositiveButton("删除") { _, _ ->
                deleteEvent(event)
            }
            .setNegativeButton("取消", null)
            .show()
    }
    
    // 删除日程（只能删除用户创建的，不能删除订阅的，根据模式自动切换本地/云端）
    private fun deleteEvent(event: Event) {
        // 检查是否是订阅的事件
        if (event.subscriptionId != null) {
            Toast.makeText(this, "不能删除订阅的日程，请在订阅管理中取消订阅", Toast.LENGTH_LONG).show()
            return
        }
        
        lifecycleScope.launch(Dispatchers.IO) {
            try {
                // 取消提醒
                withContext(Dispatchers.Main) {
                    reminderManager.cancelReminder(event.id)
                }
                
                // 根据模式删除事件
                val result = eventRepository.deleteEvent(event)
                if (result.isFailure) {
                    withContext(Dispatchers.Main) {
                        Toast.makeText(this@MainActivity, "删除失败: ${result.exceptionOrNull()?.message}", Toast.LENGTH_SHORT).show()
                    }
                    return@launch
                }
                
                // 重新加载数据
                selectedDate?.let { 
                    val millis = it.atStartOfDay(ZoneId.systemDefault()).toInstant().toEpochMilli()
                    loadEventsForSelectedDate(millis)
                }
                updateCalendarDots()  // 更新日历标记
                
                withContext(Dispatchers.Main) {
                    // 刷新周视图
                    weekCalendarView.notifyCalendarChanged()
                    Toast.makeText(this@MainActivity, "🗑️ 删除成功！", Toast.LENGTH_SHORT).show()
                }
            } catch (e: Exception) {
                withContext(Dispatchers.Main) {
                    Toast.makeText(this@MainActivity, "删除失败: ${e.message}", Toast.LENGTH_SHORT).show()
                }
            }
        }
    }
    
    // ==================== 网络功能 ====================
    // 订阅功能已移至 SubscriptionsActivity
    
    /**
     * 获取农历日期（在日程详情显示）
     */
    private fun getLunarDate(dateTime: Long, callback: (String) -> Unit) {
        lifecycleScope.launch(Dispatchers.IO) {
            try {
                val dateFormat = SimpleDateFormat("yyyy-MM-dd", Locale.getDefault())
                val dateStr = dateFormat.format(Date(dateTime))
                
                // 调用后端 API
                val lunar = RetrofitClient.api.getLunarDate(dateStr)
                
                withContext(Dispatchers.Main) {
                    callback("${lunar.lunar_date} ${lunar.zodiac}年")
                }
            } catch (e: Exception) {
                Log.e("Network", "获取农历失败", e)
                withContext(Dispatchers.Main) {
                    callback("")  // 失败就不显示
                }
            }
        }
    }
    
    // ==================== Tab 切换功能 ====================
    
    /**
     * 切换显示的内容区域
     */
    private fun switchContent(tabIndex: Int) {
        when (tabIndex) {
            0 -> {
                // 日程安排
                recyclerView.visibility = android.view.View.VISIBLE
                scrollViewHoliday.visibility = android.view.View.GONE
                scrollViewFortune.visibility = android.view.View.GONE
            }
            1 -> {
                // 今日节日
                recyclerView.visibility = android.view.View.GONE
                scrollViewHoliday.visibility = android.view.View.VISIBLE
                scrollViewFortune.visibility = android.view.View.GONE
            }
            2 -> {
                // 今日运势
                recyclerView.visibility = android.view.View.GONE
                scrollViewHoliday.visibility = android.view.View.GONE
                scrollViewFortune.visibility = android.view.View.VISIBLE
            }
        }
    }
    
    /**
     * 根据当前选中的 Tab 加载数据
     */
    private fun loadDataForSelectedDate(date: Long) {
        when (currentTab) {
            0 -> {
                // 加载日程
                loadEventsForSelectedDate(date)
            }
            1 -> {
                // 加载节日信息
                loadHolidayInfo(date)
            }
            2 -> {
                // ✅ 使用 FortuneManager 加载今日运势（结合天气）
                fortuneManager.loadFortune(
                    weatherManager.currentWeather,
                    weatherManager.currentTemperature
                )
            }
        }
    }
    
    /**
     * 加载节日信息（合并API节日 + 订阅的节日）
     */
    private fun loadHolidayInfo(date: Long) {
        // ✅ 使用 HolidayManager 处理节日信息加载
        holidayManager.loadHolidayInfo(date, eventsList, lifecycleScope)
    }
    
    // ✅ loadWeather() 已被 WeatherManager 替代，位于 ui/managers/WeatherManager.kt
    
    // ✅ addFestivalCard() 已被 HolidayManager 替代，位于 ui/managers/HolidayManager.kt
    
    // ==================== 日历设置和辅助方法 ====================
    
    /**
     * 初始化日历
     */
    private fun setupCalendar() {
        // 设置日历显示范围：当前月份前后各6个月
        val startMonth = YearMonth.now().minusMonths(6)
        val endMonth = YearMonth.now().plusMonths(6)
        val firstDayOfWeek = daysOfWeek().first()  // 周日为第一天
        
        calendarView.setup(startMonth, endMonth, firstDayOfWeek)
        calendarView.scrollToMonth(currentMonth)
        
        // 设置日期绑定器
        calendarView.dayBinder = object : MonthDayBinder<DayViewContainer> {
            override fun create(view: View) = DayViewContainer(view)
            
            override fun bind(container: DayViewContainer, data: CalendarDay) {
                container.day = data
                val textView = container.textView
                val dotView = container.dotView
                val festivalLabel = container.festivalLabel
                
                textView.text = data.date.dayOfMonth.toString()
                
                // 根据日期位置设置样式
                when (data.position) {
                    DayPosition.MonthDate -> {
                        textView.visibility = View.VISIBLE
                        
                        // 设置日期背景和颜色
                        when {
                            // 选中的日期
                            selectedDate == data.date -> {
                                textView.setBackgroundResource(R.drawable.calendar_day_selected)
                                textView.setTextColor(getColor(android.R.color.white))
                            }
                            // 今天
                            data.date == LocalDate.now() -> {
                                textView.setBackgroundResource(R.drawable.calendar_day_today)
                                textView.setTextColor(getColor(R.color.purple_500))
                            }
                            // 普通日期
                            else -> {
                                textView.background = null
                                textView.setTextColor(getColor(R.color.black))
                            }
                        }
                        
                        // 显示节日名称（有节日的日期）
                        val festivalName = datesWithFestivals[data.date]
                        if (festivalName != null) {
                            festivalLabel.text = festivalName
                            festivalLabel.visibility = View.VISIBLE
                        } else {
                            festivalLabel.visibility = View.GONE
                        }
                        
                        // 显示标记点（有用户日程的日期）
                        dotView.visibility = if (datesWithEvents.contains(data.date)) {
                            View.VISIBLE
                        } else {
                            View.GONE
                        }
                    }
                    else -> {
                        // 不属于当前月份的日期
                        textView.visibility = View.INVISIBLE
                        dotView.visibility = View.GONE
                        festivalLabel.visibility = View.GONE
                    }
                }
            }
        }
        
        // 设置月份滚动监听
        calendarView.monthScrollListener = object : MonthScrollListener {
            override fun invoke(month: CalendarMonth) {
                currentMonth = month.yearMonth
                updateMonthYearDisplay(currentMonth)
            }
        }
        
        // 更新月份显示
        updateMonthYearDisplay(currentMonth)
    }
    
    /**
     * 初始化周视图
     */
    private fun setupWeekCalendar() {
        val startWeek = LocalDate.now().minusWeeks(52)
        val endWeek = LocalDate.now().plusWeeks(52)
        val firstDayOfWeek = daysOfWeek().first()
        
        weekCalendarView.setup(startWeek, endWeek, firstDayOfWeek)
        weekCalendarView.scrollToWeek(LocalDate.now())
        
        // 设置周视图绑定器
        weekCalendarView.dayBinder = object : WeekDayBinder<WeekDayViewContainer> {
            override fun create(view: View) = WeekDayViewContainer(view)
            
            override fun bind(container: WeekDayViewContainer, data: com.kizitonwose.calendar.core.WeekDay) {
                container.day = data
                
                // 设置星期几
                val dayOfWeekMap = mapOf(
                    java.time.DayOfWeek.MONDAY to "周一",
                    java.time.DayOfWeek.TUESDAY to "周二",
                    java.time.DayOfWeek.WEDNESDAY to "周三",
                    java.time.DayOfWeek.THURSDAY to "周四",
                    java.time.DayOfWeek.FRIDAY to "周五",
                    java.time.DayOfWeek.SATURDAY to "周六",
                    java.time.DayOfWeek.SUNDAY to "周日"
                )
                val weekDayText = dayOfWeekMap[data.date.dayOfWeek] ?: "?"
                container.dayText.text = weekDayText
                container.dayText.visibility = View.VISIBLE
                container.numberText.text = data.date.dayOfMonth.toString()
                
                // 设置样式（先设置默认样式，再设置特殊样式）
                if (selectedDate == data.date) {
                    // 选中日期
                    container.numberText.setPadding(0, 0, 0, 0)
                    container.numberText.setBackgroundResource(R.drawable.calendar_day_selected)
                    container.numberText.setTextColor(getColor(android.R.color.white))
                } else if (data.date == LocalDate.now()) {
                    // 今天
                    container.numberText.setPadding(0, 0, 0, 0)
                    container.numberText.setBackgroundResource(R.drawable.calendar_day_today)
                    container.numberText.setTextColor(getColor(R.color.purple_500))
                } else {
                    // 普通日期
                    container.numberText.setPadding(0, 0, 0, 0)
                    container.numberText.background = null
                    container.numberText.setTextColor(getColor(R.color.black))
                }
                
                // 显示节日名称（有节日的日期）
                val festivalName = datesWithFestivals[data.date]
                if (festivalName != null) {
                    container.festivalLabel.text = festivalName
                    container.festivalLabel.visibility = View.VISIBLE
                } else {
                    container.festivalLabel.visibility = View.GONE
                }
                
                // 显示标记点（有用户日程的日期）
                container.dotView.visibility = if (datesWithEvents.contains(data.date)) {
                    View.VISIBLE
                } else {
                    View.GONE
                }
            }
        }
        
        // 周视图滚动监听
        weekCalendarView.weekScrollListener = { week ->
            updateMonthYearDisplay(YearMonth.from(week.days.first().date))
        }
    }
    
    /**
     * 切换视图模式（0=月 1=周 2=日）
     */
    private fun switchViewMode(mode: Int) {
        when (mode) {
            0 -> {
                // 月视图：显示整月日历 + 下方Tab + 天气
                monthViewCard.visibility = View.VISIBLE
                weekViewContainer.visibility = View.GONE
                dayViewCard.visibility = View.GONE
                bottomContentCard.visibility = View.VISIBLE
                weatherCard.visibility = View.VISIBLE
                tvSelectedDate.visibility = View.VISIBLE
                btnViewSwitch.text = "📅 月"
                
                // 滚动到选中日期所在的月份
                selectedDate?.let { 
                    val yearMonth = YearMonth.from(it)
                    currentMonth = yearMonth
                    calendarView.scrollToMonth(yearMonth)
                }
                
                // 恢复Tab内容
                switchContent(currentTab)
                
                // 重新加载所有事件并刷新显示
                loadAllEvents()
            }
            1 -> {
                // 周视图：横向7天选择器 + 时间线（不显示底部内容和天气）
                monthViewCard.visibility = View.GONE
                weekViewContainer.visibility = View.VISIBLE
                dayViewCard.visibility = View.GONE
                bottomContentCard.visibility = View.GONE
                weatherCard.visibility = View.GONE
                tvSelectedDate.visibility = View.VISIBLE
                btnViewSwitch.text = "📅 周"
                
                // 滚动到选中日期所在的周
                selectedDate?.let { weekCalendarView.scrollToWeek(it) }
                
                // 重新加载所有事件并更新时间线
                loadAllEvents()
            }
            2 -> {
                // 日视图：只显示时间线（不显示底部内容和天气）
                monthViewCard.visibility = View.GONE
                weekViewContainer.visibility = View.GONE
                dayViewCard.visibility = View.VISIBLE
                bottomContentCard.visibility = View.GONE
                weatherCard.visibility = View.GONE
                tvSelectedDate.visibility = View.VISIBLE
                btnViewSwitch.text = "📅 日"
                
                // 重新加载所有事件并更新时间线
                loadAllEvents()
            }
        }
    }
    
    /**
     * 选择日期
     */
    private fun selectDate(date: LocalDate) {
        if (selectedDate != date) {
            val oldDate = selectedDate
            selectedDate = date
            
            // 更新月视图的显示
            oldDate?.let { calendarView.notifyDateChanged(it) }
            calendarView.notifyDateChanged(date)
            
            // 刷新整个周视图（确保旧的选中状态被清除）
            weekCalendarView.notifyCalendarChanged()
            
            // 更新显示
            updateDateDisplay(date)
            
            // 转换日期为毫秒
            val millis = date.atStartOfDay(ZoneId.systemDefault()).toInstant().toEpochMilli()
            
            // **始终加载节日数据**（无论当前在哪个视图和Tab）
            // 这样切换日期后，用户点击"今日节日"Tab时能立即看到最新数据
            loadHolidayInfo(millis)
            
            // 根据当前视图模式加载其他数据
            when (viewMode) {
                0 -> {
                    // 月视图：加载当前日期的日程到eventsList并显示在底部
                    loadEventsForSelectedDate(millis)
                }
                1 -> {
                    // 周视图：如果eventsList为空，需要加载所有事件
                    // 否则直接更新时间线显示（loadAllEvents已在切换视图时调用）
                    if (eventsList.isEmpty()) {
                        loadAllEvents()
                    } else {
                        updateWeekView()
                    }
                }
                2 -> {
                    // 日视图：如果eventsList为空，需要加载所有事件
                    // 否则直接更新时间线显示（loadAllEvents已在切换视图时调用）
                    if (eventsList.isEmpty()) {
                        loadAllEvents()
                    } else {
                        updateDayView()
                    }
                }
            }
        }
    }
    
    /**
     * 更新选中日期的显示
     */
    private fun updateDateDisplay(date: LocalDate) {
        val formatter = DateTimeFormatter.ofPattern("yyyy年MM月dd日 EEEE", Locale.CHINESE)
        tvSelectedDate.text = "选中日期: ${date.format(formatter)}"
    }
    
    /**
     * 更新月份年份显示
     */
    private fun updateMonthYearDisplay(yearMonth: YearMonth) {
        val formatter = DateTimeFormatter.ofPattern("yyyy年MM月", Locale.CHINESE)
        tvMonthYear.text = yearMonth.format(formatter)
    }
    
    /**
     * 加载指定日期的数据（根据当前Tab）
     */
    private fun loadDataForDate(date: LocalDate) {
        // 转换 LocalDate 到 Long (毫秒)
        val millis = date.atStartOfDay(ZoneId.systemDefault()).toInstant().toEpochMilli()
        
        when (currentTab) {
            0 -> loadEventsForSelectedDate(millis)
            1 -> loadHolidayInfo(millis)
            2 -> {
                // ✅ 使用 FortuneManager 加载今日运势（结合天气）
                fortuneManager.loadFortune(
                    weatherManager.currentWeather,
                    weatherManager.currentTemperature
                )
            }
        }
    }
    
    /**
     * 更新日历上的标记点（显示哪些日期有日程）
     */
    private fun updateCalendarDots() {
        lifecycleScope.launch(Dispatchers.IO) {
            try {
                // 根据模式获取用户自己的事件
                val userEvents: List<Event>
                if (PreferenceManager.isCloudMode(this@MainActivity) && PreferenceManager.isLoggedIn(this@MainActivity)) {
                    // 云端模式：从API获取
                    val result = eventRepository.getAllEvents()
                    userEvents = result.getOrElse { emptyList() }
                } else {
                    // 本地模式：从数据库获取
                    userEvents = eventDao.getUserEvents()
                }
                
                // 获取订阅的日历事件（订阅始终是本地存储的）
                val festivalEvents = subscriptionManager.getVisibleEvents()
                    .filter { it.subscriptionId != null }
                
                // 转换为 LocalDate 集合
                val newDatesWithEvents = userEvents.map { event ->
                    Instant.ofEpochMilli(event.dateTime)
                        .atZone(ZoneId.systemDefault())
                        .toLocalDate()
                }.toSet()
                
                // 转换为 Map<LocalDate, 节日名称>
                val newDatesWithFestivals = festivalEvents.associate { event ->
                    val date = Instant.ofEpochMilli(event.dateTime)
                        .atZone(ZoneId.systemDefault())
                        .toLocalDate()
                    // 提取节日名称（去掉emoji）
                    val name = event.title.replace(Regex("[^\\p{L}\\p{N}]+"), "").take(4) // 最多4个字
                    date to name
                }
                
                withContext(Dispatchers.Main) {
                    datesWithEvents.clear()
                    datesWithEvents.addAll(newDatesWithEvents)
                    
                    datesWithFestivals.clear()
                    datesWithFestivals.putAll(newDatesWithFestivals)
                    
                    // 刷新日历显示
                    calendarView.notifyCalendarChanged()
                    weekCalendarView.notifyCalendarChanged()
                }
            } catch (e: Exception) {
                Log.e("MainActivity", "更新日历标记失败", e)
            }
        }
    }
    
    /**
     * 更新周视图时间线
     */
    private fun updateWeekView() {
        val selected = selectedDate ?: LocalDate.now()
        
        val filteredEvents = eventsList.filter { event ->
            val eventDate = Instant.ofEpochMilli(event.dateTime)
                .atZone(ZoneId.systemDefault())
                .toLocalDate()
            eventDate == selected
        }
        
        weekTimelineAdapter.updateEvents(filteredEvents)
    }
    
    /**
     * 更新日视图（时间线）
     */
    private fun updateDayView() {
        // 过滤出选中日期的事件
        val selected = selectedDate ?: return
        
        val filteredEvents = eventsList.filter { event ->
            val eventDate = Instant.ofEpochMilli(event.dateTime)
                .atZone(ZoneId.systemDefault())
                .toLocalDate()
            eventDate == selected
        }
        
        dayViewAdapter.updateEvents(filteredEvents)
    }
    
    /**
     * 打开节日详情页面
     */
    private fun openFestivalDetail(name: String, emoji: String, date: String) {
        val intent = android.content.Intent(this, FestivalDetailActivity::class.java).apply {
            putExtra("festivalName", name)
            putExtra("festivalEmoji", emoji)
            putExtra("festivalDate", date)
        }
        startActivity(intent)
    }
    
    /**
     * 显示添加日程对话框（传统方式）
     */
    private fun showAddEventDialog() {
        Toast.makeText(this, "传统添加日程功能（待实现）", Toast.LENGTH_SHORT).show()
    }
    
    /**
     * 显示AI创建日程对话框
     */
    private fun showAIEventDialog() {
        val dialogView = layoutInflater.inflate(R.layout.dialog_ai_event, null)
        val dialog = AlertDialog.Builder(this)
            .setView(dialogView)
            .create()
        
        // 获取视图元素
        val etAIInput = dialogView.findViewById<TextInputEditText>(R.id.etAIInput)
        val llParsedResult = dialogView.findViewById<LinearLayout>(R.id.llParsedResult)
        val llLoading = dialogView.findViewById<LinearLayout>(R.id.llLoading)
        val tvError = dialogView.findViewById<TextView>(R.id.tvError)
        val btnCancel = dialogView.findViewById<Button>(R.id.btnCancel)
        val btnParse = dialogView.findViewById<Button>(R.id.btnParse)
        val btnConfirm = dialogView.findViewById<Button>(R.id.btnConfirm)
        
        val tvParsedTitle = dialogView.findViewById<TextView>(R.id.tvParsedTitle)
        val tvParsedDate = dialogView.findViewById<TextView>(R.id.tvParsedDate)
        val tvParsedTime = dialogView.findViewById<TextView>(R.id.tvParsedTime)
        val tvParsedDesc = dialogView.findViewById<TextView>(R.id.tvParsedDesc)
        val llParsedTime = dialogView.findViewById<LinearLayout>(R.id.llParsedTime)
        val llParsedDesc = dialogView.findViewById<LinearLayout>(R.id.llParsedDesc)
        
        var parsedEventData: com.ncu.kotlincalendar.api.models.ParsedEvent? = null
        
        // 取消按钮
        btnCancel.setOnClickListener {
            dialog.dismiss()
        }
        
        // AI解析按钮
        btnParse.setOnClickListener {
            val userInput = etAIInput.text.toString().trim()
            
            if (userInput.isEmpty()) {
                Toast.makeText(this, "请输入日程描述", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }
            
            // 显示加载状态
            llLoading.visibility = View.VISIBLE
            llParsedResult.visibility = View.GONE
            tvError.visibility = View.GONE
            btnParse.isEnabled = false
            
            // 调用AI接口
            lifecycleScope.launch(Dispatchers.IO) {
                try {
                    val request = com.ncu.kotlincalendar.api.models.ParseEventRequest(userInput)
                    val response = RetrofitClient.api.parseEventFromText(request)
                    
                    withContext(Dispatchers.Main) {
                        llLoading.visibility = View.GONE
                        btnParse.isEnabled = true
                        
                        if (response.success && response.event != null) {
                            // 解析成功
                            val event = response.event
                            parsedEventData = event
                            
                            tvParsedTitle.text = event.title
                            tvParsedDate.text = event.date
                            
                            if (event.time != null) {
                                tvParsedTime.text = event.time
                                llParsedTime.visibility = View.VISIBLE
                            } else {
                                llParsedTime.visibility = View.GONE
                            }
                            
                            if (!event.description.isNullOrEmpty()) {
                                tvParsedDesc.text = event.description
                                llParsedDesc.visibility = View.VISIBLE
                            } else {
                                llParsedDesc.visibility = View.GONE
                            }
                            
                            // 显示解析结果
                            llParsedResult.visibility = View.VISIBLE
                            btnParse.visibility = View.GONE
                            btnConfirm.visibility = View.VISIBLE
                            
                            // 确保按钮可见（延迟执行以等待布局完成）
                            dialogView.postDelayed({
                                btnConfirm.requestFocus()
                                // 滚动到底部
                                val scrollView = dialogView.parent as? android.widget.ScrollView
                                scrollView?.fullScroll(View.FOCUS_DOWN)
                            }, 100)
                            
                        } else {
                            // 解析失败
                            tvError.text = response.error ?: "AI解析失败，请尝试更清晰的描述"
                            tvError.visibility = View.VISIBLE
                        }
                    }
                    
                } catch (e: Exception) {
                    withContext(Dispatchers.Main) {
                        llLoading.visibility = View.GONE
                        btnParse.isEnabled = true
                        tvError.text = "网络错误：${e.message}"
                        tvError.visibility = View.VISIBLE
                    }
                }
            }
        }
        
        // 确认创建按钮
        btnConfirm.setOnClickListener {
            val eventData = parsedEventData
            if (eventData == null) {
                Toast.makeText(this, "没有解析结果", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }
            
            // 构建事件数据
            val title = eventData.title
            val date = eventData.date
            val time = eventData.time
            val description = eventData.description ?: ""
            
            // 组装日期时间
            val dateTime = if (time != null) {
                "${date}T${time}:00"
            } else {
                "${date}T09:00:00"  // 默认早上9点
            }
            
            // 创建Event对象
            val event = Event(
                id = 0,  // 新事件ID为0
                title = title,
                description = description,
                dateTime = Instant.parse(dateTime).toEpochMilli(),
                reminderMinutes = eventData.reminder_minutes ?: 15,
                subscriptionId = null,  // 用户创建的日程
                locationName = "",
                latitude = 0.0,
                longitude = 0.0
            )
            
            // 保存到数据库
            lifecycleScope.launch(Dispatchers.IO) {
                eventDao.insert(event)
                
                withContext(Dispatchers.Main) {
                    Toast.makeText(this@MainActivity, "✅ 日程创建成功！", Toast.LENGTH_SHORT).show()
                    dialog.dismiss()
                    
                    // 刷新界面
                    loadAllEvents()
                    updateCalendarDots()
                }
            }
        }
        
        dialog.show()
    }
    
    /**
     * 切换云端/本地模式
     */
    private fun toggleCloudMode() {
        val isCurrentlyCloud = PreferenceManager.isCloudMode(this)
        
        if (isCurrentlyCloud) {
            // 当前是云端模式，切换到本地
            AlertDialog.Builder(this)
                .setTitle("切换到本地模式")
                .setMessage("切换后将使用本地数据，云端数据不会同步。确定切换吗？")
                .setPositiveButton("确定") { _, _ ->
                    PreferenceManager.setCloudMode(this, false)
                    updateCloudModeButton()
                    loadAllEvents()
                    Toast.makeText(this, "已切换到本地模式", Toast.LENGTH_SHORT).show()
                }
                .setNegativeButton("取消", null)
                .show()
        } else {
            // 当前是本地模式，切换到云端
            if (!PreferenceManager.isLoggedIn(this)) {
                // 未登录，需要先登录
                AlertDialog.Builder(this)
                    .setTitle("需要登录")
                    .setMessage("云端模式需要登录账号。是否前往登录？")
                    .setPositiveButton("去登录") { _, _ ->
                        val intent = Intent(this, LoginActivity::class.java)
                        startActivityForResult(intent, REQUEST_SETTINGS)
                    }
                    .setNegativeButton("取消", null)
                    .show()
            } else {
                // 已登录，直接切换
                AlertDialog.Builder(this)
                    .setTitle("切换到云端模式")
                    .setMessage("切换后将使用云端数据并同步到服务器。确定切换吗？")
                    .setPositiveButton("确定") { _, _ ->
                        PreferenceManager.setCloudMode(this, true)
                        updateCloudModeButton()
                        loadAllEvents()
                        Toast.makeText(this, "已切换到云端模式", Toast.LENGTH_SHORT).show()
                    }
                    .setNegativeButton("取消", null)
                    .show()
            }
        }
    }
    
    /**
     * 更新云端模式按钮的显示状态
     */
    private fun updateCloudModeButton() {
        val isCloudMode = PreferenceManager.isCloudMode(this)
        val isLoggedIn = PreferenceManager.isLoggedIn(this)
        
        if (isCloudMode && isLoggedIn) {
            btnCloudMode.text = "☁️\n云端"
            btnCloudMode.setBackgroundColor(ContextCompat.getColor(this, android.R.color.holo_blue_light))
        } else {
            btnCloudMode.text = "📱\n本地"
            btnCloudMode.setBackgroundColor(ContextCompat.getColor(this, android.R.color.darker_gray))
        }
    }
}
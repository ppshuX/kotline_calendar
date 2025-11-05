package com.ncu.kotlincalendar

import android.Manifest
import android.app.TimePickerDialog
import android.content.pm.PackageManager
import android.os.Build
import android.os.Bundle
import android.widget.ArrayAdapter
import android.widget.Button
import android.widget.CalendarView
import android.widget.Spinner
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import androidx.lifecycle.lifecycleScope
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import java.text.SimpleDateFormat
import java.util.*

class MainActivity : AppCompatActivity() {
    
    private lateinit var calendarView: CalendarView
    private lateinit var tvSelectedDate: TextView
    private lateinit var btnAddEvent: Button
    private lateinit var recyclerView: RecyclerView
    private lateinit var adapter: EventAdapter
    
    // 数据库
    private lateinit var database: AppDatabase
    private lateinit var eventDao: EventDao
    private lateinit var reminderManager: ReminderManager
    private val eventsList = mutableListOf<Event>()
    private var selectedDateMillis: Long = System.currentTimeMillis()
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        
        // 初始化数据库和提醒管理器
        database = AppDatabase.getDatabase(this)
        eventDao = database.eventDao()
        reminderManager = ReminderManager(this)
        
        // 初始化视图
        calendarView = findViewById(R.id.calendarView)
        tvSelectedDate = findViewById(R.id.tvSelectedDate)
        btnAddEvent = findViewById(R.id.btnAddEvent)
        recyclerView = findViewById(R.id.recyclerView)
        
        // 设置 RecyclerView
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
        
        // 默认显示今天的日期
        showDate(System.currentTimeMillis())
        
        // 初始化列表
        updateEventsList()
        
        // 加载数据库中的日程
        loadAllEvents()
        
        // 日期选择监听
        calendarView.setOnDateChangeListener { view, year, month, dayOfMonth ->
            val calendar = Calendar.getInstance()
            calendar.set(year, month, dayOfMonth)
            selectedDateMillis = calendar.timeInMillis
            showDate(selectedDateMillis)
        }
        
        // 点击"添加日程"按钮
        btnAddEvent.setOnClickListener {
            showAddEventDialog()
        }
        
        Toast.makeText(this, "📅 日历已加载，数据会自动保存", Toast.LENGTH_SHORT).show()
        
        // 请求通知权限（Android 13+）
        requestNotificationPermission()
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
    
    // 弹出添加日程的对话框
    private fun showAddEventDialog(eventToEdit: Event? = null) {
        // 加载自定义布局
        val dialogView = layoutInflater.inflate(R.layout.dialog_add_event, null)
        val etTitle = dialogView.findViewById<com.google.android.material.textfield.TextInputEditText>(R.id.etTitle)
        val etTime = dialogView.findViewById<com.google.android.material.textfield.TextInputEditText>(R.id.etTime)
        val etDesc = dialogView.findViewById<com.google.android.material.textfield.TextInputEditText>(R.id.etDescription)
        val spinnerReminder = dialogView.findViewById<Spinner>(R.id.spinnerReminder)
        
        // 设置提醒选项
        val reminderOptions = arrayOf("不提醒", "提前5分钟", "提前15分钟", "提前30分钟", "提前1小时", "提前1天")
        val reminderMinutes = arrayOf(0, 5, 15, 30, 60, 24 * 60)
        spinnerReminder?.adapter = ArrayAdapter(this, android.R.layout.simple_spinner_dropdown_item, reminderOptions)
        
        // 用于存储选择的日期时间
        val calendar = Calendar.getInstance()
        
        // 如果是编辑模式，填充现有数据
        if (eventToEdit != null) {
            etTitle?.setText(eventToEdit.title)
            etDesc?.setText(eventToEdit.description)
            calendar.timeInMillis = eventToEdit.dateTime
            
            // 设置提醒选项
            val reminderIndex = reminderMinutes.indexOf(eventToEdit.reminderMinutes)
            if (reminderIndex >= 0) {
                spinnerReminder?.setSelection(reminderIndex)
            }
        } else {
            // 新增模式，使用选中的日期
            calendar.timeInMillis = selectedDateMillis
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
                        updateEvent(eventToEdit.id, titleText, descText, calendar.timeInMillis, selectedReminderMinutes)
                    } else {
                        // 新增模式：添加新日程
                        addEvent(titleText, descText, calendar.timeInMillis, selectedReminderMinutes)
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
    
    // 从数据库加载所有日程
    private fun loadAllEvents() {
        lifecycleScope.launch(Dispatchers.IO) {
            try {
                val events = eventDao.getAllEvents()
                withContext(Dispatchers.Main) {
                    eventsList.clear()
                    eventsList.addAll(events)
                    updateEventsList()
                }
            } catch (e: Exception) {
                withContext(Dispatchers.Main) {
                    Toast.makeText(this@MainActivity, "加载失败: ${e.message}", Toast.LENGTH_SHORT).show()
                }
            }
        }
    }
    
    // 添加日程
    private fun addEvent(title: String, description: String = "", dateTime: Long = selectedDateMillis, reminderMinutes: Int = 0) {
        lifecycleScope.launch(Dispatchers.IO) {
            try {
                val event = Event(
                    title = title,
                    description = description,
                    dateTime = dateTime,
                    reminderMinutes = reminderMinutes
                )
                val eventId = eventDao.insert(event)
                
                // 设置提醒
                if (reminderMinutes > 0) {
                    val savedEvent = event.copy(id = eventId)
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
                val events = eventDao.getAllEvents()
                withContext(Dispatchers.Main) {
                    eventsList.clear()
                    eventsList.addAll(events)
                    updateEventsList()
                    Toast.makeText(this@MainActivity, "✅ 添加成功！", Toast.LENGTH_SHORT).show()
                }
            } catch (e: Exception) {
                withContext(Dispatchers.Main) {
                    Toast.makeText(this@MainActivity, "保存失败: ${e.message}", Toast.LENGTH_SHORT).show()
                }
            }
        }
    }
    
    // 更新日程
    private fun updateEvent(id: Long, title: String, description: String, dateTime: Long, reminderMinutes: Int = 0) {
        lifecycleScope.launch(Dispatchers.IO) {
            try {
                // 先取消旧提醒
                withContext(Dispatchers.Main) {
                    reminderManager.cancelReminder(id)
                }
                
                val event = Event(
                    id = id,
                    title = title,
                    description = description,
                    dateTime = dateTime,
                    reminderMinutes = reminderMinutes
                )
                eventDao.update(event)
                
                // 设置新提醒
                if (reminderMinutes > 0) {
                    withContext(Dispatchers.Main) {
                        reminderManager.setReminder(event)
                    }
                }
                
                // 重新加载数据
                val events = eventDao.getAllEvents()
                withContext(Dispatchers.Main) {
                    eventsList.clear()
                    eventsList.addAll(events)
                    updateEventsList()
                    Toast.makeText(this@MainActivity, "✅ 更新成功！", Toast.LENGTH_SHORT).show()
                }
            } catch (e: Exception) {
                withContext(Dispatchers.Main) {
                    Toast.makeText(this@MainActivity, "更新失败: ${e.message}", Toast.LENGTH_SHORT).show()
                }
            }
        }
    }
    
    // 更新日程列表显示
    private fun updateEventsList() {
        adapter.updateEvents(eventsList)
    }
    
    // 显示日程详情
    private fun showEventDetails(event: Event) {
        val dateFormat = SimpleDateFormat("yyyy年MM月dd日 EEEE HH:mm", Locale.CHINESE)
        val dateStr = dateFormat.format(Date(event.dateTime))
        
        val message = buildString {
            append("📅 日期：$dateStr\n\n")
            append("📝 标题：${event.title}\n\n")
            if (event.description.isNotEmpty()) {
                append("💬 描述：${event.description}")
            }
        }
        
        AlertDialog.Builder(this)
            .setTitle("📋 日程详情")
            .setMessage(message)
            .setPositiveButton("编辑") { _, _ ->
                // 编辑日程
                showAddEventDialog(event)
            }
            .setNegativeButton("删除") { _, _ ->
                deleteEvent(event)
            }
            .setNeutralButton("关闭", null)
            .show()
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
    
    // 删除日程
    private fun deleteEvent(event: Event) {
        lifecycleScope.launch(Dispatchers.IO) {
            try {
                // 取消提醒
                withContext(Dispatchers.Main) {
                    reminderManager.cancelReminder(event.id)
                }
                
                // 删除日程
                eventDao.delete(event)
                
                // 重新加载
                val events = eventDao.getAllEvents()
                withContext(Dispatchers.Main) {
                    eventsList.clear()
                    eventsList.addAll(events)
                    updateEventsList()
                    Toast.makeText(this@MainActivity, "🗑️ 删除成功！", Toast.LENGTH_SHORT).show()
                }
            } catch (e: Exception) {
                withContext(Dispatchers.Main) {
                    Toast.makeText(this@MainActivity, "删除失败: ${e.message}", Toast.LENGTH_SHORT).show()
                }
            }
        }
    }
}
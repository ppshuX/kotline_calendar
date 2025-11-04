package com.ncu.kotlincalendar

import android.os.Bundle
import android.widget.CalendarView
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import java.text.SimpleDateFormat
import java.util.*

class MainActivity : AppCompatActivity() {
    
    private lateinit var calendarView: CalendarView
    private lateinit var tvSelectedDate: TextView
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        
        // 初始化视图
        calendarView = findViewById(R.id.calendarView)
        tvSelectedDate = findViewById(R.id.tvSelectedDate)
        
        // 默认显示今天的日期
        showDate(System.currentTimeMillis())
        
        // 设置日期选择监听
        calendarView.setOnDateChangeListener { view, year, month, dayOfMonth ->
            val calendar = Calendar.getInstance()
            calendar.set(year, month, dayOfMonth)
            showDate(calendar.timeInMillis)
        }
        
        Toast.makeText(this, "日历加载成功！点击日期试试", Toast.LENGTH_SHORT).show()
    }
    
    private fun showDate(timeInMillis: Long) {
        val dateFormat = SimpleDateFormat("yyyy年MM月dd日 EEEE", Locale.CHINESE)
        val dateStr = dateFormat.format(Date(timeInMillis))
        tvSelectedDate.text = "选中日期：$dateStr"
    }
}
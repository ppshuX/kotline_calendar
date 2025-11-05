package com.ncu.kotlincalendar

import android.app.AlarmManager
import android.app.PendingIntent
import android.content.Context
import android.content.Intent
import android.os.Build
import android.util.Log
import android.widget.Toast

/**
 * 提醒管理器
 */
class ReminderManager(private val context: Context) {
    
    private val alarmManager = context.getSystemService(Context.ALARM_SERVICE) as AlarmManager
    
    /**
     * 设置提醒
     * @param event 日程
     */
    fun setReminder(event: Event) {
        if (event.reminderMinutes <= 0) {
            Log.d(TAG, "不需要提醒: ${event.title}")
            return
        }
        
        // 计算提醒时间（日程时间 - 提前分钟数）
        val reminderTime = event.dateTime - (event.reminderMinutes * 60 * 1000)
        val currentTime = System.currentTimeMillis()
        
        Log.d(TAG, "设置提醒: ${event.title}")
        Log.d(TAG, "日程时间: ${event.dateTime}")
        Log.d(TAG, "提醒时间: $reminderTime")
        Log.d(TAG, "当前时间: $currentTime")
        
        // 如果提醒时间已经过了，立即提醒
        if (reminderTime < currentTime) {
            Log.d(TAG, "提醒时间已过，立即提醒")
            Toast.makeText(context, "⚠️ 提醒时间已过，无法设置提醒", Toast.LENGTH_SHORT).show()
            return
        }
        
        val intent = Intent(context, AlarmReceiver::class.java).apply {
            putExtra("eventId", event.id)
            putExtra("eventTitle", event.title)
            putExtra("eventDesc", event.description)
        }
        
        val pendingIntent = PendingIntent.getBroadcast(
            context,
            event.id.toInt(),
            intent,
            PendingIntent.FLAG_IMMUTABLE or PendingIntent.FLAG_UPDATE_CURRENT
        )
        
        // 设置精确闹钟
        try {
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
                if (alarmManager.canScheduleExactAlarms()) {
                    alarmManager.setExactAndAllowWhileIdle(
                        AlarmManager.RTC_WAKEUP,
                        reminderTime,
                        pendingIntent
                    )
                    Log.d(TAG, "✅ 提醒设置成功（API 31+）")
                } else {
                    Log.e(TAG, "❌ 无法设置精确闹钟权限")
                    Toast.makeText(context, "需要精确闹钟权限", Toast.LENGTH_SHORT).show()
                }
            } else {
                alarmManager.setExactAndAllowWhileIdle(
                    AlarmManager.RTC_WAKEUP,
                    reminderTime,
                    pendingIntent
                )
                Log.d(TAG, "✅ 提醒设置成功（API < 31）")
            }
        } catch (e: Exception) {
            Log.e(TAG, "❌ 设置提醒失败: ${e.message}")
            Toast.makeText(context, "设置提醒失败: ${e.message}", Toast.LENGTH_SHORT).show()
        }
    }
    
    companion object {
        private const val TAG = "ReminderManager"
    }
    
    /**
     * 取消提醒
     * @param eventId 日程 ID
     */
    fun cancelReminder(eventId: Long) {
        val intent = Intent(context, AlarmReceiver::class.java)
        val pendingIntent = PendingIntent.getBroadcast(
            context,
            eventId.toInt(),
            intent,
            PendingIntent.FLAG_IMMUTABLE or PendingIntent.FLAG_NO_CREATE
        )
        
        pendingIntent?.let {
            alarmManager.cancel(it)
            it.cancel()
        }
    }
}


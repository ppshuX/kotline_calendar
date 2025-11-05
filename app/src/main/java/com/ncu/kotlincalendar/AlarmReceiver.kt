package com.ncu.kotlincalendar

import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.os.Build
import androidx.core.app.NotificationCompat

/**
 * 提醒接收器（到时间了会收到广播）
 */
class AlarmReceiver : BroadcastReceiver() {
    
    override fun onReceive(context: Context, intent: Intent) {
        val eventId = intent.getLongExtra("eventId", -1)
        val eventTitle = intent.getStringExtra("eventTitle") ?: "日程提醒"
        val eventDesc = intent.getStringExtra("eventDesc") ?: ""
        
        // 显示通知
        showNotification(context, eventId, eventTitle, eventDesc)
    }
    
    private fun showNotification(context: Context, eventId: Long, title: String, description: String) {
        val notificationManager = context.getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
        
        // 创建通知渠道（Android 8.0+）
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                CHANNEL_ID,
                "日程提醒",
                NotificationManager.IMPORTANCE_HIGH
            ).apply {
                this.description = "日历日程提醒通知"
                enableLights(true)
                enableVibration(true)
            }
            notificationManager.createNotificationChannel(channel)
        }
        
        // 点击通知打开应用
        val intent = Intent(context, MainActivity::class.java)
        val pendingIntent = PendingIntent.getActivity(
            context,
            eventId.toInt(),
            intent,
            PendingIntent.FLAG_IMMUTABLE or PendingIntent.FLAG_UPDATE_CURRENT
        )
        
        // 创建通知
        val notification = NotificationCompat.Builder(context, CHANNEL_ID)
            .setSmallIcon(android.R.drawable.ic_dialog_info)
            .setContentTitle("📅 $title")
            .setContentText(description.ifEmpty { "日程即将开始" })
            .setPriority(NotificationCompat.PRIORITY_HIGH)
            .setAutoCancel(true)
            .setContentIntent(pendingIntent)
            .build()
        
        notificationManager.notify(eventId.toInt(), notification)
    }
    
    companion object {
        private const val CHANNEL_ID = "calendar_reminders"
    }
}


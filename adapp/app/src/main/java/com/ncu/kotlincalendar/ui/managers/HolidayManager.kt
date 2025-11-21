package com.ncu.kotlincalendar.ui.managers

import android.content.Context
import android.content.Intent
import android.view.View
import android.widget.LinearLayout
import android.widget.TextView
import androidx.lifecycle.LifecycleCoroutineScope
import com.google.android.material.card.MaterialCardView
import com.ncu.kotlincalendar.FestivalDetailActivity
import com.ncu.kotlincalendar.api.client.RetrofitClient
import com.ncu.kotlincalendar.data.managers.SubscriptionManager
import com.ncu.kotlincalendar.data.models.Event
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import java.text.SimpleDateFormat
import java.time.Instant
import java.time.LocalDate
import java.time.ZoneId
import java.util.*

/**
 * 节日信息管理器
 * 
 * 职责：
 * - 加载节日信息（API + 订阅）
 * - 动态创建节日卡片
 * - 处理节日卡片点击事件
 * 
 * 使用方式：
 * ```kotlin
 * val holidayManager = HolidayManager(festivalCardsContainer, tvHolidayHint, context, subscriptionManager)
 * holidayManager.loadHolidayInfo(dateMillis, lifecycleScope)
 * ```
 */
class HolidayManager(
    private val festivalCardsContainer: LinearLayout,
    private val tvHolidayHint: TextView,
    private val context: Context,
    private val subscriptionManager: SubscriptionManager
) {
    
    /**
     * 加载节日信息
     */
    fun loadHolidayInfo(
        date: Long,
        lifecycleScope: LifecycleCoroutineScope
    ) {
        lifecycleScope.launch(Dispatchers.IO) {
            try {
                val dateFormat = SimpleDateFormat("yyyy-MM-dd", Locale.getDefault())
                val dateStr = dateFormat.format(Date(date))
                
                // 1. 调用后端 API 获取节日信息
                val response = RetrofitClient.api.checkHoliday(dateStr)
                
                // 2. 从SubscriptionManager获取该日期的有效订阅节日事件
                // 使用 getVisibleEvents 确保只获取有效且启用的订阅事件
                val allVisibleEvents = subscriptionManager.getVisibleEvents(date)
                val selectedDate = Instant.ofEpochMilli(date)
                    .atZone(ZoneId.systemDefault())
                    .toLocalDate()
                
                // 过滤出该日期的订阅节日事件（subscriptionId != null）
                val subscribedEvents = allVisibleEvents.filter { event ->
                    val eventDate = Instant.ofEpochMilli(event.dateTime)
                        .atZone(ZoneId.systemDefault())
                        .toLocalDate()
                    // 只获取订阅的事件（subscriptionId != null），且订阅必须是有效且启用的
                    eventDate == selectedDate && event.subscriptionId != null
                }
                
                withContext(Dispatchers.Main) {
                    // 清空之前的卡片
                    festivalCardsContainer.removeAllViews()
                    
                    // 数据结构：存储节日信息
                    data class FestivalItem(
                        val name: String,
                        val emoji: String,
                        val type: String // "api" 或 "subscribed"
                    )
                    
                    // 合并API节日和订阅节日，并去重
                    val allFestivals = mutableListOf<FestivalItem>()
                    
                    // 添加农历信息卡片（总是显示）
                    addFestivalCard(
                        "🏮 农历",
                        response.lunar ?: "加载中...",
                        "#FFE0B2", // 橙色系 - 农历信息
                        false, // 农历不可点击
                        "", "", ""
                    )
                    
                    // 添加法定节假日卡片
                    if (response.isHoliday) {
                        addFestivalCard(
                            "🎉 法定节假日",
                            "今日为国家法定节假日",
                            "#FFF9C4", // 黄色系 - 法定节假日
                            false, // 法定节假日不可点击
                            "", "", ""
                        )
                    }
                    
                    // 只显示订阅的节日，不显示API返回的节日（除非用户订阅了相关日历）
                    // 如果用户想要显示API返回的节日，需要订阅相应的日历
                    subscribedEvents.forEach { event ->
                        // 提取emoji和名称
                        val emoji = event.title.takeWhile { !it.isLetter() }.trim()
                        val name = event.title.dropWhile { !it.isLetter() }.trim()
                        
                        // 添加订阅的节日
                        allFestivals.add(
                            FestivalItem(name, emoji, "subscribed")
                        )
                    }
                    
                    // 注意：API返回的节日不再自动显示，只有订阅的节日才会显示
                    // 这样可以确保用户只看到他们订阅的日历内容
                    
                    // 为每个节日创建独立的小卡片（使用不同颜色区分）
                    if (allFestivals.isNotEmpty()) {
                        allFestivals.forEachIndexed { index, festival ->
                            // 使用渐变色：从粉红到紫色到蓝色
                            val cardColor = when (index % 4) {
                                0 -> "#F8BBD0" // 粉红色系
                                1 -> "#E1BEE7" // 紫色系
                                2 -> "#BBDEFB" // 蓝色系
                                else -> "#C5E1A5" // 绿色系
                            }
                            
                            addFestivalCard(
                                "${festival.emoji} ${festival.name}",
                                "点击查看详情",
                                cardColor,
                                true, // 节日可点击
                                festival.name,
                                festival.emoji,
                                dateStr
                            )
                        }
                        tvHolidayHint.visibility = View.VISIBLE
                    } else {
                        // 没有节日，显示提示卡片（不重复显示农历）
                        if (!response.isHoliday) {
                            addFestivalCard(
                                "📅 今日无特殊节日",
                                "享受平凡的一天 ☀️",
                                "#ECEFF1", // 灰蓝色系
                                false,
                                "", "", ""
                            )
                        }
                        tvHolidayHint.visibility = View.GONE
                    }
                }
            } catch (e: Exception) {
                withContext(Dispatchers.Main) {
                    festivalCardsContainer.removeAllViews()
                    addFestivalCard(
                        "❌ 加载失败",
                        "请检查网络连接或稍后重试",
                        "#FFCDD2", // 红色系 - 错误提示
                        false,
                        "", "", ""
                    )
                }
            }
        }
    }
    
    /**
     * 动态创建节日卡片
     */
    private fun addFestivalCard(
        title: String,
        subtitle: String,
        backgroundColor: String,
        clickable: Boolean,
        festivalName: String,
        festivalEmoji: String,
        dateStr: String
    ) {
        // 创建卡片布局
        val cardView = MaterialCardView(context).apply {
            layoutParams = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                LinearLayout.LayoutParams.WRAP_CONTENT
            ).apply {
                bottomMargin = (8 * resources.displayMetrics.density).toInt() // 8dp间距
            }
            setCardBackgroundColor(android.graphics.Color.parseColor(backgroundColor))
            radius = (12 * resources.displayMetrics.density)
            cardElevation = (2 * resources.displayMetrics.density)
            setContentPadding(
                (16 * resources.displayMetrics.density).toInt(),
                (12 * resources.displayMetrics.density).toInt(),
                (16 * resources.displayMetrics.density).toInt(),
                (12 * resources.displayMetrics.density).toInt()
            )
        }
        
        // 创建内容布局（垂直）
        val contentLayout = LinearLayout(context).apply {
            orientation = LinearLayout.VERTICAL
            layoutParams = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                LinearLayout.LayoutParams.WRAP_CONTENT
            )
        }
        
        // 标题
        val titleView = TextView(context).apply {
            text = title
            textSize = 18f
            setTypeface(null, android.graphics.Typeface.BOLD)
            setTextColor(android.graphics.Color.parseColor("#4A148C"))
        }
        
        // 副标题
        val subtitleView = TextView(context).apply {
            text = subtitle
            textSize = 14f
            setTextColor(android.graphics.Color.parseColor("#6A1B9A"))
            setPadding(0, (4 * resources.displayMetrics.density).toInt(), 0, 0)
        }
        
        contentLayout.addView(titleView)
        contentLayout.addView(subtitleView)
        cardView.addView(contentLayout)
        
        // 设置点击事件（如果可点击）
        if (clickable && festivalName.isNotEmpty()) {
            cardView.setOnClickListener {
                val intent = Intent(context, FestivalDetailActivity::class.java).apply {
                    putExtra("festival_name", festivalName)
                    putExtra("festival_emoji", festivalEmoji)
                    putExtra("date", dateStr)
                }
                context.startActivity(intent)
            }
            
            // 添加点击效果
            cardView.isClickable = true
            cardView.isFocusable = true
            val outValue = android.util.TypedValue()
            context.theme.resolveAttribute(
                android.R.attr.selectableItemBackground,
                outValue,
                true
            )
            cardView.foreground = context.getDrawable(outValue.resourceId)
        }
        
        festivalCardsContainer.addView(cardView)
    }
    
}


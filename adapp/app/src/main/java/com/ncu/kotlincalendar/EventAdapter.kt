package com.ncu.kotlincalendar

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView
import java.text.SimpleDateFormat
import java.util.*

/**
 * 日程列表适配器（类似 Vue 的列表渲染）
 */
class EventAdapter(
    private var events: List<Event>,
    private val onItemClick: (Event) -> Unit,
    private val onItemLongClick: (Event) -> Unit
) : RecyclerView.Adapter<EventAdapter.EventViewHolder>() {

    class EventViewHolder(view: View) : RecyclerView.ViewHolder(view) {
        val tvTitle: TextView = view.findViewById(R.id.tvTitle)
        val tvDateTime: TextView = view.findViewById(R.id.tvDateTime)
        val tvDescription: TextView = view.findViewById(R.id.tvDescription)
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): EventViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_event, parent, false)
        return EventViewHolder(view)
    }

    override fun onBindViewHolder(holder: EventViewHolder, position: Int) {
        val event = events[position]
        
        // 设置标题
        holder.tvTitle.text = event.title
        
        // 格式化日期时间
        val dateFormat = SimpleDateFormat("yyyy-MM-dd EEEE", Locale.CHINESE)
        holder.tvDateTime.text = dateFormat.format(Date(event.dateTime))
        
        // 设置描述（如果有）
        if (event.description.isNotEmpty()) {
            holder.tvDescription.text = event.description
            holder.tvDescription.visibility = View.VISIBLE
        } else {
            holder.tvDescription.visibility = View.GONE
        }
        
        // 点击事件
        holder.itemView.setOnClickListener {
            onItemClick(event)
        }
        
        // 长按事件
        holder.itemView.setOnLongClickListener {
            onItemLongClick(event)
            true
        }
    }

    override fun getItemCount() = events.size

    // 更新数据
    fun updateEvents(newEvents: List<Event>) {
        events = newEvents
        notifyDataSetChanged()
    }
}


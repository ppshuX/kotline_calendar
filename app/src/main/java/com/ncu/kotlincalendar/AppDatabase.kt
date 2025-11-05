package com.ncu.kotlincalendar

import android.content.Context
import androidx.room.Database
import androidx.room.Room
import androidx.room.RoomDatabase

/**
 * 应用数据库（单例模式）
 */
@Database(entities = [Event::class], version = 2, exportSchema = false)
abstract class AppDatabase : RoomDatabase() {
    
    abstract fun eventDao(): EventDao
    
    companion object {
        @Volatile
        private var INSTANCE: AppDatabase? = null
        
        fun getDatabase(context: Context): AppDatabase {
            return INSTANCE ?: synchronized(this) {
                val instance = Room.databaseBuilder(
                    context.applicationContext,
                    AppDatabase::class.java,
                    "calendar_database"
                )
                    .fallbackToDestructiveMigration()  // 简单粗暴：删除旧数据重建
                    .build()
                INSTANCE = instance
                instance
            }
        }
    }
}




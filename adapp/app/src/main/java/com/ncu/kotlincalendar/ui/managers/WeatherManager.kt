package com.ncu.kotlincalendar.ui.managers

import android.content.Context
import android.content.SharedPreferences
import android.util.Log
import android.view.LayoutInflater
import android.view.View
import android.widget.TextView
import androidx.appcompat.app.AlertDialog
import androidx.lifecycle.LifecycleCoroutineScope
import com.google.android.material.card.MaterialCardView
import com.google.android.material.chip.Chip
import com.google.android.material.chip.ChipGroup
import com.google.android.material.textfield.TextInputEditText
import com.ncu.kotlincalendar.R
import com.ncu.kotlincalendar.api.client.RetrofitClient
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

/**
 * 天气信息管理器
 * 
 * 职责：
 * - 加载实时天气数据
 * - 更新天气UI显示
 * - 处理天气加载失败
 * 
 * 使用方式：
 * ```kotlin
 * val weatherManager = WeatherManager(weatherCard, tvWeatherLocation, ...)
 * weatherManager.loadWeather(lifecycleScope)
 * ```
 */
class WeatherManager(
    private val context: Context,
    private val weatherCard: MaterialCardView,
    private val tvWeatherLocation: TextView,
    private val tvTemperature: TextView,
    private val tvWeatherDesc: TextView,
    private val tvFeelsLike: TextView,
    private val tvHumidity: TextView,
    private val tvWind: TextView
) {
    
    private val sharedPreferences: SharedPreferences = 
        context.getSharedPreferences("weather_prefs", Context.MODE_PRIVATE)
    
    // 当前天气数据（供其他Manager使用）
    var currentWeather: String? = null
        private set
    var currentTemperature: String? = null
        private set
    
    companion object {
        private const val TAG = "WeatherManager"
        private const val PREF_CITY = "selected_city"
        private const val DEFAULT_CITY = "北京"
    }
    
    /**
     * 加载天气信息
     * @param lifecycleScope Activity的生命周期协程作用域
     * @param location 城市名称（可选，默认使用保存的城市）
     */
    fun loadWeather(
        lifecycleScope: LifecycleCoroutineScope,
        location: String? = null
    ) {
        val city = location ?: getSavedCity()
        
        // 添加点击事件：点击天气卡片可选择城市
        weatherCard.setOnClickListener {
            showCityPickerDialog(lifecycleScope)
        }
        lifecycleScope.launch(Dispatchers.IO) {
            try {
                // 调用后端API获取天气
                val response = RetrofitClient.api.getWeather(city)
                
                withContext(Dispatchers.Main) {
                    if (response.success && response.data != null) {
                        val weather = response.data
                        
                        // 保存当前天气数据
                        currentWeather = weather.weather
                        currentTemperature = weather.temperature
                        
                        // 更新UI并显示天气卡片
                        tvWeatherLocation.text = weather.location
                        tvTemperature.text = "${weather.temperature}°"
                        tvWeatherDesc.text = weather.weather
                        tvFeelsLike.text = "体感 ${weather.feelsLike}°"
                        tvHumidity.text = "湿度 ${weather.humidity}%"
                        tvWind.text = "${weather.windDir} ${weather.windScale}级"
                        
                        // ✅ 确保天气卡片可见
                        weatherCard.visibility = View.VISIBLE
                        
                        Log.d(TAG, "天气加载成功: ${weather.location} ${weather.temperature}° ${weather.weather}")
                    } else {
                        // 加载失败，也显示卡片但显示错误信息
                        tvWeatherLocation.text = city
                        tvTemperature.text = "--°"
                        tvWeatherDesc.text = "加载失败"
                        tvFeelsLike.text = "体感 --°"
                        tvHumidity.text = "湿度 --%"
                        tvWind.text = "-- --级"
                        
                        // ✅ 显示卡片以便用户知道天气功能存在
                        weatherCard.visibility = View.VISIBLE
                        
                        Log.e(TAG, "天气加载失败: ${response.error}")
                    }
                }
            } catch (e: Exception) {
                Log.e(TAG, "获取天气失败", e)
                withContext(Dispatchers.Main) {
                    // 即使失败也显示卡片，方便用户知道功能存在
                    tvWeatherLocation.text = city
                    tvTemperature.text = "--°"
                    tvWeatherDesc.text = "网络错误"
                    tvFeelsLike.text = "点击重试"
                    tvHumidity.text = ""
                    tvWind.text = ""
                    weatherCard.visibility = View.VISIBLE
                }
            }
        }
    }
    
    /**
     * 显示城市选择对话框
     */
    private fun showCityPickerDialog(lifecycleScope: LifecycleCoroutineScope) {
        val dialogView = LayoutInflater.from(context).inflate(R.layout.dialog_city_picker, null)
        val etCityName = dialogView.findViewById<TextInputEditText>(R.id.etCityName)
        val chipGroup = dialogView.findViewById<ChipGroup>(R.id.chipGroupCities)
        
        // 设置当前选中的城市
        val currentCity = getSavedCity()
        when (currentCity) {
            "北京" -> dialogView.findViewById<Chip>(R.id.chipBeijing).isChecked = true
            "上海" -> dialogView.findViewById<Chip>(R.id.chipShanghai).isChecked = true
            "广州" -> dialogView.findViewById<Chip>(R.id.chipGuangzhou).isChecked = true
            "深圳" -> dialogView.findViewById<Chip>(R.id.chipShenzhen).isChecked = true
            "杭州" -> dialogView.findViewById<Chip>(R.id.chipHangzhou).isChecked = true
            "南昌" -> dialogView.findViewById<Chip>(R.id.chipNanchang).isChecked = true
            else -> etCityName.setText(currentCity)
        }
        
        val dialog = AlertDialog.Builder(context)
            .setView(dialogView)
            .create()
        
        // 确定按钮
        dialogView.findViewById<View>(R.id.btnConfirm).setOnClickListener {
            val selectedCity = when (chipGroup.checkedChipId) {
                R.id.chipBeijing -> "北京"
                R.id.chipShanghai -> "上海"
                R.id.chipGuangzhou -> "广州"
                R.id.chipShenzhen -> "深圳"
                R.id.chipHangzhou -> "杭州"
                R.id.chipNanchang -> "南昌"
                else -> etCityName.text?.toString()?.trim() ?: DEFAULT_CITY
            }
            
            if (selectedCity.isNotEmpty()) {
                saveCity(selectedCity)
                loadWeather(lifecycleScope, selectedCity)
                dialog.dismiss()
            }
        }
        
        // 取消按钮
        dialogView.findViewById<View>(R.id.btnCancel).setOnClickListener {
            dialog.dismiss()
        }
        
        dialog.show()
    }
    
    /**
     * 保存选择的城市
     */
    private fun saveCity(city: String) {
        sharedPreferences.edit().putString(PREF_CITY, city).apply()
        Log.d(TAG, "城市已保存: $city")
    }
    
    /**
     * 获取保存的城市
     */
    private fun getSavedCity(): String {
        return sharedPreferences.getString(PREF_CITY, DEFAULT_CITY) ?: DEFAULT_CITY
    }
}


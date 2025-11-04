@echo off
chcp 65001 >nul
echo 正在重命名文件为英文...

ren "Day01_搭建基础界面.md" "Day01_Calendar_UI.md"
ren "Day02_添加和显示日程.md" "Day02_Add_Events.md"
ren "Day03_数据库保存.md" "Day03_Database.md"
ren "Day04_列表显示优化.md" "Day04_Event_List.md"
ren "Day05_编辑和删除.md" "Day05_Edit_Delete.md"
ren "Day06_时间选择器.md" "Day06_Time_Picker.md"
ren "Day07_多视图切换.md" "Day07_Multiple_Views.md"
ren "Day08_提醒功能.md" "Day08_Reminder.md"
ren "Day09_扩展功能和优化.md" "Day09_Optimization.md"
ren "Day10_文档与演示.md" "Day10_Documentation.md"

echo 重命名完成！
pause


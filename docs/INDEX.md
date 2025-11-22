# 📚 Ralendar 项目文档索引

> **项目**: Ralendar (原 KotlinCalendar)  
> **更新时间**: 2025-11-08  
> **文档版本**: v3.0 ✨（已重组）

---

## 📖 文档结构（已优化）

```
docs/
├── README.md                    # 项目说明（入口文档）
├── INDEX.md                     # 📍 本文档（导航索引）
│
├── 📘 guides/                   # 操作指南（How-to）
│   ├── ACWING_LOGIN_GUIDE.md   # AcWing OAuth2 集成指南
│   ├── ACWING_PLATFORM_CONFIG.md # AcWing 平台配置 ⭐
│   ├── WEB_AUTH_GUIDE.md       # Web 端认证实现指南
│   ├── DEPLOYMENT_GUIDE.md     # 部署与运维指南
│   ├── MIGRATION_GUIDE.md      # 数据库迁移指南
│   ├── BAIDU_MAP_SETUP.md      # 百度地图配置 ⭐
│   └── EMAIL_REMINDER_GUIDE.md # 邮件提醒配置 ⭐
│
├── 🏗️ architecture/             # 架构设计（Design）⭐
│   ├── ARCHITECTURE.md         # 项目整体架构
│   ├── Component_Structure.md  # 组件结构设计
│   └── UNIFIED_REMINDER_ARCHITECTURE.md # 统一提醒架构
│
├── 🔗 integration/              # 集成指南（Integration）⭐
│   ├── ROAMIO_INTEGRATION_GUIDE.md    # Roamio 集成指南（详细）
│   ├── ROAMIO_INTEGRATION_STATUS.md   # 集成状态
│   ├── ROAMIO_QUICKSTART.md           # 快速开始（5 分钟）
│   └── FUSION_PROGRESS.md             # 融合进度
│
├── 📝 summaries/                # 重构总结（Summary）⭐
│   ├── CODE_CLEANUP_SUMMARY.md    # 代码清理总结
│   ├── Component_Refactoring.md   # 组件重构
│   ├── CSS_REFACTORING_SUMMARY.md # CSS 重构
│   ├── URL_REFACTORING_SUMMARY.md # URL 重构
│   └── UX_OPTIMIZATION_SUMMARY.md # UX 优化总结
│
├── 🌐 api/                      # API 文档
│   └── ROAMIO_ECOSYSTEM_API_DOCUMENTATION.md  # Roamio 生态 API 总文档
│
├── 📦 archive/                  # 归档文档（历史记录）
│   ├── daily_logs/             # 历史开发日志（已归档）
│   ├── plans/                   # 已完成计划（已归档）
│   ├── integration/             # 历史集成文档（已归档）
│   └── collaboration/          # 历史协作文档（已归档）
│   ├── Day14_COMPLETE_SUMMARY.md  # Day 14: 完整总结
│   ├── Day15_CODE_REFACTORING.md  # Day 15: 代码重构
│   ├── Day15_SUMMARY.md        # Day 15: 总结
│   ├── Day16_MAJOR_FEATURES_AND_INTEGRATION.md  # Day 16: 功能与集成
│   └── Day16_FINAL_SUMMARY.md  # Day 16: 最终总结 ⭐
│
└── 🚀 plans/                    # 未来计划
    ├── Day15_PLAN.md           # Day 15 计划
    ├── PRODUCT_ROADMAP.md      # 产品路线图
    ├── FUTURE_PLAN.md          # 未来功能计划
    ├── AI_ASSISTANT_PLAN.md    # AI 助手实现计划
    ├── CALENDAR_SHARING_PLAN.md  # 日历分享功能计划
    ├── MAP_INTEGRATION_PLAN.md  # 地图集成计划
    └── RALENDAR_ROAMIO_FUSION_PLAN.md # Roamio 融合计划
```

---

## 🚀 快速导航

### 🔰 新手入门
1. [项目说明](./README.md) - 了解项目概况
2. [系统架构](./architecture/ARCHITECTURE.md) - 理解整体设计
3. [部署指南](./guides/DEPLOYMENT_GUIDE.md) - 快速部署上线

### 👨‍💻 开发者指南

#### 📘 操作指南
1. [AcWing 平台配置](./guides/ACWING_PLATFORM_CONFIG.md) ⭐ - 平台配置步骤
2. [AcWing 登录集成](./guides/ACWING_LOGIN_GUIDE.md) - OAuth2 实现
3. [Web 认证指南](./guides/WEB_AUTH_GUIDE.md) - JWT 认证
4. [百度地图配置](./guides/BAIDU_MAP_SETUP.md) - 地图功能设置
5. [邮件提醒配置](./guides/EMAIL_REMINDER_GUIDE.md) - Celery 异步任务
6. [数据库迁移](./guides/MIGRATION_GUIDE.md) - 数据库变更管理

#### 🏗️ 架构设计
1. [整体架构](./architecture/ARCHITECTURE.md) - 系统架构设计
2. [组件结构](./architecture/Component_Structure.md) - 前端组件设计
3. [提醒架构](./architecture/UNIFIED_REMINDER_ARCHITECTURE.md) - 统一提醒系统

#### 🔗 Roamio 集成
1. [🎁 集成交付包](./integration/ROAMIO_DELIVERY_PACKAGE.md) ⭐⭐⭐ - 完整交付资料（推荐）
2. [快速开始](./integration/ROAMIO_QUICKSTART.md) ⭐ - 5 分钟快速集成
3. [集成指南](./integration/ROAMIO_INTEGRATION_GUIDE.md) - 详细集成步骤
4. [测试脚本](./integration/test_ralendar_api.py) - API 自动化测试
5. [集成状态](./integration/ROAMIO_INTEGRATION_STATUS.md) - 当前进度
6. [融合进度](./integration/FUSION_PROGRESS.md) - 功能融合情况

#### 📝 重构总结
1. [代码清理](./summaries/CODE_CLEANUP_SUMMARY.md) - 代码优化总结
2. [组件重构](./summaries/Component_Refactoring.md) - 组件模块化
3. [CSS 重构](./summaries/CSS_REFACTORING_SUMMARY.md) - 样式优化
4. [URL 重构](./summaries/URL_REFACTORING_SUMMARY.md) - 路由重构
5. [UX 优化](./summaries/UX_OPTIMIZATION_SUMMARY.md) - 用户体验提升

### 🌐 API 参考
- [Roamio 生态 API](./api/ROAMIO_ECOSYSTEM_API_DOCUMENTATION.md) - 完整 API 文档

### 📅 开发日志
- [Day 16 最终总结](./daily_logs/Day16_FINAL_SUMMARY.md) ⭐ 最新
- [Day 15 代码重构](./daily_logs/Day15_CODE_REFACTORING.md)
- [Day 14 完整总结](./daily_logs/Day14_COMPLETE_SUMMARY.md)
- [更多日志...](./daily_logs/)

### 🗓️ 未来计划
- [Roamio 融合计划](./plans/RALENDAR_ROAMIO_FUSION_PLAN.md) ⭐ 重点
- [产品路线图](./plans/PRODUCT_ROADMAP.md) - 长期规划
- [AI 助手计划](./plans/AI_ASSISTANT_PLAN.md) - 智能功能
- [地图集成计划](./plans/MAP_INTEGRATION_PLAN.md) - 地理位置
- [更多计划...](./plans/)

---

## 📊 项目概况（截至 Day 14）

### 完成功能
- ✅ Web 端（Vue 3 + Element Plus）
- ✅ AcApp 端（Vue 3）
- ✅ Android 端（Kotlin，本地版）
- ✅ 用户认证（普通/AcWing/QQ 三种方式）
- ✅ 日历 CRUD（增删改查）
- ✅ 农历显示
- ✅ 事件提醒
- ✅ 用户个人中心

### 技术栈
**后端**：Django 4.2 + DRF + JWT + SQLite  
**前端**：Vue 3 + Vite + Element Plus + FullCalendar  
**移动端**：Kotlin + Android SDK  
**部署**：Nginx + uWSGI + Linux

### 项目指标
- **代码行数**: ~8,000 行
- **API 端点**: 20+ 个
- **页面/组件**: 15+ 个
- **完成度**: 约 70%

---

## 🌟 Roamio 生态计划

### 品牌矩阵
- **Roamio** - 旅行规划与内容分享平台
- **Ralendar** - 智能日历与时间管理（本项目）
- **Rote** - 笔记与知识管理（未来）
- **Rapture** - 照片与回忆记录（未来）

### 融合目标
1. 共享用户认证体系
2. 数据互通和联动
3. 统一的 UI/UX 风格
4. 跨产品功能协同

**详见**: [Roamio 生态 API 文档](./api/ROAMIO_ECOSYSTEM_API_DOCUMENTATION.md)

---

## 📝 文档维护规范

### 命名规范
- 开发日志：`DayXX_TOPIC.md`
- 技术指南：`TOPIC_GUIDE.md`
- 功能计划：`FEATURE_PLAN.md`
- API 文档：`API_DOCUMENTATION.md`

### 更新频率
- **开发日志**: 每天结束时更新
- **API 文档**: 代码变更时同步更新
- **技术指南**: 功能完成后编写
- **计划文档**: 需求变更时更新

### 文档质量标准
- ✅ 标题清晰，层次分明
- ✅ 代码示例完整可运行
- ✅ 包含图表和流程图
- ✅ 注明更新日期和版本

---

## 🔗 外部链接

- **GitHub 仓库**: https://github.com/ppshuX/kotline_calendar
- **线上地址**: https://app7626.acapp.acwing.com.cn
- **AcWing 平台**: https://www.acwing.com
- **QQ 互联**: https://connect.qq.com

---

## 🆘 寻求帮助

### 文档相关问题
- 在 GitHub Issues 中提问
- 或查看 [常见问题](./guides/FAQ.md)（待创建）

### 技术问题
- 参考对应的技术指南
- 查看开发日志中的解决方案
- 使用项目搜索（Ctrl+F）

---

## ✨ v3.0 更新说明

### 2025-11-08 文档重组
- ✅ 创建 `architecture/`、`integration/`、`summaries/` 目录
- ✅ 按功能分类所有文档
- ✅ 移动 `AcWing_Platform_Config.md` 到 `guides/`
- ✅ 移动 `SETUP_EMAIL_REMINDER.md` 到 `guides/`
- ✅ 删除过时文档（`CHECK_DEPLOYMENT.md`、重复文件）
- ✅ 删除过时脚本（`install_celery_only.sh`、`setup_email_step_by_step.sh`）
- ✅ 删除 `docs/archive/` 目录（7 个旧文档）
- ✅ 创建 `PROJECT_STRUCTURE.md` 项目结构说明
- ✅ 更新文档索引和导航

---

**最后更新**: 2025-11-08 23:05  
**维护**: Ralendar Team  
**文档状态**: 已重组优化 ✨

**愿每一行代码都有意义，每一个功能都有温度。** 💙


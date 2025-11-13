# 🔧 500错误排查指南

## 🚨 快速排查步骤

### 1. 查看服务器日志

```bash
# uWSGI日志
tail -f ~/ralendar/backend/logs/uwsgi.log

# 或查看系统日志
sudo journalctl -u ralendar-uwsgi -f

# Django错误日志（如果配置了）
tail -f ~/ralendar/backend/logs/django.log
```

### 2. 临时开启DEBUG模式查看详细错误

**⚠️ 仅用于调试，不要在生产环境长期开启！**

```python
# backend/calendar_backend/settings.py
DEBUG = True  # 临时开启
```

然后重启uWSGI：
```bash
cd ~/ralendar/backend
uwsgi --reload uwsgi.pid
```

### 3. 检查常见问题

#### 问题1: 数据库连接失败

```bash
# 测试数据库连接
cd ~/ralendar/backend
python manage.py dbshell

# 或检查数据库配置
python manage.py check --database default
```

#### 问题2: 导入错误

```bash
# 检查Python导入
cd ~/ralendar/backend
python manage.py shell

# 尝试导入视图
from api.views import *
```

#### 问题3: 静态文件问题

```bash
# 收集静态文件
cd ~/ralendar/backend
python manage.py collectstatic --noinput
```

#### 问题4: 迁移未执行

```bash
# 检查迁移状态
python manage.py showmigrations

# 执行未应用的迁移
python manage.py migrate
```

### 4. 检查最近修改的代码

如果最近修改了以下文件，检查是否有语法错误：

- `backend/calendar_backend/settings.py` - 配置错误
- `backend/api/views/__init__.py` - 导入错误
- `backend/api/views/external/fortune.py` - 新添加的视图

### 5. 检查依赖

```bash
# 检查requirements.txt是否安装完整
cd ~/ralendar/backend
pip install -r requirements.txt

# 检查Python版本
python --version  # 应该是3.8+
```

## 🔍 常见500错误原因

### 1. 数据库连接问题

**错误信息**:
```
OperationalError: could not connect to server
```

**解决**:
- 检查数据库服务是否运行
- 检查`.env`文件中的数据库配置
- 检查数据库白名单

### 2. 导入错误

**错误信息**:
```
ModuleNotFoundError: No module named 'xxx'
ImportError: cannot import name 'xxx'
```

**解决**:
- 检查`backend/api/views/__init__.py`中的导入
- 确保所有导入的模块存在
- 检查Python路径

### 3. 配置错误

**错误信息**:
```
ImproperlyConfigured: xxx
```

**解决**:
- 检查`settings.py`中的配置
- 检查环境变量
- 检查`.env`文件

### 4. 序列化器错误

**错误信息**:
```
ValidationError: xxx
```

**解决**:
- 检查API请求的数据格式
- 检查序列化器定义

## 📝 调试命令

```bash
# 1. 检查Django配置
python manage.py check

# 2. 检查数据库
python manage.py check --database default

# 3. 测试特定视图
python manage.py shell
>>> from api.views import get_today_fortune
>>> # 测试导入

# 4. 查看uWSGI进程
ps aux | grep uwsgi

# 5. 重启服务
uwsgi --reload uwsgi.pid
```

## 🆘 紧急恢复

如果无法快速定位问题，可以：

1. **回滚到上一个稳定版本**:
```bash
cd ~/ralendar
git log --oneline -10  # 查看最近提交
git checkout <上一个稳定commit>
uwsgi --reload uwsgi.pid
```

2. **临时禁用有问题的功能**:
```python
# 在views中临时返回空响应
@api_view(['GET'])
def problematic_view(request):
    return Response({'error': 'temporarily disabled'}, status=503)
```

3. **启用详细日志**:
```python
# settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'logs/django.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
```


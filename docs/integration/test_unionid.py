#!/usr/bin/env python3
"""
QQ UnionID 测试脚本 - 在服务器上运行
使用方法：
    cd ~/kotlin_calendar/backend
    python ../QQ_UNIONID_TEST.py
"""

import os
import sys
import django

# 设置 Django 环境
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'calendar_backend.settings')
django.setup()

from api.models import QQUser
from django.contrib.auth.models import User
from django.db import connection

def test_unionid_field():
    """测试 1: 检查 unionid 字段是否存在"""
    print('\n' + '='*60)
    print('测试 1: 检查数据库字段')
    print('='*60)
    
    try:
        cursor = connection.cursor()
        cursor.execute("DESCRIBE api_qquser")
        columns = cursor.fetchall()
        
        unionid_found = False
        for col in columns:
            field_name = col[0]
            field_type = col[1]
            print(f"  字段: {field_name:20s} 类型: {field_type}")
            if field_name == 'unionid':
                unionid_found = True
        
        if unionid_found:
            print("\n✅ unionid 字段存在")
            return True
        else:
            print("\n❌ unionid 字段不存在")
            print("   请执行：python manage.py migrate")
            return False
    except Exception as e:
        print(f"\n❌ 检查失败: {e}")
        return False


def test_existing_users():
    """测试 2: 查看现有用户"""
    print('\n' + '='*60)
    print('测试 2: 查看现有 QQ 用户')
    print('='*60)
    
    try:
        users = QQUser.objects.all()
        count = users.count()
        
        print(f"\n共有 {count} 个 QQ 用户：\n")
        
        if count == 0:
            print("  （暂无 QQ 用户）")
            return True
        
        for i, qq_user in enumerate(users[:10], 1):
            print(f"  {i}. 用户: {qq_user.user.username}")
            print(f"     OpenID:  {qq_user.openid[:20]}...")
            print(f"     UnionID: {(qq_user.unionid[:20] + '...') if qq_user.unionid else '(未设置)'}")
            print(f"     昵称:    {qq_user.nickname}")
            print()
        
        if count > 10:
            print(f"  ... 还有 {count - 10} 个用户")
        
        return True
    except Exception as e:
        print(f"\n❌ 查询失败: {e}")
        return False


def test_unionid_index():
    """测试 3: 检查 unionid 索引"""
    print('\n' + '='*60)
    print('测试 3: 检查索引')
    print('='*60)
    
    try:
        cursor = connection.cursor()
        cursor.execute("SHOW INDEX FROM api_qquser WHERE Column_name = 'unionid'")
        indexes = cursor.fetchall()
        
        if indexes:
            print("\n✅ unionid 索引存在")
            for idx in indexes:
                print(f"  索引名: {idx[2]}, 列: {idx[4]}")
            return True
        else:
            print("\n⚠️  unionid 索引不存在（性能可能受影响）")
            return False
    except Exception as e:
        print(f"\n❌ 检查失败: {e}")
        return False


def test_query_performance():
    """测试 4: 测试 UnionID 查询"""
    print('\n' + '='*60)
    print('测试 4: 测试 UnionID 查询性能')
    print('='*60)
    
    try:
        import time
        
        # 测试通过 UnionID 查询
        test_unionid = 'TEST_UNION_ID_123'
        
        start = time.time()
        result = QQUser.objects.filter(unionid=test_unionid).first()
        elapsed = (time.time() - start) * 1000
        
        print(f"\n  UnionID 查询耗时: {elapsed:.2f} ms")
        
        if elapsed < 100:
            print("  ✅ 查询速度正常")
        else:
            print("  ⚠️  查询速度较慢，建议检查索引")
        
        return True
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        return False


def main():
    print('\n' + '='*60)
    print('🔍 QQ UnionID 集成测试')
    print('='*60)
    print(f'时间: {__import__("datetime").datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    
    results = {}
    
    # 运行所有测试
    results['字段检查'] = test_unionid_field()
    results['用户查询'] = test_existing_users()
    results['索引检查'] = test_unionid_index()
    results['查询性能'] = test_query_performance()
    
    # 汇总结果
    print('\n' + '='*60)
    print('📊 测试结果汇总')
    print('='*60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, success in results.items():
        status = '✅' if success else '❌'
        print(f'{status} {test_name}')
    
    print(f'\n通过: {passed}/{total}')
    
    if passed == total:
        print('\n🎉 所有测试通过！QQ UnionID 集成成功！')
        print('\n下一步：')
        print('1. 用 QQ 登录测试')
        print('2. 查看日志：tail -f backend/logs/django.log')
        print('3. 应该看到 UnionID 相关日志')
    else:
        print(f'\n⚠️  部分测试失败（{total - passed} 个）')
        print('\n建议：')
        if not results['字段检查']:
            print('- 执行：python manage.py migrate')
        if not results['索引检查']:
            print('- 重新执行迁移或手动创建索引')
    
    return passed == total


if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print('\n\n测试已取消')
        sys.exit(1)
    except Exception as e:
        print(f'\n\n❌ 测试出错: {e}')
        import traceback
        traceback.print_exc()
        sys.exit(1)


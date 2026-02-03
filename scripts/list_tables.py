"""
列出飞书多维表格下的所有数据表
"""
import sys
import os
import json

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, "src"))

from tools.feishu_bitable_tool import FeishuBitableClient, get_access_token


def list_tables(app_token):
    """
    列出多维表格下的所有数据表
    """
    client = FeishuBitableClient()
    token = get_access_token()
    
    print(f"正在查询多维表格: {app_token}\n")
    
    try:
        # 列出所有数据表
        response = client._request(token, "GET", f"/bitable/v1/apps/{app_token}/tables")
        
        tables = response.get("data", {}).get("items", [])
        
        if not tables:
            print("❌ 未找到任何数据表")
            return
        
        print(f"✅ 找到 {len(tables)} 个数据表：\n")
        print("=" * 80)
        
        for i, table in enumerate(tables, 1):
            print(f"\n📊 数据表 #{i}")
            print(f"  名称: {table.get('name', 'N/A')}")
            print(f"  ID: {table.get('table_id', 'N/A')}")
            print(f"  版本: {table.get('revision', 'N/A')}")
            
            # 获取字段信息
            try:
                fields_response = client.get_fields(token, app_token, table['table_id'])
                fields = fields_response.get("data", {}).get("items", [])
                print(f"  字段数: {len(fields)}")
                
                if fields:
                    print(f"  字段列表: {', '.join([f.get('field_name', 'N/A') for f in fields[:5]])}")
                    if len(fields) > 5:
                        print(f"          ...还有 {len(fields) - 5} 个字段")
            except Exception as e:
                print(f"  获取字段信息失败: {str(e)}")
        
        print("\n" + "=" * 80)
        print("\n💡 使用建议：")
        print("1. 从上述列表中选择你要分析的数据表")
        print("2. 复制对应的 table_id")
        print("3. 更新配置文件 scripts/daily_analysis_config.json")
        
    except Exception as e:
        print(f"❌ 查询失败: {str(e)}")
        print("\n可能的原因：")
        print("1. app_token 不正确")
        print("2. 没有访问该多维表格的权限")
        print("3. 飞书集成凭证未正确配置")


if __name__ == "__main__":
    # 使用用户提供的 app_token
    app_token = "LvSAboJTJanJKdssWs8cm49vn8c"
    
    list_tables(app_token)

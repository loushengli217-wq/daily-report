"""
调试：查看原始API返回的数据
"""
import sys
import os
import json

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, "src"))

from tools.feishu_bitable_tool import FeishuBitableClient, get_access_token


def debug_data(app_token, table_id):
    """调试数据结构"""
    client = FeishuBitableClient()
    token = get_access_token()

    try:
        # 获取第一条记录
        response = client.search_records(
            token,
            app_token,
            table_id,
            page_size=1
        )

        records = response.get("data", {}).get("items", [])

        if records:
            print("第一条记录的完整结构：")
            print("=" * 100)
            print(json.dumps(records[0], indent=2, ensure_ascii=False))
        else:
            print("没有找到记录")

    except Exception as e:
        print(f"错误: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    app_token = "LvSAboJTJanJKdssWs8cm49vn8c"
    table_id = "tblBiiYpOdRGonPy"

    debug_data(app_token, table_id)

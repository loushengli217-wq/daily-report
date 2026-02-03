"""
飞书多维表格工具
用于从飞书多维表格获取数据
"""
import json
import requests
from functools import wraps
from langchain.tools import tool, ToolRuntime
from coze_workload_identity import Client
from cozeloop.decorator import observe

client = Client()

def get_access_token() -> str:
    """
    获取飞书多维表格的访问令牌
    """
    access_token = client.get_integration_credential("integration-feishu-base")
    return access_token

def require_token(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        token = get_access_token()
        if not token:
            raise ValueError("FEISHU_TENANT_ACCESS_TOKEN is not set")
        return func(token, *args, **kwargs)
    return wrapper

class FeishuBitableClient:
    """
    飞书多维表格HTTP客户端
    """
    def __init__(self, base_url: str = "https://open.larkoffice.com/open-apis", timeout: int = 30):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def _headers(self, token: str) -> dict:
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=utf-8",
        }

    @observe
    def _request(self, token: str, method: str, path: str, params: dict | None = None, json_data: dict | None = None) -> dict:
        try:
            url = f"{self.base_url}{path}"
            resp = requests.request(method, url, headers=self._headers(token), params=params, json=json_data, timeout=self.timeout)
            resp_data = resp.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"FeishuBitable API request error: {e}")
        if resp_data.get("code") != 0:
            raise Exception(f"FeishuBitable API error: {resp_data}")
        return resp_data

    def search_records(
        self,
        token: str,
        app_token: str,
        table_id: str,
        view_id: str | None = None,
        field_names: list[str] | None = None,
        sort: list | None = None,
        filter: dict | str | None = None,
        page_size: int | None = None,
    ) -> dict:
        """
        条件查询记录
        """
        params: dict = {}
        if page_size is not None:
            params["page_size"] = page_size
        
        body: dict = {}
        if view_id is not None:
            body["view_id"] = view_id
        if field_names is not None:
            body["field_names"] = field_names
        if sort is not None:
            body["sort"] = sort
        if filter is not None:
            body["filter"] = filter
        
        return self._request(token, "POST", f"/bitable/v1/apps/{app_token}/tables/{table_id}/records/search", params=params, json_data=body)

    def get_fields(
        self,
        token: str,
        app_token: str,
        table_id: str,
    ) -> dict:
        """
        获取数据表字段信息
        """
        return self._request(token, "GET", f"/bitable/v1/apps/{app_token}/tables/{table_id}/fields")


@tool
def get_bitable_data(app_token: str, table_id: str, filter_condition: str = None, sort_field: str = None, page_size: int = 100) -> str:
    """
    从飞书多维表格获取数据
    
    Args:
        app_token: 飞书多维表格的App Token
        table_id: 数据表的Table ID
        filter_condition: 筛选条件（可选），格式为JSON字符串，例如：'{"field_name": "status", "operator": "is", "value": "active"}'
        sort_field: 排序字段（可选），例如："created_time"
        page_size: 每页获取的记录数，默认100
    
    Returns:
        JSON格式的数据，包含字段信息和记录列表
    """
    ctx = None  # 工具不需要上下文
    
    feishu_client = FeishuBitableClient()
    token = get_access_token()
    
    # 获取字段信息
    fields_response = feishu_client.get_fields(token, app_token, table_id)
    fields_info = fields_response.get("data", {}).get("items", [])
    
    # 构建查询参数
    query_params = {}
    if page_size:
        query_params["page_size"] = page_size
    
    if sort_field:
        query_params["sort"] = [{
            "field_name": sort_field,
            "desc": False
        }]
    
    # 如果有筛选条件
    if filter_condition:
        try:
            filter_obj = json.loads(filter_condition) if isinstance(filter_condition, str) else filter_condition
            query_params["filter"] = filter_obj
        except json.JSONDecodeError:
            return json.dumps({"error": "Invalid filter condition JSON format"}, ensure_ascii=False)
    
    # 搜索记录
    records_response = feishu_client.search_records(
        token, app_token, table_id,
        **query_params
    )
    
    records = records_response.get("data", {}).get("items", [])
    
    # 构建返回结果
    result = {
        "fields": fields_info,
        "total": len(records),
        "records": records
    }
    
    return json.dumps(result, ensure_ascii=False, indent=2)


@tool
def get_bitable_fields(app_token: str, table_id: str) -> str:
    """
    获取飞书多维表格的字段结构信息
    
    Args:
        app_token: 飞书多维表格的App Token
        table_id: 数据表的Table ID
    
    Returns:
        JSON格式的字段信息
    """
    ctx = None
    
    feishu_client = FeishuBitableClient()
    token = get_access_token()
    
    fields_response = feishu_client.get_fields(token, app_token, table_id)
    fields_info = fields_response.get("data", {}).get("items", [])
    
    result = {
        "table_id": table_id,
        "field_count": len(fields_info),
        "fields": fields_info
    }
    
    return json.dumps(result, ensure_ascii=False, indent=2)

# -*- coding: utf-8 -*-
"""
Tools module for Ollama function calling
Chứa các hàm demo và utility functions với type hints và docstrings
"""
import json
import requests
from typing import Dict, List, Optional, Union
from datetime import datetime


def add_two_numbers(a: int, b: int) -> int:
    """
    Cộng hai số nguyên

    Args:
        a: Số nguyên thứ nhất
        b: Số nguyên thứ hai

    Returns:
        int: Tổng của hai số
    """
    return a + b


def calculate_percentage(value: float, total: float) -> float:
    """
    Tính phần trăm

    Args:
        value: Giá trị cần tính phần trăm
        total: Tổng giá trị

    Returns:
        float: Phần trăm (0-100)
    """
    if total == 0:
        return 0.0
    return (value / total) * 100


def get_current_time() -> str:
    """
    Lấy thời gian hiện tại

    Returns:
        str: Thời gian hiện tại theo định dạng ISO
    """
    return datetime.now().isoformat()


def search_job_info(query: str, job_type: str = "all") -> Dict:
    """
    Tìm kiếm thông tin công việc (mock function)

    Args:
        query: Từ khóa tìm kiếm
        job_type: Loại công việc (full-time, part-time, internship, all)

    Returns:
        dict: Thông tin các công việc tìm được
    """
    # Mock data - trong thực tế sẽ query database
    mock_jobs = [
        {
            "id": 1,
            "title": "Python Developer",
            "company": "Tech Corp",
            "type": "full-time",
            "location": "Ho Chi Minh City",
            "salary": "$1000-2000"
        },
        {
            "id": 2,
            "title": "AI Engineer",
            "company": "AI Solutions",
            "type": "full-time",
            "location": "Hanoi",
            "salary": "$1500-3000"
        }
    ]
    
    # Filter by job_type
    if job_type != "all":
        mock_jobs = [job for job in mock_jobs if job["type"] == job_type]
    
    # Filter by query (simple contains)
    query_lower = query.lower()
    filtered_jobs = [
        job for job in mock_jobs 
        if query_lower in job["title"].lower() or query_lower in job["company"].lower()
    ]
    
    return {
        "query": query,
        "job_type": job_type,
        "total_found": len(filtered_jobs),
        "jobs": filtered_jobs
    }


def format_json_response(data: Union[Dict, List], pretty: bool = True) -> str:
    """
    Format dữ liệu thành JSON string

    Args:
        data: Dữ liệu cần format
        pretty: Có format đẹp hay không

    Returns:
        str: JSON string
    """
    if pretty:
        return json.dumps(data, indent=2, ensure_ascii=False)
    return json.dumps(data, ensure_ascii=False)


def make_safe_http_request(url: str, method: str = "GET", timeout: int = 10) -> Dict:
    """
    Thực hiện HTTP request an toàn với whitelist domain

    Args:
        url: URL cần gọi
        method: HTTP method (GET, POST)
        timeout: Timeout in seconds

    Returns:
        dict: Response data hoặc error info
    """
    # Whitelist domains for safety
    allowed_domains = [
        "httpbin.org",
        "jsonplaceholder.typicode.com",
        "api.github.com"
    ]
    
    # Check if URL is allowed
    from urllib.parse import urlparse
    parsed = urlparse(url)
    if not any(domain in parsed.netloc for domain in allowed_domains):
        return {
            "error": f"Domain {parsed.netloc} is not in allowed list",
            "allowed_domains": allowed_domains
        }
    
    try:
        if method.upper() == "GET":
            response = requests.get(url, timeout=timeout)
        elif method.upper() == "POST":
            response = requests.post(url, timeout=timeout)
        else:
            return {"error": f"Method {method} not supported"}
        
        return {
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "content": response.text[:1000],  # Limit content size
            "success": response.status_code < 400
        }
    except requests.RequestException as e:
        return {
            "error": str(e),
            "success": False
        }


# Tool registry - mapping tên tool -> function
AVAILABLE_TOOLS = {
    "add_two_numbers": add_two_numbers,
    "calculate_percentage": calculate_percentage,
    "get_current_time": get_current_time,
    "search_job_info": search_job_info,
    "format_json_response": format_json_response,
    "make_safe_http_request": make_safe_http_request,
}


def get_tool_by_name(tool_name: str):
    """
    Lấy tool function theo tên

    Args:
        tool_name: Tên tool

    Returns:
        callable: Tool function hoặc None nếu không tìm thấy
    """
    return AVAILABLE_TOOLS.get(tool_name)


def list_available_tools() -> List[str]:
    """
    Lấy danh sách tên các tool có sẵn

    Returns:
        list: Danh sách tên tools
    """
    return list(AVAILABLE_TOOLS.keys())

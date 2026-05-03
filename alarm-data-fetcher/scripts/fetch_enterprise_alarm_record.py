import aiohttp
import asyncio
import argparse
import json
import os
import shutil
from typing import Optional, List

API_URL = "http://10.168.24.39:7777/service/serviceinterface/search/run.action"
INTERFACE_ID = "bc7dd12a37d1349ab320b03253389525"
TOKEN = "38f571ce7cba5284e15452f9aaf1038a"

def prepare_tmp_dir(tmp_dir: str):
    if os.path.exists(tmp_dir):
        shutil.rmtree(tmp_dir)
    os.makedirs(tmp_dir)

async def fetch_date_range_data(
    session: aiohttp.ClientSession,
    start_date: str,
    end_date: str,
    enterprise_name: Optional[str],
    page_index: int
) -> List[dict]:
    """
    根据开始和结束日期获取报警数据
    """
    params = {
        "interfaceId": INTERFACE_ID,
        "token": TOKEN
    }

    # 修改为最新的 payload 传参方式
    payload = {
        "alarm_time_start": start_date,
        "alarm_time_end": end_date,
        "pageNum": page_index,
        "pageSize": 200
    }

    if enterprise_name:
        payload["enterprise_name"] = enterprise_name

    async with session.post(url=API_URL, params=params, json=payload) as resp:
        resp.raise_for_status()
        result = await resp.json()

        # 假设接口返回格式为 {"data": [...]} 或 [...]
        if isinstance(result, dict):
            return result.get("data", [])
        return result

async def fetch_all(args):
    all_records = []
    page = 1
    max_pages = 30
    async with aiohttp.ClientSession() as session:
        while page <= max_pages:
            try:
                print(f"⏳ 正在请求 {args.start_date} 至 {args.end_date} 的数据 (第 {page} 页)...")
                res = await fetch_date_range_data(session, args.start_date, args.end_date, args.enterprise_name, page)
                print(f"✅ 第 {page} 页获取 {len(res)} 条数据。")
                if not res or len(res) == 0:
                    print(f"第 {page} 页无数据，停止分页。")
                    break
                all_records.extend(res)
                if len(res) < 200:
                    print(f"第 {page} 页数据不足一页，判定为最后一页。")
                    break
                page += 1
            except Exception as e:
                print(f"❌ 请求第 {page} 页失败: {e}")
                break
    return all_records

def main(args):
    prepare_tmp_dir(args.tmp_dir)
    all_data = asyncio.run(fetch_all(args))
    output_file = os.path.join(args.tmp_dir, "all_alarms.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    print(f"\n✅ 共获取 {len(all_data)} 条报警数据，已保存至 {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="按日期区间获取企业全部报警数据（自动分页）")
    parser.add_argument("--start-date", type=str, required=True, help="开始日期，格式 YYYY-MM-DD")
    parser.add_argument("--end-date", type=str, required=True, help="结束日期，格式 YYYY-MM-DD")
    parser.add_argument("--enterprise-name", type=str, default=None, help="企业名称（精确匹配）")
    parser.add_argument("--tmp-dir", type=str, required=True, help="临时目录绝对路径，将在此目录生成 all_alarms.json")
    args = parser.parse_args()
    main(args)
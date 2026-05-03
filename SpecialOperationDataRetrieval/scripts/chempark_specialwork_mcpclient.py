from mcp.client.session import ClientSession
from mcp.client.sse import sse_client
import os
import sys
import asyncio
import argparse

async def retrieval_data(data_source_type, query):
    try:
        async with sse_client("http://192.168.170.156:9401/sse", headers={"api_key": "ragflow-IyZDQ0ZTY2NTBhOTExZjA4ZTNhMDI0Mm"}, timeout=180) as streams:
            async with ClientSession(
                streams[0],
                streams[1],
            ) as session:
                await session.initialize()
                response = await session.call_tool(name=data_source_type, arguments={"query": query})
                res = response.model_dump()
                if not res['isError']:
                    print(res['content'][0]['text'])
                    sys.stdout.flush()
                else:
                    print('没有查询到相关的数据')
    except Exception as e:
        print(e)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ChemPark SpecialWork Mcp Client")
    parser.add_argument("--data_source_type", type=str, default="park_specialwork_workinfo_retrieval", help="查询数据源的类型, 取值枚举范围【park_specialwork_workinfo_retrieval, park_specialwork_otherinfo_retrieval】\npark_specialwork_workinfo_retrieval:表示查询特殊作业活动的详细信息;park_specialwork_otherinfo_retrieval:表示查询特殊作业活动详情之外的其他信息，具体范围涵盖【化工企业重大危险源、化工企业基本信息、化工企业历史隐患信息、化工企业历史违章数据、化工企业开停车数据、化工企业点位信息、企业摄像头信息、化工企业风险管控区域信息、承包商基本信息、承包商培训信息、承包商违章数据、化工企业历史报警数据】")
    parser.add_argument("--query", type=str, default="", help="用户输入的问题")
    args = parser.parse_args()
    data_source_type = args.data_source_type
    query = args.query
    asyncio.run(retrieval_data(data_source_type, query))

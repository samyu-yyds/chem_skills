---
name: 化工园区特殊作业数据查询技能
description: 此技能通过Python脚本查询化工园区特殊作业相关的数据，提供的数据查询范围包括【特殊作业活动详细记录、化工企业重大危险源信息、化工企业基本信息、企业设备的开停车记录、化工企业点位设备信息、企业摄像头信息、化工企业风险管控区域信息、承包商基本信息、承包商培训记录、承包商违章记录】
---

# 化工园区特殊作业数据查询技能

由于特殊作业系统存储的数据需要借助API的形式进行查询，因此该技能封装了一个Python脚本来查询化工园区的特殊作业系统数据的方法，信息范围涵盖了特殊作业活动详细记录、化工企业的重大危险源信息、化工企业基本信息、化工企业的设备开停车历史记录、化工企业的点位设备信息、摄像头信息、企业的风险管控区域信息、作业承包商的基本信息、承包商的培训记录、承包商的作业违章记录等信息。

## 何时使用此技能

以下情况可以使用此技能：

- 查询化工园区或者化工企业特殊作业活动的详细记录
- 对特殊作业活动进行某些维度的统计
- 查询化工企业的重大危险源信息
- 搜索化工企业的基本属性信息
- 获取企业内部的开停车记录
- 搜索化工企业的点位（IOT）设备信息
- 搜索化工企业的摄像头基本信息
- 获取化工企业的风险管控区域的基本信息
- 查询承包商关于基本信息、培训记录、违章记录

## 如何使用

此技能提供一个Python脚本用于查询化工园区特殊作业数据并返回结果。

## 脚本

脚本名称：`chempark_specialwork_mcpclient.py`
路径为：`~/.deepagents/agent/skills/SpecialOperationDataRetrieval/scripts/`

### 基本用法

-- **注意：**： 始终使用技能目录的绝对路径（如上文系统提示符所示）。

如果从虚拟环境运行 deepagents：
```bash
.venv/bin/python [YOUR_SKILLS_DIR]/SpecialOperationDataRetrieval/scripts/chempark_specialwork_mcpclient.py --data_source_type "查询数据源的类型" --query "用户输入的问题"
```

或者，对于系统自带的 Python：
```bash
python [YOUR_SKILLS_DIR]/SpecialOperationDataRetrieval/scripts/chempark_specialwork_mcpclient.py --data_source_type "查询数据源的类型" --query "用户输入的问题"
```
将 `[YOUR_SKILLS_DIR]` 替换为系统提示符中显示的技能目录的绝对路径（例如，`~/.deepagents/agent/skills` 或完整的绝对路径）。

-- **参数：**：
- `data_source_type`（必需）：查询数据源的类型, 取值枚举范围['park_specialwork_workinfo_retrieval', 'park_specialwork_otherinfo_retrieval'],具体解释如下：
  -- data_source_type 'park_specialwork_workinfo_retrieval'：查询园区特殊作业活动的详情信息（例如:最近一个月的动火作业数量;园区上个月的作业数量环比增长多少;明天有哪些受限空间作业;统计最近半年进行高处作业最多的前十>家企业及其频次）;
  -- data_source_type 'park_specialwork_otherinfo_retrieval'：查询特殊作业活动详情之外的其他信息，具体范围涵盖【化工企业重大危险源、化工企业基本信息、化工企业开停车数据、化工企业点位信息、企业摄像头信息、化工企业风险管控区域信息、承包商基本信息、承包商培训信息、承包商违章数据】的工具（例如:xxxx企业在最近三个月是否有设备开停车行为;xxxx企业有哪些二级以上的重大危险源;最近一年违章最多的前三个承包商是哪些;统计一下承包商xxxx最近三个月的培训次数）。
- `query`（必需）：用户输入的问题

### 工具示例

上个月有多少次动火作业?
```bash
.venv/bin/python ~/.deepagents/agent/skills/SpecialOperationDataRetrieval/scripts/chempark_specialwork_mcpclient.py --data_source_type park_specialwork_workinfo_retrieval --query 上个月有多少次动火作业
```
或者
```bash
python ~/.deepagents/agent/skills/SpecialOperationDataRetrieval/scripts/chempark_specialwork_mcpclient.py --data_source_type park_specialwork_workinfo_retrieval --query 上个月有多少次动火作业
```

统计一下前三个月各种类型的作业的数量及其占比
```bash
.venv/bin/python ~/.deepagents/agent/skills/SpecialOperationDataRetrieval/scripts/chempark_specialwork_mcpclient.py --data_source_type park_specialwork_workinfo_retrieval --query 前三个月各种类型的作业的数量及其占比
```
或者
```bash
python ~/.deepagents/agent/skills/SpecialOperationDataRetrieval/scripts/chempark_specialwork_mcpclient.py --data_source_type park_specialwork_workinfo_retrieval --query 前三个月各种类型的作业的数量及其占比
```

上周报警最多的前三家企业有哪些?
```bash
.venv/bin/python ~/.deepagents/agent/skills/SpecialOperationDataRetrieval/scripts/chempark_specialwork_mcpclient.py --data_source_type park_specialwork_otherinfo_retrieval --query 上周报警最多的前三家企业
```
或者
```bash
python ~/.deepagents/agent/skills/SpecialOperationDataRetrieval/scripts/chempark_specialwork_mcpclient.py --data_source_type park_specialwork_otherinfo_retrieval --query 上周报警最多的前三家企业
```

园区内哪些企业有二级以上的重大危险源
```bash
.venv/bin/python ~/.deepagents/agent/skills/SpecialOperationDataRetrieval/scripts/chempark_specialwork_mcpclient.py --data_source_type park_specialwork_otherinfo_retrieval --query 园区内哪些企业有二级以上的重大危险源
```
或者
```bash
python ~/.deepagents/agent/skills/SpecialOperationDataRetrieval/scripts/chempark_specialwork_mcpclient.py --data_source_type park_specialwork_otherinfo_retrieval --query 园区内哪些企业有二级以上的重大危险源
```

## 功能

- **快速检索**：直接访问园区特殊作业系统的API，无需身份验证
- **简洁的数据**：清晰易懂的输出

## 依赖项

此技能需要 Python 包 `mcp`。脚本会检测是否缺少该包并显示错误信息。
**如果您看到“错误：mcp 软件包未安装”：**
如果从虚拟环境运行 deepagents（推荐），请使用虚拟环境的 Python：

```bash
.venv/bin/python -m pip install mcp
```
或者进行系统级安装：
```bash
python3 -m pip install mcp
```
由于该软件包是特定技能的，因此默认情况下 deepagents 中未包含。首次使用此技能时，请按需安装。

**如果您看到其他“错误：类似xxx 软件包未安装”：**
使用上述相同的方法进行安装。


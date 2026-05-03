---
name: 企业报警数据查询技能
description: 根据企业名称和日期范围，从园区平台获取全量报警数据（含数据报警和视频报警），返回JSON 文件。用于生成企业安全分析报告、报警排查或巡检前准备。
---

# 技能指令：企业报警数据查询

- 此工具用于通过 API 拉取化工企业的报警记录。脚本内部自动处理分页，无需外部循环。最终在指定临时目录生成 `all_alarms.json`。
- **执行前自动清空临时目录**，避免残留上次运行的脏数据。

## 🎯 核心执行约束 (Agent 必读)

1. **路径解析**：脚本固定存放在 `skills/alarm-data-fetcher/scripts/fetch_enterprise_alarm_record.py`。请结合当前工作目录拼接完整的绝对路径。
2. **分页已内置**：脚本内部自动翻页，Agent 只需执行一次命令。
3. **参数严格性**：不要传递未在下方定义的参数，不要修改日期格式。

## ⚙️ 参数列表 (CLI Arguments)

| 参数名 | 类型 | 必填 | 说明/约束 |
| :--- | :--- | :--- | :--- |
| `--start-date` | String | **是** | 查询起始日期。格式必须为 `YYYY-MM-DD`。 |
| `--end-date` | String | **是** | 查询结束日期。格式必须为 `YYYY-MM-DD`。 |
| `--enterprise-name` | String | 否 | 精确匹配的企业名称。如果未指定，则查询所有企业。必须且只能从以下枚举值中选择：<br> - `浙江倍合德制药有限公司`<br> - `浙江国邦药业有限公司`<br> - `上虞颖泰精细化工有限公司`<br> - `浙江巍华新材料股份有限公司`<br> - `浙江晖石药业有限公司` |
| `--tmp-dir` | String | **是** | 临时目录的绝对路径。脚本会在该目录下生成 `all_alarms.json`，并在运行开始时**自动清空该目录内的所有文件**。 |

## 💻 命令行调用模板

```bash
python3 /绝对路径/skills/alarm-data-fetcher/scripts/fetch_enterprise_alarm_record.py \
  --start-date "YYYY-MM-DD" \
  --end-date "YYYY-MM-DD" \
  --enterprise-name "xxx企业名称" \
  --tmp-dir "/tmp/alarm_data_xxx"
```

## 🔄 Agent 执行流示例

1. 确定临时目录，例如 `/tmp/alarm_data_巍华_202604`。
2. 执行命令：
   ```bash
   python3 /path/to/skills/alarm-data-fetcher/scripts/fetch_enterprise_alarm_record.py \
     --start-date "2026-04-01" \
     --end-date "2026-04-30" \
     --enterprise-name "浙江巍华新材料股份有限公司" \
     --tmp-dir "/tmp/alarm_data_巍华_202604"
   ```
3. 脚本自动清空目录 → 自动分页拉取全量数据 → 生成 `/tmp/alarm_data_巍华_202604/all_alarms.json`。
4. stdout 显示汇总信息，如“共获取 500 条报警数据，保存至 ...”。
5. 保留临时文件供后续步骤使用。

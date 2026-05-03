---
name: HighriskAlarmJudge
description: 对全量报警数据进行规则化分析，自动识别高风险报警并输出列表（含判定原因），用于安全报告编制、巡检重点确定或实时报警处置决策。
---

# 高风险报警判定（规则引擎版）

本技能基于固化的高风险规则（A级未恢复、重大危险源严重超标、复合联动风险、视频违章等），对全量报警数据进行自动判定，输出高风险报警列表。

## 输入要求
- 需要已经获取的全量报警 JSON 文件，路径通过参数传入。

## 脚本
- 脚本路径：`skills/alarm-risk-filter/scripts/high_risk_filter.py`
- 执行时需拼接工作目录的绝对路径。

## 参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `--alarm_record_file` | string | 是 | 全量报警 JSON 文件绝对路径（如 `all_alarms.json`） |
| `--output_highrisk_file` | string | 是 | 输出高风险报警 JSON 文件绝对路径（如 `high_risk_alarms.json`） |

## 命令行调用模板

```bash
python3 /绝对路径/skills/alarm-risk-filter/scripts/high_risk_filter.py \
  --alarm_record_file "/tmp/alarm_data_xxx/all_alarms.json" \
  --output_highrisk_file "/tmp/alarm_data_xxx/high_risk_alarms.json"
```

## 输出

- 指定路径生成 `high_risk_alarms.json`，内容为高风险报警列表（数组），每条记录保留所有原始字段并已中文化，同时包含 `高风险原因` 字段（数组），列出命中的规则原因。
- 控制台输出高风险报警总数及各原因统计。

## 注意事项
- 脚本不修改输入文件。
- 风险判定规则已内置，无需传参。
- 输出文件可直接供报告生成技能使用。

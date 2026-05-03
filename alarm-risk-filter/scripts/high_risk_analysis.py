#!/usr/bin/env python3
"""
高风险报警判定脚本（基于整合规则 v2.0）
读取全量报警JSON，输出高风险报警列表，附加命中规则原因。
"""

import json
import argparse
from datetime import datetime, timedelta
from collections import defaultdict, Counter

# ---------- 时间解析 ----------
def parse_time_ymd_hms(time_str):
    """解析 YYYY-MM-DD HH:MM:SS 格式"""
    if not time_str or not time_str.strip():
        return None
    try:
        return datetime.strptime(time_str.strip(), "%Y-%m-%d %H:%M:%S")
    except:
        return None

def parse_time_cst(time_str):
    """解析 WeekDay Mon DD HH:MM:SS CST YYYY 格式"""
    if not time_str or not time_str.strip():
        return None
    try:
        # 分割 CST 前后的部分
        parts = time_str.strip().split("CST")
        if len(parts) < 2:
            return None
        date_part = parts[0].strip()  # "Thu Apr 02 09:04:20"
        year_part = parts[1].strip()   # "2026"
        # 去掉星期缩写
        tokens = date_part.split()
        if len(tokens) >= 4:
            month_day = tokens[1] + " " + tokens[2]  # "Apr 02"
            time_part = tokens[3]                     # "09:04:20"
            full_str = f"{month_day} {time_part} {year_part}"  # "Apr 02 09:04:20 2026"
            return datetime.strptime(full_str, "%b %d %H:%M:%S %Y")
    except Exception as e:
        pass
    return None

def get_alarm_datetime(alarm):
    """获取报警发生时间"""
    return parse_time_ymd_hms(alarm.get("alarm_time", ""))

def get_clear_datetime(alarm):
    """获取报警恢复时间"""
    return parse_time_cst(alarm.get("clear_time", ""))

def get_close_datetime(alarm):
    """获取处置时间"""
    return parse_time_ymd_hms(alarm.get("close_time", ""))

# ---------- 辅助判断 ----------
def is_recovered(alarm):
    return get_clear_datetime(alarm) is not None

def is_handled(alarm):
    return get_close_datetime(alarm) is not None

def get_level(alarm):
    return alarm.get("alarm_level", "4")

def is_hazard_area(alarm):
    return alarm.get("is_hazard_area", "否") == "是"

def get_point_type(alarm):
    return alarm.get("point_index", "")

def get_threshold_ratio(alarm):
    try:
        v = float(alarm.get("value", 0))
        t = float(alarm.get("threshold_value", 1))
        if t > 0:
            return v / t
    except:
        pass
    return 0

# 字段名映射
FIELD_NAME_MAP = {
    "alarm_id": "报警ID",
    "point_num": "测点编号",
    "enterprise_id": "企业ID",
    "enterprise_name": "企业名称",
    "originator_name": "报警对象名称",
    "area_id": "区域ID",
    "area_name": "区域名称",
    "alarm_level": "报警等级编码",
    "alarm_level_name": "报警等级",
    "point_index": "点位类型",
    "value": "报警值",
    "threshold_value": "阈值",
    "alarm_time": "报警时间",
    "alarm_detail": "报警详情",
    "alarm_object_type": "报警归属编码",
    "alarm_object_type_name": "报警归属",
    "business_type": "业务类型编码",
    "business_type_name": "业务类型",
    "alarm_type": "报警类型编码",
    "alarm_type_name": "报警类型",
    "clear_time": "恢复时间",
    "alarm_valid": "是否有效编码",
    "alarm_valid_name": "是否有效",
    "close_time": "处置时间",
    "close_reason": "处置原因",
    "feedback_status": "反馈状态编码",
    "feedback_status_name": "反馈状态",
    "is_issue_receipt": "是否回执编码",
    "is_issue_receipt_name": "是否回执",
    "is_hazard_area": "是否重大危险源区域",
    "high_risk_reasons": "高风险原因"
}
def translate_alarm_keys(alarm):
    """将报警记录的所有英文字段名替换为中文"""
    return {FIELD_NAME_MAP.get(k, k): v for k, v in alarm.items()}

# ---------- 聚合构建 ----------
def build_date_point_counts(alarms):
    """构建 日期 -> point_num -> 报警条数 的字典，用于当天反复次数判断"""
    d = defaultdict(lambda: defaultdict(int))
    for a in alarms:
        t = get_alarm_datetime(a)
        if t:
            date_key = t.strftime("%Y-%m-%d")
            point_key = a.get("point_num", "")
            d[date_key][point_key] += 1
    return d

def build_area_sorted_alarms(alarms):
    """按区域分组，每组内按报警时间排序，返回字典 area_name -> sorted list of alarms"""
    area_map = defaultdict(list)
    for a in alarms:
        t = get_alarm_datetime(a)
        if t:
            area_map[a.get("area_name", "")].append((t, a))
    for area in area_map:
        area_map[area].sort(key=lambda x: x[0])
    return area_map

def build_point_sorted_alarms(alarms):
    """按 point_num 分组，每组内按报警时间排序"""
    point_map = defaultdict(list)
    for a in alarms:
        t = get_alarm_datetime(a)
        if t:
            point_map[a.get("point_num", "")].append((t, a))
    for p in point_map:
        point_map[p].sort(key=lambda x: x[0])
    return point_map

# ---------- 高风险判定 ----------
def detect_highrisk(alarm_record_file: str, output_highrisk_file: str):
    # 读取全量报警
    with open(alarm_record_file, "r", encoding="utf-8") as f:
        alarms = json.load(f)
    print(f"总报警数: {len(alarms)}")

    # 构建聚合结构
    date_point_counts = build_date_point_counts(alarms)
    area_sorted = build_area_sorted_alarms(alarms)
    point_sorted = build_point_sorted_alarms(alarms)

    # 用于标记高风险报警（避免重复添加）
    highrisk_set = set()         # 存 alarm_id
    highrisk_map = {}            # alarm_id -> alarm dict (含原因)
    reason_stats = Counter()

    # 辅助函数：记录高风险
    def mark_highrisk(alarm, reason):
        aid = alarm.get("alarm_id", "")
        if aid not in highrisk_set:
            alarm_copy = dict(alarm)
            alarm_copy["high_risk_reasons"] = [reason]
            highrisk_map[aid] = alarm_copy
            highrisk_set.add(aid)
            reason_stats[reason] += 1
        else:
            # 已经存在，追加原因
            if reason not in highrisk_map[aid]["high_risk_reasons"]:
                highrisk_map[aid]["high_risk_reasons"].append(reason)
                reason_stats[reason] += 1

    # ===== 规则一：最高等级报警未恢复 =====
    for alarm in alarms:
        level = get_level(alarm)
        if level != "1":
            continue
        alarm_t = get_alarm_datetime(alarm)
        recovered = is_recovered(alarm)
        handled = is_handled(alarm)
        # 子条件1: A级未恢复
        if not recovered:
            mark_highrisk(alarm, "规则一：A级报警未恢复")
        else:
            # 子条件2: A级已恢复但超3小时未处置
            close_t = get_close_datetime(alarm)
            if not close_t:
                # 从未处置
                mark_highrisk(alarm, "规则一：A级报警已恢复但企业未处置")
            elif alarm_t:
                diff_hours = (close_t - alarm_t).total_seconds() / 3600
                if diff_hours > 3:
                    mark_highrisk(alarm, f"规则一：A级报警处置时间超过3小时（{diff_hours:.1f}h）")
                # 否则不算高风险

    # ===== 规则二：重大危险源区域严重超标 =====
    for alarm in alarms:
        if not is_hazard_area(alarm):
            continue
        level = get_level(alarm)
        if level not in ("1", "2"):
            continue
        point_type = get_point_type(alarm)
        ratio = get_threshold_ratio(alarm)
        alarm_t = get_alarm_datetime(alarm)
        point_key = alarm.get("point_num", "")
        date_key = alarm_t.strftime("%Y-%m-%d") if alarm_t else None

        if point_type == "可燃气体" and ratio > 3:
            # 持续时间 > 30分钟
            clear_t = get_clear_datetime(alarm)
            if clear_t and alarm_t:
                duration_min = (clear_t - alarm_t).total_seconds() / 60
                if duration_min > 30:
                    mark_highrisk(alarm, "规则二：重大危险源可燃气体超标>3倍且持续>30分钟")
            # 当天反复 > 3次
            if date_key and date_point_counts[date_key][point_key] > 3:
                mark_highrisk(alarm, f"规则二：重大危险源可燃气体超标>3倍且当天报警{date_point_counts[date_key][point_key]}次")
        elif point_type == "有毒气体" and ratio > 2:
            clear_t = get_clear_datetime(alarm)
            if clear_t and alarm_t:
                duration_min = (clear_t - alarm_t).total_seconds() / 60
                if duration_min > 30:
                    mark_highrisk(alarm, "规则二：重大危险源有毒气体超标>2倍且持续>30分钟")
            if date_key and date_point_counts[date_key][point_key] > 3:
                mark_highrisk(alarm, f"规则二：重大危险源有毒气体超标>2倍且当天报警{date_point_counts[date_key][point_key]}次")

    # ===== 规则三：复合联动风险 =====
    # 子条件1：同区域30分钟内≥3种不同类型
    for area, time_alarm_list in area_sorted.items():
        n = len(time_alarm_list)
        for i in range(n):
            start_t = time_alarm_list[i][0]
            window_end = start_t + timedelta(minutes=30)
            # 扩展右边界，收集窗口内报警
            j = i
            while j < n and time_alarm_list[j][0] <= window_end:
                j += 1
            window_alarms = [ta[1] for ta in time_alarm_list[i:j]]
            types_in_window = set(get_point_type(a) for a in window_alarms)
            if len(types_in_window) >= 3:
                # 将该窗口内所有报警标记为高风险
                for a in window_alarms:
                    mark_highrisk(a, "规则三：同一区域30分钟内出现≥3种不同类型报警")

    # 子条件2：急速升级（同一测点≤3分钟从C/D升至A）
    for point, time_alarm_list in point_sorted.items():
        for i in range(len(time_alarm_list) - 1):
            t1, a1 = time_alarm_list[i]
            t2, a2 = time_alarm_list[i+1]
            if (t2 - t1).total_seconds() <= 180:  # ≤3分钟
                lv1 = get_level(a1)
                lv2 = get_level(a2)
                # 前一条为C或D，后一条为A
                if lv1 in ("3", "4") and lv2 == "1":
                    mark_highrisk(a2, "规则三：同一测点≤3分钟从低级跃升至A级（急速升级）")

    # ===== 规则四：视频智能识别违章 =====
    for alarm in alarms:
        alarm_type = alarm.get("alarm_type", "")
        if alarm_type != "2":
            continue
        detail = alarm.get("alarm_detail", "")
        area = alarm.get("area_name", "")
        # 明火/烟雾
        if "明火" in detail or "烟雾" in detail:
            mark_highrisk(alarm, "规则四：视频识别明火/烟雾报警")
        # 罐区吸烟/接打电话
        if "罐区" in area and ("吸烟" in detail or "电话" in detail):
            mark_highrisk(alarm, "规则四：罐区视频识别违章（吸烟/接打电话）")

    # 输出结果
    highrisk_list = list(highrisk_map.values())
    print(f"\n高风险报警数: {len(highrisk_list)}")
    print("\n高风险原因统计:")
    for reason, cnt in reason_stats.most_common():
        print(f"  {reason}: {cnt}条")

    translated_list = [translate_alarm_keys(alarm) for alarm in highrisk_list]
    with open(output_highrisk_file, "w", encoding="utf-8") as f:
        json.dump(translated_list, f, ensure_ascii=False, indent=2)
    print(f"\n高风险报警数据已保存至: {output_highrisk_file}")

def main():
    parser = argparse.ArgumentParser(description="高风险报警判定脚本 v2.0")
    parser.add_argument("--alarm_record_file", type=str, required=True,
                        help="全量报警JSON文件路径")
    parser.add_argument("--output_highrisk_file", type=str, required=True,
                        help="输出高风险报警JSON文件路径")
    args = parser.parse_args()

    detect_highrisk(args.alarm_record_file, args.output_highrisk_file)

if __name__ == "__main__":
    main()
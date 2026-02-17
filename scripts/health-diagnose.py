#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
设备健康诊断与理财建议生成器
Equipment Health Diagnosis & Financial Advice Generator

功能：
1. 分析设备使用效率（日均成本 vs 行业基准）
2. 生成出售/保留/更新建议
3. 提供年度预算规划
"""

import json
import argparse
from datetime import datetime, date
from pathlib import Path

# 行业基准日均成本（参考值）
INDUSTRY_BENCHMARKS = {
    "电脑": {"low": 15, "high": 35, "lifespan_years": 4},
    "手机": {"low": 5, "high": 15, "lifespan_years": 3},
    "平板": {"low": 2, "high": 8, "lifespan_years": 4},
    "可穿戴": {"low": 1, "high": 4, "lifespan_years": 3},
    "智能家居": {"low": 0.5, "high": 3, "lifespan_years": 5},
    "游戏设备": {"low": 2, "high": 8, "lifespan_years": 5},
    "EV配件": {"low": 5, "high": 15, "lifespan_years": 6},
    "车辆": {"low": 200, "high": 500, "lifespan_years": 8},
    "default": {"low": 1, "high": 10, "lifespan_years": 3}
}

# 残值率（按使用年限）
RESIDUAL_RATES = {
    (0, 1): 0.80,      # <1年
    (1, 2): 0.65,      # 1-2年
    (2, 3): 0.50,      # 2-3年
    (3, 4): 0.35,      # 3-4年
    (4, float('inf')): 0.20  # 4年+
}

def calculate_days_used(purchase_date_str, base_date=None):
    """计算已使用天数"""
    if base_date is None:
        base_date = date.today()
    purchase_date = datetime.strptime(purchase_date_str, "%Y-%m-%d").date()
    return (base_date - purchase_date).days

def get_residual_rate(years):
    """获取残值率"""
    for (min_yr, max_yr), rate in RESIDUAL_RATES.items():
        if min_yr <= years < max_yr:
            return rate
    return 0.20

def calculate_health_score(device, base_date=None):
    """
    计算设备健康度评分
    评分维度：日均成本效率、使用年限、残值比率
    """
    if base_date is None:
        base_date = date.today()
    
    days_used = calculate_days_used(device["purchase_date"], base_date)
    if days_used <= 0:
        days_used = 1  # 避免除零
    
    years_used = days_used / 365.25
    daily_cost = device["price"] / days_used
    residual_rate = get_residual_rate(years_used)
    
    # 获取行业基准
    category = device.get("category", "default")
    benchmark = INDUSTRY_BENCHMARKS.get(category, INDUSTRY_BENCHMARKS["default"])
    
    # 计算评分（100分制）
    # 成本效率分（40分）：日均成本低于基准low得满分，高于high得0分
    if daily_cost <= benchmark["low"]:
        cost_score = 40
    elif daily_cost >= benchmark["high"]:
        cost_score = 10
    else:
        cost_score = 40 - (daily_cost - benchmark["low"]) / (benchmark["high"] - benchmark["low"]) * 30
    
    # 使用年限分（30分）：在推荐寿命内得满分
    lifespan_ratio = years_used / benchmark["lifespan_years"]
    if lifespan_ratio <= 0.5:
        age_score = 30
    elif lifespan_ratio >= 1.5:
        age_score = 5
    else:
        age_score = 30 - (lifespan_ratio - 0.5) * 25
    
    # 状态分（30分）
    status = device.get("status", "active")
    if status == "active":
        status_score = 30
    elif status == "idle":
        status_score = 15
    else:
        status_score = 5
    
    total_score = cost_score + age_score + status_score
    
    return {
        "device_id": device["id"],
        "name": device["name"],
        "daily_cost": round(daily_cost, 2),
        "years_used": round(years_used, 1),
        "residual_rate": residual_rate,
        "residual_value": round(device["price"] * residual_rate, 2),
        "health_score": round(total_score, 1),
        "benchmark": benchmark
    }

def generate_health_rating(score):
    """根据评分生成健康评级"""
    if score >= 85:
        return ("🏆 史诗级", "continue", "继续用到坏为止，超值")
    elif score >= 70:
        return ("🟢 优秀", "continue", "性能良好，建议继续使用")
    elif score >= 55:
        return ("🟡 良好", "monitor", "正常使用，关注维护")
    elif score >= 40:
        return ("🟠 一般", "evaluate", "评估是否需要更换")
    else:
        return ("🔴 建议更换", "replace", "考虑出售或升级")

def generate_report(data_file, output_file=None, base_date=None):
    """生成健康诊断报告"""
    if base_date is None:
        base_date = date.today()
    
    # 读取数据
    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    equipment = data.get("equipment", [])
    
    # 分析每台设备
    results = []
    for device in equipment:
        health = calculate_health_score(device, base_date)
        rating, action, advice = generate_health_rating(health["health_score"])
        health["rating"] = rating
        health["action"] = action
        health["advice"] = advice
        results.append(health)
    
    # 排序：按健康度评分
    results.sort(key=lambda x: x["health_score"], reverse=True)
    
    # 生成报告
    report_lines = [
        "# 🔍 设备健康诊断报告",
        "",
        f"> 📅 诊断日期：{base_date}",
        f"> 📊 设备数量：{len(equipment)}台",
        "",
        "---",
        "",
        "## 📈 健康度评级标准",
        "",
        "| 评分 | 评级 | 建议 |",
        "|:---:|:---:|:---|",
        "| 85+ | 🏆 史诗级 | 继续用到坏为止 |",
        "| 70-84 | 🟢 优秀 | 建议继续使用 |",
        "| 55-69 | 🟡 良好 | 正常使用，关注维护 |",
        "| 40-54 | 🟠 一般 | 评估是否需要更换 |",
        "| < 40 | 🔴 建议更换 | 考虑出售或升级 |",
        "",
        "---",
        "",
        "## 🏆 超值资产 TOP 5",
        "",
        "| 排名 | 设备 | 健康度 | 日均成本 | 使用年限 | 建议 |",
        "|:---:|:---|:---:|:---:|:---:|:---|"
    ]
    
    for i, r in enumerate(results[:5], 1):
        report_lines.append(
            f"| {i} | {r['name']} | {r['rating']} {r['health_score']}分 | "
            f"¥{r['daily_cost']} | {r['years_used']}年 | {r['advice']} |"
        )
    
    report_lines.extend([
        "",
        "---",
        "",
        "## 📋 全部设备诊断",
        "",
        "| 设备 | 健康度 | 日均成本 | 残值 | 使用年限 | 诊断建议 |",
        "|:---|:---:|:---:|:---:|:---:|:---|"
    ])
    
    for r in results:
        report_lines.append(
            f"| {r['name']} | {r['rating']} {r['health_score']}分 | "
            f"¥{r['daily_cost']} | ¥{r['residual_value']} | {r['years_used']}年 | {r['advice']} |"
        )
    
    report_lines.extend([
        "",
        "---",
        "",
        "## 💰 理财建议摘要",
        "",
        "### 立即出售建议",
        ""
    ])
    
    # 找出建议出售的设备
    sell_candidates = [r for r in results if r["action"] == "replace"]
    if sell_candidates:
        total_recover = sum(r["residual_value"] for r in sell_candidates)
        report_lines.append(f"建议出售 **{len(sell_candidates)}** 台设备，预计回血 **¥{total_recover:,.0f}**")
        report_lines.append("")
        report_lines.append("| 设备 | 残值 | 建议 |")
        report_lines.append("|:---|---:|:---|")
        for r in sell_candidates:
            report_lines.append(f"| {r['name']} | ¥{r['residual_value']:,.0f} | {r['advice']} |")
    else:
        report_lines.append("✅ 当前设备状态良好，无需立即出售")
    
    report_lines.extend([
        "",
        "### 年度预算规划",
        "",
        f"- 📊 设备总价值：¥{sum(r['residual_value'] for r in results):,.0f}（预估残值）",
        f"- 💡 建议年度更新预算：¥{sum(r['residual_value'] for r in results) * 0.02:,.0f}（资产2%）",
        "",
        "---",
        "",
        "*🤖 由 equipment-asset-management 自动生成*",
        f"*诊断日期：{base_date}*"
    ])
    
    report = "\n".join(report_lines)
    
    # 输出
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"✅ 报告已生成：{output_file}")
    else:
        print(report)
    
    return results

def main():
    parser = argparse.ArgumentParser(description="设备健康诊断工具")
    parser.add_argument("--data", "-d", required=True, help="设备数据JSON文件路径")
    parser.add_argument("--output", "-o", help="输出报告文件路径（默认输出到控制台）")
    parser.add_argument("--date", help="基准日期（YYYY-MM-DD，默认今天）")
    
    args = parser.parse_args()
    
    base_date = None
    if args.date:
        base_date = datetime.strptime(args.date, "%Y-%m-%d").date()
    
    generate_report(args.data, args.output, base_date)

if __name__ == "__main__":
    main()
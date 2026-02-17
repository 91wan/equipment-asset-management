#!/usr/bin/env python3
"""
Equipment Asset Management - Cost Calculator
计算设备使用天数、日均成本、残值
"""

import json
import argparse
from datetime import datetime
from pathlib import Path


def calculate(purchase_date: str, price: float, today: datetime = None) -> dict:
    """
    计算设备成本指标
    
    Args:
        purchase_date: 购买日期 (YYYY-MM-DD)
        price: 购买价格
        today: 计算基准日期（默认今天）
    
    Returns:
        dict: 包含使用天数、日均成本、残值等
    """
    if today is None:
        today = datetime.now()
    
    purchase = datetime.strptime(purchase_date, "%Y-%m-%d")
    days_used = (today - purchase).days
    
    if days_used <= 0:
        days_used = 1
    
    daily_cost = price / days_used
    years = days_used / 365
    
    # 折旧率计算
    if years < 1:
        residual_rate = 0.80
        status = "new"
        status_emoji = "🟢"
    elif years < 2:
        residual_rate = 0.65
        status = "growing"
        status_emoji = "🟢"
    elif years < 3:
        residual_rate = 0.50
        status = "mature"
        status_emoji = "🟡"
    elif years < 4:
        residual_rate = 0.35
        status = "aging"
        status_emoji = "🟡"
    else:
        residual_rate = 0.20
        status = "old"
        status_emoji = "🔴"
    
    residual = price * residual_rate
    
    # 建议售价范围（出二手）
    sell_min = residual * 0.7
    sell_mid = residual * 0.85
    sell_max = residual * 1.0
    
    return {
        "purchase_date": purchase_date,
        "price": price,
        "days_used": days_used,
        "years_used": round(years, 2),
        "daily_cost": round(daily_cost, 2),
        "residual_value": round(residual, 2),
        "residual_rate": residual_rate,
        "status": status,
        "status_emoji": status_emoji,
        "sell_price_suggested": round(sell_mid, 0),
        "sell_price_range": f"{round(sell_min, 0)}-{round(sell_max, 0)}"
    }


def format_currency(amount: float, currency: str = "CNY") -> str:
    """格式化货币显示"""
    symbols = {
        "CNY": "¥",
        "USD": "$",
        "EUR": "€",
        "GBP": "£",
        "JPY": "¥",
        "KRW": "₩"
    }
    symbol = symbols.get(currency, "¥")
    return f"{symbol}{amount:,.0f}"


def print_equipment_line(item: dict, calc: dict) -> None:
    """打印单行设备信息"""
    currency = item.get("currency", "CNY")
    price_str = format_currency(item["price"], currency)
    cost_str = format_currency(calc["daily_cost"], currency)
    residual_str = format_currency(calc["residual_value"], currency)
    
    print(f"{item.get('id', '?'):<4} "
          f"{item.get('name', 'Unknown')[:25]:<25} "
          f"{item['purchase_date']:<12} "
          f"{price_str:>10} "
          f"{calc['days_used']:>5}天 "
          f"{cost_str:>8}/天 "
          f"{calc['status_emoji']} "
          f"{residual_str:>10}")


def main():
    parser = argparse.ArgumentParser(description="设备成本计算器")
    parser.add_argument("--registry", "-r", required=True,
                        help="设备注册表 JSON 文件路径")
    parser.add_argument("--date", "-d", 
                        help="计算基准日期 (YYYY-MM-DD)，默认今天")
    parser.add_argument("--output", "-o", 
                        help="输出 JSON 文件路径")
    parser.add_argument("--category", "-c",
                        help="按类别过滤")
    args = parser.parse_args()
    
    # 加载注册表
    registry_path = Path(args.registry)
    if not registry_path.exists():
        print(f"❌ 文件不存在: {registry_path}")
        return 1
    
    with open(registry_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # 基准日期
    if args.date:
        today = datetime.strptime(args.date, "%Y-%m-%d")
    else:
        today = datetime.now()
    
    print("=" * 110)
    print(f"📊 设备资产成本统计表")
    print(f"计算日期: {today.strftime('%Y-%m-%d')}")
    print("=" * 110)
    print()
    
    # 表头
    print(f"{'ID':<4} {'设备名称':<25} {'购买日期':<12} {'价格':>10} {'已用天数':>6} {'日均成本':>10} {'状态':>4} {'残值':>10}")
    print("-" * 110)
    
    # 计算并显示
    results = []
    total_price = 0
    total_residual = 0
    
    for item in data.get("equipment", []):
        # 类别过滤
        if args.category and item.get("category") != args.category:
            continue
        
        calc = calculate(item["purchase_date"], item["price"], today)
        item_with_calc = {**item, **calc}
        results.append(item_with_calc)
        
        print_equipment_line(item, calc)
        total_price += item["price"]
        total_residual += calc["residual_value"]
    
    print("=" * 110)
    
    # 合计
    print(f"{'合计':<4} {'':<25} {'':<12} "
          f"{format_currency(total_price):>10} "
          f"{'':>6} "
          f"{'':>10} "
          f"{'':>4} "
          f"{format_currency(total_residual):>10}")
    print()
    
    # 统计摘要
    print("📈 统计摘要:")
    print(f"  设备数量: {len(results)} 台")
    print(f"  总投入: {format_currency(total_price)}")
    print(f"  估计残值: {format_currency(total_residual)}")
    print(f"  累计折旧: {format_currency(total_price - total_residual)}")
    if results:
        avg_daily = sum(r["daily_cost"] for r in results) / len(results)
        print(f"  平均日均成本: {format_currency(avg_daily)}/天")
    print()
    
    # 分类统计
    categories = {}
    for r in results:
        cat = r.get("category", "other")
        if cat not in categories:
            categories[cat] = {"count": 0, "price": 0, "daily_cost_sum": 0}
        categories[cat]["count"] += 1
        categories[cat]["price"] += r["price"]
        categories[cat]["daily_cost_sum"] += r["daily_cost"]
    
    if categories:
        print("📂 分类统计:")
        cat_names = {
            "computer": "💻 电脑",
            "phone": "📱 手机",
            "tablet": "📱 平板",
            "wearable": "⌚ 可穿戴",
            "smart-home": "🏠 智能家居",
            "other": "📦 其他"
        }
        for cat, stats in sorted(categories.items()):
            avg = stats["daily_cost_sum"] / stats["count"]
            print(f"  {cat_names.get(cat, cat)}: {stats['count']}台, "
                  f"{format_currency(stats['price'])}, 日均{format_currency(avg)}")
        print()
    
    # 输出 JSON
    if args.output:
        output_data = {
            "meta": {
                "calculated_at": today.strftime("%Y-%m-%d"),
                "total_equipment": len(results),
                "total_price": total_price,
                "total_residual": total_residual
            },
            "equipment": results
        }
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        print(f"💾 结果已保存: {args.output}")
    
    return 0


if __name__ == "__main__":
    exit(main())

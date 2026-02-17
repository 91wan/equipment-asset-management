#!/usr/bin/env python3
"""
Equipment Asset Management - Report Generator (Fixed)
生成可视化报表（HTML + 图表）
"""

import json
import argparse
from pathlib import Path
from datetime import datetime


def calculate(purchase_date: str, price: float, today: datetime = None) -> dict:
    """计算设备成本指标"""
    if today is None:
        today = datetime.now()
    purchase = datetime.strptime(purchase_date, "%Y-%m-%d")
    days_used = (today - purchase).days
    if days_used <= 0:
        days_used = 1
    daily_cost = price / days_used
    years = days_used / 365
    
    if years < 1:
        residual_rate = 0.80
        status = "new"
    elif years < 2:
        residual_rate = 0.65
        status = "growing"
    elif years < 3:
        residual_rate = 0.50
        status = "mature"
    else:
        residual_rate = 0.30
        status = "old"
    
    residual_value = price * residual_rate
    
    return {
        "days_used": days_used,
        "daily_cost": daily_cost,
        "residual_value": residual_value,
        "residual_rate": residual_rate,
        "status": status
    }


def generate_html_report(data: dict, output_path: str) -> str:
    """生成 HTML 报表"""
    equipment = data.get("equipment", [])
    
    # 计算每个设备的成本和状态
    for item in equipment:
        calc = calculate(item.get("purchase_date", ""), item.get("price", 0))
        item.update(calc)
    
    # 统计数据
    total_price = sum(item.get("price", 0) for item in equipment)
    total_residual = sum(item.get("residual_value", 0) for item in equipment)
    avg_daily = sum(item.get("daily_cost", 0) for item in equipment) / len(equipment) if equipment else 0
    
    # 按类别分组
    categories = {}
    for item in equipment:
        cat = item.get("category", "other")
        if cat not in categories:
            categories[cat] = {"count": 0, "price": 0, "items": []}
        categories[cat]["count"] += 1
        categories[cat]["price"] += item.get("price", 0)
        categories[cat]["items"].append(item)
    
    # 构建设备表格行
    table_rows = []
    for item in equipment:
        status_emoji = {"new": "🟢", "growing": "🟢", "mature": "🟡", "old": "🔴"}.get(item.get("status", ""), "⚪")
        table_rows.append(f"""
        <tr>
            <td>{item.get('id', '')}</td>
            <td>{item.get('name', '')}</td>
            <td>{item.get('purchase_date', '')}</td>
            <td>¥{item.get('price', 0):,.0f}</td>
            <td>{item.get('days_used', 0)}天</td>
            <td>¥{item.get('daily_cost', 0):.1f}/天</td>
            <td>{status_emoji}</td>
            <td>¥{item.get('residual_value', 0):,.0f}</td>
        </tr>""")
    
    rows_html = "".join(table_rows)
    
    # 构建类别卡片
    category_cards = []
    cat_names = {
        "computer": "💻 电脑", "phone": "📱 手机", "tablet": "📱 平板",
        "wearable": "⌚ 可穿戴", "smart-home": "🏠 智能家居",
        "gaming": "🎮 游戏", "vehicle": "🚗 车辆", "其他": "📦 其他"
    }
    for cat, info in categories.items():
        cat_name = cat_names.get(cat, cat)
        category_cards.append(f"""
        <div class="category-card">
            <h3>{cat_name}</h3>
            <p>{info['count']}台设备</p>
            <p>投入: ¥{info['price']:,.0f}</p>
        </div>""")
    
    cards_html = "".join(category_cards)
    
    # 当前日期
    today_str = datetime.now().strftime('%Y-%m-%d')
    
    html = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>设备资产报告</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
            background: #f5f7fa; 
            padding: 40px 20px; 
        }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { 
            text-align: center; 
            margin-bottom: 40px; 
            padding: 30px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 16px;
            color: white;
        }
        .header h1 { font-size: 2.5em; margin-bottom: 10px; }
        .stats { 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
            gap: 20px; 
            margin-bottom: 40px; 
        }
        .stat-card { 
            background: white; 
            border-radius: 12px; 
            padding: 25px; 
            text-align: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .stat-value { font-size: 2em; font-weight: bold; color: #333; }
        .stat-label { color: #666; margin-top: 5px; }
        .categories { 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); 
            gap: 20px; 
            margin-bottom: 40px; 
        }
        .category-card { 
            background: white; 
            border-radius: 12px; 
            padding: 20px; 
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        table { 
            width: 100%; 
            background: white; 
            border-radius: 12px; 
            overflow: hidden;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            border-collapse: collapse;
        }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #eee; }
        th { background: #f8fafc; font-weight: 600; }
        tr:hover { background: #f8fafc; }
        .section-title { font-size: 1.5em; margin: 30px 0 20px; color: #333; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📱 设备资产报告</h1>
            <p>生成日期: """ + today_str + """</p>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-value">""" + str(len(equipment)) + """</div>
                <div class="stat-label">设备总数</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">¥""" + f"{total_price:,.0f}" + """</div>
                <div class="stat-label">总投入</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">¥""" + f"{total_residual:,.0f}" + """</div>
                <div class="stat-label">当前残值</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">¥""" + f"{avg_daily:.1f}" + """</div>
                <div class="stat-label">平均日成本</div>
            </div>
        </div>
        
        <h2 class="section-title">📊 分类统计</h2>
        <div class="categories">""" + cards_html + """</div>
        
        <h2 class="section-title">📋 设备明细</h2>
        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>设备名称</th>
                    <th>购买日期</th>
                    <th>价格</th>
                    <th>已用天数</th>
                    <th>日成本</th>
                    <th>状态</th>
                    <th>残值</th>
                </tr>
            </thead>
            <tbody>""" + rows_html + """</tbody>
        </table>
        
        <div style="text-align: center; margin-top: 40px; color: #999;">
            Generated by Equipment Asset Management
        </div>
    </div>
</body>
</html>"""
    
    # 写入文件
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    return output_path


def main():
    parser = argparse.Argument
#!/usr/bin/env python3
"""
Equipment Asset Management - Report Generator
生成可视化报表（HTML + 图表）
"""

import json
import argparse
from pathlib import Path
from datetime import datetime
from calculate_cost import calculate


def generate_html_report(data: dict, output_path: str) -> str:
    """生成 HTML 报表"""
    
    meta = data.get("meta", {})
    equipment = data.get("equipment", [])
    
    # 统计数据
    total_price = sum(item.get("price", 0) for item in equipment)
    total_residual = sum(item.get("residual_value", 0) for item in equipment)
    total_days = sum(item.get("days_used", 0) for item in equipment)
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
    
    cat_names = {
        "computer": "💻 电脑",
        "phone": "📱 手机",
        "tablet": "📱 平板",
        "wearable": "⌚ 可穿戴",
        "smart-home": "🏠 智能家居",
        "other": "📦 其他"
    }
    
    # Pie chart data (JavaScript)
    pie_labels = [cat_names.get(k, k) for k in categories.keys()]
    pie_values = [v["price"] for v in categories.values()]
    
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Equipment Asset Report</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 40px 20px;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        .header {{
            text-align: center;
            color: white;
            margin-bottom: 40px;
        }}
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }}
        .header p {{
            opacity: 0.9;
            font-size: 1.1em;
        }}
        .cards {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}
        .card {{
            background: white;
            border-radius: 16px;
            padding: 30px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
            transition: transform 0.3s;
        }}
        .card:hover {{
            transform: translateY(-5px);
        }}
        .card-icon {{
            font-size: 3em;
            margin-bottom: 15px;
        }}
        .card-value {{
            font-size: 2.2em;
            font-weight: bold;
            color: #333;
            margin-bottom: 5px;
        }}
        .card-label {{
            color: #666;
            font-size: 0.95em;
        }}
        .card-change {{
            margin-top: 10px;
            font-size: 0.9em;
        }}
        .positive {{ color: #10b981; }}
        .negative {{ color: #ef4444; }}
        .charts {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin-bottom: 40px;
        }}
        @media (max-width: 768px) {{
            .charts {{ grid-template-columns: 1fr; }}
        }}
        .chart-card {{
            background: white;
            border-radius: 16px;
            padding: 30px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        }}
        .chart-title {{
            font-size: 1.3em;
            font-weight: 600;
            margin-bottom: 20px;
            color: #333;
        }}
        .table-card {{
            background: white;
            border-radius: 16px;
            padding: 30px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
            overflow-x: auto;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.95em;
        }}
        th, td {{
            padding: 15px 12px;
            text-align: left;
            border-bottom: 1px solid #e5e7eb;
        }}
        th {{
            background: #f8fafc;
            font-weight: 600;
            color: #475569;
            text-transform: uppercase;
            font-size: 0.85em;
        }}
        tr:hover {{
            background: #f8fafc;
        }}
        .status-new {{ background: #dcfce7; color: #166534; padding: 4px 12px; border-radius: 20px; font-size: 0.85em; }}
        .status-growing {{ background: #dbeafe; color: #1e40af; padding: 4px 12px; border-radius: 20px; font-size: 0.85em; }}
        .status-mature {{ background: #fef3c7; color: #92400e; padding: 4px 12px; border-radius: 20px; font-size: 0.85em; }}
        .status-old {{ background: #fee2e2; color: #991b1b; padding: 4px 12px; border-radius: 20px; font-size: 0.85em; }}
        .footer {{
            text-align: center;
            color: rgba(255,255,255,0.7);
            margin-top: 40px;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📱 Equipment Asset Report</h1>
            <p>Generated on {meta.get('calculated_at', datetime.now().strftime('%Y-%m-%d'))}</p>
        </div>
        
        <div class="cards">
            <div class="card">
                <div class="card-icon">📦</div>
                <div class="card-value">{len(equipment)}</div>
                <div class="card-label">Total Equipment</div>
            </div>
            <div class="card">
                <div class="card-icon">💰</div>
                <div class="card-value">¥{total_price:,.0f}</div>
                <div class="card-label">Total Investment</div>
            </div>
            <div class="card">
                <div class="card-icon">📉</div>
                <div class="card-value">¥{total_residual:,.0f}</div>
                <div class="card-label">Residual Value</div>
                <div class="card-change">{(total_residual/total_price*100):.1f}% remaining</div>
            </div>
            <div class="card">
                <div class="card-icon">📊</div>
                <div class="card-value">¥{avg_daily:.1f}</div>
                <div class="card-label">Avg Daily Cost</div>
            </div>
        </div>
        
        <div class="charts">
            <div class="chart-card">
                <div class="chart-title">Cost by Category</div>
                <canvas id="pieChart"></canvas>
            </div>
            <div class="chart-card">
                <div class="chart-title">Daily Cost Comparison</div>
                <canvas id="barChart"></canvas>
            </div>
        </div>
        
        <div class="table-card">
            <h3 style="margin-bottom: 20px; color: #333;">Equipment Details</h3>
            <table>
                <thead>
                    <tr>
                        <th>Name</th>
                        <th>Category</th>
                        <th>Purchase Date</th>
                        <th>Price</th>
                        <th>Days Used</th>
                        <th>Daily Cost</th>
                        <th>Status</th>
                        <th
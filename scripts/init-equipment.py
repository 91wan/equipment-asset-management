#!/usr/bin/env python3
"""
Equipment Asset Management - Initialize Registry
创建设备注册表模板
"""

import json
import argparse
from pathlib import Path
from datetime import datetime


def create_registry_template() -> dict:
    """创建注册表模板"""
    return {
        "meta": {
            "version": "1.0",
            "created_at": datetime.now().strftime("%Y-%m-%d"),
            "updated_at": datetime.now().strftime("%Y-%m-%d"),
            "base_currency": "CNY"
        },
        "owner": {
            "name": "",
            "email": "",
            "timezone": "Asia/Shanghai"
        },
        "config": {
            "depreciation_method": "linear",
            "residual_rates": {
                "lt_1yr": 0.80,
                "lt_2yr": 0.65,
                "lt_3yr": 0.50,
                "lt_4yr": 0.35,
                "gte_4yr": 0.20
            }
        },
        "equipment": []
    }


def create_sample_equipment() -> list:
    """创建示例设备"""
    return [
        {
            "id": "001",
            "name": "MacBook Air M3",
            "brand": "Apple",
            "model": "MacBook Air 15-inch M3 2024",
            "specs": "24GB RAM, 512GB SSD",
            "color": "Midnight",
            "serial_number": "",
            "category": "computer",
            "purchase_date": "2025-03-07",
            "purchase_channel": "jingdong",
            "seller": "Apple官方旗舰店",
            "order_id": "",
            "price": 8944.00,
            "currency": "CNY",
            "payment_method": "credit_card",
            "warranty_months": 12,
            "warranty_expiry": "2026-03-07",
            "owner": "self",
            "status": "active",
            "location": "home",
            "frequency": "daily",
            "notes": "主力开发机",
            "attachments": ["receipt.jpg"]
        },
        {
            "id": "002",
            "name": "iPhone 15",
            "brand": "Apple",
            "model": "iPhone 15 256GB",
            "specs": "256GB, Blue",
            "color": "Blue",
            "serial_number": "",
            "category": "phone",
            "purchase_date": "2024-05-16",
            "purchase_channel": "jingdong",
            "seller": "Apple官方旗舰店",
            "order_id": "",
            "price": 5768.00,
            "currency": "CNY",
            "payment_method": "credit_card",
            "warranty_months": 12,
            "warranty_expiry": "2025-05-16",
            "owner": "self",
            "status": "active",
            "location": "carry",
            "frequency": "daily",
            "notes": "主力手机",
            "attachments": ["receipt.jpg"]
        }
    ]


def main():
    parser = argparse.ArgumentParser(description="创建设备注册表")
    parser.add_argument("--output", "-o", default="equipment-data.json",
                        help="输出文件路径 (默认: equipment-data.json)")
    parser.add_argument("--with-samples", "-s", action="store_true",
                        help="包含示例设备数据")
    parser.add_argument("--format", "-f", choices=["json", "markdown"], default="json",
                        help="输出格式: json 或 markdown")
    args = parser.parse_args()
    
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 创建数据
    data = create_registry_template()
    if args.with_samples:
        data["equipment"] = create_sample_equipment()
    
    if args.format == "json":
        # JSON 格式
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"✅ 注册表已创建: {output_path}")
        print()
        print("📋 使用说明:")
        print("  1. 编辑文件添加你的设备信息")
        print("  2. 运行计算: python scripts/calculate-cost.py -r equipment-data.json")
        print("  3. 生成报表: python scripts/generate-report.py -r equipment-data.json")
        
    else:
        # Markdown 格式（简化版）
        md_content = f"""# 🖥️ 设备资产登记簿

> 创建日期: {data['meta']['created_at']}
> 基础货币: {data['meta']['base_currency']}

---

## 📋 设备清单

| ID | 名称 | 购买日期 | 价格 | 货币 | 类别 | 状态 | 所有者 |
|:---|:---|:---|---:|:---|:---|:---|:---|
{"| \"-\" | \"-\" | \"-\" | - | \"-\" | \"-\" | \"-\" | \"-\" |" if not args.with_samples else ""}

---

## 📊 统计

**待添加设备后自动计算**

---

_创建自 Equipment Asset Management Skill_
"""
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(md_content)
        print(f"✅ Markdown 注册表已创建: {output_path}")
    
    return 0


if __name__ == "__main__":
    exit(main())

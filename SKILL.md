---
name: equipment-asset-management
description: Personal hardware asset tracking and cost analysis. Track device purchases, calculate daily cost amortization, estimate residual value, generate disposal recommendations, and sync to GitHub. Supports multi-currency, depreciation forecasting, and visual charts. Use when managing personal electronics inventory, analyzing hardware ROI, planning device upgrades, calculating cost-per-day metrics, or exporting asset data to GitHub.
---

# 📱 Equipment Asset Management

Track personal hardware devices with automated cost analysis, depreciation forecasting, and daily cost metrics.

## 🎯 When to Use This Skill

Use this skill for:
- Creating a hardware asset register
- Calculating daily cost amortization (投入÷使用天数)
- Estimating current device residual value
- Generation disposal/sell recommendations
- Exporting data to GitHub for backup
- Multi-currency price tracking
- Creating visual cost charts
- Family device allocation tracking

## 🚀 Quick Start

```bash
# Initialize equipment registry
python3 scripts/init-equipment.py --output ./equipment-registry.md

# Calculate costs for today's date
python3 scripts/calculate-cost.py --registry ./equipment-registry.md

# Generate full report with charts
python3 scripts/generate-report.py --registry ./equipment-registry.md --charts

# Sync to GitHub Gist
python3 scripts/github-sync.py --registry ./equipment-registry.md --gist
```

## 📋 Core Concepts

### Cost Calculation
- **Days Used**: Today - Purchase Date
- **Daily Cost**: Price ÷ Days Used
- **Residual Value**: Price × Depreciation Rate based on years

### Depreciation Rates (Default)
| Years | Rate | Status |
|:---|:---:|:---|
| <1 | 80% | 🟢 New |
| 1-2 | 65% | 🟢 Growing |
| 2-3 | 50% | 🟡 Mature |
| 3-4 | 35% | 🟡 Aging |
| 4+ | 20% | 🔴 Old |

### Multi-Currency
See [references/multi-currency.md](references/multi-currency.md) for supported currencies and exchange rates.

## 📁 File Structure

### Required Files (Create These)
```
equipment-asset-management/
├── SKILL.md (this file)
├── scripts/
│   ├── calculate-cost.py      # Core cost calculation
│   ├── generate-report.py     # Report + chart generation
│   ├── init-equipment.py      # Initialize registry
│   └── github-sync.py         # GitHub/Gist sync
├── references/
│   ├── schema.md              # Data structure
│   ├── multi-currency.md      # Currency support
│   └── examples.md            # Usage examples
└── assets/
    └── templates/
        ├── equipment-registry.md   # Master registry template
        └── equipment-template.md   # Single device template
```

### Output Files (Generated)
```
./
├── equipment-registry.md      # Your device registry
├── equipment-report.html      # Visual report with charts
└── .equipment-data.json       # Machine-readable data
```

## 📝 Data Schema

See [references/schema.md](references/schema.md) for complete schema specification.

**Minimal Required Fields:**
```yaml
equipment:
  - id: "001"
    name: "MacBook Air"
    purchase_date: "2025-03-07"
    price: 8944.01
    currency: "CNY"        # Supports CNY, USD, EUR, JPY, etc.
    category: "computer"   # computer | phone | tablet | wearable | smart-home | other
    owner: "self"          # self | spouse | child | family | work
    status: "active"       # active | idle | sold | lost
```

## 💰 Supported Currencies

See [references/multi-currency.md](references/multi-currency.md)

| Currency | Code | Example |
|:---|:---:|:---|
| Chinese Yuan | CNY | ¥8,944 |
| US Dollar | USD | $1,299 |
| Euro | EUR | €1,199 |
| Japanese Yen | JPY | ¥180,000 |
| British Pound | GBP | £1,099 |

**Auto-conversion**: Reports can show costs in preferred currency.

## 📊 Chart Generation

Requires `matplotlib` and `plotly`:

```bash
pip install matplotlib plotly pandas
```

Generate charts:
```bash
python3 scripts/generate-report.py --charts --format html
```

Chart types:
- **Pie**: Cost by category
- **Bar**: Daily cost comparison
- **Line**: Depreciation over time
- **Table**: Full equipment matrix

## 🔗 GitHub Sync

Export to GitHub Gist or Repository:

```bash
# To Gist (anonymous)
python3 scripts/github-sync.py --registry ./equipment-registry.md --gist

# To Repository (requires token)
python3 scripts/github-sync.py --registry ./equipment-registry.md \
  --repo username/repo \
  --token $GITHUB_TOKEN
```

See [references/examples.md](references/examples.md) for GitHub Actions automation.

## 💡 Disposal Recommendations

The skill automatically suggests:

| Status | Recommendation |
|:---|:---|
| 🟢 Daily cost < ¥10 | Keep using, very cost-effective |
| 🟡 Daily cost ¥10-20 | Normal, consider usage frequency |
| 🔴 Daily cost > ¥30 | High, consider selling if underutilized |
| 🔴 Device age > 4yr | Consider upgrade for performance |

## 🎁 Sell Price Estimation

```python
# Estimated resale price
min_price = residual_value * 0.7  # Quick sell
max_price = residual_value * 1.0  # Patient sell
suggested = residual_value * 0.85 # Sweet spot
```

## 📖 Examples

See [references/examples.md](references/examples.md) for:
- Full equipment registry sample
- Family device allocation
- Multi-currency scenario
- GitHub Actions workflow
- CLI batch operations

## ⚙️ Configuration

Create `.equipment-config.json`:

```json
{
  "base_currency": "CNY",
  "depreciation_method": "linear",
  "chart_style": "modern",
  "github_gist_id": "...",
  "alerts": {
    "warranty_days_before": 30,
    "high_daily_cost_threshold": 30
  }
}
```

---

_🏠 Personal finance skill - Track hardware, optimize costs_
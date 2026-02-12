# 🏎️ MaxSpeeding Meta Ads 智能日报系统

> 自动化 Meta Ads 数据采集、智能分析、异常预警的完整解决方案

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## ✨ 功能特性

| 功能 | 描述 |
|------|------|
| ⏰ **定时自动推送** | 每天 17:00 自动获取数据，报告直达飞书群 |
| 📈 **多时间维度对比** | 支持 3天/5天/7天 历史数据趋势分析 |
| 🎯 **Benchmark 智能对比** | 基于汽车配件行业标准，自动评估表现优劣 |
| 🤖 **AI 智能解读** | 自动生成数据洞察和优化建议 |
| ⚠️ **异常智能告警** | ROAS 骤降、CPC 暴涨、无转化等情况自动预警 |
| 📊 **飞书卡片通知** | 精美格式化日报，一目了然 |

---

## 📊 报告示例

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🏎️ MaxSpeeding 广告日报 - 2026/02/10
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 【今日概览】
   花费: $2,450 (+8% vs 昨日)
   点击: 3,245
   转化: 86 单 (+15% vs 昨日)
   ROAS: 3.85

📈 【ROAS 走势】
   7天: 3.15
   3天: 3.28
   1天: 3.85
   趋势判断: ✅ 持续上升，优化策略有效

🎯 【Benchmark 对比】
   ├─ ROAS: 3.85 ✅ 优于行业标准 (2.5-3.5)
   ├─ CPC: 0.68 ✅ 优于行业标准 (0.50-1.20)
   ├─ CTR: 1.2% ⚠️ 略低于行业标准 (0.8-1.5%)
   └─ CPA: 28.5 ✅ 优于行业标准 (15-35)
   📊 整体评分: 82/100

💡 【今日建议】
   1. ROAS 持续上升，当前优化策略有效，建议继续保持
   2. Turbo 产品线表现优异，建议增加 20% 预算
   3. 周末流量高峰即将到来，建议提前调整出价

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 🚀 快速开始

### 1. 安装依赖

```bash
cd maxspeeding-meta-ads-daily-report
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env` 并填写配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件，填写必要参数：

```env
# Meta API 配置
META_ACCESS_TOKEN=your_access_token_here
META_AD_ACCOUNT_ID=act_your_account_id_here

# 飞书通知配置
FEISHU_WEBHOOK_URL=https://open.feishu.cn/open-apis/bot/v2/hook/your_webhook_id

# 系统配置
DAILY_REPORT_TIME=17:00
```

### 3. 运行测试

```bash
# 测试模式（生成报告但不发送通知）
python main.py --test

# 手动运行一次（发送通知）
python main.py

# 指定日期
python main.py --date 2026-02-09
```

### 4. 启动定时任务

```bash
python scheduler.py
```

程序将持续运行，每天在指定时间自动生成和推送日报。

---

## 📁 项目结构

```
maxspeeding-meta-ads-daily-report/
├── config/                 # 配置模块
│   ├── settings.py        # 系统配置
│   └── benchmarks.py      # 行业基准
├── data/                   # 数据层
│   ├── meta_api.py        # Meta API 封装
│   └── cache.py           # 数据缓存
├── analysis/              # 分析层
│   ├── trend.py           # 趋势分析
│   ├── benchmark.py       # Benchmark 对比
│   └── anomaly.py         # 异常检测
├── report/                # 报告层
│   ├── generator.py       # 报告生成
│   └── templates.py       # 报告模板
├── notification/           # 通知层
│   └── feishu.py          # 飞书通知
├── main.py                # 主程序
├── scheduler.py           # 定时任务
├── requirements.txt       # 依赖包
└── README.md             # 本文件
```

---

## ⚙️ 配置说明

### Meta API 配置

1. 访问 [Meta Developers](https://developers.facebook.com/)
2. 创建应用并获取 Access Token
3. 获取广告账户 ID（act_xxxxxxxxx）

### 飞书通知配置

1. 在飞书群中添加自定义机器人
2. 复制 Webhook URL 到 `.env` 文件

### 异常告警阈值

```env
ALERT_ROAS_THRESHOLD=2.0          # ROAS 低于此值告警
ALERT_CPC_THRESHOLD=2.0           # CPC 高于此值告警
ALERT_NO_CONVERSION_SPEND=100.0   # 无转化时花费告警
ALERT_FREQUENCY_THRESHOLD=4.0    # 展示频次告警
```

---

## 📈 行业基准

系统内置汽车配件行业 Meta 广告基准指标：

| 指标 | 行业标准 | 优秀水平 | 告警阈值 |
|------|----------|----------|----------|
| ROAS | 2.5 - 3.5 | ≥ 4.0 | < 2.0 |
| CPC | $0.50 - $1.20 | ≤ $0.50 | > $2.00 |
| CTR | 0.8% - 1.5% | ≥ 2.0% | < 0.5% |
| CPA | $15 - $35 | ≤ $15 | > $50 |
| Frequency | 1.5 - 3.0 | 1.5 - 2.5 | > 4.0 |

---

## 🔧 开发指南

### 添加新的指标分析

编辑 `analysis/benchmark.py`，在 `BENCHMARKS` 字典中添加新指标：

```python
'BENCHMARKS': {
    'YourMetric': MetricBenchmark(
        industry_min=1.0,
        industry_max=5.0,
        excellent=5.0,
        alert_threshold=0.5,
        higher_better=True
    ),
}
```

### 自定义报告模板

编辑 `report/templates.py`，修改 `ReportTemplates` 类中的模板方法。

---

## 📝 日志

日志文件位于 `logs/app.log`，包含：

- 数据获取记录
- 分析过程日志
- 通知发送状态
- 异常信息

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

## 📄 License

MIT License - 详见 [LICENSE](LICENSE) 文件

---

## 📞 联系方式

- 项目地址: https://github.com/yourusername/maxspeeding-meta-ads-daily-report

---

> 🏎️ MaxSpeeding - 汽车配件领域的领跑者

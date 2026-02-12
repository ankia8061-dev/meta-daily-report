"""
MaxSpeeding Meta Ads 智能日报系统 - 报告模板

定义各类报告的文本模板
"""
from typing import Dict, List


class ReportTemplates:
    """报告模板类"""

    @staticmethod
    def daily_header(date: str) -> str:
        """日报头部模板"""
        return f"""━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🏎️ MaxSpeeding 广告日报 - {date}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

    @staticmethod
    def overview_section(data: Dict, comparison: Dict = None) -> str:
        """今日概览模板"""
        spend = data.get('spend', 0)
        clicks = data.get('clicks', 0)
        conversions = data.get('conversions', 0)
        roas = data.get('roas', 0)

        # 添加对比信息
        spend_text = f"${spend:,.2f}"
        if comparison:
            spend_change = comparison.get('spend', {}).get('change_percent', 0)
            trend = comparison.get('spend', {}).get('trend', '')
            spend_text += f" ({trend}{abs(spend_change):.0f}% vs 昨日)"

        conv_text = f"{conversions} 单"
        if comparison:
            conv_change = comparison.get('conversions', {}).get('change_percent', 0)
            trend = comparison.get('conversions', {}).get('trend', '')
            conv_text += f" ({trend}{abs(conv_change):.0f}% vs 昨日)"

        return f"""📊 【今日概览】
   花费: {spend_text}
   点击: {clicks:,}
   转化: {conv_text}
   ROAS: {roas:.2f}
"""

    @staticmethod
    def trend_section(trend_analysis: Dict) -> str:
        """趋势分析模板"""
        sections = []

        # ROAS 趋势
        roas_trend = trend_analysis.get('metrics_trend', {}).get('roas', {})
        if roas_trend.get('values'):
            sections.append("📈 【ROAS 走势】")
            for item in roas_trend['values']:
                sections.append(f"   {item['period']}: {item['value']:.2f}")
            trend_desc = roas_trend.get('trend', '')
            if trend_desc:
                trend_status = roas_trend.get('trend_status', '')
                status_emoji = '✅' if trend_status == 'positive' else '⚠️' if trend_status == 'negative' else '➡️'
                sections.append(f"   趋势判断: {status_emoji} {trend_desc}")

        # 花费趋势
        spend_trend = trend_analysis.get('metrics_trend', {}).get('spend', {})
        if spend_trend.get('values'):
            sections.append("\n📊 【花费走势】")
            for item in spend_trend['values']:
                sections.append(f"   {item['period']}: ${item['value']:,.2f}")

        return '\n'.join(sections) if sections else ""

    @staticmethod
    def anomaly_section(anomalies: List[str]) -> str:
        """异常告警模板"""
        if not anomalies:
            return "✅ 【异常告警】\n   未发现异常\n"

        return f"⚠️ 【异常告警】\n{anomalies}"

    @staticmethod
    def benchmark_section(evaluation: Dict, score: float) -> str:
        """Benchmark 对比模板"""
        lines = ["🎯 【Benchmark 对比】"]

        for metric, result in evaluation.items():
            value = result['value']
            benchmark = result['benchmark_range']
            rating = result['rating']
            gap = result['gap_percent']

            line = f"   ├─ {metric}: {value} {rating} "
            if result['status'] == 'excellent':
                line += f"优于行业 {abs(gap)}%"
            elif result['status'] == 'good':
                line += f"符合行业标准 ({benchmark})"
            else:
                line += f"低于行业均值 ({benchmark})"

            lines.append(line)

        lines.append(f"\n   📊 整体评分: {score}/100")

        return '\n'.join(lines)

    @staticmethod
    def insights_section(insights: List[str]) -> str:
        """智能洞察模板"""
        if not insights:
            return ""

        lines = ["💡 【今日建议】"]
        for i, insight in enumerate(insights, 1):
            lines.append(f"   {i}. {insight}")

        return '\n'.join(lines)

    @staticmethod
    def footer() -> str:
        """报告尾部模板"""
        return """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📈 MaxSpeeding Meta Ads 智能日报系统
🤖 数据自动采集 | 智能分析 | 异常预警
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

    @staticmethod
    def full_report(
        date: str,
        overview: Dict,
        trend_analysis: Dict,
        anomalies: str,
        benchmark_evaluation: Dict,
        benchmark_score: float,
        insights: List[str]
    ) -> str:
        """完整报告模板"""
        parts = [
            ReportTemplates.daily_header(date),
            ReportTemplates.overview_section(overview),
            ReportTemplates.trend_section(trend_analysis),
            "\n" + ReportTemplates.anomaly_section([]),
            "\n" + ReportTemplates.benchmark_section(benchmark_evaluation, benchmark_score),
            "\n" + ReportTemplates.insights_section(insights),
            ReportTemplates.footer()
        ]

        return ''.join(parts)


# 简化版模板（用于飞书消息）
class FeishuMessageTemplates:
    """飞书消息模板"""

    @staticmethod
    def card_message(
        title: str,
        summary: Dict,
        trend: str,
        anomalies: List[str],
        benchmark: str,
        insights: List[str]
    ) -> Dict:
        """
        生成飞书卡片消息格式

        Args:
            title: 消息标题
            summary: 数据摘要
            trend: 趋势信息
            anomalies: 异常列表
            benchmark: Benchmark 信息
            insights: 建议列表

        Returns:
            飞书消息字典
        """
        return {
            "msg_type": "interactive",
            "card": {
                "header": {
                    "title": {
                        "tag": "plain_text",
                        "content": title
                    },
                    "template": "blue"
                },
                "elements": [
                    {
                        "tag": "div",
                        "text": {
                            "tag": "lark_md",
                            "content": summary
                        }
                    },
                    {
                        "tag": "hr"
                    },
                    {
                        "tag": "div",
                        "text": {
                            "tag": "lark_md",
                            "content": trend
                        }
                    },
                    {
                        "tag": "hr"
                    },
                    {
                        "tag": "div",
                        "text": {
                            "tag": "lark_md",
                            "content": benchmark
                        }
                    },
                    {
                        "tag": "hr"
                    }
                ]
            }
        }

    @staticmethod
    def text_message(content: str) -> Dict:
        """生成飞书文本消息"""
        return {
            "msg_type": "text",
            "content": {
                "text": content
            }
        }

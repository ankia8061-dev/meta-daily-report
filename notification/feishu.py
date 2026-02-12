"""
MaxSpeeding Meta Ads 智能日报系统 - 飞书通知

发送日报到飞书群
"""
import requests
import json
from typing import Dict, Optional
from loguru import logger
from config.settings import Settings


class FeishuNotifier:
    """飞书通知器"""

    def __init__(self, settings: Settings):
        """
        初始化通知器

        Args:
            settings: 系统配置
        """
        self.settings = settings
        self.webhook_url = settings.FEISHU_WEBHOOK_URL

    def send_text_message(self, content: str) -> bool:
        """
        发送文本消息

        Args:
            content: 消息内容

        Returns:
            是否发送成功
        """
        if not self.webhook_url:
            logger.error("飞书 Webhook URL 未配置")
            return False

        message = {
            "msg_type": "text",
            "content": {
                "text": content
            }
        }

        return self._send_message(message)

    def send_card_message(self, report: Dict) -> bool:
        """
        发送卡片消息（格式化日报）

        Args:
            report: 报告数据

        Returns:
            是否发送成功
        """
        if not self.webhook_url:
            logger.error("飞书 Webhook URL 未配置")
            return False

        card = self._build_card_message(report)
        message = {
            "msg_type": "interactive",
            "card": card
        }

        return self._send_message(message)

    def _build_card_message(self, report: Dict) -> Dict:
        """
        构建卡片消息

        Args:
            report: 报告数据

        Returns:
            飞书卡片消息字典
        """
        date = report.get('date', '')
        summary = report.get('summary', {})
        analysis = report.get('analysis', {})

        # 标题
        title = f"🏎️ MaxSpeeding 广告日报 - {date}"

        # 核心指标
        content = f"""📊 **今日概览**
• 花费: ${summary.get('spend', 0):,.2f}
• 点击: {summary.get('clicks', 0):,}
• 转化: {summary.get('conversions', 0)} 单
• ROAS: {summary.get('roas', 0):.2f}
• CPC: ${summary.get('cpc', 0):.2f}
"""

        # 趋势分析
        trend_analysis = analysis.get('trend', {}).get('multi_period', {})
        if trend_analysis:
            roas_trend = trend_analysis.get('metrics_trend', {}).get('roas', {})
            if roas_trend.get('values'):
                roas_values = roas_trend['values']
                trend_emoji = '📈' if roas_trend.get('trend_status') == 'positive' else '📉' if roas_trend.get('trend_status') == 'negative' else '➡️'

                content += f"""
📈 **趋势分析**
• ROAS 3天走势: {' → '.join([str(v['value']) for v in roas_trend['values'][:3]])}
• 趋势: {trend_emoji} {roas_trend.get('trend', '稳定')}
"""

        # Benchmark
        benchmark_eval = analysis.get('benchmark', {}).get('evaluation', {})
        benchmark_score = analysis.get('benchmark', {}).get('score', 0)
        content += f"""
🎯 **行业对比**
"""

        for metric, result in list(benchmark_eval.items())[:4]:  # 最多显示4个指标
            rating = result['rating']
            content += f"• {metric}: {result['value']} {rating}\n"

        content += f"• 整体评分: {benchmark_score}/100\n"

        # 异常告警
        anomalies = analysis.get('anomalies', {}).get('list', [])
        if anomalies:
            content += f"""
⚠️ **异常告警**
"""
            for anomaly in anomalies[:3]:  # 最多显示3个异常
                emoji = '🚨' if anomaly.severity == 'critical' else '⚠️'
                content += f"{emoji} {anomaly.metric}: {anomaly.value:.2f}\n"

        # 建议
        insights = analysis.get('insights', [])
        if insights:
            content += """
💡 **今日建议**
"""
            for insight in insights[:3]:  # 最多显示3条建议
                content += f"• {insight}\n"

        # 构建卡片
        card = {
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
                        "content": content
                    }
                },
                {
                    "tag": "hr"
                },
                {
                    "tag": "note",
                    "elements": [
                        {
                            "tag": "plain_text",
                            "content": "📈 MaxSpeeding Meta Ads 智能日报系统 | 自动采集 | 智能分析 | 异常预警"
                        }
                    ]
                }
            ]
        }

        return card

    def _send_message(self, message: Dict) -> bool:
        """
        发送消息到飞书

        Args:
            message: 消息内容

        Returns:
            是否发送成功
        """
        try:
            response = requests.post(
                self.webhook_url,
                json=message,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            response.raise_for_status()

            result = response.json()
            if result.get('StatusCode') == 0 or result.get('code') == 0:
                logger.info("飞书消息发送成功")
                return True
            else:
                logger.error(f"飞书消息发送失败: {result}")
                return False

        except Exception as e:
            logger.error(f"发送飞书消息异常: {e}")
            return False

    def send_report(self, report: Dict, use_card: bool = True) -> bool:
        """
        发送报告

        Args:
            report: 报告数据
            use_card: 是否使用卡片格式

        Returns:
            是否发送成功
        """
        logger.info("开始发送飞书通知...")

        if use_card:
            return self.send_card_message(report)
        else:
            return self.send_text_message(report.get('text_report', ''))

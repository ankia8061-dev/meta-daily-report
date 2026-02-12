"""
MaxSpeeding Meta Ads 智能日报系统 - 异常检测

自动识别数据异常并生成告警
"""
from typing import Dict, List, Optional
from datetime import datetime
from loguru import logger
from statistics import mean, stdev
from config.settings import Settings


class Anomaly:
    """异常类"""

    def __init__(
        self,
        metric: str,
        value: float,
        threshold: float,
        campaign: str = 'All',
        severity: str = 'warning',
        suggestion: str = ''
    ):
        self.metric = metric
        self.value = value
        self.threshold = threshold
        self.campaign = campaign
        self.severity = severity  # warning, critical
        self.suggestion = suggestion
        self.timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'metric': self.metric,
            'value': self.value,
            'threshold': self.threshold,
            'campaign': self.campaign,
            'severity': self.severity,
            'suggestion': self.suggestion,
            'timestamp': self.timestamp
        }


class AnomalyDetector:
    """异常检测器"""

    def __init__(self, settings: Settings):
        """
        初始化检测器

        Args:
            settings: 系统配置
        """
        self.settings = settings

        # 告警阈值配置
        self.thresholds = {
            'roas_min': settings.ALERT_ROAS_THRESHOLD,
            'cpc_max': settings.ALERT_CPC_THRESHOLD,
            'no_conversion_spend': settings.ALERT_NO_CONVERSION_SPEND,
            'frequency_max': settings.ALERT_FREQUENCY_THRESHOLD
        }

    def detect_all(self, data: Dict, campaign_data: Optional[List[Dict]] = None) -> List[Anomaly]:
        """
        检测所有异常

        Args:
            data: 聚合数据
            campaign_data: 广告系列级数据（可选）

        Returns:
            异常列表
        """
        anomalies = []

        # 检测账户级别异常
        anomalies.extend(self._detect_account_anomalies(data))

        # 检测广告系列级别异常
        if campaign_data:
            anomalies.extend(self._detect_campaign_anomalies(campaign_data))

        logger.info(f"检测到 {len(anomalies)} 个异常")
        return anomalies

    def _detect_account_anomalies(self, data: Dict) -> List[Anomaly]:
        """检测账户级别异常"""
        anomalies = []

        # ROAS 过低
        roas = data.get('roas', 0)
        if roas < self.thresholds['roas_min']:
            anomalies.append(Anomaly(
                metric='ROAS',
                value=roas,
                threshold=self.thresholds['roas_min'],
                campaign='Account',
                severity='critical',
                suggestion='ROAS 低于告警阈值，建议检查广告目标设置和受众定位'
            ))

        # CPC 过高
        cpc = data.get('cpc', 0)
        if cpc > self.thresholds['cpc_max']:
            anomalies.append(Anomaly(
                metric='CPC',
                value=cpc,
                threshold=self.thresholds['cpc_max'],
                campaign='Account',
                severity='warning',
                suggestion='CPC 接近告警阈值，建议检查受众重叠情况和出价策略'
            ))

        # 无转化高花费
        spend = data.get('spend', 0)
        conversions = data.get('conversions', 0)
        if conversions == 0 and spend > self.thresholds['no_conversion_spend']:
            anomalies.append(Anomaly(
                metric='转化',
                value=0,
                threshold=f'花费>${self.thresholds["no_conversion_spend"]}但无转化',
                campaign='Account',
                severity='critical',
                suggestion=f'已花费 ${spend:.2f} 但无转化，请检查转化跟踪设置和着陆页'
            ))

        # 展示频次过高
        frequency = data.get('frequency', 0)
        if frequency > self.thresholds['frequency_max']:
            anomalies.append(Anomaly(
                metric='Frequency',
                value=frequency,
                threshold=self.thresholds['frequency_max'],
                campaign='Account',
                severity='warning',
                suggestion='展示频次过高，可能导致广告疲劳，建议扩展受众或更换创意'
            ))

        return anomalies

    def _detect_campaign_anomalies(self, campaign_data: List[Dict]) -> List[Anomaly]:
        """检测广告系列级别异常"""
        anomalies = []

        # 按广告系列聚合数据
        campaign_aggregates = self._aggregate_by_campaign(campaign_data)

        for campaign_name, data in campaign_aggregates.items():
            # 计算 ROAS
            spend = data.get('spend', 0)
            conversion_values = data.get('conversion_values', 0)
            roas = conversion_values / spend if spend > 0 else 0

            # 检测 ROAS 异常
            if roas < self.thresholds['roas_min']:
                anomalies.append(Anomaly(
                    metric='ROAS',
                    value=roas,
                    threshold=self.thresholds['roas_min'],
                    campaign=campaign_name,
                    severity='warning',
                    suggestion=f'{campaign_name} ROAS 偏低，建议检查该广告系列的受众和创意'
                ))

            # 检测无转化高花费
            conversions = data.get('conversions', 0)
            if conversions == 0 and spend > self.thresholds['no_conversion_spend'] * 0.5:
                anomalies.append(Anomaly(
                    metric='转化',
                    value=0,
                    threshold=f'花费>${self.thresholds["no_conversion_spend"] * 0.5}但无转化',
                    campaign=campaign_name,
                    severity='warning',
                    suggestion=f'{campaign_name} 已花费 ${spend:.2f} 但无转化'
                ))

        return anomalies

    def _aggregate_by_campaign(self, campaign_data: List[Dict]) -> Dict[str, Dict]:
        """按广告系列聚合数据"""
        aggregates = {}

        for item in campaign_data:
            campaign_name = item.get('campaign_name', 'Unknown')

            if campaign_name not in aggregates:
                aggregates[campaign_name] = {
                    'impressions': 0,
                    'clicks': 0,
                    'spend': 0,
                    'conversions': 0,
                    'conversion_values': 0
                }

            agg = aggregates[campaign_name]
            agg['impressions'] += int(item.get('impressions', 0) or 0)
            agg['clicks'] += int(item.get('clicks', 0) or 0)
            agg['spend'] += float(item.get('spend', 0) or 0)
            agg['conversions'] += int(item.get('conversions', 0) or 0)
            agg['conversion_values'] += float(item.get('conversion_values', 0) or 0)

        return aggregates

    def detect_statistical_anomaly(
        self,
        values: List[float],
        threshold: float = 2.0
    ) -> List[tuple]:
        """
        使用统计学方法检测异常值（基于标准差）

        Args:
            values: 数值列表
            threshold: 标准差倍数阈值

        Returns:
            异常值列表 (索引, 值)
        """
        if len(values) < 3:
            return []

        avg = mean(values)
        std_dev = stdev(values)

        anomalies = []
        for i, value in enumerate(values):
            z_score = abs((value - avg) / std_dev) if std_dev > 0 else 0
            if z_score > threshold:
                anomalies.append((i, value, z_score))

        return anomalies

    def format_anomalies(self, anomalies: List[Anomaly]) -> str:
        """
        格式化异常信息为文本

        Args:
            anomalies: 异常列表

        Returns:
            格式化的异常文本
        """
        if not anomalies:
            return "✅ 未发现异常"

        lines = ["⚠️ 发现以下异常：\n"]

        # 按严重程度排序
        anomalies_sorted = sorted(
            anomalies,
            key=lambda x: 0 if x.severity == 'critical' else 1
        )

        for anomaly in anomalies_sorted:
            emoji = '🚨' if anomaly.severity == 'critical' else '⚠️'
            lines.append(
                f"{emoji} [{anomaly.campaign}] {anomaly.metric}: {anomaly.value:.2f} "
                f"(阈值: {anomaly.threshold})"
            )
            if anomaly.suggestion:
                lines.append(f"   💡 建议: {anomaly.suggestion}")
            lines.append("")

        return '\n'.join(lines)

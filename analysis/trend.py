"""
MaxSpeeding Meta Ads 智能日报系统 - 趋势分析

支持 3天/5天/7天 多时间维度对比分析
"""
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from loguru import logger
import statistics


class TrendAnalyzer:
    """趋势分析器"""

    def __init__(self):
        """初始化分析器"""
        pass

    def compare_periods(
        self,
        current_data: Dict,
        previous_data: Dict
    ) -> Dict:
        """
        对比两个时期的数据

        Args:
            current_data: 当前时期数据
            previous_data: 前期数据

        Returns:
            对比结果，包含变化百分比
        """
        comparison = {}

        metrics = [
            'spend', 'clicks', 'impressions', 'conversions',
            'roas', 'cpc', 'ctr', 'cpa', 'conversion_rate'
        ]

        for metric in metrics:
            current = current_data.get(metric, 0)
            previous = previous_data.get(metric, 0)

            # 计算变化百分比
            if previous > 0:
                change_percent = ((current - previous) / previous) * 100
            else:
                change_percent = 0 if current == 0 else 100

            comparison[metric] = {
                'current': round(current, 2),
                'previous': round(previous, 2),
                'change_percent': round(change_percent, 2),
                'trend': self._get_trend(change_percent)
            }

        return comparison

    def _get_trend(self, change_percent: float) -> str:
        """
        获取趋势描述

        Args:
            change_percent: 变化百分比

        Returns:
            趋势符号 (↑ ↓ →)
        """
        if change_percent > 5:
            return '↑'
        elif change_percent < -5:
            return '↓'
        else:
            return '→'

    def analyze_multi_period(
        self,
        data_by_period: Dict[int, Dict]
    ) -> Dict:
        """
        分析多时间周期数据

        Args:
            data_by_period: {天数: 聚合数据}

        Returns:
            多周期分析结果
        """
        result = {
            'periods': sorted(data_by_period.keys()),
            'trend_summary': {},
            'metrics_trend': {}
        }

        # 获取所有周期的时间线数据
        periods = sorted(data_by_period.keys())

        # 对每个指标进行趋势分析
        metrics = ['roas', 'cpc', 'ctr', 'conversions', 'spend']

        for metric in metrics:
            values = []
            for days in periods:
                value = data_by_period.get(days, {}).get(metric, 0)
                values.append({
                    'period': f'{days}天',
                    'value': round(value, 2)
                })

            # 计算趋势方向
            if len(values) >= 2:
                first = values[0]['value']
                last = values[-1]['value']

                if last > first * 1.1:
                    trend = '持续上升'
                    trend_status = 'positive'
                elif last < first * 0.9:
                    trend = '持续下降'
                    trend_status = 'negative'
                else:
                    trend = '相对稳定'
                    trend_status = 'neutral'
            else:
                trend = '数据不足'
                trend_status = 'unknown'

            result['metrics_trend'][metric] = {
                'values': values,
                'trend': trend,
                'trend_status': trend_status
            }

        return result

    def calculate_moving_average(
        self,
        values: List[float],
        window: int = 3
    ) -> List[float]:
        """
        计算移动平均值

        Args:
            values: 数值列表
            window: 窗口大小

        Returns:
            移动平均值列表
        """
        if len(values) < window:
            return values

        return [
            sum(values[i:i+window]) / window
            for i in range(len(values) - window + 1)
        ]

    def detect_weekly_pattern(
        self,
        daily_data: List[Dict],
        metric: str = 'roas'
    ) -> Dict:
        """
        检测周内模式（周末 vs 工作日）

        Args:
            daily_data: 每日数据列表
            metric: 分析的指标

        Returns:
            周内模式分析结果
        """
        weekday_values = []  # 周一至周五
        weekend_values = []  # 周六、周日

        for item in daily_data:
            date_str = item.get('date_start', '')
            if not date_str:
                continue

            try:
                dt = datetime.strptime(date_str, '%Y-%m-%d')
                weekday = dt.weekday()  # 0=周一, 6=周日

                value = item.get(metric, 0)

                if weekday < 5:  # 周一至周五
                    weekday_values.append(value)
                else:  # 周六、周日
                    weekend_values.append(value)
            except ValueError:
                continue

        # 计算平均值
        weekday_avg = statistics.mean(weekday_values) if weekday_values else 0
        weekend_avg = statistics.mean(weekend_values) if weekend_values else 0

        if weekend_avg > 0:
            ratio = weekday_avg / weekend_avg
        else:
            ratio = 0

        return {
            'weekday_avg': round(weekday_avg, 2),
            'weekend_avg': round(weekend_avg, 2),
            'ratio': round(ratio, 2),
            'pattern': (
                '周末表现更好' if ratio < 0.9 else
                '工作日表现更好' if ratio > 1.1 else
                '无明显差异'
            )
        }

    def generate_trend_insight(self, analysis: Dict) -> str:
        """
        生成趋势分析文字总结

        Args:
            analysis: 趋势分析结果

        Returns:
            文字总结
        """
        insights = []

        # ROAS 趋势
        roas_trend = analysis['metrics_trend'].get('roas', {})
        if roas_trend.get('trend_status') == 'positive':
            insights.append("✅ ROAS 持续上升，优化策略有效")
        elif roas_trend.get('trend_status') == 'negative':
            insights.append("⚠️ ROAS 持续下降，需要关注")
        elif roas_trend.get('trend') == '相对稳定':
            insights.append("➡️ ROAS 保持稳定")

        # 花费趋势
        spend_trend = analysis['metrics_trend'].get('spend', {})
        if spend_trend.get('trend_status') == 'positive':
            insights.append("📈 花费持续增加")

        # 转化趋势
        conv_trend = analysis['metrics_trend'].get('conversions', {})
        if conv_trend.get('trend_status') == 'positive':
            insights.append("🎯 转化数量上升")
        elif conv_trend.get('trend_status') == 'negative':
            insights.append("📉 转化数量下降")

        return '\n'.join(insights) if insights else "暂无明显趋势"

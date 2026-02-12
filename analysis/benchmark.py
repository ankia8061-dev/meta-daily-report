"""
MaxSpeeding Meta Ads 智能日报系统 - Benchmark 对比分析

与行业标准对比，评估广告表现
"""
from typing import Dict, List, Optional
from loguru import logger
from config.benchmarks import BenchmarkManager


class BenchmarkAnalyzer:
    """Benchmark 分析器"""

    def __init__(self, custom_benchmarks: Optional[Dict] = None):
        """
        初始化分析器

        Args:
            custom_benchmarks: 自定义基准数据
        """
        self.benchmark_manager = BenchmarkManager(custom_benchmarks)

    def analyze_all_metrics(self, data: Dict) -> Dict:
        """
        分析所有指标与基准的对比

        Args:
            data: 广告数据

        Returns:
            各指标的对比结果
        """
        results = {}

        # 映射数据字段到基准指标名称
        metric_mapping = {
            'roas': 'ROAS',
            'cpc': 'CPC',
            'ctr': 'CTR',
            'cpa': 'CPA',
            'frequency': 'Frequency',
            'conversion_rate': 'ConversionRate'
        }

        for data_field, benchmark_key in metric_mapping.items():
            value = data.get(data_field, 0)
            evaluation = self.benchmark_manager.evaluate(benchmark_key, value)

            results[benchmark_key] = {
                'value': round(value, 2),
                'benchmark_range': evaluation['industry_range'],
                'excellent': evaluation['excellent'],
                'status': evaluation['status'],
                'rating': evaluation['rating'],
                'gap_percent': evaluation['gap_percent'],
                'is_alert': evaluation['is_alert']
            }

        return results

    def get_overall_score(self, evaluation: Dict) -> float:
        """
        计算整体表现评分（0-100分）

        Args:
            evaluation: 指标评估结果

        Returns:
            整体评分
        """
        if not evaluation:
            return 0

        scores = []

        for metric, result in evaluation.items():
            status = result.get('status', '')

            # 根据状态评分
            if status == 'excellent':
                score = 100
            elif status == 'good':
                score = 75
            elif status == 'warning':
                score = 50
            elif status == 'critical':
                score = 25
            else:
                score = 50

            scores.append(score)

        return round(sum(scores) / len(scores), 1) if scores else 0

    def generate_benchmark_insight(self, evaluation: Dict) -> List[str]:
        """
        生成 Benchmark 对比分析洞察

        Args:
            evaluation: 指标评估结果

        Returns:
            洞察列表
        """
        insights = []

        for metric, result in evaluation.items():
            status = result['status']
            value = result['value']
            gap = result['gap_percent']

            if status == 'excellent':
                insights.append(f"✅ {metric}: {value} 优于行业标准 {abs(gap)}%")
            elif status == 'good':
                insights.append(f"✅ {metric}: {value} 符合行业标准")
            elif status == 'warning':
                if result.get('rating') == '⚠️':
                    insights.append(f"⚠️ {metric}: {value} 略低于行业均值")
            elif status == 'critical':
                insights.append(f"🚨 {metric}: {value} 低于行业标准，需重点关注")

        return insights

    def compare_with_previous(
        self,
        current_evaluation: Dict,
        previous_evaluation: Dict
    ) -> Dict:
        """
        对比当前与上期的 Benchmark 表现

        Args:
            current_evaluation: 当前评估
            previous_evaluation: 上期评估

        Returns:
            对比结果
        """
        comparison = {}

        for metric in current_evaluation.keys():
            current_status = current_evaluation[metric]['status']
            previous_status = previous_evaluation.get(metric, {}).get('status', '')

            # 状态变化判断
            status_change = self._get_status_change(previous_status, current_status)

            comparison[metric] = {
                'current_status': current_status,
                'previous_status': previous_status,
                'change': status_change,
                'improved': status_change == 'improved',
                'declined': status_change == 'declined'
            }

        return comparison

    def _get_status_change(self, previous: str, current: str) -> str:
        """
        判断状态变化

        Args:
            previous: 上期状态
            current: 当前状态

        Returns:
            变化类型 (improved, declined, stable)
        """
        status_order = ['critical', 'warning', 'good', 'excellent']

        try:
            prev_index = status_order.index(previous) if previous else 1
            curr_index = status_order.index(current) if current else 1

            if curr_index > prev_index:
                return 'improved'
            elif curr_index < prev_index:
                return 'declined'
            else:
                return 'stable'
        except ValueError:
            return 'stable'

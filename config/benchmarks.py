"""
MaxSpeeding Meta Ads 智能日报系统 - 行业基准配置

汽车配件行业 Meta 广告基准指标
"""
from typing import Dict, Optional
from dataclasses import dataclass


@dataclass
class MetricBenchmark:
    """单个指标的基准配置"""
    industry_min: float      # 行业标准最低值
    industry_max: float      # 行业标准最高值
    excellent: float         # 优秀水平
    alert_threshold: float   # 告警阈值
    higher_better: bool = True  # 数值越高越好（如ROAS）


class BenchmarkManager:
    """行业基准管理器"""

    # 汽车配件行业基准指标（基于 Meta 2024 年数据）
    BENCHMARKS: Dict[str, MetricBenchmark] = {
        'ROAS': MetricBenchmark(
            industry_min=2.5,
            industry_max=3.5,
            excellent=4.0,
            alert_threshold=2.0,
            higher_better=True
        ),
        'CPC': MetricBenchmark(
            industry_min=0.50,
            industry_max=1.20,
            excellent=0.50,
            alert_threshold=2.00,
            higher_better=False
        ),
        'CTR': MetricBenchmark(
            industry_min=0.8,
            industry_max=1.5,
            excellent=2.0,
            alert_threshold=0.5,
            higher_better=True
        ),
        'CPA': MetricBenchmark(
            industry_min=15,
            industry_max=35,
            excellent=15,
            alert_threshold=50,
            higher_better=False
        ),
        'Frequency': MetricBenchmark(
            industry_min=1.5,
            industry_max=3.0,
            excellent=2.5,
            alert_threshold=4.0,
            higher_better=False
        ),
        'ConversionRate': MetricBenchmark(
            industry_min=2.0,
            industry_max=4.0,
            excellent=5.0,
            alert_threshold=1.0,
            higher_better=True
        ),
    }

    def __init__(self, custom_benchmarks: Optional[Dict] = None):
        """
        初始化基准管理器

        Args:
            custom_benchmarks: 自定义基准数据（可选）
        """
        self.benchmarks = self.BENCHMARKS.copy()
        if custom_benchmarks:
            self._apply_custom_benchmarks(custom_benchmarks)

    def _apply_custom_benchmarks(self, custom: Dict) -> None:
        """应用自定义基准数据"""
        for metric, values in custom.items():
            if metric in self.benchmarks and isinstance(values, dict):
                self.benchmarks[metric] = MetricBenchmark(**values)

    def get_benchmark(self, metric: str) -> Optional[MetricBenchmark]:
        """获取指定指标的基准配置"""
        return self.benchmarks.get(metric)

    def evaluate(self, metric: str, value: float) -> Dict[str, any]:
        """
        评估指标表现

        Args:
            metric: 指标名称（ROAS, CPC, CTR等）
            value: 当前值

        Returns:
            评估结果字典，包含状态、评级、差距等
        """
        benchmark = self.get_benchmark(metric)
        if not benchmark:
            return {'status': 'unknown', 'message': '未知指标'}

        # 判断表现
        if benchmark.higher_better:
            if value >= benchmark.excellent:
                status = 'excellent'
                rating = '✅'
            elif value >= benchmark.industry_min:
                status = 'good'
                rating = '✅'
            elif value < benchmark.alert_threshold:
                status = 'critical'
                rating = '🚨'
            else:
                status = 'warning'
                rating = '⚠️'
        else:
            if value <= benchmark.excellent:
                status = 'excellent'
                rating = '✅'
            elif value <= benchmark.industry_max:
                status = 'good'
                rating = '✅'
            elif value > benchmark.alert_threshold:
                status = 'critical'
                rating = '🚨'
            else:
                status = 'warning'
                rating = '⚠️'

        # 计算差距
        if status != 'unknown':
            if benchmark.higher_better:
                gap_percent = ((value - benchmark.industry_max) / benchmark.industry_max * 100)
            else:
                gap_percent = ((benchmark.industry_min - value) / benchmark.industry_min * 100)
        else:
            gap_percent = 0

        return {
            'status': status,
            'rating': rating,
            'industry_range': f"{benchmark.industry_min}-{benchmark.industry_max}",
            'excellent': benchmark.excellent,
            'gap_percent': round(gap_percent, 1),
            'is_alert': status == 'critical'
        }

    def get_all_benchmarks(self) -> Dict[str, Dict]:
        """获取所有基准配置的摘要"""
        return {
            metric: {
                'industry_range': f"{bm.industry_min}-{bm.industry_max}",
                'excellent': bm.excellent,
                'alert_threshold': bm.alert_threshold,
                'higher_better': bm.higher_better
            }
            for metric, bm in self.benchmarks.items()
        }

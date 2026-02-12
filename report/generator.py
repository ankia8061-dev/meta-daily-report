"""
MaxSpeeding Meta Ads 智能日报系统 - 报告生成器

整合所有分析模块，生成完整日报
"""
from typing import Dict, List, Optional
from datetime import date
from loguru import logger

from data.meta_api import MetaAdsClient
from data.cache import DataCache
from analysis.trend import TrendAnalyzer
from analysis.benchmark import BenchmarkAnalyzer
from analysis.anomaly import AnomalyDetector
from report.templates import ReportTemplates
from config.settings import Settings


class ReportGenerator:
    """报告生成器"""

    def __init__(self, settings: Settings):
        """
        初始化生成器

        Args:
            settings: 系统配置
        """
        self.settings = settings
        self.cache = DataCache(
            expire_seconds=settings.CACHE_EXPIRE_SECONDS
        )
        self.trend_analyzer = TrendAnalyzer()
        self.benchmark_analyzer = BenchmarkAnalyzer()
        self.anomaly_detector = AnomalyDetector(settings)

    def generate_daily_report(
        self,
        report_date: Optional[str] = None,
        use_cache: bool = True
    ) -> Dict:
        """
        生成日报

        Args:
            report_date: 报告日期 (YYYY-MM-DD)，默认今天
            use_cache: 是否使用缓存

        Returns:
            报告数据字典
        """
        if not report_date:
            report_date = date.today().strftime('%Y-%m-%d')

        logger.info(f"开始生成 {report_date} 的日报...")

        # 获取数据
        data = self._fetch_data(use_cache)

        # 分析数据
        analysis = self._analyze_data(data)

        # 生成报告
        report = self._build_report(report_date, data, analysis)

        logger.info("日报生成完成")
        return report

    def _fetch_data(self, use_cache: bool) -> Dict:
        """获取数据"""
        cache_key = f"ads_data_{date.today().strftime('%Y-%m-%d')}"

        # 尝试从缓存获取
        if use_cache:
            cached = self.cache.get(cache_key)
            if cached:
                logger.info("使用缓存数据")
                return cached

        # 初始化 API 客户端
        api_client = MetaAdsClient(self.settings)

        # 获取多周期数据
        multi_period_data = api_client.get_multi_period_data(periods=[1, 3, 7])

        # 聚合数据
        aggregated = {}
        for period_days, raw_data in multi_period_data.items():
            aggregated[period_days] = api_client.aggregate_metrics(raw_data)

        # 保存到缓存
        self.cache.set(cache_key, aggregated)

        return aggregated

    def _analyze_data(self, data: Dict) -> Dict:
        """分析数据"""
        analysis = {}

        # 当前数据
        current_data = data.get(1, {})
        previous_data = data.get(3, {})

        # 趋势分析
        comparison = self.trend_analyzer.compare_periods(
            current_data,
            previous_data
        )
        trend_analysis = self.trend_analyzer.analyze_multi_period(data)
        analysis['trend'] = {
            'comparison': comparison,
            'multi_period': trend_analysis
        }

        # Benchmark 分析
        benchmark_evaluation = self.benchmark_analyzer.analyze_all_metrics(current_data)
        benchmark_score = self.benchmark_analyzer.get_overall_score(benchmark_evaluation)
        analysis['benchmark'] = {
            'evaluation': benchmark_evaluation,
            'score': benchmark_score
        }

        # 异常检测
        anomalies = self.anomaly_detector.detect_all(current_data)
        analysis['anomalies'] = {
            'list': anomalies,
            'formatted': self.anomaly_detector.format_anomalies(anomalies)
        }

        # 生成智能建议
        insights = self._generate_insights(
            comparison,
            trend_analysis,
            benchmark_evaluation,
            anomalies
        )
        analysis['insights'] = insights

        return analysis

    def _generate_insights(
        self,
        comparison: Dict,
        trend_analysis: Dict,
        benchmark_evaluation: Dict,
        anomalies: List
    ) -> List[str]:
        """生成智能建议"""
        insights = []

        # 基于趋势的建议
        roas_trend = trend_analysis.get('metrics_trend', {}).get('roas', {})
        if roas_trend.get('trend_status') == 'positive':
            insights.append("✅ ROAS 持续上升，当前优化策略有效，建议继续保持")
        elif roas_trend.get('trend_status') == 'negative':
            insights.append("⚠️ ROAS 持续下降，建议检查受众定位和广告创意")

        # 基于对比的建议
        spend_change = comparison.get('spend', {}).get('change_percent', 0)
        conv_change = comparison.get('conversions', {}).get('change_percent', 0)

        if spend_change > 20 and conv_change < 10:
            insights.append("📉 花费增加但转化未同步增长，建议优化出价策略")

        # 基于 Benchmark 的建议
        for metric, result in benchmark_evaluation.items():
            if result['is_alert']:
                insights.append(f"🚨 {metric} 低于行业标准，需要重点关注和优化")

        # 基于异常的建议
        for anomaly in anomalies:
            if anomaly.severity == 'critical' and anomaly.suggestion:
                insights.append(f"💡 {anomaly.suggestion}")

        # 去重并限制数量
        insights = list(dict.fromkeys(insights))  # 去重
        return insights[:5]  # 最多5条建议

    def _build_report(
        self,
        report_date: str,
        data: Dict,
        analysis: Dict
    ) -> Dict:
        """构建报告"""
        current_data = data.get(1, {})
        comparison = analysis.get('trend', {}).get('comparison', {})
        trend_analysis = analysis.get('trend', {}).get('multi_period', {})
        anomalies_text = analysis.get('anomalies', {}).get('formatted', '')
        benchmark_eval = analysis.get('benchmark', {}).get('evaluation', {})
        benchmark_score = analysis.get('benchmark', {}).get('score', 0)
        insights = analysis.get('insights', [])

        # 生成文本报告
        text_report = ReportTemplates.full_report(
            report_date,
            current_data,
            trend_analysis,
            anomalies_text,
            benchmark_eval,
            benchmark_score,
            insights
        )

        return {
            'date': report_date,
            'data': current_data,
            'analysis': analysis,
            'text_report': text_report,
            'summary': {
                'spend': current_data.get('spend', 0),
                'clicks': current_data.get('clicks', 0),
                'conversions': current_data.get('conversions', 0),
                'roas': current_data.get('roas', 0),
                'cpc': current_data.get('cpc', 0),
                'benchmark_score': benchmark_score
            }
        }

    def save_report(self, report: Dict, output_path: str) -> None:
        """
        保存报告到文件

        Args:
            report: 报告数据
            output_path: 输出文件路径
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report['text_report'])

        logger.info(f"报告已保存到: {output_path}")

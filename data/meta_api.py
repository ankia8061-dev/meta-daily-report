"""
MaxSpeeding Meta Ads 智能日报系统 - Meta Ads API 封装

使用 Meta Marketing API 获取广告数据
"""
from typing import Dict, List, Optional, Any
from datetime import datetime, date, timedelta
from config.settings import Settings
from loguru import logger
import requests


class MetaAdsClient:
    """Meta Ads API 客户端"""

    def __init__(self, settings: Settings):
        """
        初始化客户端

        Args:
            settings: 系统配置
        """
        self.settings = settings
        self.base_url = f"https://graph.facebook.com/{self.settings.META_API_VERSION}"
        self.access_token = self.settings.META_ACCESS_TOKEN
        self.account_id = self.settings.META_AD_ACCOUNT_ID

    def _make_request(self, endpoint: str, params: Dict[str, Any] = None) -> Dict:
        """
        发送 API 请求

        Args:
            endpoint: API 端点
            params: 请求参数

        Returns:
            API 响应数据
        """
        url = f"{self.base_url}/{endpoint}"
        params = params or {}
        params['access_token'] = self.access_token

        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API 请求失败: {endpoint}, 错误: {e}")
            raise

    def get_campaign_insights(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        level: str = 'campaign',
        breakdowns: Optional[List[str]] = None
    ) -> List[Dict]:
        """
        获取广告系列洞察数据

        Args:
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            level: 数据层级 (account, campaign, adset, ad)
            breakdowns: 分组维度

        Returns:
            洞察数据列表
        """
        if not start_date:
            start_date = (date.today() - timedelta(days=1)).strftime('%Y-%m-%d')
        if not end_date:
            end_date = date.today().strftime('%Y-%m-%d')

        # 默认字段
        fields = [
            'campaign_id',
            'campaign_name',
            'impressions',
            'clicks',
            'spend',
            'cpc',
            'ctr',
            'cpm',
            'conversions',
            'conversion_values',
            'cost_per_conversion',
            'roas',
            'frequency',
            'actions',  # 各类转化动作详情
            'date_start',
            'date_stop'
        ]

        params = {
            'fields': ','.join(fields),
            'date_preset': 'last_7d',  # 默认获取最近7天数据，支持灵活切片
            'level': level,
            'time_increment': 1,  # 按天聚合
        }

        if breakdowns:
            params['breakdowns'] = ','.join(breakdowns)

        logger.info(f"获取 {start_date} 至 {end_date} 的广告数据...")

        endpoint = f"{self.account_id}/insights"
        data = self._make_request(endpoint, params)

        return data.get('data', [])

    def get_account_summary(self) -> Dict:
        """
        获取账户摘要信息

        Returns:
            账户信息字典
        """
        fields = [
            'id',
            'name',
            'account_status',
            'currency',
            'timezone_name',
            'amount_spent'
        ]

        params = {'fields': ','.join(fields)}
        data = self._make_request(self.account_id, params)

        return data

    def get_campaigns(self, status: str = 'ACTIVE') -> List[Dict]:
        """
        获取广告系列列表

        Args:
            status: 状态过滤 (ACTIVE, PAUSED, ARCHIVED, ALL)

        Returns:
            广告系列列表
        """
        fields = [
            'id',
            'name',
            'status',
            'objective',
            'daily_budget',
            'lifetime_budget',
            'start_time',
            'stop_time',
            'configured_status'
        ]

        params = {'fields': ','.join(fields)}

        if status != 'ALL':
            params['effective_status'] = f'[{status}]'

        endpoint = f"{self.account_id}/campaigns"
        data = self._make_request(endpoint, params)

        return data.get('data', [])

    def get_multi_period_data(
        self,
        periods: List[int] = [1, 3, 7]
    ) -> Dict[int, List[Dict]]:
        """
        获取多个时间周期的数据

        Args:
            periods: 时间周期列表（天数），默认 [1, 3, 7]

        Returns:
            {天数: 数据列表}
        """
        result = {}

        for days in periods:
            start_date = (date.today() - timedelta(days=days)).strftime('%Y-%m-%d')
            end_date = date.today().strftime('%Y-%m-%d')

            data = self.get_campaign_insights(
                start_date=start_date,
                end_date=end_date
            )

            result[days] = data
            logger.info(f"获取 {days} 天数据完成，共 {len(data)} 条记录")

        return result

    def aggregate_metrics(self, data: List[Dict]) -> Dict:
        """
        聚合指标数据

        Args:
            data: 洞察数据列表

        Returns:
            聚合后的指标字典
        """
        if not data:
            return {}

        total = {
            'impressions': 0,
            'clicks': 0,
            'spend': 0,
            'conversions': 0,
            'conversion_values': 0,
            'days': len(set(d.get('date_start') for d in data))
        }

        for item in data:
            total['impressions'] += int(item.get('impressions', 0) or 0)
            total['clicks'] += int(item.get('clicks', 0) or 0)
            total['spend'] += float(item.get('spend', 0) or 0)
            total['conversions'] += int(item.get('conversions', 0) or 0)
            total['conversion_values'] += float(item.get('conversion_values', 0) or 0)

        # 计算衍生指标
        if total['impressions'] > 0:
            total['ctr'] = total['clicks'] / total['impressions'] * 100
        else:
            total['ctr'] = 0

        if total['clicks'] > 0:
            total['cpc'] = total['spend'] / total['clicks']
        else:
            total['cpc'] = 0

        if total['conversions'] > 0:
            total['cpa'] = total['spend'] / total['conversions']
            total['conversion_rate'] = total['conversions'] / total['clicks'] * 100
        else:
            total['cpa'] = 0
            total['conversion_rate'] = 0

        if total['spend'] > 0:
            total['roas'] = total['conversion_values'] / total['spend']
        else:
            total['roas'] = 0

        # 计算平均频次
        if total['impressions'] > 0 and total['days'] > 0:
            total['frequency'] = total['impressions'] / total['days']
        else:
            total['frequency'] = 0

        return total


# 使用 facebook-business SDK 的版本（推荐）
try:
    from facebook_business.api import FacebookAdsApi
    from facebook_business.adobjects.adaccount import AdAccount
    from facebook_business.adobjects.campaign import Campaign
    from facebook_business.exceptions import FacebookRequestError

    FacebookAdsApi.init(access_token='')
except ImportError:
    logger.warning("facebook-business SDK 未安装，将使用 HTTP 方式调用 API")

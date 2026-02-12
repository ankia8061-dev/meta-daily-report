"""
MaxSpeeding Meta Ads 智能日报系统 - 配置管理

从环境变量加载系统配置
"""
import os
from dotenv import load_dotenv
from typing import Optional

# 加载环境变量
load_dotenv()


class Settings:
    """系统配置类"""

    # ==================== Meta API 配置 ====================
    META_ACCESS_TOKEN: str = os.getenv('META_ACCESS_TOKEN', '')
    META_AD_ACCOUNT_ID: str = os.getenv('META_AD_ACCOUNT_ID', '')
    META_API_VERSION: str = os.getenv('META_API_VERSION', 'v19.0')

    # ==================== 飞书通知配置 ====================
    FEISHU_WEBHOOK_URL: str = os.getenv('FEISHU_WEBHOOK_URL', '')
    FEISHU_APP_ID: Optional[str] = os.getenv('FEISHU_APP_ID', None)
    FEISHU_APP_SECRET: Optional[str] = os.getenv('FEISHU_APP_SECRET', None)

    # ==================== 系统配置 ====================
    DAILY_REPORT_TIME: str = os.getenv('DAILY_REPORT_TIME', '17:00')
    TIMEZONE: str = os.getenv('TIMEZONE', 'Asia/Shanghai')

    # ==================== 数据缓存配置 ====================
    CACHE_EXPIRE_SECONDS: int = int(os.getenv('CACHE_EXPIRE_SECONDS', '86400'))

    # ==================== Benchmark 配置 ====================
    USE_CUSTOM_BENCHMARK: bool = os.getenv('USE_CUSTOM_BENCHMARK', 'false').lower() == 'true'
    CUSTOM_BENCHMARK_FILE_PATH: Optional[str] = os.getenv('CUSTOM_BENCHMARK_FILE_PATH', None)

    # ==================== 异常告警阈值配置 ====================
    ALERT_ROAS_THRESHOLD: float = float(os.getenv('ALERT_ROAS_THRESHOLD', '2.0'))
    ALERT_CPC_THRESHOLD: float = float(os.getenv('ALERT_CPC_THRESHOLD', '2.0'))
    ALERT_NO_CONVERSION_SPEND: float = float(os.getenv('ALERT_NO_CONVERSION_SPEND', '100.0'))
    ALERT_FREQUENCY_THRESHOLD: float = float(os.getenv('ALERT_FREQUENCY_THRESHOLD', '4.0'))

    # ==================== AI 智能解读配置 ====================
    OPENAI_API_KEY: Optional[str] = os.getenv('OPENAI_API_KEY', None)
    OPENAI_MODEL: str = os.getenv('OPENAI_MODEL', 'gpt-4')

    # ==================== 日志配置 ====================
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE: str = os.getenv('LOG_FILE', 'logs/app.log')

    @classmethod
    def validate(cls) -> tuple[bool, list[str]]:
        """
        验证配置是否完整

        Returns:
            (是否有效, 缺失的配置项列表)
        """
        missing = []

        if not cls.META_ACCESS_TOKEN:
            missing.append('META_ACCESS_TOKEN')
        if not cls.META_AD_ACCOUNT_ID:
            missing.append('META_AD_ACCOUNT_ID')
        if not cls.FEISHU_WEBHOOK_URL:
            missing.append('FEISHU_WEBHOOK_URL')

        return len(missing) == 0, missing

    def __repr__(self) -> str:
        """配置信息摘要（隐藏敏感信息）"""
        return (
            f"Settings(\n"
            f"  META_AD_ACCOUNT_ID={self.META_AD_ACCOUNT_ID},\n"
            f"  DAILY_REPORT_TIME={self.DAILY_REPORT_TIME},\n"
            f"  TIMEZONE={self.TIMEZONE},\n"
            f"  LOG_LEVEL={self.LOG_LEVEL}\n"
            f")"
        )

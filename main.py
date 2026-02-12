"""
MaxSpeeding Meta Ads 智能日报系统 - 主程序

自动获取 Meta Ads 数据，生成智能日报，推送到飞书
"""
import sys
import os
from datetime import date
from pathlib import Path
from loguru import logger

from config.settings import Settings
from data.meta_api import MetaAdsClient
from report.generator import ReportGenerator
from notification.feishu import FeishuNotifier


# 配置日志
log_path = Path("logs")
log_path.mkdir(parents=True, exist_ok=True)
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
    level="INFO"
)
logger.add(
    log_path / "app.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}",
    rotation="1 day",
    retention="30 days",
    level="DEBUG"
)


def validate_settings(settings: Settings) -> bool:
    """
    验证配置

    Args:
        settings: 系统配置

    Returns:
        配置是否有效
    """
    is_valid, missing = settings.validate()

    if not is_valid:
        logger.error("配置验证失败，缺少以下配置项:")
        for item in missing:
            logger.error(f"  - {item}")
        logger.error("请在 .env 文件中配置这些参数")

    return is_valid


def generate_and_send_report(
    report_date: str = None,
    send_notification: bool = True
) -> dict:
    """
    生成并发送日报

    Args:
        report_date: 报告日期 (YYYY-MM-DD)
        send_notification: 是否发送通知

    Returns:
        报告数据字典
    """
    # 加载配置
    settings = Settings()

    # 验证配置
    if not validate_settings(settings):
        return None

    # 生成报告
    generator = ReportGenerator(settings)
    report = generator.generate_daily_report(report_date, use_cache=True)

    if not report:
        logger.error("报告生成失败")
        return None

    logger.info("报告生成成功")
    logger.info(report['summary'])

    # 保存报告到文件
    output_dir = Path("reports")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / f"daily_report_{report['date']}.txt"
    generator.save_report(report, str(output_path))

    # 发送通知
    if send_notification:
        notifier = FeishuNotifier(settings)
        success = notifier.send_report(report, use_card=True)

        if success:
            logger.info("飞书通知发送成功")
        else:
            logger.error("飞书通知发送失败")

    return report


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(
        description='MaxSpeeding Meta Ads 智能日报系统'
    )
    parser.add_argument(
        '--date',
        type=str,
        help='报告日期 (YYYY-MM-DD)，默认今天'
    )
    parser.add_argument(
        '--no-notify',
        action='store_true',
        help='不发送通知'
    )
    parser.add_argument(
        '--test',
        action='store_true',
        help='测试模式，不发送通知，输出到控制台'
    )

    args = parser.parse_args()

    logger.info("=" * 50)
    logger.info("MaxSpeeding Meta Ads 智能日报系统启动")
    logger.info("=" * 50)

    report = generate_and_send_report(
        report_date=args.date,
        send_notification=not args.no_notify and not args.test
    )

    if report:
        logger.info("=" * 50)
        logger.info("任务完成")
        logger.info("=" * 50)

        if args.test:
            print("\n" + "=" * 50)
            print("报告内容:")
            print("=" * 50)
            print(report['text_report'])
    else:
        logger.error("任务失败")
        sys.exit(1)


if __name__ == '__main__':
    main()

"""
MaxSpeeding Meta Ads 智能日报系统 - 定时任务调度器

每天自动生成和推送日报
"""
import schedule
import time
from datetime import datetime
from loguru import logger

from config.settings import Settings
from main import generate_and_send_report


class DailyReportScheduler:
    """日报定时任务调度器"""

    def __init__(self, settings: Settings):
        """
        初始化调度器

        Args:
            settings: 系统配置
        """
        self.settings = settings
        self.report_time = settings.DAILY_REPORT_TIME
        self.timezone = settings.TIMEZONE

    def run_daily_report(self):
        """执行日报生成任务"""
        try:
            logger.info(f"开始执行定时日报任务: {datetime.now()}")
            report = generate_and_send_report(send_notification=True)

            if report:
                logger.info("定时日报任务执行成功")
            else:
                logger.error("定时日报任务执行失败")

        except Exception as e:
            logger.exception(f"定时日报任务异常: {e}")

    def start(self):
        """启动调度器"""
        logger.info("=" * 50)
        logger.info("MaxSpeeding 日报调度器启动")
        logger.info(f"推送时间: 每天 {self.report_time} ({self.timezone})")
        logger.info("=" * 50)

        # 设置定时任务
        schedule.every().day.at(self.report_time).do(self.run_daily_report)

        # 启动时立即执行一次（可选）
        # self.run_daily_report()

        logger.info("调度器已启动，等待定时任务...")

        # 持续运行
        while True:
            schedule.run_pending()
            time.sleep(60)  # 每分钟检查一次


def main():
    """主函数"""
    import sys

    try:
        settings = Settings()
        scheduler = DailyReportScheduler(settings)
        scheduler.start()

    except KeyboardInterrupt:
        logger.info("\n收到中断信号，调度器停止")
        sys.exit(0)

    except Exception as e:
        logger.exception(f"调度器异常: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()

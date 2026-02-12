"""
MaxSpeeding Meta Ads 智能日报系统 - 数据缓存

避免重复调用 API，提高响应速度
"""
import json
import time
from typing import Any, Optional, Dict
from pathlib import Path
from loguru import logger


class DataCache:
    """简单文件缓存系统"""

    def __init__(self, cache_dir: str = '.cache', expire_seconds: int = 86400):
        """
        初始化缓存

        Args:
            cache_dir: 缓存目录
            expire_seconds: 过期时间（秒）
        """
        self.cache_dir = Path(cache_dir)
        self.expire_seconds = expire_seconds
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _get_cache_key(self, key: str) -> Path:
        """获取缓存文件路径"""
        safe_key = key.replace('/', '_').replace(':', '-')
        return self.cache_dir / f"{safe_key}.json"

    def get(self, key: str) -> Optional[Any]:
        """
        获取缓存

        Args:
            key: 缓存键

        Returns:
            缓存数据，不存在或过期返回 None
        """
        cache_file = self._get_cache_key(key)

        if not cache_file.exists():
            return None

        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # 检查是否过期
            if time.time() - data['timestamp'] > self.expire_seconds:
                logger.debug(f"缓存已过期: {key}")
                cache_file.unlink()
                return None

            logger.debug(f"缓存命中: {key}")
            return data['value']

        except Exception as e:
            logger.error(f"读取缓存失败: {key}, 错误: {e}")
            return None

    def set(self, key: str, value: Any) -> None:
        """
        设置缓存

        Args:
            key: 缓存键
            value: 缓存值
        """
        cache_file = self._get_cache_key(key)

        data = {
            'timestamp': time.time(),
            'value': value
        }

        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.debug(f"缓存已保存: {key}")
        except Exception as e:
            logger.error(f"保存缓存失败: {key}, 错误: {e}")

    def delete(self, key: str) -> bool:
        """
        删除缓存

        Args:
            key: 缓存键

        Returns:
            是否删除成功
        """
        cache_file = self._get_cache_key(key)

        if cache_file.exists():
            cache_file.unlink()
            logger.debug(f"缓存已删除: {key}")
            return True

        return False

    def clear(self) -> None:
        """清空所有缓存"""
        for file in self.cache_dir.glob('*.json'):
            file.unlink()
        logger.info("所有缓存已清空")

    def get_stats(self) -> Dict:
        """获取缓存统计信息"""
        files = list(self.cache_dir.glob('*.json'))
        total_size = sum(f.stat().st_size for f in files)

        return {
            'count': len(files),
            'total_size': total_size,
            'total_size_mb': round(total_size / 1024 / 1024, 2)
        }

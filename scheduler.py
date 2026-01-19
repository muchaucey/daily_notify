"""
定时检查PB值的脚本
可使用schedule库定时执行
"""

import schedule
import time
from pb_monitor import PBMonitor


def job():
    """定时执行的任务"""
    monitor = PBMonitor()
    monitor.check_and_notify()


def start_scheduler(check_interval=5):
    """
    启动定时器
    
    参数:
        check_interval: 检查间隔（分钟），默认5分钟
    """
    print(f"定时器已启动，每{check_interval}分钟检查一次")
    
    # 设置定时任务（每N分钟执行一次）
    schedule.every(check_interval).minutes.do(job)
    
    # 程序启动时立即执行一次
    job()
    
    # 保持运行
    while True:
        try:
            schedule.run_pending()
            time.sleep(60)  # 每60秒检查一次是否需要执行任务
        except KeyboardInterrupt:
            print("\n定时器已停止")
            break
        except Exception as e:
            print(f"错误: {e}")
            time.sleep(60)


if __name__ == '__main__':
    # 设置每5分钟检查一次
    start_scheduler(check_interval=5)

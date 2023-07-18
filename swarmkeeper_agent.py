from apscheduler.schedulers.background import BlockingScheduler
import logging
import atexit

from apscheduler.triggers.cron import CronTrigger

from container_service import ContainerService
from config import config


# Initiate logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(threadName)s - %(levelname)-4s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.StreamHandler()]
)

scheduler = BlockingScheduler()


def close_scheduler():
    scheduler.shutdown()


if __name__ == '__main__':
    run_interval: list = config.get("DEFAULT", "run_interval").split(" ")
    container_service: ContainerService = ContainerService()
    scheduler = BlockingScheduler()
    scheduler.add_job(container_service.execute, trigger=CronTrigger(second=run_interval[0], minute=run_interval[1], hour=run_interval[2], day=run_interval[3], month=run_interval[4], year=run_interval[5]))
    scheduler.start()
    atexit.register(close_scheduler)

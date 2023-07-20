from apscheduler.schedulers.background import BlockingScheduler
import logging
import atexit

from apscheduler.triggers.cron import CronTrigger

from docker_service.container_service import ContainerService
from config.config import config


# Initiate logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(threadName)s - %(levelname)-4s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.StreamHandler()]
)
logging.getLogger('apscheduler.executors.default').propagate = False

scheduler = BlockingScheduler()


def close_scheduler():
    scheduler.shutdown()


if __name__ == '__main__':
    report_schedule: list = config.get("DEFAULT", "report_cron_schedule").split(" ")
    cleanup_schedule: list = config.get("DEFAULT", "cleanup_cron_schedule").split(" ")
    container_service: ContainerService = ContainerService()
    scheduler = BlockingScheduler()
    scheduler.add_job(func=container_service.report_container_status,
                      name="Report job",
                      trigger=CronTrigger(second=report_schedule[0], minute=report_schedule[1], hour=report_schedule[2], day=report_schedule[3], month=report_schedule[4], year=report_schedule[5]))
    scheduler.add_job(func=container_service.cleanup,
                      name="Cleanup job",
                      trigger=CronTrigger(second=cleanup_schedule[0], minute=cleanup_schedule[1], hour=cleanup_schedule[2], day=cleanup_schedule[3], month=cleanup_schedule[4], year=cleanup_schedule[5]))
    scheduler.start()
    atexit.register(close_scheduler)

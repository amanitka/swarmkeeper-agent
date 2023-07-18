import logging
import requests
from requests import Response

from config import config
from docker_api import DockerApi


class ContainerService:

    def __init__(self):
        self.__docker_api: DockerApi = DockerApi(config.get("DEFAULT", "docker_base_url"))
        self.__swarmkeeper_url: str = config.get("DEFAULT", "swarmkeeper_url")
        self.__container_cleanup: bool = config.getboolean("DEFAULT", "container_cleanup")
        self.__image_cleanup: bool = config.getboolean("DEFAULT", "image_cleanup")

    def __remove_stopped_container(self):
        logging.info("Cleanup stopped containers")
        self.__docker_api.remove_stopped_container()

    def __remove_unused_image(self):
        logging.info("Cleanup unused images")
        self.__docker_api.remove_unused_image()

    def __report_container_status(self):
        logging.info("Report container status to swarmkeeper")
        container_list: list[dict] = self.__docker_api.get_running_container_list()
        try:
            response: Response = requests.post(f"{self.__swarmkeeper_url}/api/status/container", json=container_list)
            if response.status_code == 200:
                logging.info(f"Container status was sent to swarmkeeper. Response: {response.json()}")
            else:
                logging.error(f"Unable to send container status to swarmkeeper. Http status: {response.status_code}, response: {response.json()}")
        except Exception as e:
            logging.error(f"Unable to send container status to swarmkeeper. Error: {e}")

    def execute(self):
        self.__remove_stopped_container()
        self.__remove_unused_image()
        self.__report_container_status()

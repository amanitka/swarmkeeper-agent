import logging
import requests
from requests import Response

from config.config import config
from docker_service.docker_api import DockerApi


class ContainerService:

    def __init__(self):
        self.__docker_api: DockerApi = DockerApi()
        self.__swarmkeeper_url: str = config.get("DEFAULT", "swarmkeeper_url")
        self.__container_cleanup: bool = config.getboolean("DEFAULT", "container_cleanup")
        self.__image_cleanup: bool = config.getboolean("DEFAULT", "image_cleanup")

    def __remove_stopped_container(self):
        logging.info("Cleanup stopped containers")
        self.__docker_api.remove_stopped_container()

    def __remove_unused_image(self):
        logging.info("Cleanup unused images")
        self.__docker_api.remove_unused_image()

    def cleanup(self):
        if self.__container_cleanup:
            self.__remove_stopped_container()
        if self.__image_cleanup:
            self.__remove_unused_image()

    def report_container_status(self):
        logging.info("Report docker_service status to swarmkeeper")
        container_list: list[dict] = self.__docker_api.get_running_container_list()
        try:
            response: Response = requests.post(f"{self.__swarmkeeper_url}/api/status/container", json=container_list)
            if response.status_code == 200:
                logging.info(f"Container status was sent to swarmkeeper. Response: {response.json()}")
            else:
                logging.error(f"Unable to send docker_service status to swarmkeeper. Http status: {response.status_code}, text: {response.text}")
        except Exception as e:
            logging.error(f"Unable to send docker_service status to swarmkeeper. Error: {e}")

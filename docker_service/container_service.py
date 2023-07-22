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

    def __report_service_container_status(self, service_container_list: list[dict]):
        logging.info("Report service container status to swarmkeeper")
        try:
            response: Response = requests.post(f"{self.__swarmkeeper_url}/api/status/container", json=service_container_list)
            if response.status_code == 200:
                logging.info(f"Container status was sent to swarmkeeper. Response: {response.json()}")
            else:
                logging.error(f"Unable to send docker_service status to swarmkeeper. Http status: {response.status_code}, text: {response.text}")
        except Exception as e:
            logging.error(f"Unable to send docker_service status to swarmkeeper. Error: {e}")

    @staticmethod
    def __can_process_container(container: dict) -> bool:
        if container["process_flag"] == "N":
            logging.info(f"Skip processing of container {container['name']}, because it was disabled label")
            return False
        else:
            return True

    def __process_container(self, container: dict):
        if self.__can_process_container(container):
            image_digest_repository: str = self.__docker_api.get_image_digest_registry(container["image_tag"])
            if image_digest_repository in container["image_digest_list"]:
                logging.info(f"Container {container['name']} is using up to date image")
            else:
                logging.info(f"Container {container['name']} is using outdated image and should be updated!")

    def __process_container_list(self, non_service_container_list: list[dict]):
        logging.info("Process containers which doesn't belong to any service")
        for container in non_service_container_list:
            self.__process_container(container)

    def cleanup(self):
        if self.__container_cleanup:
            self.__remove_stopped_container()
        if self.__image_cleanup:
            self.__remove_unused_image()

    def process_running_container(self):
        service_container_list, container_list = self.__docker_api.get_running_container_list()
        self.__report_service_container_status(service_container_list)
        self.__process_container_list(container_list)

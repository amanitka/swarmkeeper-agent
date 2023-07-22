import logging
import docker
from docker.models.containers import Container

from config.config import config


class DockerApi:

    def __init__(self):
        docker_base_url: str = config.get("DEFAULT", "docker_base_url")
        logging.info(f"Initialize docker_service client with base url: {docker_base_url}")
        self.__client = docker.DockerClient(base_url=docker_base_url)

    @staticmethod
    def __get_swarmkeeper_flag_from_label(container: Container) -> str:
        if "swarmkeeper.enable" in container.labels:
            if container.labels["swarmkeeper.enable"] == "true":
                return "Y"
            else:
                return "N"
        else:
            return "X"

    @staticmethod
    def __get_image_digest_for_container(image_id: str, image_dict: dict) -> list[str]:
        image_repo_digest: list[str] = []
        if image_id in image_dict:
            for image_digest in image_dict[image_id]["image_digest_list"]:
                image_repo_digest.append(image_digest[image_digest.find("sha256:"):])
        return image_repo_digest

    def remove_stopped_container(self):
        result = self.__client.containers.prune()
        if result["ContainersDeleted"] is not None:
            logging.info(f"Removed containers: {result['ContainersDeleted']}, reclaimed space: {result['SpaceReclaimed']}")

    def remove_unused_image(self):
        result = self.__client.images.prune()
        if result["ImagesDeleted"] is not None:
            logging.info(f"Removed images: {result['ImagesDeleted']}, reclaimed space: {result['SpaceReclaimed']}")

    def get_image_digest_registry(self, image_tag: str) -> str:
        image_registry_data = self.__client.images.get_registry_data(image_tag)
        return image_registry_data.id

    def get_image_dict(self) -> dict:
        image_dict: dict = {}
        image_list = self.__client.images.list()
        for image in image_list:
            image_dict[image.id] = {"image_tag_list": image.tags,
                                    "image_digest_list": image.attrs.get("RepoDigests")}
        return image_dict

    def get_running_container_list(self) -> tuple[list[dict], list[dict]]:
        logging.info("Retrieve running docker container list")
        image_dict: dict = self.get_image_dict()
        service_container_list: list[dict] = []
        container_list: list[dict] = []
        for container in self.__client.containers.list():
            if "com.docker.swarm.service.id" in container.labels:
                service_container_list.append({"id": container.id,
                                               "name": container.name,
                                               "image_digest_list": self.__get_image_digest_for_container(container.image.id, image_dict),
                                               "stack_namespace": container.labels["com.docker.stack.namespace"] if "com.docker.stack.namespace" in container.labels else "",
                                               "id_service": container.labels["com.docker.swarm.service.id"] if "com.docker.swarm.service.id" in container.labels else "",
                                               "service_name": container.labels["com.docker.swarm.service.name"] if "com.docker.swarm.service.name" in container.labels else ""})
            else:
                container_list.append({"id": container.id,
                                       "name": container.name,
                                       "image_tag": container.image.tags[0] if container.image.tags else "",
                                       "image_digest_list": self.__get_image_digest_for_container(container.image.id, image_dict),
                                       "process_flag": self.__get_swarmkeeper_flag_from_label(container)})
        return service_container_list, container_list

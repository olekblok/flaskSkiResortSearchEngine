import logging
import random
import requests


class Utilities:
    @staticmethod
    def load_user_agents(file_path='./ua_list.txt') -> list:
        """
        Load user agents from a file.
        :param file_path: file to user agent files
        :return: list of user agents
        """
        try:
            with open(file_path, 'r') as f:
                return f.read().splitlines()
        except Exception as e:
            logging.exception('Failed to load user agents:', exc_info=e)
            exit(0)

    @staticmethod
    def get_page(page_url: str):
        """
        Send a GET request to the page using a random user agent.
        :param page_url: page url to request
        :return: page content
        """
        user_agents = Utilities.load_user_agents()
        user_agent = random.choice(user_agents)
        headers = {'User-Agent': user_agent}
        try:
            page = requests.get(page_url, headers=headers)
            page.raise_for_status()
            logging.info("Successful request for %s", page_url)
            return page.content
        except requests.RequestException as e:
            logging.exception("Connection error: %s - URL: %s", e, page_url)
            return None

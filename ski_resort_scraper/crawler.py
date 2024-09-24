from bs4 import BeautifulSoup
from ski_resort_scraper.utilities import Utilities


class SkiResortCrawler:
    def __init__(self, page_url_list: list):
        self.page_url_list = page_url_list

    def crawl(self) -> list:
        """
        Crawls the website and finds the links to resorts
        :return: the list of links to resorts
        """
        links = []
        for url in self.page_url_list:
            page = Utilities.get_page(url)
            soup = BeautifulSoup(page, 'html.parser')
            page_scroll = soup.find('div', id='resortList')
            links_html = page_scroll.find_all("a",  class_="h3")

            for link in links_html:
                links.append(link['href'])

        return links

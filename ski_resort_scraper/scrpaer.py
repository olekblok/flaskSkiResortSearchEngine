from bs4 import BeautifulSoup
from geolocation import GeoLocator
from utilities import Utilities


class SkiResortScraper:
    def __init__(self):
        self.geo_locator = GeoLocator()

    @staticmethod
    def safe_find_text(page_content: BeautifulSoup, tag: str, class_name=None, id_name=None, itemprop=None, title=None,
                       default=None) -> str:
        """
        A helper function to safely extract text from a BeautifulSoup object.
        :param page_content: The BeautifulSoup object to extract from
        :param tag: The tag to find (e.g., 'span', 'div')
        :param class_name: The class name of the tag
        :param id_name: The id name of the tag
        :param itemprop: The itemprop attribute of the tag
        :param title: The title attribute of the tag
        :param default: Default value to return if extraction fails
        :return: Extracted text or default value if not found
        """
        try:
            if class_name:
                return page_content.find(tag, class_=class_name).text.strip()
            if id_name:
                return page_content.find(tag, id=id_name).text.strip()
            if itemprop:
                return page_content.find(tag, itemprop=itemprop).text.strip()
            if title:
                return page_content.find(tag, title=title).text.strip()
            else:
                return page_content.find(tag).text.strip()
        except Exception as e:
            print(f"Error extracting {tag} with class '{class_name}', id '{id_name}', itemprop '{itemprop}', or title '"
                  f"{title}': {e}")
            return default

    @staticmethod
    def safe_find_content(page_content: BeautifulSoup, tag: str, class_name=None, default=None) -> BeautifulSoup:
        """
        A helper function to safely extract page content from a BeautifulSoup object
        :param page_content:
        :param tag:
        :param class_name:
        :param default:
        :return:
        """
        try:
            if class_name:
                return page_content.find(tag, class_=class_name)
            else:
                return page_content.find(tag)
        except Exception as e:
            print(f"Error extracting {tag} with class '{class_name}': {e}")
            return default

    def get_ski_resort_data(self, page_content: BeautifulSoup) -> dict:
        """
        Get ski resort details from the HTML page.
        :param page_content: The HTML page to extract the elements from
        :return: A dictionary containing the ski resort data
        """
        # Use helper functions to safely extract data
        ski_resort_name = self.safe_find_text(page_content, 'span', class_name='fn')
        city_content = self.safe_find_content(page_content, 'div', 'subnavi-header')
        city_content = self.safe_find_content(city_content, 'span', 'hidden-small')
        city = self.safe_find_text(city_content, 'a')
        country = self.safe_find_text(page_content, 'li', class_name='with-drop active', itemprop='name')
        rating = self.safe_find_text(page_content, 'div', class_name="report-rating")
        elevation_info_content = self.safe_find_content(page_content, 'div', 'detail-links')
        elevation_info = self.safe_find_text(elevation_info_content, 'div', class_name='description')

        # Slopes data
        slopes = self.safe_find_content(page_content, 'a', class_name='detail-links link-img shaded zero-pad-bottom '
                                                                      'chart')
        total_slopes = self.safe_find_text(slopes, 'strong', default=0)
        blue_slopes = self.safe_find_text(slopes, 'td', id_name='selBeginner', default=0)
        red_slopes = self.safe_find_text(slopes, 'td', id_name='selInter', default=0)
        black_slopes = self.safe_find_text(slopes, 'td', id_name='selAdv', default=0)

        # Lifts data
        lifts = self.safe_find_content(page_content, 'a', class_name='shaded detail-links link-img no-pad-bottom')
        total_lifts = self.safe_find_text(lifts, 'strong', default=0)
        total_big_gondolas = self.safe_find_text(lifts, 'div', title='Aerial tramway/reversible ropeway', default=0)
        total_gondolas = self.safe_find_text(lifts, 'div', title='Circulating ropeway/gondola lift', default=0)
        total_chairlifts = self.safe_find_text(lifts, 'div', title='Chairlift', default=0)
        total_t_bars = self.safe_find_text(lifts, 'div', title='T-bar lift/platter/button lift', default=0)
        total_moving_carpets = self.safe_find_text(lifts, 'div', title='People mover/Moving Carpet', default=0)
        latitude, longitude = self.geo_locator.get_coordinates(city, country)

        # Return all extracted data as a dictionary
        return {
            'ski_resort_name': ski_resort_name,
            'city': city,
            'country': country,
            'longitude': longitude,
            'latitude': latitude,
            'rating': rating,
            'elevation_info': elevation_info,
            'total_slopes': total_slopes,
            'blue_slopes': blue_slopes,
            'red_slopes': red_slopes,
            'black_slopes': black_slopes,
            'total_lifts': total_lifts,
            'total_big_gondolas': total_big_gondolas,
            'total_gondolas': total_gondolas,
            'total_chairlifts': total_chairlifts,
            'total_t_bars': total_t_bars,
            'total_moving_carpets': total_moving_carpets
        }

    def get_ski_resort_urls(self, page_url_list: list) -> list:
        """
        Find and return a list of ski resort data.
        :param page_url_list: List of page URLs
        :return: List of dictionaries containing ski resort data
        """
        data = []
        count = 0
        for page_url in page_url_list:
            count += 1
            print('page number' + str(count))
            page_content = Utilities.get_page(page_url)
            if page_content:
                soup = BeautifulSoup(page_content, 'html.parser')
                data.append(self.get_ski_resort_data(soup))

        return data

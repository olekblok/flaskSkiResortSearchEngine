import pandas as pd
from ski_resort_scraper.scrpaer import SkiResortScraper
from ski_resort_scraper.crawler import SkiResortCrawler
from ski_resort_scraper.procesor import DataProcessor


def main():
    ITER_PAGE_START = 2
    ITER_PAGE_END = 22
    page_url_list = [f'https://www.skiresort.info/ski-resorts/europe/page/{i}/' for i in
                     range(ITER_PAGE_START, ITER_PAGE_END)]
    page_url_list.append('https://www.skiresort.info/ski-resorts/europe')

    c = SkiResortCrawler(page_url_list)
    links = c.crawl()

    scraper = SkiResortScraper()
    data = scraper.get_ski_resort_urls(links)

    df = pd.DataFrame(data)
    d = DataProcessor()

    # Create DataFrame and clean data
    df = d.process(df)

    # Save DataFrame to CSV or further processing
    df.to_csv('ski_resorts.csv', index=False)


if __name__ == '__main__':
    main()

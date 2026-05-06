"""
Crawler implementation.
"""

# pylint: disable=too-many-arguments, too-many-instance-attributes, unused-import, undefined-variable, unused-argument
import datetime
import json
import pathlib
import re

import requests
from bs4 import BeautifulSoup, Tag

from core_utils.article.article import Article
from core_utils.config_dto import ConfigDTO


class Config:
    """
    Class for unpacking and validating configurations.
    """

    def __init__(self, path_to_config: pathlib.Path) -> None:
        """
        Initialize an instance of the Config class.

        Args:
            path_to_config (pathlib.Path): Path to configuration.
        """
        self.path_to_config = path_to_config
        self.config_dto = self._extract_config_content()
        self._validate_config_content()

    def _extract_config_content(self) -> ConfigDTO:
        """
        Get config values.

        Returns:
            ConfigDTO: Config values
        """
        with open(self.path_to_config, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        
        return ConfigDTO(
            seed_urls=config_data.get('seed_urls', []),
            headers=config_data.get('headers', {}),
            total_articles_to_find_and_parse=config_data.get('total_articles_to_find_and_parse', 0),
            encoding=config_data.get('encoding', 'utf-8'),
            timeout=config_data.get('timeout', 10),
            should_verify_certificate=config_data.get('should_verify_certificate', True),
            headless_mode=config_data.get('headless_mode', True)
        )

    def _validate_config_content(self) -> None:
        """
        Ensure configuration parameters are not corrupt.
        """
        if not isinstance(self.config_dto.seed_urls, list) or len(self.config_dto.seed_urls) == 0:
            raise ValueError("seed_urls must be a non-empty list")
        if not isinstance(self.config_dto.total_articles_to_find_and_parse, int) or self.config_dto.total_articles_to_find_and_parse <= 0:
            raise ValueError("total_articles_to_find_and_parse must be a positive integer")
        if not isinstance(self.config_dto.timeout, int) or self.config_dto.timeout <= 0:
            raise ValueError("timeout must be a positive integer")

    def get_seed_urls(self) -> list[str]:
        """
        Retrieve seed urls.

        Returns:
            list[str]: Seed urls
        """
        return self.config_dto.seed_urls

    def get_num_articles(self) -> int:
        """
        Retrieve total number of articles to scrape.

        Returns:
            int: Total number of articles to scrape
        """
        return self.config_dto.total_articles_to_find_and_parse

    def get_headers(self) -> dict[str, str]:
        """
        Retrieve headers to use during requesting.

        Returns:
            dict[str, str]: Headers
        """
        return self.config_dto.headers

    def get_encoding(self) -> str:
        """
        Retrieve encoding to use during parsing.

        Returns:
            str: Encoding
        """
        return self.config_dto.encoding

    def get_timeout(self) -> int:
        """
        Retrieve number of seconds to wait for response.

        Returns:
            int: Number of seconds to wait for response
        """
        return self.config_dto.timeout

    def get_verify_certificate(self) -> bool:
        """
        Retrieve whether to verify certificate.

        Returns:
            bool: Whether to verify certificate or not
        """
        return self.config_dto.should_verify_certificate

    def get_headless_mode(self) -> bool:
        """
        Retrieve whether to use headless mode.

        Returns:
            bool: Whether to use headless mode or not
        """
        return self.config_dto.headless_mode


def make_request(url: str, config: Config) -> requests.models.Response:
    """
    Deliver a response from a request with given configuration.

    Args:
        url (str): Site url
        config (Config): Configuration

        
    Returns:
        requests.models.Response: A response from a request
    """
    response = requests.get(
        url,
        headers=config.get_headers(),
        timeout=config.get_timeout(),
        verify=config.get_verify_certificate()
    )
    response.encoding = config.get_encoding()
    return response


class Crawler:
    """
    Crawler implementation.
    """

    #: Url pattern
    url_pattern: re.Pattern | str = re.compile(r'news\.php\?id=\d+')

    def __init__(self, config: Config) -> None:
        """
        Initialize an instance of the Crawler class.

        Args:
            config (Config): Configuration
        """
        self.config = config
        self.seed_urls = config.get_seed_urls()
        self.urls_to_crawl = []
        self.total_articles = config.get_num_articles()

    def _extract_url(self, article_bs: Tag) -> str:
        """
        Find and retrieve url from HTML.

        Args:
            article_bs (bs4.Tag): Tag instance

        Returns:
            str: Url from HTML
        """
        link_tag = article_bs.find('a', href=True)
        if link_tag:
            href = link_tag.get('href')
            if href.startswith('news.php?id='):
                return f"https://fabulae.ru/{href}"
            elif href.startswith('http'):
                return href
        return ""

    def find_articles(self) -> None:
        """
        Find articles.
        """
        for seed_url in self.seed_urls:
            try:
                response = make_request(seed_url, self.config)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    article_links = soup.find_all('a', href=re.compile(r'news\.php\?id=\d+'))
                    
                    for link in article_links:
                        if len(self.urls_to_crawl) >= self.total_articles:
                            break
                        url = link.get('href')
                        if url:
                            if url.startswith('news.php?id='):
                                full_url = f"https://fabulae.ru/{url}"
                            else:
                                full_url = url
                            if full_url not in self.urls_to_crawl:
                                self.urls_to_crawl.append(full_url)
                else:
                    print(f"Failed to fetch {seed_url}: {response.status_code}")
            except Exception as e:
                print(f"Error fetching {seed_url}: {e}")

    def get_search_urls(self) -> list:
        """
        Get seed_urls param.

        Returns:
            list: seed_urls param
        """
        return self.seed_urls



# 10


class CrawlerRecursive(Crawler):
    """
    Recursive implementation.

    Get one URL of the title page and find requested number of articles recursively.
    """

    def __init__(self, config: Config) -> None:
        """
        Initialize an instance of the CrawlerRecursive class.

        Args:
            config (Config): Configuration
        """
        super().__init__(config)
        self.visited_urls = set()

    def find_articles(self) -> None:
        """
        Find number of article urls requested.
        """


# 4, 6, 8, 10


class HTMLParser:
    """
    HTMLParser implementation.
    """

    def __init__(self, full_url: str, article_id: int, config: Config) -> None:
        """
        Initialize an instance of the HTMLParser class.

        Args:
            full_url (str): Site url
            article_id (int): Article id
            config (Config): Configuration
        """
        self.full_url = full_url
        self.article_id = article_id
        self.config = config
        self.article = Article(full_url, article_id)

    def _fill_article_with_text(self, article_soup: BeautifulSoup) -> None:
        """
        Find text of article.

        Args:
            article_soup (bs4.BeautifulSoup): BeautifulSoup instance
        """
        content_div = article_soup.find('div', class_='news_text')
        if not content_div:
            content_div = article_soup.find('div', class_='content')
        if content_div:
            for unwanted in content_div.find_all(['script', 'style', 'iframe']):
                unwanted.decompose()
            text = content_div.get_text(separator='\n', strip=True)
            self.article.text = text
        title_tag = article_soup.find('h1')
        if title_tag:
            self.article.title = title_tag.get_text(strip=True)

    def _fill_article_with_meta_information(self, article_soup: BeautifulSoup) -> None:
        """
        Find meta information of article.

        Args:
            article_soup (bs4.BeautifulSoup): BeautifulSoup instance
        """
        author_tag = article_soup.find('div', class_='author')
        if not author_tag:
            author_tag = article_soup.find('span', class_='author')
        if author_tag:
            self.article.author = author_tag.get_text(strip=True)
        else:
            self.article.author = "Unknown"
        date_tag = article_soup.find('div', class_='date')
        if not date_tag:
            date_tag = article_soup.find('span', class_='date')
        if date_tag:
            date_text = date_tag.get_text(strip=True)
            self.article.date = self.unify_date_format(date_text)
        else:
            self.article.date = datetime.datetime.now()
        topics = []
        topic_tags = article_soup.find_all('a', class_='topic')
        if not topic_tags:
            topic_tags = article_soup.find_all('div', class_='category')
        for tag in topic_tags:
            topics.append(tag.get_text(strip=True))
        self.article.topics = topics if topics else ["General"]

    def unify_date_format(self, date_str: str) -> datetime.datetime:
        """
        Unify date format.

        Args:
            date_str (str): Date in text format

        Returns:
            datetime.datetime: Datetime object
        """
        date_formats = [
            '%d.%m.%Y',
            '%Y-%m-%d',
            '%d/%m/%Y',
            '%b %d, %Y',
            '%d %B %Y',
            '%Y.%m.%d'
        ]
        date_str = date_str.strip()
        for date_format in date_formats:
            try:
                return datetime.datetime.strptime(date_str, date_format)
            except ValueError:
                continue
        year_match = re.search(r'\d{4}', date_str)
        if year_match:
            return datetime.datetime(int(year_match.group()), 1, 1)
        return datetime.datetime.now()

    def parse(self) -> Article | bool:
        """
        Parse each article.

        Returns:
            Article | bool: Article instance, False in case of request error
        """
        try:
            response = make_request(self.full_url, self.config)
            if response.status_code != 200:
                return False
            soup = BeautifulSoup(response.content, 'html.parser')
            self._fill_article_with_text(soup)
            self._fill_article_with_meta_information(soup)
            return self.article
        except Exception as e:
            print(f"Error parsing {self.full_url}: {e}")
            return False


def prepare_environment(base_path: pathlib.Path | str) -> None:
    """
    Create ASSETS_PATH folder if no created and remove existing folder.

    Args:
        base_path (pathlib.Path | str): Path where articles stores
    """


def main() -> None:
    """
    Entrypoint for scraper module.
    """
    config_path = pathlib.Path('scraper_config.json')
    output_path = pathlib.Path('articles')
    prepare_environment(output_path)
    config = Config(config_path)
    crawler = CrawlerRecursive(config)
    crawler.find_articles()
    urls = crawler.urls_to_crawl
    print(f"Found {len(urls)} articles to parse")
    for idx, url in enumerate(urls):
        parser = HTMLParser(url, idx + 1, config)
        article = parser.parse()
        if article:
            file_path = output_path / f'article_{idx + 1}.json'
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump({
                    'id': article.id,
                    'url': article.url,
                    'title': article.title,
                    'author': article.author,
                    'date': article.date.isoformat() if article.date else None,
                    'text': article.text,
                    'topics': article.topics
                }, f, ensure_ascii=False, indent=2)
            print(f"Saved article {idx + 1}: {article.title}")
    
    print("Scraping completed!")


if __name__ == "__main__":
    main()

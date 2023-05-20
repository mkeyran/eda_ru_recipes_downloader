from eda_ru_parser.recipe import Recipe, NutritionInformation
import abc
import requests
from bs4 import BeautifulSoup


class AbstractParser:
    """Abstract class for parsers."""

    def get_content(self, url: str) -> str:
        """Download the content of a web page."""
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        return soup

    def condense_html(self, soup):
        # Remove non-text related elements
        for tag in soup.find_all(
            [
                "script",
                "style",
                "link",
                "meta",
                "noscript",
                "svg",
                "use",
                "input",
            ]
        ):
            tag.decompose()

        # Iterate through all elements, and remove attributes except 'class' and 'id'
        for tag in soup.find_all(True):
            allowed_attrs = {"class", "id"}
            tag.attrs = {
                attr: value[0]
                for attr, value in tag.attrs.items()
                if attr in allowed_attrs
            }

        return soup

    @abc.abstractmethod
    def parse(self, html_content: str) -> Recipe:
        """Parse the HTML content and return the recipe information."""
        pass

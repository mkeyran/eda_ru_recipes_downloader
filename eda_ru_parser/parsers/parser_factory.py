from eda_ru_parser.parsers.eda_ru_parser import EdaRuParser

from eda_ru_parser.parsers.abstract_parser import AbstractParser
from eda_ru_parser.parsers.wprm_based_parser import (
    RecipeTinEatsParser,
    R196FlavorsParser,
)


class ParserFactory:
    def parser_factory(self, url: str) -> AbstractParser:
        """Return the parser for a given URL."""
        for i in [RecipeTinEatsParser, R196FlavorsParser, EdaRuParser]:
            if i.base_url in url:
                return i()
        raise ValueError(f"Unsupported URL: {url}")

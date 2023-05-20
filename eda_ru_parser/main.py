#!/bin/env python
from bs4 import BeautifulSoup
import requests
import json
import click
import pathlib
from typing import Dict, List, Union, Optional
from eda_ru_parser.parsers.parser_factory import ParserFactory


def download_web_page(url: str) -> str:
    """Download the content of a web page."""
    response = requests.get(url)
    return response.text


@click.command()
@click.argument("url")
@click.option("-o", "--output", type=click.File("w"), help="Output JSON file")
@click.option(
    "-n",
    "--nextcloud-path",
    type=click.Path(),
    help="Nextcloud recipies directories to export",
)
def parse_recipe(
    url: str, output: Optional[click.File], nextcloud_path: Optional[str]
) -> None:
    """Parse a recipe from a given URL and save it as a JSON file or print it to stdout."""
    # Remove the trailing slash if present
    if url.endswith("/"):
        url = url[:-1]

    parser = ParserFactory().parser_factory(url)
    recipe = parser.parse(url)
    if nextcloud_path:
        nextcloud_path_obj = pathlib.Path(nextcloud_path)
        path_name = url.split("/")[-1]
        recipe_path = nextcloud_path_obj / path_name
        recipe_path.mkdir(exist_ok=True)
        with open(recipe_path / "recipe.json", "w") as f:
            json = recipe.to_json()
            f.write(json)

        recipe.get_photo(recipe_path)
    elif output:
        output.write(json.dumps(recipe, ensure_ascii=False, indent=2))
    else:
        print(recipe)


if __name__ == "__main__":
    parse_recipe()

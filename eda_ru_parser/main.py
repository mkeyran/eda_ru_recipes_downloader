#!/bin/env python
import requests
from bs4 import BeautifulSoup
import json
import click
import pathlib
from PIL import Image
from io import BytesIO
from typing import Dict, List, Union, Optional


def download_web_page(url: str) -> str:
    """Download the content of a web page."""
    response = requests.get(url)
    return response.text


def parse_html_content(html_content: str) -> BeautifulSoup:
    """Parse the HTML content and return a BeautifulSoup object."""
    return BeautifulSoup(html_content, "html.parser")


def extract_recipe(soup: BeautifulSoup, url: str) -> Dict:
    """Extract the recipe information from the parsed HTML content."""
    recipe_container = soup.find("div", {"itemtype": "http://schema.org/Recipe"})

    recipe: Dict = {}
    for itemprop in recipe_container.find_all(attrs={"itemprop": True}):
        prop_name = itemprop["itemprop"]
        prop_value = extract_property_value(itemprop)

        if prop_name in ["recipeIngredient", "recipeInstructions"]:
            handle_array_properties(recipe, itemprop, prop_name, prop_value)
        elif prop_name == "author":
            recipe[prop_name] = itemprop.find(class_="emotion-1utpb33").text.strip()
        elif prop_name == "nutrition":
            recipe[prop_name] = extract_nutrition_info(itemprop)
        elif prop_name == "name":
            try:
                recipe[prop_name] = extract_property_value(
                    itemprop.find(class_="emotion-gl52ge")
                )
            except:
                pass

        else:
            recipe[prop_name] = prop_value

    try:
        recipe["description"] = recipe_container.find(
            class_="emotion-aiknw3"
        ).text.strip()
    except AttributeError:
        pass

    try:
        recipe["image"] = recipe_container.find("picture", class_="emotion-0").find(
            "img"
        )["src"]
    except AttributeError:
        pass

    recipe["url"] = url

    allowed_fields = [
        "name",
        "image",
        "author",
        "recipeCategory",
        "recipeCuisine",
        "description",
        "recipeIngredient",
        "recipeInstructions",
        "recipeYield",
        "prepTime",
        "cookTime",
        "totalTime",
        "nutrition",
        "url",
    ]
    return {k: v for k, v in recipe.items() if k in allowed_fields}


def extract_property_value(itemprop: BeautifulSoup) -> str:
    """Extract the value of a property from an itemprop element."""
    if itemprop.get("itemtype", "") == "http://schema.org/HowToStep":
        return itemprop.find(itemprop="text").text.strip().replace("\xa0", " ")
    elif itemprop.name == "meta":
        return itemprop["content"]
    elif itemprop.name == "h1":
        return itemprop.text.replace("\xa0", " ")
    else:
        return itemprop.text.strip().replace("\xa0", " ")


def handle_array_properties(
    recipe: Dict, itemprop: BeautifulSoup, prop_name: str, prop_value: str
) -> None:
    """Handle array properties like ingredients and instructions."""
    if prop_name == "recipeIngredient":
        ingredient_container = itemprop.find_parent(class_="emotion-ydhjlb")
        if ingredient_container:
            ingredient_amount = ingredient_container.find(
                class_="emotion-bsdd3p"
            ).text.strip()
            prop_value = f"{prop_value} ({ingredient_amount})"
    elif prop_name == "recipeInstructions":
        step_number = itemprop.find(class_="emotion-1hreea5")
        if step_number:
            prop_value = f"{step_number.text} {prop_value}"

    if prop_name not in recipe:
        recipe[prop_name] = []
    recipe[prop_name].append(prop_value)


def extract_nutrition_info(itemprop: BeautifulSoup) -> Dict[str, str]:
    """Extract nutrition information from an itemprop element."""
    nutrition_info = {}
    for nutrition_item in itemprop.find_all(attrs={"itemprop": True}):
        nutrition_prop = nutrition_item["itemprop"]
        nutrition_value = nutrition_item.text.strip()
        nutrition_info[nutrition_prop] = nutrition_value
    return nutrition_info


def get_photo(
    recipe_json: Dict[str, Union[str, List[str], Dict[str, str]]],
    recipe_path: pathlib.Path,
) -> None:
    """Download image from recipe_json, save it and create thumbnails."""
    image_url = recipe_json["image"]
    response = requests.get(image_url)

    image = Image.open(BytesIO(response.content))
    image.save(f"{recipe_path}/full.jpg")

    # Create 145x145 thumbnail
    image_145 = image.copy()
    image_145.thumbnail((145, 145))
    image_145.save(f"{recipe_path}/thumb.jpg")

    # Create 9x9 thumbnail
    image_16 = image.copy()
    image_16.thumbnail((9, 9))
    image_16.save(f"{recipe_path}/thumb16.jpg")


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
    html_content = download_web_page(url)
    soup = parse_html_content(html_content)
    recipe = extract_recipe(soup, url)
    if nextcloud_path:
        nextcloud_path_obj = pathlib.Path(nextcloud_path)
        path_name = url.split("/")[-1]
        recipe_path = nextcloud_path_obj / path_name
        recipe_path.mkdir(exist_ok=True)
        with open(recipe_path / "recipe.json", "w") as f:
            f.write(json.dumps(recipe, ensure_ascii=False, indent=2))
            get_photo(recipe, recipe_path)
    elif output:
        output.write(json.dumps(recipe, ensure_ascii=False, indent=2))
    else:
        print(recipe)


if __name__ == "__main__":
    parse_recipe()

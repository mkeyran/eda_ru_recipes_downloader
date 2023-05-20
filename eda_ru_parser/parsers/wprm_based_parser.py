from bs4 import BeautifulSoup
from eda_ru_parser.recipe import Recipe, NutritionInformation
from eda_ru_parser.parsers.abstract_parser import AbstractParser
from typing import Dict
import re
import json


def remove_emoticons(text):
    emoticon_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # flags (iOS)
        "▢"
        "]+",
        flags=re.UNICODE,
    )
    return emoticon_pattern.sub(r"", text)


class WPRMParser(AbstractParser):
    def __init__(self, main_selector="wprm-recipe-container") -> None:
        super().__init__()
        self.main_selector = main_selector

    def parse(self, url) -> Recipe:
        """Parse the HTML content and return the recipe information."""

        soup = self.get_content(url)
        try:
            sub = soup.find("script", type="application/ld+json")
            sub_json = json.loads(sub.text)
            recipe = [x for x in sub_json["@graph"] if x["@type"] == "Recipe"][0]
            recipe = self.process_json_recipe(recipe, soup)
            recipe["url"] = url
        except:
            sub = soup.find("div", {"class": self.main_selector})
            # parsed = self.condense_html(sub)
            # return sub
            recipe = self.extract_recipe(sub, url)
        recipe = {k: v for k, v in recipe.items() if k[0] != "@"}

        return Recipe(**recipe)

    def process_json_recipe(self, r, soup):
        recipe = r.copy()
        recipe["image"] = recipe["image"][0]
        recipe["recipeYield"] = recipe["recipeYield"][0]
        recipe["recipeInstructions"] = [x["text"] for x in recipe["recipeInstructions"]]

        notes = soup.find("div", {"class": "wprm-recipe-notes"})
        if notes:
            notes = [x.text for x in notes.children]
            recipe["recipeInstructions"].append("NOTES: \n" + "".join(notes))

        return recipe

    def extract_recipe(self, soup: BeautifulSoup, url: str) -> Dict:
        recipe = {}

        # Get recipe name
        if selector := soup.find("h2", {"class": "wprm-recipe-name"}):
            recipe["name"] = selector.text

        # Get recipe category
        if selector := soup.find("span", {"class": "wprm-recipe-course"}):
            recipe["recipeCategory"] = selector.text

        # Get recipe cuisine
        if selector := soup.find("span", {"class": "wprm-recipe-cuisine"}):
            recipe["recipeCuisine"] = selector.text

        # Get recipe servings
        if selector := soup.find("span", {"class": "wprm-recipe-servings"}):
            recipe["recipeYield"] = selector.text

        # Get recipe ingredients
        if selector := soup.find("ul", {"class": "wprm-recipe-ingredients"}):
            recipe["recipeIngredient"] = [
                remove_emoticons(ingredient.text.strip())
                for ingredient in selector.find_all("li")
            ]

        # Get recipe instructions
        instructions = soup.find_all("div", {"class": "wprm-recipe-instruction-text"})
        recipe["recipeInstructions"] = [
            instruction.text.strip() for instruction in instructions
        ]

        # Get recipe notes
        if selector := soup.find("div", {"class": "wprm-recipe-notes"}):
            notes = selector.text.strip()
            recipe["recipeInstructions"].append("NOTES: \n" + notes)

        # Get prep time
        if selector := soup.find("span", {"class": "wprm-recipe-prep_time-minutes"}):
            prep_time = selector.text
            recipe["prepTime"] = f"PT{prep_time}M"

        recipe["url"] = url

        if selector := soup.find("span", {"class": "wprm-recipe-author"}):
            recipe["author"] = selector.text

        if selector := soup.find("span", {"class": "wprm-recipe-cook_time-minutes"}):
            cooktime = selector.text
            recipe["cookTime"] = f"PT{cooktime}M"

        if selector := soup.find("div", {"class": "wprm-recipe-summary"}):
            recipe["description"] = selector.text

        if selector := soup.find("span", {"class": "wprm-recipe-total_time-minutes"}):
            total_time = selector.text
            recipe["totalTime"] = f"PT{total_time}M"

        if selector := soup.find("div", {"class": "wprm-recipe-image"}).findChild(
            "noscript"
        ):
            recipe["image"] = selector.findChild("img")["src"].split("?")[0]
        elif selector := soup.find("div", {"class": "wprm-recipe-image"}).findChild(
            "img"
        ):
            recipe["image"] = selector["src"].split("?")[0]

        return recipe


class RecipeTinEatsParser(WPRMParser):
    base_url = "www.recipetineats.com"


class R196FlavorsParser(WPRMParser):
    base_url = "196flavors.com"

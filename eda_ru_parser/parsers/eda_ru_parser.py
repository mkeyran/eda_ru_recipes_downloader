from eda_ru_parser.parsers.abstract_parser import AbstractParser
from eda_ru_parser.recipe import Recipe
from bs4 import BeautifulSoup
from typing import Dict


class EdaRuParser(AbstractParser):
    """Parser for eda.ru recipes."""

    base_url = "eda.ru"

    def parse(self, url) -> Recipe:
        """Parse the HTML content and return the recipe information."""

        soup = self.get_content(url)
        recipe = self.extract_recipe(soup, url)
        print(recipe)
        return Recipe(**recipe)

    def extract_recipe(self, soup: BeautifulSoup, url: str) -> Dict:
        """Extract the recipe information from the parsed HTML content."""
        recipe_container = soup.find("div", {"itemtype": "http://schema.org/Recipe"})

        recipe: Dict = {}
        for itemprop in recipe_container.find_all(attrs={"itemprop": True}):
            prop_name = itemprop["itemprop"]
            prop_value = self.extract_property_value(itemprop)

            if prop_name in ["recipeIngredient", "recipeInstructions"]:
                self.handle_array_properties(recipe, itemprop, prop_name, prop_value)
            elif prop_name == "author":
                recipe[prop_name] = itemprop.find(class_="emotion-1utpb33").text.strip()
            elif prop_name == "nutrition":
                recipe[prop_name] = self.extract_nutrition_info(itemprop)
            elif prop_name == "name":
                try:
                    recipe[prop_name] = self.extract_property_value(
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

    def extract_property_value(self, itemprop: BeautifulSoup) -> str:
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
        self, recipe: Dict, itemprop: BeautifulSoup, prop_name: str, prop_value: str
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

    def extract_nutrition_info(self, itemprop: BeautifulSoup) -> Dict[str, str]:
        """Extract nutrition information from an itemprop element."""
        nutrition_info = {}
        for nutrition_item in itemprop.find_all(attrs={"itemprop": True}):
            nutrition_prop = nutrition_item["itemprop"]
            nutrition_value = nutrition_item.text.strip()
            nutrition_info[nutrition_prop] = nutrition_value
        return nutrition_info

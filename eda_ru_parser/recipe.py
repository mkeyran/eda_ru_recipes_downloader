import dataclasses

import json
from dataclasses import dataclass, field
from typing import List, Optional
from PIL import Image
from io import BytesIO
import pathlib
import requests


@dataclass
class NutritionInformation:
    calories: str
    carbohydrateContent: str
    proteinContent: str
    fatContent: str


@dataclass
class Recipe:
    author: str
    description: str
    url: str
    image: str
    recipeIngredient: List[str]
    name: str
    recipeInstructions: str

    prepTime: Optional[str] = None
    totalTime: Optional[str] = None
    cookTime: Optional[str] = None
    recipeCategory: Optional[str] = None
    recipeCuisine: Optional[str] = None
    recipeYield: Optional[str] = None
    nutrition: Optional[NutritionInformation] = None
    datePublished: Optional[str] = None

    def __init__(self, **kwargs):
        names = set([f.name for f in dataclasses.fields(self)])
        for k, v in kwargs.items():
            if k in names:
                setattr(self, k, v)

    def to_json(self) -> str:
        return json.dumps(
            self, ensure_ascii=False, default=lambda o: o.__dict__, indent=4
        )

    def get_photo(
        self,
        recipe_path: pathlib.Path,
    ) -> None:
        """Download image from recipe_json, save it and create thumbnails."""
        image_url = self.image
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

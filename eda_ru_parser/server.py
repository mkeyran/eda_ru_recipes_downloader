""" This is a webserver that provides API to parse web pages and store the recipes"""

from eda_ru_parser.parsers.parser_factory import ParserFactory
from flask import Flask, jsonify, request, Response
from flask.json import dumps
import json
import pathlib


nextcloud_path = "/home/keyran/Nextcloud2/Recipes"


def store(url, recipe):
    nextcloud_path_obj = pathlib.Path(nextcloud_path)
    if url[-1] == "/":
        url = url[:-1]
    path_name = url.split("/")[-1]
    recipe_path = nextcloud_path_obj / path_name
    recipe_path.mkdir(exist_ok=True)
    with open(recipe_path / "recipe.json", "w") as f:
        json_recipe = recipe.to_json()
        f.write(json_recipe)

    recipe.get_photo(recipe_path)


app = Flask(__name__)


@app.route("/parse", methods=["GET", "POST"])
def parse():
    # Extract Get parameters
    data = request.args
    uri = data["uri"]
    save = data.get("save", False)
    try:
        parser = ParserFactory().parser_factory(uri)
        result = parser.parse(uri)
        if save:
            store(uri, result)
        response = Response(
            result.to_json(),
            status=200,
            mimetype="application/json; charset=utf-8",
        )
        return response
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def main():
    app.run(debug=True, port=9541)


if __name__ == "__main__":
    main()

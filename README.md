# EDA.ru Recipe Downloader
Recipe Downloader is a command-line utility to download and parse recipes from the eda.ru website. The program can print the downloaded recipe, save it to a JSON file according to the Recipe Schema, or save it in a folder that is used by the Nextcloud Cookbook app.

##  Installation
This project uses Poetry for dependency management. Make sure you have Poetry installed on your system.

To install the project dependencies, navigate to the project root directory and run:

```
poetry install
```

## Usage
After installing the dependencies, you can use the recipe_downloader command with the following options:

```
Usage: recipe_downloader [OPTIONS] URL

Arguments:
  URL  The URL of the recipe on eda.ru

Options:
  -o, --output FILE          Output JSON file
  -n, --nextcloud-path PATH  Nextcloud recipes directory to export
  --help                     Show this message and exit.
```

## Examples
1. Print the recipe to stdout:

```
poetry run recipe_downloader https://eda.ru/recipes/some-recipe
```

2. Save the recipe to a JSON file:

```
poetry run recipe_downloader -o output.json https://eda.ru/recipes/some-recipe
```

3. Save the recipe to the Nextcloud Cookbook directory:

```
poetry run recipe_downloader -n /path/to/nextcloud/recipes https://eda.ru/recipes/some-recipe
```

## Contributing
If you'd like to contribute to the project, feel free to open a pull request or create an issue on the repository. We appreciate your help and feedback.

## License
This project is licensed under the MIT License. See the LICENSE file for more information.


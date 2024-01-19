import csv
import json
import logging
import os

import requests
from bs4 import BeautifulSoup
from huggingface_hub import hf_api

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

BASE_URL = "https://huggingface.co"


def is_dir(title: str) -> bool:
    if "kB" in title or "Bytes" in title or "MB" in title or "GB" in title:
        return False
    return True


def update_csv(csv_file, row):
    with open(csv_file, mode="a", newline="") as outfile:
        writer = csv.writer(outfile)
        if outfile.tell() == 0:
            writer.writerow(["category", "model", "space", "size"])
        writer.writerow(row)
        outfile.flush()


def convert_size(size_text: str) -> int:
    if "kB" in size_text:
        return int(float(size_text.split(" kB")[0]) * 1024)
    if "MB" in size_text:
        return int(float(size_text.split(" MB")[0]) * 1024 * 1024)
    if "GB" in size_text:
        return int(float(size_text.split(" GB")[0]) * 1024 * 1024 * 1024)
    elif "Bytes" in size_text:
        return int(size_text.split(" Bytes")[0])
    return 0


def soup_crawl(url: str) -> int:
    size = 0
    try:
        content = requests.get(f"{BASE_URL}{url}")
        soup = BeautifulSoup(content.text, "html.parser")
        i = 0
        for tag in soup.findAll("ul"):
            if i < 2:
                i += 1
                continue
            for t in tag.findAll("li"):
                a_tag = t.find("a")
                if a_tag:
                    href_value = a_tag.get("href")
                    a_tag = t.find("a", title="Download file")
                    if a_tag:
                        size_text = a_tag.get_text(strip=True)
                        converted_size = convert_size(size_text)
                        size += converted_size
                    else:
                        size += soup_crawl(href_value)
    except Exception as e:
        logger.error(e)
    return size


def crawl_spaces(category: str, number=20):
    input_file_path = f"models-{category}-{number}.csv"
    result_file_path = f"{category}.csv"
    current_spaces = set()

    if os.path.exists(result_file_path):
        with open(result_file_path, mode="r") as infile:
            reader = csv.reader(infile)
            next(reader)
            for row in reader:
                space = row[2]
                current_spaces.add(space)
    with open(input_file_path, mode="r") as infile:
        reader = csv.reader(infile)
        next(reader)
        for row in reader:
            model_id = row[1]
            logger.info("MODEL:{}".format(model_id))
            spaces = list(hf_api.list_spaces(models=model_id))
            for index, space in enumerate(spaces):
                if space.id in current_spaces:
                    continue
                current_spaces.add(space.id)
                logger.info(space.id)
                size = soup_crawl(f"/spaces/{space.id}/tree/main")
                logger.info(f"Space: {space.id}, size: {size}")
                update_csv(
                    csv_file=result_file_path,
                    row=[
                        category,
                        model_id,
                        space.id,
                        round(float(size) / 1024.0, ndigits=1),
                    ],
                )


def crawl_models(category: str, sort="downloads", number=20):
    models_file = f"models-{category}-{number}.csv"
    model_dict = {}
    top_models = requests.get(
        f"{BASE_URL}/api/models",
        params={
            "pipeline_tag": category,
            "sort": sort,
            "direction": -1,
            "limit": number,
        },
    )
    prettified_models = json.loads(top_models.text)
    for model in prettified_models:
        spaces = list(hf_api.list_spaces(models=model["id"]))
        model_dict[model["id"]] = len(spaces)
    cnt = 0
    with open(models_file, mode="w") as outfile:
        writer = csv.writer(outfile)
        if outfile.tell() == 0:
            writer.writerow(["category", "model", "number_of_apps"])
        for k, v in model_dict.items():
            writer.writerow([category, k, v])
            cnt += v
        outfile.flush()
    logger.info(f"Category: {category}, Sum: {cnt}")


if __name__ == "__main__":
    logger.info("Starting the app...")
    crawl_spaces(category="text-classification")

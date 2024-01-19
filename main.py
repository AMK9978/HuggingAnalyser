import csv
import json
import logging

import requests
from bs4 import BeautifulSoup
from huggingface_hub import hf_api

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

BASE_URL = 'https://huggingface.co'


def is_dir(title):
    if "kB" in title or "Bytes" in title or "MB" in title or "GB" in title:
        return False
    return True


def update_csv(csv_file, row):
    with open(csv_file, mode='a', newline='') as outfile:
        writer = csv.writer(outfile)
        if outfile.tell() == 0:
            writer.writerow(['category', 'model', 'space', 'size'])
        writer.writerow(row)
        outfile.flush()


def convert_size(size_text):
    if "kB" in size_text:
        return int(float(size_text.split(" kB")[0]) * 1024)
    if "MB" in size_text:
        return int(float(size_text.split(" MB")[0]) * 1024 * 1024)
    if "GB" in size_text:
        return int(float(size_text.split(" GB")[0]) * 1024 * 1024 * 1024)
    elif "Bytes" in size_text:
        return int(size_text.split(" Bytes")[0])
    return 0


def soup_crawl(url):
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


def crawl_spaces(task):
    input_file_path = f'models-{task}.csv'
    output_file_path = f'{task}.csv'
    current_spaces = set()

    with open(output_file_path, mode='r') as infile:
        reader = csv.reader(infile)
        next(reader)
        for row in reader:
            space = row[2]
            current_spaces.add(space)
    with open(input_file_path, mode='r') as infile:
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
                update_csv(csv_file=output_file_path, row=[task, model_id, space.id,
                                                           round(float(size) / 1024.0, ndigits=1)])


def crawl_models(category):
    inp = f'models-{category}.csv'
    inp2 = f'{category}.csv'
    out2 = f'new-{category}.csv'
    out3 = f'identical-{category}.csv'
    all_data = []
    identical_spaces = set()
    data = []
    with open(inp2, mode='r') as infile:
        reader = csv.reader(infile)
        next(reader)
        for row in reader:
            all_data.append({"category": row[0], "model": row[1], "space": row[2], "size": row[3]})


    with open(inp, mode='r') as infile:
        reader = csv.reader(infile)
        next(reader)
        for row in reader:
            model = row[1]
            data.append(model)
    spaces = set()
    old_models = []

    for model in data:
        new_spaces = list(hf_api.list_spaces(models=model))
        for sp in new_spaces:
            spaces.add(f"{model}|{sp.id}")
    with open(inp2, mode='r') as infile:
        reader = csv.reader(infile)
        next(reader)
        for row in reader:
            old_models.append(row[1])

    difference_models = list(set(old_models) - set(data))

    with open(out2, mode='w') as outfile:
        with open(out3, mode='w') as iden_out:
            writer = csv.writer(outfile)
            iden_writer = csv.writer(iden_out)
            if outfile.tell() == 0:
                writer.writerow(['category', 'model', 'space", "size'])
            if iden_out.tell() == 0:
                iden_writer.writerow(['category', 'model', 'space", "size'])
            for elem in all_data:
                if elem["model"] in difference_models:
                    continue
                writer.writerow([elem["category"], elem["model"], elem["space"], elem["size"]])
                if f"{elem['model']}|{elem['space']}" not in identical_spaces:
                    iden_writer.writerow([elem["category"], elem["model"], elem["space"], elem["size"]])
                identical_spaces.add(f"{elem['model']}|{elem['space']}")
            iden_out.flush()
        outfile.flush()


def model_apps_finder(category, number):
    models_file = f'models-{category}-{number}.csv'
    model_dict = {}
    top_models = requests.get(f"{BASE_URL}/api/models",
                              params={"pipeline_tag": category, "sort": "downloads",
                                      "direction": -1,
                                      "limit": number})
    prettified_models = json.loads(top_models.text)
    for model in prettified_models:
        spaces = list(hf_api.list_spaces(models=model["id"]))
        model_dict[model["id"]] = len(spaces)
    cnt = 0
    with open(models_file, mode='w') as outfile:
        writer = csv.writer(outfile)
        if outfile.tell() == 0:
            writer.writerow(['category', 'model', 'number_of_apps'])
        for k, v in model_dict.items():
            writer.writerow([category, k, v])
            cnt += v
        outfile.flush()
    logger.info(f"Category: {category}, Sum: {cnt}")


if __name__ == '__main__':
    logger.info("Starting the app...")
    crawl_spaces(task="text-generation")
    crawl_spaces(task="text-classification")


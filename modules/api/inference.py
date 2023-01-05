import asyncio
import base64
import io
import json
import os
import time
from uuid import UUID

import aiohttp
import requests
from PIL import Image, PngImagePlugin

from modules import utils
from modules.api.request_types import *


def samplers(url: str):
    response = requests.get(url=f"{url}/sdapi/v1/samplers")
    if response.status_code != 200:
        print(f"API request error ({response.status_code})!")
    else:
        response_json = response.json()

        samplers_list = []
        for sampler in response_json:
            samplers_list.append(sampler["name"])

        return samplers_list


def get_settings(url: str):
    response = requests.get(url=f"{url}/sdapi/v1/options")

    if response.status_code != 200:
        print(f"API request error ({response.status_code})!")
    else:
        response_json = response.json()

        return response_json


def set_setting(url: str, name: str, value):
    payload = {
        name: value
    }
    response = requests.post(url=f"{url}/sdapi/v1/options", json=payload)

    if response.status_code != 200:
        print(f"API request error ({response.status_code})!")


def progress(url: str):
    response = requests.get(url=f"{url}/sdapi/v1/progress")

    if response.status_code != 200:
        print(f"API request error ({response.status_code})!")
    else:
        response_json = response.json()

        return response_json["progress"]


def interrupt(url: str):
    response = requests.post(url=f"{url}/sdapi/v1/interrupt")

    if response.status_code != 200:
        print(f"API request error ({response.status_code})!")


def txt2img(api_url: str, request: Text2Img):
    request.mark_processing()

    utils.prepare_folder(os.path.join("request_history", request.get_snowflake_id()))
    utils.prepare_folder(os.path.join("temp", "txt2img", request.get_snowflake_id()))

    response = requests.post(url=f"{api_url}/sdapi/v1/txt2img", json=request.options.get())
    if response.status_code != 200:
        print(f"API request error ({response.status_code})!")
    else:
        response_json = response.json()
        for index, raw_image in enumerate(response_json['images']):
            image = Image.open(io.BytesIO(base64.b64decode(raw_image.split(",", 1)[0])))

            json.dump(request.options.get(), open(os.path.join("request_history", request.get_snowflake_id(), "txt2img.json"), "w"))

            image.save(os.path.join("temp", request.get_snowflake_id(), "txt2img", f"image_{index}.png"))

    utils.create_grid("txt2img", request.get_snowflake_id(), request.options.get()['width'], request.options.get()['height'], request.options.get()['batch_size'])

    request.mark_finished()


def upscale(url: str, request: Upscale):
    request.mark_processing()

    utils.prepare_folder(os.path.join("request_history", request.get_snowflake_id()))
    utils.prepare_folder(os.path.join("temp", request.get_snowflake_id(), "upscaling"))

    response = requests.post(url=f'{url}/sdapi/v1/extra-single-image', json=request.options.get_payload())
    if response.status_code != 200:
        print(f"API request error ({response.status_code})!\nError content details: {response.content.decode('utf-8')}")
    else:
        json_response = response.json()
        encoded_image = json_response["image"]

        json.dump(request.options.get(), open(os.path.join("request_history", request.get_snowflake_id(), f"upscale_{request.options.get()['image_index']}.json"), 'w'))

        image = Image.open(io.BytesIO(base64.b64decode(encoded_image.split(",", 1)[0])))

        image.save(os.path.join("temp", "upscaling", request.get_snowflake_id(), f"image_{request.options.get()['image_index']}.png"))

    request.mark_finished()

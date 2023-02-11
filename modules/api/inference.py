import base64
import io
import json
import os

import aiohttp
import requests
from PIL import Image

from modules import utils, singleton
from modules.api.request_types import *


class API(metaclass=singleton.SingletonMetaclass):
    def __init__(self, webui_url: str):
        self.url = webui_url

    def samplers(self):
        response = requests.get(url=f"{self.url}/sdapi/v1/samplers")
        if response.status_code != 200:
            print(f"API request error ({response.status_code})!\n{response}")
        else:
            response_json = response.json()

            return [sampler["name"] for sampler in response_json]

    def upscalers(self):
        response = requests.get(url=f'{self.url}/sdapi/v1/upscalers')
        if response.status_code != 200:
            print(f"API request error ({response.status_code})!\n{response}")
        else:
            response_json = response.json()

            return [upscaler["name"] for upscaler in response_json if upscaler["name"] != 'None']


    async def progress(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(url=f"{self.url}/sdapi/v1/progress") as response:
                if response.status != 200:
                    print(f"API request error ({response.status})!\n{response}")
                else:
                    return (await response.json())["progress"]

    async def interrupt(self):
        async with aiohttp.ClientSession() as session:
            async with session.post(url=f"{self.url}/sdapi/v1/interrupt") as response:
                if response.status != 200:
                    print(f"API request error ({response.status})!\n{response}")

    def txt2img(self, request: Text2Img):
        request.mark_processing()

        os.makedirs(os.path.join("data", "history"), exist_ok=True)
        os.makedirs(os.path.join("cache", "txt2img", request.get_inference_id()), exist_ok=True)

        response = requests.post(url=f"{self.url}/sdapi/v1/txt2img", json=request.options.get())
        if response.status_code != 200:
            print(f"API request error ({response.status_code})!\n{response}")
        else:
            response_json = response.json()
            for index, raw_image in enumerate(response_json['images']):
                image = Image.open(io.BytesIO(base64.b64decode(raw_image.split(",", 1)[0])))

                image.save(os.path.join("cache", "txt2img", request.get_inference_id(), f"image_{index}.png"))

        with open(os.path.join("data", "history", f"{request.get_inference_id()}.json"), "w") as io_stream:
            json.dump({"type": "txt2img", "author": {"id": request.author_id, "name": request.author_name}, "data": request.options.get()}, io_stream)

        utils.create_grid(request.get_inference_id(), "txt2img", request.options.get()['width'], request.options.get()['height'], request.options.get()['batch_size'])

        request.mark_finished()

    def upscale(self, request: Upscale):
        request.mark_processing()

        os.makedirs(os.path.join("data", "history"), exist_ok=True)
        os.makedirs(os.path.join("cache", "upscale", request.get_inference_id()), exist_ok=True)

        payload = request.options.get_payload()
        payload["image"] = base64.b64encode(open(os.path.join("cache", "txt2img", request.get_base_inference_id(), f"image_{request.options.get()['image_index']}.png"), "rb").read()).decode("utf-8")

        response = requests.post(url=f"{self.url}/sdapi/v1/extra-single-image", json=payload)
        if response.status_code != 200:
            print(f"API request error ({response.status_code})!\n{response}")
        else:
            response_json = response.json()

            with open(os.path.join("data", "history", f"{request.get_inference_id()}.json"), "w") as io_stream:
                json.dump({"type": "upscaling", "author": {"id": request.author_id, "name": request.author_name}, "data": request.options.get()}, io_stream)

            image = Image.open(io.BytesIO(base64.b64decode(response_json['image'].split(",", 1)[0])))
            image.save(os.path.join("cache", "upscale", request.get_inference_id(), f"image_{request.options.get()['image_index']}.jpg"))

        request.mark_finished()

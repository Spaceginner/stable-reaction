import base64
import os.path
import random
import time

import discord


class _APIRequestStatus:
    def __init__(self):
        self.place = None
        self.priority = None
        self.is_finished = False
        self.is_processing = False
        self.is_interrupted = False

    def get(self):
        return {
            "place": self.place,
            "priority": self.priority,
            "is_finished": self.is_finished,
            "is_processing": self.is_processing,
            "is_interrupted": self.is_interrupted
        }


class _APIRequest:
    def __init__(self, response: discord.InteractionMessage, response_id: int, prioritization: int):
        self.prioritization = prioritization

        self.response_object = response
        self.snowflake_id = str(response_id)

        current_time = time.time()

        self.birth_time = current_time
        self.processing_start_time = current_time

        self.status = _APIRequestStatus()

    def get_snowflake_id(self):
        return self.snowflake_id

    def get_lifetime(self):
        return time.time() - self.birth_time

    def get_waiting_time(self):
        return self.processing_start_time - self.birth_time

    def get_processing_time(self):
        return time.time() - self.processing_start_time

    def get_prioritization(self):
        return self.prioritization

    def mark_processing(self):
        self.processing_start_time = time.time()

        self.status.is_processing = True

    def mark_finished(self):
        self.status.is_finished = True

    def mark_interrupted(self):
        self.status.is_interrupted = True


class _Text2ImgOptions:
    def __init__(self, prompt, neg_prompt, steps, count, seed, cfg_scale, width, height, sampler):
        self.prompt = prompt
        self.neg_prompt = neg_prompt
        self.steps = steps
        self.count = count
        self.seed = seed if seed != -1 else random.randint(0, 2 ** 32)
        self.cfg_scale = cfg_scale
        self.width = width
        self.height = height
        self.sampler = sampler

    def get(self):
        return {
                "prompt": self.prompt,
                "negative_prompt": self.neg_prompt,
                "steps": self.steps,
                "batch_size": self.count,
                "seed": self.seed,
                "cfg_scale": self.cfg_scale,
                "width": self.width,
                "height": self.height,
                "sampler_name": self.sampler,
                "firstphase_width": min(self.width, 768),
                "firstphase_height": min(self.height, 768),
                "enable_hr": True if self.width > 768 or self.height > 768 else False
            }


class Text2Img(_APIRequest):
    def __init__(self, prompt, neg_prompt, steps, count, seed, cfg_scale, width, height, sampler, response, response_id, prioritization=1):
        super().__init__(response, response_id, prioritization=prioritization)

        self.options = _Text2ImgOptions(
            prompt,
            neg_prompt,
            steps,
            count,
            seed,
            cfg_scale,
            width,
            height,
            sampler
        )


class _UpscaleOptions:
    def __init__(self, origin: str, image_index: int, multiplier: int, upscaler: str, snowflake_id: int):
        self.origin = origin
        self.image_index = image_index
        self.multiplier = multiplier
        self.upscaler = upscaler
        self.snowflake_id = snowflake_id

    def get(self):
        return {
            "origin": self.origin,
            "image_index": self.image_index,
            "multiplier": self.multiplier,
            "upscaler": self.upscaler
        }

    def get_payload(self):
        return {
            "upscaling_resize": self.multiplier,
            "upscaler_1": self.upscaler,
            "image": "data:image/png;base64," + base64.b64encode(open(os.path.join("temp", self.origin, str(self.snowflake_id), f"image_{self.image_index}.png"), 'rb').read()).decode('utf-8')
        }


class Upscale(_APIRequest):
    def __init__(self, origin: str, image_index: int, multiplier: int, upscaler: str, response, response_id, prioritization: int):
        super().__init__(response, response_id, prioritization)

        self.options = _UpscaleOptions(origin, image_index, multiplier, upscaler, response_id)




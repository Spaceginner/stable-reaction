import random
import time

from modules import progress


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
    def __init__(self, inference_id: int, prioritization: int, author_id: int, author_name: str):
        self.prioritization = prioritization

        self.snowflake_id = str(inference_id)

        current_time = time.time()

        self.birth_time = current_time
        self.processing_start_time = current_time

        self.status = _APIRequestStatus()

        self.author_id = author_id
        self.author_name = author_name

    def get_inference_id(self):
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
    def __init__(self, prompt, neg_prompt, steps, count, seed, cfg_scale, width, height, sampler, inference_id, author_id, author_name, prioritization):
        super().__init__(inference_id, prioritization, author_id, author_name)

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

        self.progress = progress.Progress(steps)


class _UpscaleOptions:
    def __init__(self, image_index: int, multiplier: int, upscaler: str, base_id: str):
        self.image_index = image_index
        self.multiplier = multiplier
        self.upscaler = upscaler
        self.base_id = base_id

    def get(self):
        return {
            "image_index": self.image_index,
            "multiplier": self.multiplier,
            "upscaler": self.upscaler,
            "base_id": self.base_id
        }

    def get_payload(self):
        return {
            "upscaling_resize": self.multiplier,
            "upscaler_1": self.upscaler,
        }


class Upscale(_APIRequest):
    def __init__(self, image_index: int, multiplier: int, upscaler: str, inference_id, base_inference_id, author_id, author_name, prioritization: int):
        super().__init__(inference_id, prioritization, author_id, author_name)

        self.options = _UpscaleOptions(image_index, multiplier, upscaler, base_inference_id)
        self.base_inference_id = base_inference_id

    def get_base_inference_id(self):
        return self.base_inference_id

def convert(request_type_str: str):
    options = ["txt2img", "upscale"]
    if request_type_str not in options:
        raise ValueError(f"Unrecognized request type: {request_type_str}. Available options: {','.join(options)}")

    if request_type_str == "txt2img":
        return Text2Img
    elif request_type_str == "upscale":
        return Upscale


import math
import threading
from typing import Type

from modules.singleton import SingletonMetaclass
from modules.api import inference
from modules.api.request_types import Text2Img, Upscale


def _get_priority(item):
    if item is None:
        return 10000
    else:
        return item.status.get()["priority"]


class Queue(metaclass=SingletonMetaclass):
    def __init__(self, forced_prioritization_seconds: float, waiting_reward: float):
        self.waiting_reward = waiting_reward

        self.requests = []
        self.lock = threading.Lock()
        self.current_request: Text2Img | Upscale | None = None

        max_forced_prioritization_seconds = (9 * waiting_reward ** 4) / (2 * waiting_reward ** 3)
        if forced_prioritization_seconds > max_forced_prioritization_seconds:
            raise ValueError("forced_prioritization_seconds is too high, maximal value: {}".format(max_forced_prioritization_seconds))

        self.enigma = (9 * waiting_reward ** 2 - 3 * math.sqrt(9 * waiting_reward ** 4 - 2 * waiting_reward ** 3 * forced_prioritization_seconds) - waiting_reward * forced_prioritization_seconds) / forced_prioritization_seconds

    def put(self, request: Text2Img | Upscale | None):
        with self.lock:
            self.requests.append(request)

    def get(self):
        with self.lock:
            return self.requests.pop(0)

    def safe_get(self, snowflake_id, request_type: Type[Text2Img] | Type[Upscale]):
        with self.lock:
            for request in self.requests:
                if request.get_inference_id() == snowflake_id and type(request) == request_type:
                    return request

            return self.current_request

    def get_status(self, snowflake_id, request_type: Type[Text2Img] | Type[Upscale]):
        with self.lock:
            for request in self.requests:
                if request.get_inference_id() == snowflake_id and type(request) == request_type:
                    return request.status.get()

            return self.current_request.status.get()

    def delete(self, snowflake_id, request_type: Type[Text2Img] | Type[Upscale]):
        with self.lock:
            for index, request in enumerate(self.requests):
                if request.get_inference_id() == snowflake_id and type(request) == request_type:
                    self.requests.pop(index)

    def prioritize(self):
        if len(self.requests) == 0:
            return

        with self.lock:
            for request in self.requests:
                if request is None:
                    continue

                prioritization = request.get_prioritization()
                lifetime = request.get_lifetime()

                if prioritization == 1:
                    priority = lifetime / self.enigma + lifetime / self.waiting_reward
                else:
                    priority = 3 * prioritization * math.sqrt(lifetime / (prioritization * self.enigma))

                request.status.priority = priority

            self.requests.sort(key=_get_priority, reverse=True)

    def update_status(self):
        with self.lock:
            for i, request in enumerate(self.requests):
                request.status.place = i + 1

    def process(self, api: inference.API):
        while True:
            if len(self.requests) == 0:
                continue

            if None in self.requests:
                break

            self.current_request: Text2Img = self.get()

            if isinstance(self.current_request, Text2Img):
                api.txt2img(self.current_request)
            elif isinstance(self.current_request, Upscale):
                api.upscale(self.current_request)

    def update_requests(self):
        while True:
            if len(self.requests) == 0:
                continue

            if None in self.requests:
                break

            self.prioritize()
            self.update_status()

    def __len__(self):
        return len(self.requests)

    def __contains__(self, item):
        return item in self.requests

import math
from threading import Lock
from typing import Type

from modules.utils import ArgumentError
from modules.api import inference
from modules.api.request_types import *


def _get_priority(item):
    if item is None:
        return 10000
    else:
        return item.status.get()["priority"]


class Queue:
    def __init__(self, forced_prioritization_seconds: float, waiting_reward: float):
        self.waiting_reward = waiting_reward

        self.requests = []
        self.current_request = None
        self.lock = Lock()

        max_forced_prioritization_seconds = (9 * waiting_reward ** 4) / (2 * waiting_reward ** 3)
        if forced_prioritization_seconds > max_forced_prioritization_seconds:
            raise ArgumentError("Argument `forced_prioritization_seconds` is too high, maximal value: {}".format(max_forced_prioritization_seconds))

        self.enigma = (9 * waiting_reward ** 2 - 3 * math.sqrt(9 * waiting_reward ** 4 - 2 * waiting_reward ** 3 * forced_prioritization_seconds) - waiting_reward * forced_prioritization_seconds) / forced_prioritization_seconds

    def put(self, request: Text2Img | Upscale | None):
        self.lock.acquire()
        self.requests.append(request)
        self.lock.release()

    def get(self):
        self.lock.acquire()
        return_value = self.requests.pop(0)
        self.lock.release()
        return return_value

    def safe_get(self, snowflake_id, request_type: Type[Text2Img] | Type[Upscale]):
        for request in self.requests:
            if request.get_snowflake_id() != snowflake_id or not isinstance(request, request_type):
                continue

            return request

        return self.current_request

    def get_status(self, snowflake_id, request_type: Type[Text2Img] | Type[Upscale]):
        for request in self.requests:
            if request.get_snowflake_id() != snowflake_id or not isinstance(request, request_type):
                continue

            return request.status.get()

        return self.current_request.status.get()

    def delete(self, snowflake_id, request_type: Type[Text2Img] | Type[Upscale], webui_url):
        self.lock.acquire()

        for index, request in enumerate(self.requests):
            if request.get_snowflake_id() != snowflake_id or not isinstance(request, request_type):
                continue

            self.requests.pop(index)

            self.lock.release()
            return

        inference.interrupt(webui_url)

        self.lock.release()

    def prioritize(self):
        if len(self.requests) == 0:
            return

        self.lock.acquire()

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

        self.lock.release()

    def update_status(self):
        self.lock.acquire()
        for i, request in enumerate(self.requests):
            request.status.place = i + 1
        self.lock.release()

    def process(self, api_url: str):
        while True:
            if len(self.requests) == 0:
                continue

            if self.requests.__contains__(None):
                break

            self.current_request = self.get()

            if isinstance(self.current_request, Text2Img):
                inference.txt2img(api_url, self.current_request)
            elif isinstance(self.current_request, Upscale):
                inference.upscale(api_url, self.current_request)

            self.current_request = None

    def update_requests(self):
        while True:
            if len(self.requests) == 0:
                continue

            if self.requests.__contains__(None):
                break

            self.prioritize()
            self.update_status()

    def __len__(self):
        return len(self.requests)

    def __contains__(self, item):
        return self.requests.__contains__(item)

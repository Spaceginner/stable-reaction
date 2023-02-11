import math

from modules.localization import Localization


class Progress:
    def __init__(self, total_steps):
        self._progress: float = 0.0
        self._is_finishing: bool = False
        self._is_started: bool = False

        self._total_steps = total_steps

    def reset(self):
        self.__init__(self._total_steps)

    def reset_flags(self):
        progress = self._progress
        self.reset()
        self._progress = progress

    def get_is_finishing(self):
        self._update_is_finishing()

        return self._is_finishing

    def get_is_started(self):
        self._update_is_started()

        return self._is_finishing

    def set_progress(self, progress):
        self._progress = progress

    def __str__(self):
        self._update_flags()

        return f"{Localization(str()).get_localization('bot')['messages']['start_wait']}..." if not self._is_started else f"{round(max(self._progress - 0.01, 0) * 100)}%" if not self._is_finishing else f"{Localization(str()).get_localization('bot')['messages']['finish_wait']}..."

    def _update_flags(self):
        self._update_is_finishing()
        self._update_is_started()

    def _update_is_finishing(self):
        self._is_finishing = self._is_finishing if self._is_finishing else self._progress >= math.floor((self._total_steps - 1) / self._total_steps * 100) / 100 + 0.01  # We need a precision of at least one decimal to be sure we are accurate enough

    def _update_is_started(self):
        self._is_started = self._is_started if self._is_started else self._progress not in [0, 0.01]

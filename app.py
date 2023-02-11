import asyncio
import os.path
import signal
import threading

import discord

from modules.localization import Localization
from modules.config import Config
from modules.api import inference, queue
from modules.settings import Settings


async def main():
    config = Config(str(), str())
    local = Localization(str())

    print(local.get_localization("console")["start"])

    # Discord bot instance and events listeners
    bot = discord.Bot(debug_guilds=[1005722426941915187, 1070385362205155408])

    @bot.event
    async def on_ready():
        print(local.get_localization("console")["bot_launched"])

    # Loading cogs
    from cogs.inference import diffuse
    from cogs.utils import ping, settings

    bot.add_cog(diffuse.Diffuse(bot))

    bot.add_cog(ping.Ping(bot))
    bot.add_cog(settings.Settings(bot))

    # Launching bot
    print(local.get_localization("console")["bot_launches"])
    await bot.start(config.get_environment()["token"] if config.get_environment() else config.get_bot()['token'])


def launch():
    print("Press CRTL + C to exit\n")

    config = Config("config.yaml", "environment.json")
    api = inference.API(config.get_inference()['url'])
    config.init_remote(api)
    settings = Settings(os.path.join("data", "user"))

    local = Localization(config.get_general()['locale'])

    # Setting up a queue
    api_request_queue = queue.Queue(45, 10)

    queue_processor_thread = threading.Thread(target=api_request_queue.process, args=(api,))
    queue_requests_updater_thread = threading.Thread(target=api_request_queue.update_requests)

    queue_processor_thread.start()
    queue_requests_updater_thread.start()

    asyncio.run(main())


if __name__ == "__main__":
    # code was stolen from a1111's webui
    # make the program just exit at ctrl+c without waiting for anything
    def sigint_handler(sig, frame):
        print("Interrupted with signal {} in {}".format(sig, frame))
        os._exit(0)

    signal.signal(signal.SIGINT, sigint_handler)

    launch()

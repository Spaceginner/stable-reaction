# Stable Reaction

## About

A discord bot that allows to use Stable Diffusion with Midjourney-like feel.
Uses an API from [AUTOMATIC1111's WebUI](https://github.com/AUTOMATIC1111/stable-diffusion-webui) for interfering with Stable Diffusion

## How to use

It provides few commands for now:

- `/diffuse` — txt2img inference

- `/settings` — change settings on per-user bases

- `/ping` — allows to ping a bot

And also provides buttons:

- `Cancle Job` — equivalent to `Interrupt` button in the WebUI

- `S<N>` — where `<N>` is the image number; provides unchanged generated image

- `U<N>` — where `<N>` is the image number; upscales image with the user settings

- `Info` — shows all information about the job

- `Regen` — regenerates the request with the same parameteres, except for the seed

## Installation

1. Install [AUTOMATIC1111's WebUI](https://github.com/AUTOMATIC1111/stable-diffusion-webui) and launch it with `--api` flag

2. Clone this repository in any* folder using this command:

```commandline
git clone https://github.com/Spaceginner/stable-reaction
```

*In folders that don't require administrative privileges to create and edit files in them

3. Now, you have to activate venv, run this in Stable Reaction folder if you have Windows:

```commandline
cd venv\Scripts\
.\activate
cd ..\..\
```

or this if you have anything else than Windows:

```commandline
cd venv\bin\
.\activate
cd ..\..\
```

4. Then install all dependencies by running this command:

```commandline
pip install -r requirements.txt
```

5. Go to [Discord Developer Portal](https://discord.com/developers/) and create
a new application

6. Go to `Bot` tab and create a bot, then press `Reset Token` and copy a token
**DO NOT SHARE TOKEN WITH ANYBODY**. Then open `config.yaml` with any text editor
and put your token in `token` field.

7. To invite a bot to your server, go to `OAuth2` tab in [Discord Developer Portal](https://discord.com/developers/)
and then go to `URL Generator`, then select following scopes: `bot`, `applications.commands`
and these permissions: `Send Messages`, `Send Messages in Threads`, `Attach Files`,
`Use Slash Commands`. At the bottom you will have an invite link.

7. If you changed default URL in [AUTOMATIC1111's WebUI](https://github.com/AUTOMATIC1111/stable-diffusion-webui), then open `config.yaml` and change `webui_url` field respectively .

9. Launch this bot (make sure venv is still active):

```commandline
python app.py
```

10. To test it, issue this command in discord: `/diffuse prompt:austronaut on a horse in space, Earth, concept art`

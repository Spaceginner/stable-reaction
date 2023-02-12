# Stable Reaction

## About

A discord bot that allows to use Stable Diffusion with Midjourney-like feel.
Uses an API from [AUTOMATIC1111's WebUI](https://github.com/AUTOMATIC1111/stable-diffusion-webui) for interfering with Stable Diffusion

## Community

### Where to find

I live in [Discord server](https://discord.gg/7a7s9ausfz)

### Contribution

if you want to help this project, go to its [todo list](https://github.com/users/Spaceginner/projects/3)
and implement something from there, it would help a lot

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

3. Create venv using following:

```commandline
python -m venv venv
```

4. Now, you have to activate venv, run this in Stable Reaction folder if you have Windows:

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

5. Then install all dependencies by running this command:

```commandline
pip install -r requirements.txt
```

6. Go to [Discord Developer Portal](https://discord.com/developers/) and create
a new application

7. Go to `Bot` tab and create a bot, then press `Reset Token` and copy a token
**DO NOT SHARE TOKEN WITH ANYBODY**. Then open `config.yaml` with any text editor
and put your token in `token` field.

8. To invite a bot to your server, go to `OAuth2` tab in [Discord Developer Portal](https://discord.com/developers/)
and then go to `URL Generator`, then select following scopes: `bot`, `applications.commands`
and these permissions: `Send Messages`, `Send Messages in Threads`, `Attach Files`,
`Use Slash Commands`. At the bottom you will have an invite link.

8.1. (Optional) You can change the bot icon in `Application` tab, just click upload an icon,
the icon itself you can find in `resources\icon\` folder, you are interested in `final.png`

9. If you changed default URL in [AUTOMATIC1111's WebUI](https://github.com/AUTOMATIC1111/stable-diffusion-webui),
10. then open `config.yaml` and change `webui_url` field respectively.

10. Launch this bot (make sure venv is still active):

```commandline
python app.py
```

11. To test it, issue this command in discord: `/diffuse prompt:austronaut on a horse in space, Earth, concept art`

## Credits

### Libraries

Used libraries: [PIL (Pillow)](https://pypi.org/project/Pillow/), [PyCord](https://pypi.org/project/py-cord/),
[requests](https://pypi.org/project/requests/) and [PyYAML](https://pypi.org/project/PyYAML/)

### Icon
Tool used: [Pattern Collider](https://aatishb.com/patterncollider/)

Bot icon's pattern: [link](https://aatishb.com/patterncollider/?symmetry=19&pattern=0.5&radius=38&zoom=0.91&stroke=84&hue=316&hueRange=139&contrast=33&sat=67&orientationColoring=true)
    
To convert from SVG to PNG [ImageMagick](https://imagemagick.org/) was used with the following command:
    
```
convert .\original.svg -resize 1024x1024^ -gravity center -crop 1024x1024+0+0 +repage .\final.png
```

## License

This project is licensed under GPL-3.0 license



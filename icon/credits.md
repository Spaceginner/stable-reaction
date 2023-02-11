Tool used: [Pattern Collider](https://aatishb.com/patterncollider/)

Bot icon's pattern: [link](https://aatishb.com/patterncollider/?symmetry=19&pattern=0.5&radius=38&zoom=0.91&stroke=84&hue=316&hueRange=139&contrast=33&sat=67&orientationColoring=true)

To convert from SVG to PNG [ImageMagick](https://imagemagick.org/) was used with the following command:

```
convert .\original.svg -resize 1024x1024^ -gravity center -crop 1024x1024+0+0 +repage .\final.png
```

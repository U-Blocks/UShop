![header](https://capsule-render.vercel.app/api?type=venom&height=150&color=gradient&text=UShop&fontColor=0:8871e5,100:b678c4&fontSize=50&desc=A%20powerful%20shop%20system%20plug-in%.&descAlignY=80&descSize=20&animation=fadeIn)

****

<code><a href="https://github.com/umarurize/UShop"><img height="25" src="https://github.com/umarurize/UShop/blob/master/logo/UShop.jpg" alt="UShop" /></a>&nbsp;UShop</code>

[![Minecraft - Version](https://img.shields.io/badge/minecraft-v1.21.60_(Bedrock)-black)](https://feedback.minecraft.net/hc/en-us/sections/360001186971-Release-Changelogs)
[![PyPI - Version](https://img.shields.io/pypi/v/endstone)](https://pypi.org/project/endstone)

### Introductions
* **Rich features:** `good purchase`, `good recycling`, `good collection`
* **Easy to edit:** `good category add/remove/edit`, `good add/remove/edit`
* **Full GUI:** Beautiful GUI forms for easy operation rather than commands.
* **Hot reload support:** Operators can edit/update `config.json` or `shop.json` in game directly.

### Installation
[Required pre-plugin] UMoney

[Optional pre-plugin] ZX_UI

Put `.whl` file into the endstone plugins folder, and then start the server. Enter the command `/us` to call out the main form.

### Download
Now, you can get the release version form this repo or <code><a href="https://www.minebbs.com/resources/ushop.10103/"><img height="20" src="https://github.com/umarurize/umaru-cdn/blob/main/images/minebbs.png" alt="Minebbs" /></a>&nbsp;Minebbs</code>.

### File structure
```
Plugins/
├─ ushop/
│  ├─ config.json
│  ├─ shop.json
│  ├─ good-collection.json
```

### Configuration
UShop allows operators or players to edit/update relevant settings through GUI forms with ease, here are just simple explanations for relevant configurations.

To add/remove/edit good categories or remove/edit goods, operators only need to operate through GUI forms。

To add goods to target good category, operators only need to turn on the `product add mode` and then interact with the ground with the target good in hand.

`config.json`
```json
{
    "reclaim_rate": 0.6 // discount rate when recycling goods (it should be a decimal less than 1.0 but more than 0.0) 
}
```

`shop.json`
```json
{
    "blocks-building blocks-logs": {
        "category_icon": "textures/blocks/log_oak",
        "minecraft:oak_log": {
            "good_name": "Oak Log",
            "good_price": 32
        }
}
```

### Screenshots
You can view related screenshots of UShop from images folder of this repo.

### Development plans
As soon as the NBT API of EndstoneMC is available, Ushop will roll out the `player shop` feature

![](https://img.shields.io/badge/language-python-blue.svg) [![GitHub License](https://img.shields.io/github/license/umarurize/UTP)](LICENSE)

## UShop

<code><a href="https://github.com/umarurize/UShop"><img height="25" src="https://github.com/umarurize/UShop/blob/master/logo/UShop.jpg" alt="UShop" /></a>&nbsp;UShop</code>

![Total Git clones](https://img.shields.io/badge/dynamic/json?label=Total%20Git%20clones&query=$&url=https://cdn.jsdelivr.net/gh/umarurize/UShop@master/clone_count.txt&color=brightgreen)
![GitHub Downloads (all assets, all releases)](https://img.shields.io/github/downloads/umarurize/UShop/total)

### :bell:Introductions
* **Multiple ecnonomy cores support**
    *  UMoney
    *  arc_core 
* **Easy to create shop categories**
    *  Shop categories' icons can be automatically created
    *  Shop categories can be edited at any time through GUI forms
* **Easy to add goods**
    *  goods' names can be automatically getted (local languages support)
    *  goods' icons can be automatically getted
    *  goods' attributes can be automatically getted
        *  enchantments (local languages support)
        *  lore
        *  type
    *  goods' purchase price and reclaim price can be set independently
    *  three good modes are provided
        *  purchase and reclaim
        *  only purchase
        *  only reclaim
    *  goods can be edited at any time through GUI forms
*  **Accurate players' inventory detection**
*  **Items' durability can be detected during reclaiming process**
*  **Good collections**
*  **Good search**
*  **DLCs**
   *  [ULore](https://github.com/umarurize/ULore) (A plugin that allows you to add or edit lore for items)
   *  Player shop (under development)
   *  Customizable disenchantment (under development)
*  **Full GUI support**
*  **Hot reload support**
*  **Local languages support**
        
### :hammer:Installation
<details>
<summary>Check your Endstone's version</summary>

*  **Endstone 0.10.0+**
   *   250816
*  **Endstone 0.7.3 - Endstone 0.8.2**
    *  250511 
*  **Endstone 0.6.0 - Endstone 0.7.2**
    *  250309
    *  250227
    
</details>

[Optional pre-plugin] [UMoney](https://github.com/umarurize/UMoney)

[Optional pre-plugin] [arc_core](https://github.com/DEVILENMO/EndstoneMC-ARC-Core-Plugin)

*At least one of UMoney and arc_core should be installed on the server*

[Optional pre-plugin] ZX_UI

Put `.whl` file into the endstone plugins folder, and then start the server. Enter the command `/us` to call out the main form.

### :computer:Download
Now, you can get the release version form this repo or <code><a href="https://www.minebbs.com/resources/ushop.10103/"><img height="20" src="https://github.com/umarurize/umaru-cdn/blob/main/images/minebbs.png" alt="Minebbs" /></a>&nbsp;Minebbs</code>.

### :file_folder:File structure
```
Plugins/
├─ ushop/
│  ├─ textures.json
│  ├─ config.json
│  ├─ shop.json
│  ├─ lang/
│  │  ├─ zh_CN.json
│  │  ├─ en_US.json
```

### :pencil:Configuration
UShop allows operators or players to edit/update relevant settings through GUI forms with ease, here are just simple explanations for relevant configurations.

`config.json`
```json5
{
    "good_reclaim_durability_threshold": 0.5
}
/**
 * This will have an impact during reclaiming process (if the target item has duraibility attribute)
 * If set to 0.0, the durability detection will not work
 * If set to 1.0, the target item to reclaim must be brand new
 */
```

`shop.json`
```json5
{
    "test": {   // shop category's name
        "673e2c6f5e0f9c7003548fdeaad81f4ba170eb49d4aefe0b90c6152035ea305b": {    // good's hex dig
            "good_type_translation_key": "item.diamond_sword.name",    // good's translation key
            "good_type_id": "minecraft:diamond_sword",    // good's type
            "good_enchants": {    // good's enchant(s)
                "fire_aspect": 1,
                "unbreaking": 3,
                "sharpness": 5,
                "knockback": 2,
                "mending": 1
            },
            "good_lore": [    // good's lore
                "Sword Art Online",
                "oh yeah"
            ],
            "good_purchase_price": 2000,    // good's purchase price
            "good_reclaim_price": 1000,    // good's reclaim price
            "good_mode": "purchase and reclaim",    // good's mode
            "collectors": []    // players who have collected this good
        }
    }
}
```

### :globe_with_meridians:Languages
- [x] `zh_CN`
- [x] `en_US`

Off course you can add your mother language to UShop, just creat `XX_XX.json` (such as `ja_JP.json`) and translate value with reference to `en_US.json`.

You can also creat a PR to this repo to make your mother language one of the official languages of UShop.

### :camera:Screenshots
You can view related screenshots of UShop from images folder of this repo.

### :fire:Operation document
you can download the operation document folder of this repo to learn how to use UShop.

<div style="width: 100%; text-align: center;">
  <img src="https://github.com/umarurize/UShop/blob/master/logo/UShop2.png" style="max-width: 100%; height: auto;">
</div>

</br>

![](https://img.shields.io/badge/language-python-blue.svg) [![GitHub License](https://img.shields.io/github/license/umarurize/UTP)](LICENSE)

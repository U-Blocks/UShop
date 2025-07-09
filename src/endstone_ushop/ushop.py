import os
import json
import hashlib
import datetime

from endstone import ColorFormat, Player, NamespacedKey
from endstone.plugin import Plugin
from endstone.inventory import ItemStack
from endstone.command import Command, CommandSender, CommandSenderWrapper
from endstone.form import ActionForm, ModalForm, Dropdown, TextInput
from endstone.event import event_handler, PlayerInteractEvent, ServerCommandEvent

from endstone_ushop.lang import load_langs
from endstone_ushop.textures import load_textures

current_dir = os.getcwd()

first_dir = os.path.join(current_dir, 'plugins', 'ushop')

if not os.path.exists(first_dir):
    os.mkdir(first_dir)

shop_data_file_path = os.path.join(first_dir, 'shop.json')

config_data_file_path = os.path.join(first_dir, 'config.json')

langs_dir = os.path.join(first_dir, 'langs')

if not os.path.exists(langs_dir):
    os.mkdir(langs_dir)


class ushop(Plugin):
    api_version = '0.9'

    def __init__(self):
        super().__init__()

        # Load shop data
        if not os.path.exists(shop_data_file_path):
            shop_data = {}
            with open(shop_data_file_path, 'w', encoding='utf-8') as f:
                json_str = json.dumps(shop_data, indent=4, ensure_ascii=False)
                f.write(json_str)
        else:
            with open(shop_data_file_path, 'r', encoding='utf-8') as f:
                shop_data = json.loads(f.read())
        self.shop_data = shop_data

        # Load config data
        if not os.path.exists(config_data_file_path):
            config_data = {
                'good_reclaim_durability_threshold': 0.5
            }
            with open(config_data_file_path, 'w', encoding='utf-8') as f:
                json_str = json.dumps(config_data, indent=4, ensure_ascii=False)
                f.write(json_str)
        else:
            with open(config_data_file_path, 'r', encoding='utf-8') as f:
                config_data = json.loads(f.read())
        self.config_data = config_data

        # Load langs
        self.langs = load_langs(langs_dir)

        # Load textures
        self.textures = load_textures()

        self.good_enchant_translation_keys = {}

    def on_enable(self):
        # Check whether pre-plugin UMoney is installed.
        if self.server.plugin_manager.get_plugin('umoney') is None:
            self.logger.error(
                f'{ColorFormat.RED}'
                f'Pre-plugin UMoney is required...'
            )

            self.server.plugin_manager.disable_plugin(self)

        self.command_sender = CommandSenderWrapper(
            self.server.command_sender,
            on_message=None
        )

        self.register_events(self)

        self.logger.info(f'{ColorFormat.YELLOW}UShop is enabled...')

    commands = {
        'us': {
            'description': 'Call out main form of UShop',
            'usages': ['/us'],
            'permissions': ['ushop.command.us']
        },
        'ustr': {
            'description': 'Convert old shop data to brand new',
            'usages': ['/ustr'],
            'permissions': ['ushop.command.ustr']
        }
    }

    permissions = {
        'ushop.command.us': {
            'description': 'Call out main form of UShop',
            'default': True
        },
        'ushop.command.ustr': {
            'description': 'Convert old shop data to brand new',
            'default': True
        }
    }

    def on_command(self, sender: CommandSender, command: Command, args: list[str]) -> None:
        if command.name == 'ustr':
            if isinstance(sender, Player):
                sender.send_message(
                    f'{ColorFormat.RED}'
                    f'This command can only be executed by console...'
                )

                return

        if command.name == 'us':
            if not isinstance(sender, Player):
                sender.send_message(
                    f'{ColorFormat.RED}'
                    f'This command can only be executed by a player...'
                )
                return

            player = sender

            player_money = self.server.plugin_manager.get_plugin('umoney').api_get_player_money(player.name)

            main_form = ActionForm(
                title=f'{ColorFormat.BOLD}{ColorFormat.LIGHT_PURPLE}'
                      f'{self.get_text(player, "main_form.title")}',
                content=f'{ColorFormat.GREEN}'
                        f'{self.get_text(player, "your_money")}: '
                        f'{ColorFormat.WHITE}'
                        f'{player_money}\n'
                        f'\n'
                        f'{ColorFormat.GREEN}'
                        f'{self.get_text(player, "main_form.content")}'
            )

            # Button - Official shop
            main_form.add_button(
                f'{ColorFormat.YELLOW}'
                f'{self.get_text(player, "main_form.button.official_shop")}',
                icon='textures/ui/permissions_op_crown',
                on_click=self.official_shop
            )

            # Button - Player shop
            main_form.add_button(
                f'{ColorFormat.YELLOW}'
                f'{self.get_text(player, "main_form.button.player_shop")}',
                icon='textures/ui/FriendsIcon',
                on_click=self.player_shop
            )

            # Button - Reload configurations
            if player.is_op:
                main_form.add_button(
                    f'{ColorFormat.YELLOW}'
                    f'{self.get_text(player, "main_form.reload_config")}',
                    icon='textures/ui/icon_setting',
                    on_click=self.reload_config_r
                )

            if self.server.plugin_manager.get_plugin('ZX_UI') is not None:
                main_form.on_close = self.back_to_menu

                main_form.add_button(
                    f'{ColorFormat.YELLOW}'
                    f'{self.get_text(player, "main_form.button.back_to_zx_ui")}',
                    icon='textures/ui/refresh_light',
                    on_click=self.back_to_menu
                )
            else:
                main_form.on_close = None

                main_form.add_button(
                    f'{ColorFormat.YELLOW}'
                    f'{self.get_text(player, "main_form.button.close")}',
                    icon='textures/ui/cancel',
                    on_click=None
                )

            player.send_form(main_form)

    # Official shop: main form
    def official_shop(self, player: Player):
        player_money = self.server.plugin_manager.get_plugin('umoney').api_get_player_money(player.name)

        official_shop_form = ActionForm(
            title=f'{ColorFormat.BOLD}{ColorFormat.LIGHT_PURPLE}'
                  f'{self.get_text(player, "official_shop_main_form.title")}',
            content=f'{ColorFormat.GREEN}'
                    f'{self.get_text(player, "your_money")}: '
                    f'{ColorFormat.WHITE}'
                    f'{player_money}\n'
                    f'\n'
                    f'{ColorFormat.GREEN}'
                    f'{self.get_text(player, "official_shop_main_form.content")}',
            on_close=self.back_to_main_form
        )

        if player.is_op:
            # Button - Official shop: add good category
            official_shop_form.add_button(
                f'{ColorFormat.YELLOW}'
                f'{self.get_text(player, "official_shop_main_form.add_shop_category")}',
                icon='textures/ui/color_plus',
                on_click=self.official_shop_add_shop_category
            )

            # Button - Official shop: add good
            official_shop_form.add_button(
                f'{ColorFormat.YELLOW}'
                f'{self.get_text(player, "official_shop_main_form.add_good")}',
                icon='textures/ui/color_plus',
                on_click=self.official_shop_add_good
            )

            # Button - Official shop: add lore for item(s)
            official_shop_form.add_button(
                f'{ColorFormat.YELLOW}'
                f'{self.get_text(player, "official_shop_main_form.add_lore")}',
                icon='textures/ui/color_plus',
                on_click=self.official_shop_add_lore
            )

        # Button - Official shop: good collections
        official_shop_form.add_button(
            f'{ColorFormat.YELLOW}'
            f'{self.get_text(player, "official_shop_main_form.good_collections")}',
            icon='textures/ui/icon_blackfriday',
            on_click=self.official_shop_good_collections
        )

        # Button - Official shop: good search
        official_shop_form.add_button(
            f'{ColorFormat.YELLOW}'
            f'{self.get_text(player, "official_shop_main_form.search_good")}',
            icon='textures/ui/magnifyingGlass',
            on_click=self.official_shop_search_good
        )

        # Button - Back to main form
        official_shop_form.add_button(
            f'{ColorFormat.YELLOW}'
            f'{self.get_text(player, "button.back")}',
            icon='textures/ui/refresh_light',
            on_click=self.back_to_main_form
        )

        # Buttons - Official shop: categories
        for shop_category, shop_category_info in self.shop_data.items():
            if len(shop_category_info) == 0:
                shop_category_button_icon = ''
            else:
                temple_list = list(shop_category_info.items())

                shop_category_button_icon = self.get_texture(temple_list[0][1]['good_type_id'])

            official_shop_form.add_button(
                f'{ColorFormat.YELLOW}'
                f'{shop_category}',
                icon=shop_category_button_icon,
                on_click=self.official_shop_single_shop_category(shop_category)
            )

        player.send_form(official_shop_form)

    # Official shop: add shop category
    def official_shop_add_shop_category(self, player: Player) -> None:
        textinput = TextInput(
            label=f'{ColorFormat.GREEN}'
                  f'{self.get_text(player, "official_shop_add_shop_category_form.textinput.label")}',
            placeholder=self.get_text(player, "official_shop_add_shop_category_form.textinput.placeholder")
        )

        official_shop_add_shop_category_form = ModalForm(
            title=f'{ColorFormat.BOLD}{ColorFormat.LIGHT_PURPLE}'
                  f'{self.get_text(player, "official_shop_add_shop_category_form.title")}',
            controls=[
                textinput,
            ],
            submit_button=f'{ColorFormat.YELLOW}'
                          f'{self.get_text(player, "official_shop_add_shop_category_form.submit_button")}',
            on_close=self.official_shop
        )

        def on_submit(p: Player, json_str: str):
            data = json.loads(json_str)

            if len(data[0]) == 0:
                p.send_message(
                    f'{ColorFormat.RED}'
                    f'{self.get_text(p, "message.type_error")}'
                )
                return

            shop_category_list = [key for key in self.shop_data.keys()]

            if data[0] in shop_category_list:
                p.send_message(
                    f'{ColorFormat.RED}'
                    f'{self.get_text(p, "official_shop_add_shop_category.message.fail")}: '
                    f'{ColorFormat.WHITE}' +
                    self.get_text(p, "official_shop_add_shop_category.message.fail.reason").format(data[0]))
                return

            shop_category = data[0]

            self.shop_data[shop_category] = {}
            self.save_shop_data()

            p.send_message(
                f'{ColorFormat.YELLOW}'
                f'{self.get_text(p, "official_shop_add_shop_category.message.success")}')

        official_shop_add_shop_category_form.on_submit = on_submit

        player.send_form(official_shop_add_shop_category_form)

    # Official shop: single shop category
    def official_shop_single_shop_category(self, shop_category):
        def on_click(player: Player):
            player_money = self.server.plugin_manager.get_plugin('umoney').api_get_player_money(player.name)

            official_shop_single_shop_category_form = ActionForm(
                title=f'{ColorFormat.BOLD}{ColorFormat.LIGHT_PURPLE}'
                      f'{shop_category}',
                content=f'{ColorFormat.GREEN}'
                        f'{self.get_text(player, "your_money")}: '
                        f'{ColorFormat.WHITE}{player_money}\n'
                        f'\n'
                        f'{ColorFormat.GREEN}'
                        f'{self.get_text(player, "tags")}:\n'
                        f'{ColorFormat.LIGHT_PURPLE}'
                        f'+ '
                        f'{ColorFormat.WHITE}'
                        f'{self.get_text(player, "has_enchants")}\n'
                        f'{ColorFormat.AQUA}'
                        f'+ '
                        f'{ColorFormat.WHITE}'
                        f'{self.get_text(player, "has_lore")}\n'
                        f'\n'
                        f'{ColorFormat.GREEN}'
                        f'{self.get_text(player, "official_shop_single_shop_category_form.content")}',
                on_close=self.official_shop
            )

            if player.is_op:
                # Button - Official shop: edit single shop category
                official_shop_single_shop_category_form.add_button(
                    f'{ColorFormat.YELLOW}'
                    f'{self.get_text(player, "official_shop_single_shop_category_form.button.edit_shop_category")}',
                    icon='textures/ui/hammer_l',
                    on_click=self.official_shop_edit_single_shop_category(shop_category)
                )

            # Buttons - Official shop: goods
            official_shop_single_shop_category_form.add_button(
                f'{ColorFormat.YELLOW}'
                f'{self.get_text(player, "button.back")}',
                icon='textures/ui/refresh_light',
                on_click=self.back_to_main_form
            )

            for good_hex_dig, good_info in self.shop_data[shop_category].items():
                good_type_translation_key = good_info['good_type_translation_key']

                good_name = self.server.language.translate(
                    good_type_translation_key,
                    None,
                    player.locale
                )

                good_type_id = good_info['good_type_id']

                good_enchants = good_info['good_enchants']

                good_lore = good_info['good_lore']

                good_purchase_price = good_info['good_purchase_price']

                good_reclaim_price = good_info['good_reclaim_price']

                good_mode = good_info['good_mode']

                collectors = good_info['collectors']

                if good_enchants and not good_lore:
                    good_button_text = (
                        f'{ColorFormat.YELLOW}'
                        f'{good_name} '
                        f'{ColorFormat.LIGHT_PURPLE}'
                        f'+'
                    )
                elif not good_enchants and good_lore:
                    good_button_text = (
                        f'{ColorFormat.YELLOW}'
                        f'{good_name} '
                        f'{ColorFormat.AQUA}'
                        f'+'
                    )
                elif good_enchants and good_lore:
                    good_button_text = (
                        f'{ColorFormat.YELLOW}'
                        f'{good_name} '
                        f'{ColorFormat.LIGHT_PURPLE}'
                        f'+ '
                        f'{ColorFormat.AQUA}'
                        f'+'
                    )
                else:
                    good_button_text = (
                        f'{ColorFormat.YELLOW}'
                        f'{good_name}'
                    )

                official_shop_single_shop_category_form.add_button(
                    good_button_text,
                    icon=self.get_texture(good_type_id),
                    on_click=self.official_shop_single_good(
                        shop_category,
                        good_hex_dig,
                        good_name,
                        good_type_id,
                        good_enchants,
                        good_lore,
                        good_purchase_price,
                        good_reclaim_price,
                        good_mode,
                        collectors
                    )
                )

            player.send_form(official_shop_single_shop_category_form)

        return on_click

    # Official shop: edit single shop category
    def official_shop_edit_single_shop_category(self, shop_category):
        def on_click(player: Player):
            official_shop_edit_single_shop_category_form = ActionForm(
                title=f'{ColorFormat.BOLD}{ColorFormat.LIGHT_PURPLE}'
                      f'{self.get_text(player, "official_shop_edit_single_shop_category_form.title")}',
                content=f'{ColorFormat.GREEN}'
                        f'{self.get_text(player, "category_name")}: '
                        f'{ColorFormat.WHITE}'
                        f'{shop_category}\n'
                        f'\n'
                        f'{ColorFormat.GREEN}'
                        f'{self.get_text(player, "official_shop_edit_single_shop_category_form.content")}',
                on_close=self.official_shop
            )

            # Button - Official shop: delete single shop category
            official_shop_edit_single_shop_category_form.add_button(
                f'{ColorFormat.YELLOW}'
                f'{self.get_text(player, "official_shop_edit_single_shop_category_form.button.delete_shop_category")}',
                icon='textures/ui/icon_trash',
                on_click=self.official_shop_delete_single_shop_category(shop_category)
            )

            # Button - Official shop: update single shop category
            official_shop_edit_single_shop_category_form.add_button(
                f'{ColorFormat.YELLOW}'
                f'{self.get_text(player, "official_shop_edit_single_shop_category_form.button.update_shop_category")}',
                icon='textures/ui/refresh',
                on_click=self.official_shop_update_single_shop_category(shop_category)
            )

            # Button - Back to official shop main form
            official_shop_edit_single_shop_category_form.add_button(
                f'{ColorFormat.YELLOW}'
                f'{self.get_text(player, "button.back")}',
                icon='textures/ui/refresh_light',
                on_click=self.official_shop
            )

            player.send_form(official_shop_edit_single_shop_category_form)

        return on_click

    # Official shop: delete single shop category
    def official_shop_delete_single_shop_category(self, shop_category):
        def on_click(player: Player):
            confirm_form = ActionForm(
                title=f'{ColorFormat.BOLD}{ColorFormat.LIGHT_PURPLE}'
                      f'{self.get_text(player, "official_shop_delete_single_shop_category_form.title")}',
                content=f'{ColorFormat.GREEN}'
                        f'{self.get_text(player, "category_name")}: '
                        f'{ColorFormat.WHITE}'
                        f'{shop_category}\n'
                        f'\n'
                        f'{ColorFormat.GREEN}'
                        f'{self.get_text(player, "official_shop_delete_single_shop_category_form.content")}',
                on_close=self.official_shop
            )

            # Button - Official shop: delete single shop category (confirm)
            confirm_form.add_button(
                f'{ColorFormat.YELLOW}'
                f'{self.get_text(player, "official_shop_delete_single_shop_category_form.button.confirm")}',
                icon='textures/ui/realms_slot_check',
                on_click=self.official_shop_delete_single_shop_category_confirm(shop_category)
            )

            # Button - Back to official shop main form
            confirm_form.add_button(
                f'{ColorFormat.YELLOW}'
                f'{self.get_text(player, "button.back")}',
                icon='textures/ui/refresh_light',
                on_click=self.official_shop
            )

            player.send_form(confirm_form)

        return on_click

    def official_shop_delete_single_shop_category_confirm(self, shop_category):
        def on_click(player: Player):
            self.shop_data.pop(shop_category)

            self.save_shop_data()

            player.send_message(
                f'{ColorFormat.YELLOW}'
                f'{self.get_text(player, "official_shop_delete_single_shop_category.message.success")}'
            )

        return on_click

    # Official shop: update single shop category
    def official_shop_update_single_shop_category(self, shop_category):
        def on_click(player: Player):
            textinput = TextInput(
                label=f'{ColorFormat.GREEN}'
                      f'{self.get_text(player, "category_name")}: '
                      f'{ColorFormat.WHITE}'
                      f'{shop_category}\n'
                      f'\n'
                      f'{ColorFormat.GREEN}'
                      f'{self.get_text(player, "official_shop_update_single_shop_category_form.textinput.label")}',
                placeholder=self.get_text(player, "official_shop_update_single_shop_category_form.textinput.placeholder"),
                default_value=shop_category
            )

            official_shop_update_single_shop_category_form = ModalForm(
                title=f'{ColorFormat.BOLD}{ColorFormat.LIGHT_PURPLE}'
                      f'{self.get_text(player, "official_shop_update_single_shop_category_form.title")}',
                controls=[
                    textinput
                ],
                submit_button=f'{ColorFormat.YELLOW}'
                              f'{self.get_text(player, "official_shop_update_single_shop_category_form.submit_button")}',
                on_close = self.back_to_main_form
            )

            def on_submit(p: Player, json_str: str):
                data = json.loads(json_str)

                if len(data[0]) == 0:
                    player.send_message(
                        self.get_text(player, "message.type_error")
                    )
                    return

                shop_category_list = [key for key in self.shop_data.keys() if key != shop_category]

                if data[0] in shop_category_list:
                    player.send_message(
                        f'{ColorFormat.RED}'
                        f'{self.get_text(player, "official_shop_update_single_shop_category.message.fail")}: '
                        f'{ColorFormat.WHITE}' +
                        self.get_text(player, "official_shop_update_single_shop_category.message.fail.reason").format(data[0])
                    )

                    return

                update_shop_category = data[0]

                shop_category_info = self.shop_data[shop_category]

                self.shop_data.pop(shop_category)

                self.shop_data[update_shop_category] = shop_category_info

                self.save_shop_data()

                p.send_message(
                    f'{ColorFormat.YELLOW}'
                    f'{self.get_text(player, "official_shop_update_single_shop_category.message.success")}'
                )

            official_shop_update_single_shop_category_form.on_submit = on_submit

            player.send_form(official_shop_update_single_shop_category_form)

        return on_click

    # Official shop: add good
    def official_shop_add_good(self, player: Player) -> None:
        if len(self.shop_data) == 0:
            player.send_message(
                f'{ColorFormat.RED}'
                f'{self.get_text(player, "official_shop_add_good.message.fail")}: '
                f'{ColorFormat.WHITE}'
                f'{self.get_text(player, "official_shop_add_good.message.fail.reason")}'
            )

            return

        official_shop_add_good_form = ActionForm(
            title=f'{ColorFormat.BOLD}{ColorFormat.LIGHT_PURPLE}'
                  f'{self.get_text(player, "official_shop_add_good_form.title")}',
            content=f'{ColorFormat.GREEN}'
                    f'{self.get_text(player, "tags")}: \n'
                    f'{ColorFormat.LIGHT_PURPLE}'
                    f'+ {self.get_text(player, "has_enchants")}\n'
                    f'{ColorFormat.AQUA}'
                    f'+ {self.get_text(player, "has_lore")}\n'
                    f'\n'
                    f'{ColorFormat.GREEN}'
                    f'{self.get_text(player, "official_shop_add_good_form.content")}',
            on_close=self.official_shop
        )

        official_shop_add_good_form.add_button(
            f'{ColorFormat.YELLOW}'
            f'{self.get_text(player, "button.back")}',
            icon='textures/ui/refresh_light',
            on_click=self.official_shop
        )

        for itemstack in player.inventory.contents:
            if itemstack is None:
                continue

            item_type_id = itemstack.type.id

            item_type_translation_key = itemstack.type.translation_key

            item_name = self.server.language.translate(
                item_type_translation_key,
                None,
                player.locale
            )

            item_meta = itemstack.item_meta

            item_enchants = item_meta.enchants

            if item_meta.has_lore:
                item_lore = item_meta.lore
            else:
                item_lore = []

            if item_enchants and not item_lore:
                button_text = (
                    f'{ColorFormat.YELLOW}'
                    f'{item_name} '
                    f'{ColorFormat.LIGHT_PURPLE}'
                    f'+'
                )
            elif not item_enchants and item_lore:
                button_text = (
                    f'{ColorFormat.YELLOW}'
                    f'{item_name} '
                    f'{ColorFormat.AQUA}'
                    f'+'
                )
            elif item_enchants and item_lore:
                button_text = (
                    f'{ColorFormat.YELLOW}'
                    f'{item_name} '
                    f'{ColorFormat.LIGHT_PURPLE}'
                    f'+ '
                    f'{ColorFormat.AQUA}'
                    f'+'
                )
            else:
                button_text = (
                    f'{ColorFormat.YELLOW}'
                    f'{item_name}'
                )

            official_shop_add_good_form.add_button(
                button_text,
                icon=self.get_texture(item_type_id),
                on_click=self.official_shop_add_good_further(
                    item_name,
                    item_type_translation_key,
                    item_type_id,
                    item_enchants,
                    item_lore
                )
            )

        player.send_form(official_shop_add_good_form)

    def official_shop_add_good_further(self, good_name, good_type_translation_key, good_type_id, good_enchants, good_lore):
        def on_click(player: Player):
            good_enchants_display = '\n'

            for good_enchant_key, good_enchant_level in good_enchants.items():
                good_enchant_translation_key = self.get_enchant_translation_key(good_enchant_key)

                good_enchant_name = self.server.language.translate(
                    good_enchant_translation_key,
                    None,
                    player.locale
                )

                good_enchants_display += f'{good_enchant_name} [lvl {good_enchant_level}]\n'

            good_lore_display = '\n'

            for gl in good_lore:
                good_lore_display += f'{gl}\n'

            shop_category_list = [key for key in self.shop_data.keys()]

            dropdown1 = Dropdown(
                label=f'{ColorFormat.GREEN}'
                      f'{self.get_text(player, "good_name")}: '
                      f'{ColorFormat.WHITE}'
                      f'{good_name}\n'
                      f'\n'
                      f'{ColorFormat.GREEN}'
                      f'{self.get_text(player, "good_type")}: '
                      f'{ColorFormat.WHITE}'
                      f'{good_type_id}\n'
                      f'\n'
                      f'{ColorFormat.GREEN}'
                      f'{self.get_text(player, "good_enchants")}: '
                      f'{ColorFormat.WHITE}'
                      f'{good_enchants_display}'
                      f'{ColorFormat.GREEN}'
                      f'{self.get_text(player, "good_lore")}: '
                      f'{ColorFormat.WHITE}'
                      f'{good_lore_display}'
                      f'\n'
                      f'{ColorFormat.GREEN}'
                      f'{self.get_text(player, "official_shop_add_good_further_form.dropdown1.label")}',
                options=shop_category_list
            )

            good_mode_list = [
                'purchase and reclaim',
                'only purchase',
                'only reclaim'
            ]

            dropdown2 = Dropdown(
                label=f'{ColorFormat.GREEN}'
                      f'{self.get_text(player, "official_shop_add_good_further_form.dropdown2.label")}',
                options=good_mode_list
            )

            textinput1 = TextInput(
                label=f'{ColorFormat.GREEN}'
                      f'{self.get_text(player, "official_shop_add_good_further_form.textinput1.label")}',
                placeholder=self.get_text(player, "official_shop_add_good_further_form.textinput.placeholder")
            )

            textinput2 = TextInput(
                label=f'{ColorFormat.GREEN}'
                      f'{self.get_text(player, "official_shop_add_good_further_form.textinput2.label")}',
                placeholder=self.get_text(player, "official_shop_add_good_further_form.textinput.placeholder")
            )

            official_shop_add_good_further_form = ModalForm(
                title=f'{ColorFormat.BOLD}{ColorFormat.LIGHT_PURPLE}'
                      f'{self.get_text(player, "official_shop_add_good_further_form.title")}',
                controls=[
                    dropdown1,
                    dropdown2,
                    textinput1,
                    textinput2
                ],
                submit_button=f'{ColorFormat.YELLOW}'
                              f'{self.get_text(player, "official_shop_add_good_further_form.submit_button")}',
                on_close=self.official_shop_add_good
            )

            def on_submit(p: Player, json_str: str):
                data = json.loads(json_str)

                try:
                    good_purchase_price = int(data[2])
                    good_reclaim_price = int(data[3])
                except:
                    p.send_message(
                        f'{ColorFormat.RED}'
                        f'{self.get_text(p, "message.type_error")}'
                    )

                    return

                if good_purchase_price <= 0 or good_reclaim_price <= 0:
                    p.send_message(
                        f'{ColorFormat.RED}'
                        f'{self.get_text(p, "message.type_error")}'
                    )

                    return

                shop_category = shop_category_list[data[0]]

                hash_object = hashlib.sha256(str(datetime.datetime.now()).encode())
                good_hex_dig = hash_object.hexdigest()

                good_mode = good_mode_list[data[1]]

                self.shop_data[shop_category][good_hex_dig] = {
                    'good_type_translation_key': good_type_translation_key,
                    'good_type_id': good_type_id,
                    'good_enchants': good_enchants,
                    'good_lore': good_lore,
                    'good_purchase_price': good_purchase_price,
                    'good_reclaim_price': good_reclaim_price,
                    'good_mode': good_mode,
                    'collectors': []
                }

                self.save_shop_data()

                p.send_message(
                    f'{ColorFormat.YELLOW}'
                    f'{self.get_text(player, "official_shop_add_good_further.message.success")}'
                )

            official_shop_add_good_further_form.on_submit = on_submit

            player.send_form(official_shop_add_good_further_form)

        return on_click

    def get_enchant_translation_key(self, good_enchant_key: str):
        if not self.good_enchant_translation_keys.get(good_enchant_key):
            good_enchant_translation_key = self.server.enchantment_registry.get(NamespacedKey.from_string(good_enchant_key)).translation_key

            self.good_enchant_translation_keys[good_enchant_key] = good_enchant_translation_key
        else:
            good_enchant_translation_key = self.good_enchant_translation_keys[good_enchant_key]

        return good_enchant_translation_key

    # Official shop: single good
    def official_shop_single_good(self, shop_category, good_hex_dig, good_name, good_type_id, good_enchants, good_lore, good_purchase_price, good_reclaim_price, good_mode, collectors):
        def on_click(player: Player):
            player_money = self.server.plugin_manager.get_plugin('umoney').api_get_player_money(player.name)

            good_enchants_display = '\n'

            for good_enchant_key, good_enchant_level in good_enchants.items():
                good_enchant_translation_key = self.get_enchant_translation_key(good_enchant_key)

                good_enchant_name = self.server.language.translate(
                    good_enchant_translation_key,
                    None,
                    player.locale
                )

                good_enchants_display += f'{good_enchant_name} [lvl {good_enchant_level}]\n'

            good_lore_display = '\n'

            for gl in good_lore:
                good_lore_display += f'{gl}\n'

            official_shop_single_good_form = ActionForm(
                title=f'{ColorFormat.BOLD}{ColorFormat.LIGHT_PURPLE}'
                      f'{self.get_text(player, "official_shop_single_good_form.title")}',
                content=f'{ColorFormat.GREEN}'
                        f'{self.get_text(player, "your_money")}: '
                        f'{ColorFormat.WHITE}'
                        f'{player_money}\n'
                        f'\n'
                        f'{ColorFormat.GREEN}'
                        f'{self.get_text(player, "good_name")}: '
                        f'{ColorFormat.WHITE}'
                        f'{good_name}\n'
                        f'\n'
                        f'{ColorFormat.GREEN}'
                        f'{self.get_text(player, "good_type")}: '
                        f'{ColorFormat.WHITE}'
                        f'{good_type_id}\n'
                        f'\n'
                        f'{ColorFormat.GREEN}'
                        f'{self.get_text(player, "good_enchants")}: '
                        f'{ColorFormat.WHITE}'
                        f'{good_enchants_display}'
                        f'{ColorFormat.GREEN}'
                        f'{self.get_text(player, "good_lore")}: '
                        f'{ColorFormat.WHITE}'
                        f'{good_lore_display}'
                        f'\n'
                        f'{ColorFormat.GREEN}'
                        f'{self.get_text(player, "good_purchase_price")}: '
                        f'{ColorFormat.WHITE}'
                        f'{good_purchase_price}\n'
                        f'{ColorFormat.GREEN}'
                        f'{self.get_text(player, "good_reclaim_price")}: '
                        f'{ColorFormat.WHITE}'
                        f'{good_reclaim_price}\n'
                        f'{ColorFormat.GREEN}'
                        f'{self.get_text(player, "good_mode")}: '
                        f'{ColorFormat.WHITE}'
                        f'{self.get_text(player, good_mode)}\n'
                        f'\n'
                        f'{ColorFormat.GREEN}' +
                        self.get_text(player, "official_shop_single_good_form.content").format(len(collectors)),
                on_close=self.official_shop
            )

            if player.is_op:
                official_shop_single_good_form.add_button(
                    f'{ColorFormat.YELLOW}'
                    f'{self.get_text(player, "official_shop_single_good_form.button.edit_good")}',
                    icon='textures/ui/hammer_l',
                    on_click=self.official_shop_edit_single_good(
                        shop_category,
                        good_hex_dig,
                        good_name,
                        good_type_id,
                        good_enchants,
                        good_lore,
                        good_purchase_price,
                        good_reclaim_price,
                        good_mode,
                        collectors
                    )
                )

            if good_mode == 'only purchase' or good_mode == 'purchase and reclaim':
                official_shop_single_good_form.add_button(
                    f'{ColorFormat.YELLOW}'
                    f'{self.get_text(player, "official_shop_single_good_form.button.purchase")}',
                    icon='textures/ui/village_hero_effect',
                    on_click=self.official_shop_purchase_single_good(
                        good_name,
                        good_type_id,
                        good_enchants,
                        good_lore,
                        good_purchase_price
                    )
                )

            if good_mode == 'only reclaim' or good_mode == 'purchase and reclaim':
                official_shop_single_good_form.add_button(
                    f'{ColorFormat.YELLOW}'
                    f'{self.get_text(player, "official_shop_single_good_form.button.reclaim")}',
                    icon='textures/ui/trade_icon',
                    on_click=self.official_shop_reclaim_single_good(
                        good_name,
                        good_type_id,
                        good_enchants,
                        good_lore,
                        good_reclaim_price
                    )
                )

            if player.name not in collectors:
                official_shop_single_good_form.add_button(
                    f'{ColorFormat.YELLOW}'
                    f'{self.get_text(player, "official_shop_single_good_form.button.collect_good")}',
                    icon='textures/ui/heart_new',
                    on_click=self.official_shop_collect_single_good(
                        shop_category,
                        good_hex_dig
                    )
                )
            else:
                official_shop_single_good_form.add_button(
                    f'{ColorFormat.YELLOW}'
                    f'{self.get_text(player, "official_shop_single_good_form.button.de_collect_good")}',
                    icon='textures/ui/heart_background',
                    on_click=self.official_shop_de_collect_single_good(
                        shop_category,
                        good_hex_dig
                    )
                )

            official_shop_single_good_form.add_button(
                f'{ColorFormat.YELLOW}'
                f'{self.get_text(player, "button.back")}',
                icon='textures/ui/refresh_light',
                on_click=self.official_shop
            )

            player.send_form(official_shop_single_good_form)

        return on_click

    # Official shop: edit single good
    def official_shop_edit_single_good(self, shop_category, good_hex_dig, good_name, good_type_id, good_enchants, good_lore, good_purchase_price, good_reclaim_price, good_mode, collectors):
        def on_click(player: Player):
            good_enchants_display = '\n'

            for good_enchant_key, good_enchant_level in good_enchants.items():
                good_enchant_translation_key = self.get_enchant_translation_key(good_enchant_key)

                good_enchant_name = self.server.language.translate(
                    good_enchant_translation_key,
                    None,
                    player.locale
                )

                good_enchants_display += f'{good_enchant_name} [lvl {good_enchant_level}]\n'

            good_lore_display = '\n'

            for gl in good_lore:
                good_lore_display += f'{gl}\n'

            official_shop_edit_single_good_form = ActionForm(
                title=f'{ColorFormat.BOLD}{ColorFormat.LIGHT_PURPLE}'
                      f'{self.get_text(player, "official_shop_edit_single_good_form.title")}',
                content=f'{ColorFormat.GREEN}'
                        f'{self.get_text(player, "good_name")}: '
                        f'{ColorFormat.WHITE}'
                        f'{good_name}\n'
                        f'\n'
                        f'{ColorFormat.GREEN}'
                        f'{self.get_text(player, "good_type")}: '
                        f'{ColorFormat.WHITE}'
                        f'{good_type_id}\n'
                        f'\n'
                        f'{ColorFormat.GREEN}'
                        f'{self.get_text(player, "good_enchants")}: '
                        f'{ColorFormat.WHITE}'
                        f'{good_enchants_display}'
                        f'{ColorFormat.GREEN}'
                        f'{self.get_text(player, "good_lore")}: '
                        f'{ColorFormat.WHITE}'
                        f'{good_lore_display}'
                        f'\n'
                        f'{ColorFormat.GREEN}'
                        f'{self.get_text(player, "good_purchase_price")}: '
                        f'{ColorFormat.WHITE}'
                        f'{good_purchase_price}\n'
                        f'{ColorFormat.GREEN}'
                        f'{self.get_text(player, "good_reclaim_price")}: '
                        f'{ColorFormat.WHITE}'
                        f'{good_reclaim_price}\n'
                        f'{ColorFormat.GREEN}'
                        f'{self.get_text(player, "good_mode")}: '
                        f'{ColorFormat.WHITE}'
                        f'{self.get_text(player, good_mode)}\n'
                        f'\n'
                        f'{ColorFormat.GREEN}' +
                        self.get_text(player, "official_shop_single_good_form.content").format(len(collectors)) + '\n'
                        '\n' +
                        f'{ColorFormat.GREEN}'
                        f'{self.get_text(player, "official_shop_edit_single_good_form.content")}',
                on_close=self.official_shop
            )

            official_shop_edit_single_good_form.add_button(
                f'{ColorFormat.YELLOW}'
                f'{self.get_text(player, "official_shop_edit_single_good_form.button.delete_good")}',
                icon='textures/ui/icon_trash',
                on_click=self.official_shop_delete_single_good(
                    shop_category,
                    good_hex_dig,
                    good_name
                )
            )

            official_shop_edit_single_good_form.add_button(
                f'{ColorFormat.YELLOW}'
                f'{self.get_text(player, "official_shop_edit_single_good_form.button.update_good")}',
                icon='textures/ui/refresh',
                on_click=self.official_shop_update_single_good(
                    shop_category,
                    good_hex_dig,
                    good_name,
                    good_purchase_price,
                    good_reclaim_price,
                    good_mode
                )
            )

            official_shop_edit_single_good_form.add_button(
                f'{ColorFormat.YELLOW}'
                f'{self.get_text(player, "button.back")}',
                icon='textures/ui/refresh_light',
                on_click=self.official_shop
            )

            player.send_form(official_shop_edit_single_good_form)

        return on_click

    # Official shop: delete single good
    def official_shop_delete_single_good(self, shop_category, good_hex_dig, good_name):
        def on_click(player: Player):
            confirm_form = ActionForm(
                title=f'{ColorFormat.BOLD}{ColorFormat.LIGHT_PURPLE}'
                      f'{self.get_text(player, "official_shop_delete_single_good_form.title")}',
                content=f'{ColorFormat.GREEN}'
                        f'{self.get_text(player, "good_name")}: '
                        f'{ColorFormat.WHITE}'
                        f'{good_name}\n'
                        f'\n'
                        f'{ColorFormat.GREEN}'
                        f'{self.get_text(player, "official_shop_delete_single_good_form.content")}',
                on_close=self.official_shop
            )

            confirm_form.add_button(
                f'{ColorFormat.YELLOW}'
                f'{self.get_text(player, "official_shop_delete_single_good_form.button.confirm")}',
                icon='textures/ui/realms_slot_check',
                on_click=self.official_shop_delete_single_good_confirm(
                    shop_category,
                    good_hex_dig
                )
            )

            confirm_form.add_button(
                f'{ColorFormat.YELLOW}'
                f'{self.get_text(player, "button.back")}',
                icon='textures/ui/refresh_light',
                on_click=self.official_shop
            )

            player.send_form(confirm_form)

        return on_click

    def official_shop_delete_single_good_confirm(self, shop_category, good_hex_dig):
        def on_click(player: Player):
            self.shop_data[shop_category].pop(good_hex_dig)

            self.save_shop_data()

            player.send_message(
                f'{ColorFormat.YELLOW}'
                f'{self.get_text(player, "official_shop_delete_single_good.message.success")}'
            )

        return on_click

    # Official shop: update single good
    def official_shop_update_single_good(self, shop_category, good_hex_dig, good_name, good_purchase_price, good_reclaim_price, good_mode):
        def on_click(player: Player):
            shop_category_list = [key for key in self.shop_data.keys()]

            dropdown1 = Dropdown(
                label=f'{ColorFormat.GREEN}'
                      f'{self.get_text(player, "good_name")}: '
                      f'{ColorFormat.WHITE}'
                      f'{good_name}\n'
                      f'\n'
                      f'{ColorFormat.GREEN}'
                      f'{self.get_text(player, "official_shop_update_single_good_form.dropdown1.label")}',
                options=shop_category_list,
                default_index=shop_category_list.index(shop_category)
            )

            good_mode_list = [
                'only purchase',
                'only reclaim',
                'purchase and reclaim'
            ]

            dropdown2 = Dropdown(
                label=f'{ColorFormat.GREEN}'
                      f'{self.get_text(player, "official_shop_update_single_good_form.dropdown2.label")}',
                options=good_mode_list,
                default_index=good_mode_list.index(good_mode)
            )

            textinput1 = TextInput(
                label=f'{ColorFormat.GREEN}'
                      f'{self.get_text(player, "official_shop_update_single_good_form.textinput1.label")}',
                placeholder=self.get_text(player, "official_shop_update_single_good_form.textinput1.placeholder"),
                default_value=str(good_purchase_price)
            )

            textinput2 = TextInput(
                label=f'{ColorFormat.GREEN}'
                      f'{self.get_text(player, "official_shop_update_single_good_form.textinput2.label")}',
                placeholder=self.get_text(player, "official_shop_update_single_good_form.textinput2.placeholder"),
                default_value=str(good_reclaim_price)
            )

            official_shop_update_single_good_form = ModalForm(
                title=f'{ColorFormat.BOLD}{ColorFormat.LIGHT_PURPLE}'
                      f'{self.get_text(player, "official_shop_update_single_good_form.title")}',
                controls=[
                    dropdown1,
                    dropdown2,
                    textinput1,
                    textinput2
                ],
                submit_button=f'{ColorFormat.YELLOW}'
                              f'{self.get_text(player, "official_shop_update_single_good_form.submit_button")}',
                on_close=self.official_shop
            )

            def on_submit(p: Player, json_str: str):
                data = json.loads(json_str)

                try:
                    update_good_purchase_price = int(data[2])
                    update_good_reclaim_price = int(data[3])
                except:
                    p.send_message(
                        f'{ColorFormat.RED}'
                        f'{self.get_text(p, "message.type_error")}'
                    )

                    return

                if (
                    update_good_purchase_price <= 0
                    or
                    update_good_reclaim_price <= 0
                ):
                    p.send_message(
                        f'{ColorFormat.RED}'
                        f'{self.get_text(p, "message.type_error")}'
                    )

                    return

                update_good_mode = good_mode_list[data[1]]

                self.shop_data[shop_category][good_hex_dig]['good_purchase_price'] = update_good_purchase_price

                self.shop_data[shop_category][good_hex_dig]['good_reclaim_price'] = update_good_reclaim_price

                self.shop_data[shop_category][good_hex_dig]['good_mode'] = update_good_mode

                update_shop_category = shop_category_list[data[0]]

                if update_shop_category != shop_category:
                    self.shop_data[update_shop_category][good_hex_dig] = self.shop_data[shop_category][good_hex_dig]

                    self.shop_data[shop_category].pop(good_hex_dig)

                self.save_shop_data()

                p.send_message(
                    f'{ColorFormat.YELLOW}'
                    f'{self.get_text(p, "official_shop_update_single_good.message.success")}'
                )

            official_shop_update_single_good_form.on_submit = on_submit

            player.send_form(official_shop_update_single_good_form)

        return on_click

    # Official shop: purchase single good
    def official_shop_purchase_single_good(self, good_name, good_type_id, good_enchants, good_lore, good_purchase_price):
        def on_click(player: Player):
            good_itemstack = ItemStack(
                type=good_type_id
            )

            good_itemstack_itemmeta_copy = good_itemstack.item_meta

            if good_enchants:
                for good_enchant_key, good_enchant_level in good_enchants.items():
                    good_itemstack_itemmeta_copy.add_enchant(
                        id=good_enchant_key,
                        level=good_enchant_level
                    )

            if good_lore:
                good_itemstack_itemmeta_copy.lore = good_lore

            good_itemstack.set_item_meta(good_itemstack_itemmeta_copy)

            good_itemstack_max_stack_size = good_itemstack.max_stack_size

            good_purchase_max_num = 0

            for itemstack in player.inventory.contents:
                if itemstack is None:
                    good_purchase_max_num += good_itemstack_max_stack_size
                else:
                    if (
                        itemstack.type.id == good_itemstack.type.id
                        and
                        itemstack.item_meta.enchants == good_itemstack.item_meta.enchants
                        and
                        itemstack.item_meta.lore == good_itemstack.item_meta.lore
                    ):
                        if itemstack.amount < good_itemstack_max_stack_size:
                            good_purchase_max_num += (good_itemstack_max_stack_size - itemstack.amount)

            if good_purchase_max_num == 0:
                player.send_message(
                    f'{ColorFormat.RED}'
                    f'{self.get_text(player, "official_shop_purchase_single_good.message.fail")}: '
                    f'{ColorFormat.WHITE}'
                    f'{self.get_text(player, "official_shop_purchase_single_good.message.fail.reason1")}'
                )

                return

            textinput = TextInput(
                label=f'{ColorFormat.GREEN}'
                      f'{self.get_text(player, "good_name")}: '
                      f'{ColorFormat.WHITE}'
                      f'{good_name}\n'
                      f'\n'
                      f'{ColorFormat.GREEN}'
                      f'{self.get_text(player, "official_shop_purchase_single_good_form.textinput.label")}',
                placeholder=self.get_text(player, "official_shop_purchase_single_good_form.textinput.placeholder").format(good_purchase_max_num)
            )

            official_shop_purchase_single_good_form = ModalForm(
                title=f'{ColorFormat.BOLD}{ColorFormat.LIGHT_PURPLE}'
                      f'{self.get_text(player, "official_shop_purchase_single_good_form.title")}',
                controls=[textinput],
                submit_button=f'{ColorFormat.YELLOW}'
                              f'{self.get_text(player, "official_shop_purchase_single_good_form.submit_button")}',
                on_close=self.official_shop
            )

            def on_submit(p: Player, json_str: str):
                data = json.loads(json_str)

                try:
                    good_purchase_num = int(data[0])
                except:
                    p.send_message(
                        f'{ColorFormat.RED}'
                        f'{self.get_text(p, "message.type_error")}'
                    )

                    return

                if good_purchase_num > good_purchase_max_num:
                    p.send_message(
                        f'{ColorFormat.RED}'
                        f'{self.get_text(p, "message.type_error")}'
                    )

                    return

                good_purchase_total_price = good_purchase_price * good_purchase_num

                p_money = self.server.plugin_manager.get_plugin('umoney').api_get_player_money(p.name)

                if p_money < good_purchase_total_price:
                    p.send_message(
                        f'{ColorFormat.RED}'
                        f'{self.get_text(p, "official_shop_purchase_single_good.message.fail")}: '
                        f'{ColorFormat.WHITE}'
                        f'{self.get_text(p, "official_shop_purchase_single_good.message.fail.reason2")}'
                    )

                    return

                p.send_message(
                    f'{ColorFormat.YELLOW}'
                    f'{self.get_text(p, "official_shop_purchase_single_good.message.success")}'
                )

                self.server.plugin_manager.get_plugin('umoney').api_change_player_money(p.name, -good_purchase_total_price)

                for i in range(36):
                    if good_purchase_num == 0:
                        break

                    isk = p.inventory.contents[i]

                    if isk is None:
                        if good_purchase_num <= good_itemstack_max_stack_size:
                            give_amount = good_purchase_num
                        else:
                            give_amount = good_itemstack_max_stack_size

                        good_itemstack.amount = give_amount

                        p.inventory.set_item(i, good_itemstack)
                    else:
                        if (
                            isk.type.id == good_itemstack.type.id
                            and
                            isk.item_meta.enchants == good_itemstack.item_meta.enchants
                            and
                            isk.item_meta.lore == good_itemstack.item_meta.lore
                        ):
                            if isk.amount < good_itemstack_max_stack_size:
                                free = good_itemstack_max_stack_size - isk.amount

                                if good_purchase_num <= free:
                                    give_amount = good_purchase_num

                                    good_itemstack.amount = isk.amount + good_purchase_num
                                else:
                                    give_amount = free

                                    good_itemstack.amount = good_itemstack_max_stack_size

                                p.inventory.set_item(i, good_itemstack)

                            else:
                                continue
                        else:
                            continue

                    good_purchase_num -= give_amount

                if good_purchase_num != 0:
                    money_to_refund = good_purchase_num * good_purchase_price

                    p.send_message(
                        f'{ColorFormat.YELLOW}' +
                        self.get_text(p, "official_shop_purchase_single_good.message").format(good_purchase_num)
                    )

                    self.server.plugin_manager.get_plugin('umoney').api_change_player_money(p.name, money_to_refund)

            official_shop_purchase_single_good_form.on_submit = on_submit

            player.send_form(official_shop_purchase_single_good_form)

        return on_click

    # Official shop: reclaim single good
    def official_shop_reclaim_single_good(self, good_name, good_type_id, good_enchants, good_lore, good_reclaim_price):
        def on_click(player: Player):
            good_itemstack = ItemStack(
                good_type_id
            )

            good_itemstack_itemmeta_copy = good_itemstack.item_meta

            if good_enchants:
                for good_enchant_key, good_enchant_level in good_enchants.items():
                    good_itemstack_itemmeta_copy.add_enchant(
                        id=good_enchant_key,
                        level=good_enchant_level
                    )

            if good_lore:
                good_itemstack_itemmeta_copy.lore = good_lore

            good_itemstack.set_item_meta(good_itemstack_itemmeta_copy)

            good_reclaim_max_num = 0

            for itemstack in player.inventory.contents:
                if itemstack is None:
                    continue
                else:
                    if (
                        itemstack.type.id == good_itemstack.type.id
                        and
                        itemstack.item_meta.enchants == good_itemstack.item_meta.enchants
                        and
                        itemstack.item_meta.lore == good_itemstack.item_meta.lore
                    ):
                        itemstack_max_durability = itemstack.type.max_durability

                        if itemstack_max_durability == 0:
                            good_reclaim_max_num += itemstack.amount
                        else:   # It must be an un-stackable item
                            itemstack_durability = ((itemstack_max_durability - itemstack.item_meta.damage + 1) / itemstack_max_durability)

                            if itemstack_durability >= self.config_data['good_reclaim_durability_threshold']:
                                good_reclaim_max_num += 1

            if good_reclaim_max_num == 0:
                player.send_message(
                    f'{ColorFormat.RED}'
                    f'{self.get_text(player, "official_shop_reclaim_single_good.message.fail")}: '
                    f'{ColorFormat.WHITE}'
                    f'{self.get_text(player, "official_shop_reclaim_single_good.message.fail.reason")}'
                )

                return

            textinput = TextInput(
                label=f'{ColorFormat.GREEN}'
                      f'{self.get_text(player, "good_name")}: '
                      f'{ColorFormat.WHITE}'
                      f'{good_name}\n'
                      f'\n'
                      f'{ColorFormat.GREEN}'
                      f'{self.get_text(player, "official_shop_reclaim_single_good_form.textinput.label")}',
                placeholder=self.get_text(player, "official_shop_reclaim_single_good_form.textinput.placeholder").format(good_reclaim_max_num)
            )

            official_shop_reclaim_single_good_form = ModalForm(
                title=f'{ColorFormat.BOLD}{ColorFormat.LIGHT_PURPLE}'
                      f'{self.get_text(player, "official_shop_reclaim_single_good_form.title")}',
                controls=[textinput],
                submit_button=f'{ColorFormat.YELLOW}'
                              f'{self.get_text(player, "official_shop_reclaim_single_good_form.submit_button")}',
                on_close=self.official_shop
            )

            def on_submit(p: Player, json_str: str):
                data = json.loads(json_str)

                try:
                    good_reclaim_num = int(data[0])
                except:
                    p.send_message(
                        f'{ColorFormat.RED}'
                        f'{self.get_text(p, "message.type_error")}'
                    )

                    return

                if good_reclaim_num > good_reclaim_max_num:
                    p.send_message(
                        f'{ColorFormat.RED}'
                        f'{self.get_text(p, "message.type_error")}'
                    )

                    return

                good_reclaim_total_price = good_reclaim_num * good_reclaim_price

                p.send_message(
                    f'{ColorFormat.YELLOW}'
                    f'{self.get_text(p, "official_shop_reclaim_single_good.message.success")}'
                )

                self.server.plugin_manager.get_plugin('umoney').api_change_player_money(p.name, good_reclaim_total_price)

                for i in range(36):
                    if good_reclaim_num == 0:
                        break

                    isk = p.inventory.contents[i]

                    if isk is None:
                        continue
                    else:
                        if (
                            isk.type.id == good_itemstack.type.id
                            and
                            isk.item_meta.enchants == good_itemstack.item_meta.enchants
                            and
                            isk.item_meta.lore == good_itemstack.item_meta.lore
                        ):
                            isk_max_durability = isk.type.max_durability

                            if isk_max_durability == 0:
                                if isk.amount <= good_reclaim_num:
                                    remove_amount = isk.amount

                                    good_itemstack.amount = 0
                                else:
                                    remove_amount = good_reclaim_num

                                    good_itemstack.amount = isk.amount - good_reclaim_num

                                p.inventory.set_item(i, good_itemstack)
                            else:   # It must be an un-stackable item
                                isk_durability = ((isk_max_durability - isk.item_meta.damage + 1) / isk_max_durability)

                                if isk_durability >= self.config_data['good_reclaim_durability_threshold']:
                                    remove_amount = 1

                                    good_itemstack.amount = 0

                                    p.inventory.set_item(i, good_itemstack)
                                else:
                                    continue
                        else:
                            continue

                        good_reclaim_num -= remove_amount

            official_shop_reclaim_single_good_form.on_submit = on_submit

            player.send_form(official_shop_reclaim_single_good_form)

        return on_click

    # Official shop: add lore for item(s)
    def official_shop_add_lore(self, player: Player):
        if player.inventory.item_in_main_hand is None:
            player.send_message(
                f'{ColorFormat.RED}'
                f'{self.get_text(player, "official_shop_add_lore.message.fail")}: '
                f'{ColorFormat.WHITE}'
                f'{self.get_text(player, "official_shop_add_lore.message.fail.reason")}'
            )

            return

        itemstack = player.inventory.item_in_main_hand

        item_amount = itemstack.amount

        item_type_id = itemstack.type.id

        item_type_translation_key = itemstack.type.translation_key

        item_name = self.server.language.translate(
            item_type_translation_key,
            None,
            player.locale
        )

        item_enchants = itemstack.item_meta.enchants

        item_enchants_display = '\n'

        for item_enchant_key, item_enchant_level in item_enchants.items():
            item_enchant_translation_key = self.get_enchant_translation_key(item_enchant_key)

            item_enchant_name = self.server.language.translate(
                item_enchant_translation_key,
                None,
                player.locale
            )

            item_enchants_display += f'{item_enchant_name} [lvl {item_enchant_level}]\n'

        if itemstack.item_meta.has_lore:
            item_lore = itemstack.item_meta.lore
        else:
            item_lore = []

        item_lore_display = '\n'

        if item_lore:
            for il in item_lore:
                item_lore_display += f'{il}\n'

        official_shop_add_lore_form = ActionForm(
            title=f'{ColorFormat.BOLD}{ColorFormat.LIGHT_PURPLE}'
                  f'{self.get_text(player, "official_shop_add_lore_form.title")}',
            content=f'{ColorFormat.GREEN}'
                    f'{self.get_text(player, "item_name")}: '
                    f'{ColorFormat.WHITE}'
                    f'{item_name}\n'
                    f'\n'
                    f'{ColorFormat.GREEN}'
                    f'{self.get_text(player, "item_type")}: '
                    f'{ColorFormat.WHITE}'
                    f'{item_type_id}\n'
                    f'\n'
                    f'{ColorFormat.GREEN}'
                    f'{self.get_text(player, "item_enchants")}: '
                    f'{ColorFormat.WHITE}'
                    f'{item_enchants_display}'
                    f'{ColorFormat.GREEN}'
                    f'{self.get_text(player, "item_lore")}: '
                    f'{ColorFormat.WHITE}'
                    f'{item_lore_display}'
                    f'\n'
                    f'{ColorFormat.GREEN}'
                    f'{self.get_text(player, "official_shop_add_lore_form.content")}',
            on_close=self.official_shop
        )

        official_shop_add_lore_form.add_button(
            f'{ColorFormat.YELLOW}'
            f'{self.get_text(player, "official_shop_add_lore_form.button.add_new_lore_text")}',
            icon='textures/ui/color_plus',
            on_click=self.official_shop_add_new_lore_text(
                item_name,
                item_amount,
                item_type_id,
                item_enchants,
                item_lore
            )
        )

        il_index = 0

        for il in item_lore:
            official_shop_add_lore_form.add_button(
                il,
                icon='textures/items/name_tag',
                on_click=self.official_shop_edit_single_lore_text(
                    item_amount,
                    item_type_id,
                    item_enchants,
                    item_lore,
                    il,
                    il_index
                )
            )

            il_index += 1

        player.send_form(official_shop_add_lore_form)

    def official_shop_add_new_lore_text(self, item_name, item_amount, item_type_id, item_enchants, item_lore):
        def on_click(player: Player):
            textinput = TextInput(
                label=f'{ColorFormat.GREEN}'
                      f'{self.get_text(player, "item_name")}: '
                      f'{ColorFormat.WHITE}'
                      f'{item_name}\n'
                      f'\n'
                      f'{ColorFormat.GREEN}'
                      f'{self.get_text(player, "official_shop_add_new_lore_text_form.textinput.label")}',
                placeholder=self.get_text(player, "official_shop_add_new_lore_text_form.textinput.placeholder")
            )

            official_shop_add_new_lore_form = ModalForm(
                title=f'{ColorFormat.BOLD}{ColorFormat.LIGHT_PURPLE}'
                      f'{self.get_text(player, "official_shop_add_new_lore_text_form.title")}',
                controls=[textinput],
                submit_button=f'{ColorFormat.YELLOW}'
                              f'{self.get_text(player, "official_shop_add_new_lore_text_form.submit_button")}',
                on_close=self.official_shop_add_lore
            )

            def on_submit(p: Player, json_str: str):
                data = json.loads(json_str)

                if len(data[0]) == 0:
                    player.send_message(
                        f'{ColorFormat.RED}'
                        f'{self.get_text(player, "message.type_error")}'
                    )

                    return

                new_lore_text = data[0]

                item_lore.append(new_lore_text)

                itemstack = ItemStack(
                    type=item_type_id,
                    amount=item_amount
                )

                itemmeta_copy = itemstack.item_meta

                if item_enchants:
                    for item_enchant_key, item_enchant_level in item_enchants.items():
                        itemmeta_copy.add_enchant(
                            id=item_enchant_key,
                            level=item_enchant_level
                        )

                itemmeta_copy.lore = item_lore

                itemstack.set_item_meta(itemmeta_copy)

                player.inventory.item_in_main_hand = None

                player.inventory.item_in_main_hand = itemstack

                self.official_shop_add_lore(p)

            official_shop_add_new_lore_form.on_submit = on_submit

            player.send_form(official_shop_add_new_lore_form)

        return on_click

    def official_shop_edit_single_lore_text(self, item_amount, item_type_id, item_enchants, item_lore, lore_text, lore_index):
        def on_click(player: Player):
            official_shop_edit_single_lore_text_form = ActionForm(
                title=f'{ColorFormat.BOLD}{ColorFormat.LIGHT_PURPLE}'
                      f'{self.get_text(player, "official_shop_single_lore_text_form.title")}',
                content=f'{ColorFormat.GREEN}'
                        f'{self.get_text(player, "lore_text")}: '
                        f'{ColorFormat.WHITE}'
                        f'{lore_text}\n'
                        f'\n'
                        f'{ColorFormat.GREEN}'
                        f'{self.get_text(player, "official_shop_single_lore_text_form.content")}',
                on_close=self.official_shop_add_lore
            )

            # Delete single lore text
            official_shop_edit_single_lore_text_form.add_button(
                f'{ColorFormat.YELLOW}'
                f'{self.get_text(player, "official_shop_single_lore_text_form.button.delete_lore_text")}',
                icon='textures/ui/icon_trash',
                on_click=self.official_shop_delete_single_lore_text(
                    item_amount,
                    item_type_id,
                    item_enchants,
                    item_lore,
                    lore_index
                )
            )

            # Update single lore text
            official_shop_edit_single_lore_text_form.add_button(
                f'{ColorFormat.YELLOW}'
                f'{self.get_text(player, "official_shop_single_lore_text_form.button.update_lore_text")}',
                icon='textures/ui/refresh',
                on_click=self.official_shop_update_single_lore_text(
                    item_amount,
                    item_type_id,
                    item_enchants,
                    item_lore,
                    lore_index
                )
            )

            official_shop_edit_single_lore_text_form.add_button(
                f'{ColorFormat.YELLOW}'
                f'{self.get_text(player, "button.back")}',
                icon='textures/ui/refresh_light',
                on_click=self.official_shop_add_lore
            )

            player.send_form(official_shop_edit_single_lore_text_form)

        return on_click

    def official_shop_delete_single_lore_text(self, item_amount, item_type_id, item_enchants, item_lore, lore_index):
        def on_click(player: Player):
            item_lore.pop(lore_index)

            itemstack = ItemStack(
                type=item_type_id,
                amount=item_amount
            )

            itemmeta_copy = itemstack.item_meta

            if item_enchants:
                for item_enchant_key, item_enchant_level in item_enchants.items():
                    itemmeta_copy.add_enchant(
                        id=item_enchant_key,
                        level=item_enchant_level
                    )

            itemmeta_copy.lore = item_lore

            itemstack.set_item_meta(itemmeta_copy)

            player.inventory.item_in_main_hand = None

            player.inventory.item_in_main_hand = itemstack

            self.official_shop_add_lore(player)

        return on_click

    def official_shop_update_single_lore_text(self, item_amount, item_type_id, item_enchants, item_lore, lore_index):
        def on_click(player: Player):
            textinput = TextInput(
                label=f'{ColorFormat.GREEN}'
                      f'{self.get_text(player, "official_shop_update_single_lore_text_form.textinput.label")}',
                placeholder=self.get_text(player, "official_shop_update_single_lore_text_form.textinput.placeholder"),
                default_value=item_lore[lore_index]
            )

            official_shop_update_single_lore_text_form = ModalForm(
                title=f'{ColorFormat.BOLD}{ColorFormat.LIGHT_PURPLE}'
                      f'{self.get_text(player, "official_shop_update_single_lore_text_form.title")}',
                controls=[textinput],
                submit_button=f'{ColorFormat.YELLOW}'
                              f'{self.get_text(player, "official_shop_update_single_lore_text_form.submit_button")}',
                on_close=self.official_shop_add_good
            )

            def on_submit(p: Player, json_str: str):
                data = json.loads(json_str)

                if len(data[0]) == 0:
                    p.send_message(
                        f'{ColorFormat.RED}'
                        f'{self.get_text(p, "message.type_error")}'
                    )

                    return

                update_lore_text = data[0]

                item_lore.pop(lore_index)

                item_lore.insert(lore_index, update_lore_text)

                itemstack = ItemStack(
                    type=item_type_id,
                    amount=item_amount
                )

                itemmeta_copy = itemstack.item_meta

                if item_enchants:
                    for item_enchant_key, item_enchant_level in item_enchants.items():
                        itemmeta_copy.add_enchant(
                            id=item_enchant_key,
                            level=item_enchant_level
                        )

                itemmeta_copy.lore = item_lore

                itemstack.set_item_meta(itemmeta_copy)

                p.inventory.item_in_main_hand = None

                p.inventory.item_in_main_hand = itemstack

                self.official_shop_add_lore(p)

            official_shop_update_single_lore_text_form.on_submit = on_submit

            player.send_form(official_shop_update_single_lore_text_form)

        return on_click

    # Official shop: collect single good
    def official_shop_collect_single_good(self, shop_category, good_hex_dig):
        def on_click(player: Player):
            self.shop_data[shop_category][good_hex_dig]['collectors'].append(player.name)

            self.save_shop_data()

            player.send_message(
                f'{ColorFormat.YELLOW}'
                f'{self.get_text(player, "official_shop_collect_single_good.message.success")}'
            )

        return on_click

    # Official shop: de-collect single good
    def official_shop_de_collect_single_good(self, shop_category, good_hex_dig):
        def on_click(player: Player):
            self.shop_data[shop_category][good_hex_dig]['collectors'].remove(player.name)

            self.save_shop_data()

            player.send_message(
                f'{ColorFormat.YELLOW}'
                f'{self.get_text(player, "official_shop_de_collect_single_good.message.success")}'
            )

        return on_click

    # Official shop: good collections
    def official_shop_good_collections(self, player: Player):
        official_shop_good_collection_form = ActionForm(
            title=f'{ColorFormat.BOLD}{ColorFormat.LIGHT_PURPLE}'
                  f'{self.get_text(player, "official_shop_good_collections_form.title")}',
            on_close=self.official_shop
        )

        official_shop_good_collection_form.add_button(
            f'{ColorFormat.YELLOW}'
            f'{self.get_text(player, "button.back")}',
            icon='textures/ui/refresh_light',
            on_click=self.official_shop
        )

        good_collections_num = 0

        for shop_category, shop_category_info in self.shop_data.items():
            for good_hex_dig, good_info in shop_category_info.items():
                collectors = good_info['collectors']

                if player.name in collectors:
                    good_collections_num += 1

                    good_type_id = good_info['good_type_id']

                    good_type_translation_key = good_info['good_type_translation_key']

                    good_name = self.server.language.translate(
                        good_type_translation_key,
                        None,
                        player.locale
                    )

                    good_enchants = good_info['good_enchants']

                    good_lore = good_info['good_lore']

                    good_purchase_price = good_info['good_purchase_price']

                    good_reclaim_price = good_info['good_reclaim_price']

                    good_mode = good_info['good_mode']

                    if good_enchants and not good_lore:
                        good_button_text = (
                            f'{ColorFormat.YELLOW}'
                            f'{good_name} '
                            f'{ColorFormat.LIGHT_PURPLE}'
                            f'+'
                        )
                    elif not good_enchants and good_lore:
                        good_button_text = (
                            f'{ColorFormat.YELLOW}'
                            f'{good_name} '
                            f'{ColorFormat.AQUA}'
                            f'+'
                        )
                    elif good_enchants and good_lore:
                        good_button_text = (
                            f'{ColorFormat.YELLOW}'
                            f'{good_name} '
                            f'{ColorFormat.LIGHT_PURPLE}'
                            f'+ '
                            f'{ColorFormat.AQUA}'
                            f'+'
                        )
                    else:
                        good_button_text = (
                            f'{ColorFormat.YELLOW}'
                            f'{good_name}'
                        )

                    official_shop_good_collection_form.add_button(
                        good_button_text,
                        icon=self.get_texture(good_type_id),
                        on_click=self.official_shop_single_good(
                            shop_category,
                            good_hex_dig,
                            good_name,
                            good_type_id,
                            good_enchants,
                            good_lore,
                            good_purchase_price,
                            good_reclaim_price,
                            good_mode,
                            collectors
                        )
                    )

        official_shop_good_collection_form.content = (
            f'{ColorFormat.GREEN}' +
            self.get_text(player, "official_shop_good_collections_form.content").format(good_collections_num)
        )

        player.send_form(official_shop_good_collection_form)

    # Official shop: search good
    def official_shop_search_good(self, player: Player):
        textinput = TextInput(
            label=f'{ColorFormat.GREEN}'
                  f'{self.get_text(player, "official_shop_search_good_form.textinput.label")}',
            placeholder=self.get_text(player, "official_shop_search_good_form.textinput.placeholder")
        )

        official_shop_search_good_form = ModalForm(
            title=f'{ColorFormat.BOLD}{ColorFormat.LIGHT_PURPLE}'
                  f'{self.get_text(player, "official_shop_search_good_form.title")}',
            controls=[textinput],
            submit_button=f'{ColorFormat.YELLOW}'
                          f'{self.get_text(player, "official_shop_search_good_form.submit_button")}',
            on_close=self.official_shop
        )

        def on_submit(p: Player, json_str: str):
            data = json.loads(json_str)

            if len(data[0]) == 0:
                p.send_message(
                    f'{ColorFormat.GREEN}'
                    f'{self.get_text(p, "type_error")}'
                )

                return

            keyword = data[0]

            result_from = ActionForm(
                title=f'{ColorFormat.BOLD}{ColorFormat.LIGHT_PURPLE}'
                      f'{self.get_text(p, "result_form.title")}',
                on_close=self.official_shop_search_good
            )

            result_from.add_button(
                f'{ColorFormat.YELLOW}'
                f'{self.get_text(p, "button.back")}',
                icon='textures/ui/refresh_light',
                on_click=self.official_shop_search_good
            )

            match_num = 0

            for shop_category, shop_category_info in self.shop_data.items():
                for good_hex_dig, good_info in shop_category_info.items():
                    good_type_translation_key = good_info['good_type_translation_key']

                    good_name = self.server.language.translate(
                        good_type_translation_key,
                        None,
                        player.locale
                    )

                    if keyword in good_name.lower():
                        match_num += 1

                        good_type_id = good_info['good_type_id']

                        good_enchants = good_info['good_enchants']

                        good_lore = good_info['good_lore']

                        good_purchase_price = good_info['good_purchase_price']

                        good_reclaim_price = good_info['good_reclaim_price']

                        good_mode = good_info['good_mode']

                        collectors = good_info['collectors']

                        if good_enchants and not good_lore:
                            good_button_text = (
                                f'{ColorFormat.YELLOW}'
                                f'{good_name} '
                                f'{ColorFormat.LIGHT_PURPLE}'
                                f'+'
                            )
                        elif not good_enchants and good_lore:
                            good_button_text = (
                                f'{ColorFormat.YELLOW}'
                                f'{good_name} '
                                f'{ColorFormat.AQUA}'
                                f'+'
                            )
                        elif good_enchants and good_lore:
                            good_button_text = (
                                f'{ColorFormat.YELLOW}'
                                f'{good_name} '
                                f'{ColorFormat.LIGHT_PURPLE}'
                                f'+ '
                                f'{ColorFormat.AQUA}'
                                f'+'
                            )
                        else:
                            good_button_text = (
                                f'{ColorFormat.YELLOW}'
                                f'{good_name}'
                            )

                        result_from.add_button(
                            good_button_text,
                            icon=self.get_texture(good_type_id),
                            on_click=self.official_shop_single_good(
                                shop_category,
                                good_hex_dig,
                                good_name,
                                good_type_id,
                                good_enchants,
                                good_lore,
                                good_purchase_price,
                                good_reclaim_price,
                                good_mode,
                                collectors
                            )
                        )

            result_from.content = (
                f'{ColorFormat.GREEN}' +
                self.get_text(p, "result_form.content").format(match_num)
            )

            p.send_form(result_from)

        official_shop_search_good_form.on_submit = on_submit

        player.send_form(official_shop_search_good_form)

    # Official shop: reload configurations
    def reload_config_r(self, player: Player):
        textinput = TextInput(
            label=f'{ColorFormat.GREEN}'
                  f'> {self.get_text(player, "official_shop")}\n'
                  f'\n'
                  f'{ColorFormat.GREEN}'
                  f'{self.get_text(player, "official_shop_reload_config_form.textinput.label")}: '
                  f'{ColorFormat.WHITE}'
                  f'{self.config_data["good_reclaim_durability_threshold"]}',
            placeholder=self.get_text(player, "official_shop_reload_config_form.textinput.placeholder"),
            default_value=str(self.config_data['good_reclaim_durability_threshold'])
        )

        official_shop_reload_config_form = ModalForm(
            title=f'{ColorFormat.BOLD}{ColorFormat.LIGHT_PURPLE}'
                  f'{self.get_text(player, "official_shop_reload_config_form.title")}',
            controls=[
                textinput
            ],
            submit_button=f'{ColorFormat.YELLOW}'
                          f'{self.get_text(player, "official_shop_reload_config_form.submit_button")}',
            on_close=self.back_to_main_form
        )

        def on_submit(p: Player, json_str: str):
            data = json.loads(json_str)

            try:
                update_good_reclaim_durability_threshold = float(data[0])
            except:
                p.send_message(
                    f'{ColorFormat.RED}'
                    f'{self.get_text(p, "message.type_error")}'
                )

                return

            if (
                update_good_reclaim_durability_threshold < 0
                or
                update_good_reclaim_durability_threshold > 1
            ):
                p.send_message(
                    f'{ColorFormat.RED}'
                    f'{self.get_text(p, "message.type_error")}'
                )

                return

            self.config_data['good_reclaim_durability_threshold'] = round(update_good_reclaim_durability_threshold, 1)

            self.save_config_data()

            p.send_message(
                f'{ColorFormat.YELLOW}'
                f'{self.get_text(p, "official_shop_reload_config.message.success")}'
            )

        official_shop_reload_config_form.on_submit = on_submit

        player.send_form(official_shop_reload_config_form)

    # Player shop: main form
    def player_shop(self, player: Player):
        player_shop_form = ActionForm(
            title=f'{ColorFormat.BOLD}{ColorFormat.LIGHT_PURPLE}'
                  f'{self.get_text(player, "player_shop_form.title")}',
            content=f'{ColorFormat.GREEN}'
                    f'{self.get_text(player, "player_shop_form.content")}',
            on_close=self.back_to_main_form
        )

        player_shop_form.add_button(
            f'{ColorFormat.YELLOW}'
            f'{self.get_text(player, "button.back")}',
            icon='textures/ui/refresh_light',
            on_click=self.back_to_main_form
        )

        player.send_form(player_shop_form)

    # Save shop data
    def save_shop_data(self):
        with open(shop_data_file_path, 'w+', encoding='utf-8') as f:
            json_str = json.dumps(
                self.shop_data,
                indent=4,
                ensure_ascii=False
            )

            f.write(json_str)

    # Save config data
    def save_config_data(self):
        with open(config_data_file_path, 'w+', encoding='utf-8') as f:
            json_str = json.dumps(
                self.config_data,
                indent=4,
                ensure_ascii=False
            )

            f.write(json_str)

    @event_handler
    def on_player_interact(self, event: PlayerInteractEvent):
        if not event.player.is_op:
            if (
                    (
                        event.block.type == 'minecraft:mob_spawner'
                        or
                        event.block.type == 'minecraft:trial_spawner'
                    )
                    and
                    'spawn_egg' in event.item.type.id
            ):
                event.cancel()

    @event_handler
    def on_server_command(self, event: ServerCommandEvent):
        if event.command == '/ustr':
            new_shop_data = {}

            with open(shop_data_file_path, 'r', encoding='utf-8') as f:
                old_shop_data = json.loads(f.read())

            for old_shop_category in old_shop_data.keys():
                new_shop_data[old_shop_category] = {}

            for old_shop_category, old_shop_category_info in old_shop_data.items():
                for key, value in old_shop_category_info.items():
                    if key == 'category_icon':
                        continue

                    hash_object = hashlib.sha256(str(datetime.datetime.now()).encode())
                    good_hex_dig = hash_object.hexdigest()

                    print(good_hex_dig)

                    good_type_id = key

                    itemstack = ItemStack(
                        type=good_type_id
                    )

                    good_type_translation_key = itemstack.type.translation_key

                    good_purchase_price = value['good_price']

                    good_reclaim_price = int(good_purchase_price * 0.5)

                    good_mode = value['good_mode'].replace('_', ' ')

                    collectors = value['collectors']

                    new_shop_data[old_shop_category][good_hex_dig] = {
                        'good_type_translation_key': good_type_translation_key,
                        'good_type_id': good_type_id,
                        'good_enchants': {},
                        'good_lore': [],
                        'good_purchase_price': good_purchase_price,
                        'good_reclaim_price': good_reclaim_price,
                        'good_mode': good_mode,
                        'collectors': collectors
                    }

            self.shop_data = new_shop_data

            self.save_shop_data()

            self.logger.info(
                f'{ColorFormat.YELLOW}'
                f'All done! Enjoy your new journey...'
            )

    # Get text
    def get_text(self, player: Player, text_key: str) -> str:
        player_lang = player.locale

        try:
            if self.langs.get(player_lang) is None:
                text_value = self.langs['en_US'][text_key]
            else:
                if self.langs[player_lang].get(text_key) is None:
                    text_value = self.langs['en_US'][text_key]
                else:
                    text_value = self.langs[player_lang][text_key]

            return text_value
        except Exception as e:
            self.logger.error(
                f'{ColorFormat.RED}'
                f'{e}'
            )

            return text_key

    # Get texture
    def get_texture(self, texture_key: str):
        if self.textures.get(texture_key) is not None:
            texture_value = self.textures[texture_key]

            return texture_value
        else:
            return None

    def back_to_main_form(self, player: Player):
        player.perform_command('us')

    def back_to_menu(self, player: Player):
        player.perform_command('cd')

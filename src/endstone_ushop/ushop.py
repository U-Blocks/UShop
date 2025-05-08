import os
import json

from endstone_ushop.lang import lang

from endstone.plugin import Plugin
from endstone import ColorFormat, Player
from endstone.command import Command, CommandSender, CommandSenderWrapper
from endstone.form import ActionForm, ModalForm, Dropdown, TextInput
from endstone.event import event_handler, PlayerInteractEvent

current_dir = os.getcwd()
first_dir = os.path.join(current_dir, 'plugins', 'ushop')
if not os.path.exists(first_dir):
    os.mkdir(first_dir)

lang_dir = os.path.join(first_dir, 'lang')
if not os.path.exists(lang_dir):
    os.mkdir(lang_dir)

shop_data_file_path = os.path.join(first_dir, 'shop.json')
config_data_file_path = os.path.join(first_dir, 'config.json')

menu_data_file_path = os.path.join(current_dir, 'plugins', 'zx_ui')
money_data_file_path = os.path.join(current_dir, 'plugins', 'umoney', 'money.json')


class ushop(Plugin):
    api_version = '0.7'

    def on_enable(self):
        # Check whether pre-plugin UMoney is installed.
        if not os.path.exists(money_data_file_path):
            self.logger.error(f'{ColorFormat.RED}缺少前置 UMoney...')
            self.server.plugin_manager.disable_plugin(self)

        # Load shop data
        if not os.path.exists(shop_data_file_path):
            shop_data = {}
            with open(shop_data_file_path, 'w', encoding='utf-8') as f:
                json_str = json.dumps(shop_data, indent=4, ensure_ascii=False)
                f.write(json_str)
        else:
            with open(shop_data_file_path, 'r', encoding='utf-8') as f:
                shop_data = json.loads(f.read())

        # Initialize shop data
        if len(shop_data) != 0:
            for catgory_info in shop_data.values():
                for key, value in catgory_info.items():
                    if key == 'category_icon':
                        continue
                    if value.get('good_mode') is None:
                        value['good_mode'] = 'purchase_and_reclaim'
                    if value.get('collectors') is None:
                        value['collectors'] = []

            with open(shop_data_file_path, 'w+', encoding='utf-8') as f:
                json_str = json.dumps(shop_data, indent=4, ensure_ascii=False)
                f.write(json_str)

        self.shop_data = shop_data

        # Load config data
        if not os.path.exists(config_data_file_path):
            config_data = {
                'reclaim_rate': 0.5
            }
            with open(config_data_file_path, 'w', encoding='utf-8') as f:
                json_str = json.dumps(config_data, indent=4, ensure_ascii=False)
                f.write(json_str)
        else:
            with open(config_data_file_path, 'r', encoding='utf-8') as f:
                config_data = json.loads(f.read())
        self.config_data = config_data

        # Load lang data
        self.lang_data = lang.load_lang(self, lang_dir)

        self.command_sender = CommandSenderWrapper(
            self.server.command_sender,
            on_message=None
        )
        self.player_with_add_good_mode_list = []
        self.register_events(self)
        self.logger.info(f'{ColorFormat.YELLOW}UShop is enabled...')

    commands = {
        'us': {
            'description': 'Call out main form of UShop',
            'usages': ['/us'],
            'permissions': ['ushop.command.us']
        }
    }

    permissions = {
        'ushop.command.us': {
            'description': 'Call out main form of UShop',
            'default': True
        }
    }

    def on_command(self, sender: CommandSender, command: Command, args: list[str]) -> None:
        if command.name == 'us':
            if not isinstance(sender, Player):
                sender.send_message(f'{ColorFormat.RED}This command can only be executed by a player...')
                return
            player = sender
            player_money = self.server.plugin_manager.get_plugin('umoney').api_get_player_money(player.name)
            main_form = ActionForm(
                title=f'{ColorFormat.BOLD}{ColorFormat.LIGHT_PURPLE}{self.get_text(player, "main_form.title")}',
                content=f'{ColorFormat.GREEN}{self.get_text(player, "your_money")}: '
                        f'{ColorFormat.WHITE}{player_money}\n'
                        f'{ColorFormat.GREEN}{self.get_text(player, "main_form.content")}'
            )
            if player.is_op:
                main_form.add_button(f'{ColorFormat.YELLOW}{self.get_text(player, "main_form.button.add_shop_category")}',
                                     icon='textures/ui/color_plus', on_click=self.add_shop_category)
                main_form.add_button(f'{ColorFormat.YELLOW}{self.get_text(player, "main_form.button.toggle_add_good_mode")}',
                                     icon='textures/ui/toggle_on', on_click=self.toggle_add_good_mode)
                main_form.add_button(f'{ColorFormat.YELLOW}{self.get_text(player, "main_form.button.reload_config")}',
                                     icon='textures/ui/icon_setting', on_click=self.reload_config_data)
            main_form.add_button(f'{ColorFormat.YELLOW}{self.get_text(player, "main_form.button.search_good")}',
                                 icon='textures/ui/magnifyingGlass', on_click=self.good_search)
            main_form.add_button(f'{ColorFormat.YELLOW}{self.get_text(player, "main_form.button.collect_good")}',
                                 icon='textures/ui/icon_blackfriday', on_click=self.good_collection)

            for category_name in self.shop_data.keys():
                category_icon = self.shop_data[category_name]['category_icon']
                main_form.add_button(f'{ColorFormat.YELLOW}{category_name}',
                                     icon=category_icon, on_click=self.shop_category(category_name))

            if os.path.exists(menu_data_file_path):
                main_form.add_button(f'{ColorFormat.YELLOW}{self.get_text(player, "main_form.button.back_to_zx_ui")}',
                                     icon='textures/ui/refresh_light', on_click=self.back_to_menu)
                main_form.on_close = self.back_to_menu
            else:
                main_form.add_button(f'{ColorFormat.YELLOW}{self.get_text(player, "main_form.button.close")}',
                                     icon='textures/ui/cancel', on_click=None)
                main_form.on_close = None
            player.send_form(main_form)

    # Add a new shop category
    def add_shop_category(self, player: Player) -> None:
        textinput1 = TextInput(
            label=f'{ColorFormat.GREEN}{self.get_text(player, "add_shop_category_form.textinput1.label")}',
            placeholder=self.get_text(player, "add_shop_category_form.textinput1.placeholder")
        )
        textinput2 = TextInput(
            label=f'{ColorFormat.GREEN}{self.get_text(player, "add_shop_category_form.textinput2.label")}',
            placeholder=self.get_text(player, "add_shop_category_form.textinput2.placeholder")
        )
        add_shop_category_form = ModalForm(
            title=f'{ColorFormat.BOLD}{ColorFormat.LIGHT_PURPLE}{self.get_text(player, "add_shop_category_form.title")}',
            controls=[textinput1, textinput2],
            on_close=self.back_to_main_form,
            submit_button=f'{ColorFormat.YELLOW}{self.get_text(player, "add_shop_category_form.submit_button")}'
        )
        def on_submit(player: Player, json_str: str):
            data = json.loads(json_str)
            if len(data[0]) == 0:
                player.send_message(f'{ColorFormat.RED}{self.get_text(player, "message.type_error")}')
                return
            already_exist_category_list = [key for key in self.shop_data.keys()]
            if data[0] in already_exist_category_list:
                player.send_message(f'{ColorFormat.RED}{self.get_text(player, "add_shop_category.message.fail")}: '
                                    f'{ColorFormat.WHITE}'
                                    + self.get_text(player, "add_shop_category.message.fail.reason").format(data[0]))
                return
            category_name = data[0]
            category_icon = data[1]
            self.shop_data[category_name] = {'category_icon': category_icon}
            self.save_shop_data()
            player.send_message(f'{ColorFormat.YELLOW}{self.get_text(player, "add_shop_category.message.success")}')
        add_shop_category_form.on_submit = on_submit
        player.send_form(add_shop_category_form)

    # Shop category
    def shop_category(self, category_name):
        def on_click(player: Player):
            player_money = self.server.plugin_manager.get_plugin('umoney').api_get_player_money(player.name)
            shop_category_form = ActionForm(
                title=f'{ColorFormat.BOLD}{ColorFormat.LIGHT_PURPLE}{category_name}',
                content=f'{ColorFormat.GREEN}{self.get_text(player, "your_money")}: '
                        f'{ColorFormat.WHITE}{player_money}\n'
                        f'{ColorFormat.GREEN}{self.get_text(player, "shop_category_form.content")}',
                on_close=self.back_to_main_form
            )
            if player.is_op:
                shop_category_form.add_button(f'{ColorFormat.YELLOW}{self.get_text(player, "shop_category_form.button.edit_shop_category")}',
                                              icon='textures/ui/hammer_l', on_click=self.edit_shop_category(category_name))
            for key, value in self.shop_data[category_name].items():
                if key == 'category_icon':
                    continue
                good_type = key
                good_price = value['good_price']
                good_name = value['good_name']
                good_mode = value['good_mode']
                collectors = value['collectors']
                shop_category_form.add_button(f'{ColorFormat.YELLOW}{good_name}\n'
                                              f'{ColorFormat.GREEN}{self.get_text(player, "purchase_price")}: {good_price}',
                                              on_click=self.good(category_name, good_type, good_name, good_price, good_mode, collectors))
            shop_category_form.add_button(f'{ColorFormat.YELLOW}{self.get_text(player, "button.back")}',
                                          icon='textures/ui/refresh_light', on_click=self.back_to_main_form)
            player.send_form(shop_category_form)
        return on_click

    # Edit shop category
    def edit_shop_category(self, category_name):
        def on_click(player: Player):
            edit_shop_category_form = ActionForm(
                title=f'{ColorFormat.BOLD}{ColorFormat.LIGHT_PURPLE}{self.get_text(player, "edit_shop_category_form.title")}',
                content=f'{ColorFormat.GREEN}{self.get_text(player, "category_name")}: '
                        f'{ColorFormat.WHITE}{category_name}\n\n'
                        f'{ColorFormat.GREEN}{self.get_text(player, "edit_shop_category_form.content")}',
                on_close=self.back_to_main_form
            )
            edit_shop_category_form.add_button(f'{ColorFormat.YELLOW}{self.get_text(player, "edit_shop_category_form.button.delete_shop_category")}',
                                               icon='textures/ui/cancel', on_click=self.delete_shop_category(category_name))
            edit_shop_category_form.add_button(f'{ColorFormat.YELLOW}{self.get_text(player, "edit_shop_category_form.button.update_shop_category")}',
                                               icon='textures/ui/refresh', on_click=self.update_shop_category(category_name))
            edit_shop_category_form.add_button(f'{ColorFormat.YELLOW}{self.get_text(player, "button.back")}',
                                               icon='textures/ui/refresh_light', on_click=self.back_to_main_form)
            player.send_form(edit_shop_category_form)
        return on_click

    # Delete shop category
    def delete_shop_category(self, category_name):
        def on_click(player: Player):
            confirm_form = ActionForm(
                title=f'{ColorFormat.BOLD}{ColorFormat.LIGHT_PURPLE}{self.get_text(player, "delete_shop_category_form.title")}',
                content=f'{ColorFormat.GREEN}{self.get_text(player, "category_name")}: '
                        f'{ColorFormat.WHITE}{category_name}\n\n'
                        f'{ColorFormat.GREEN}{self.get_text(player, "delete_shop_category_form.content")}',
                on_close=self.back_to_main_form
            )
            confirm_form.add_button(f'{ColorFormat.YELLOW}{self.get_text(player, "delete_shop_category_form.button.confirm")}',
                                    icon='textures/ui/realms_slot_check', on_click=self.delete_shop_category_confirm(category_name))
            confirm_form.add_button(f'{ColorFormat.YELLOW}{self.get_text(player, "button.back")}',
                                    icon='textures/ui/refresh_light', on_click=self.back_to_main_form)
            player.send_form(confirm_form)
        return on_click

    def delete_shop_category_confirm(self, category_name):
        def on_click(player: Player):
            self.shop_data.pop(category_name)
            self.save_shop_data()
            player.send_message(f'{ColorFormat.YELLOW}{self.get_text(player, "delete_shop_category.message.success")}')
        return on_click

    # Update shop category
    def update_shop_category(self, category_name):
        def on_click(player: Player):
            textinput1 = TextInput(
                label=f'{ColorFormat.GREEN}{self.get_text(player, "category_name")}: '
                      f'{ColorFormat.WHITE}{category_name}\n\n'
                      f'{ColorFormat.GREEN}{self.get_text(player, "update_shop_category_form.textinput1.label")}',
                placeholder=self.get_text(player, "update_shop_category_form.textinput1.placeholder"),
                default_value=category_name
            )
            textinput2 = TextInput(
                label=f'{ColorFormat.GREEN}{self.get_text(player, "update_shop_category_form.textinput2.label")}',
                placeholder=self.get_text(player, "update_shop_category_form.textinput1.placeholder"),
                default_value=self.shop_data[category_name]['category_icon']
            )
            update_shop_category_form = ModalForm(
                title=f'{ColorFormat.BOLD}{ColorFormat.LIGHT_PURPLE}{self.get_text(player, "update_shop_category_form.title")}',
                controls=[textinput1, textinput2],
                on_close=self.back_to_main_form,
                submit_button=f'{ColorFormat.YELLOW}{self.get_text(player, "update_shop_category_form.submit_button")}'
            )
            def on_submit(player: Player, json_str: str):
                data = json.loads(json_str)
                if len(data[0]) == 0:
                    player.send_message(self.get_text(player, "message.type_error"))
                    return
                update_category_name = data[0]
                category_list = [key for key in self.shop_data.keys() if key != category_name]
                if update_category_name in category_list:
                    player.send_message(f'{ColorFormat.RED}{self.get_text(player, "update_shop_category.message.fail")}: {ColorFormat.WHITE}'
                                        + self.get_text(player, "update_shop_category.message.fail.reason").format(update_category_name))
                    return
                update_category_icon = data[1]
                self.shop_data[update_category_name] = self.shop_data[category_name]
                if update_category_name != category_name:
                    self.shop_data.pop(category_name)
                self.shop_data[update_category_name]['category_icon'] = update_category_icon
                self.save_shop_data()
                player.send_message(f'{ColorFormat.YELLOW}{self.get_text(player, "update_shop_category.message.success")}')
            update_shop_category_form.on_submit = on_submit
            player.send_form(update_shop_category_form)
        return on_click

    # Add good
    @event_handler
    def on_player_interact(self, event: PlayerInteractEvent):
        if event.player.name in self.player_with_add_good_mode_list:
            try:
                good_type = event.item.type
            except:
                return
            category_list = [key for key in self.shop_data.keys()]
            dropdown1 = Dropdown(
                label=f'{ColorFormat.GREEN}{self.get_text(event.player, "good_type")}: '
                      f'{ColorFormat.WHITE}{good_type}\n\n'
                      f'{ColorFormat.GREEN}{self.get_text(event.player, "add_good_form.dropdown1.label")}',
                options=category_list
            )
            good_mode_list = ['purchase_and_reclaim', 'only_purchase', 'only_reclaim']
            dropdown2 = Dropdown(
                label=f'{ColorFormat.GREEN}{self.get_text(event.player, "add_good_form.dropdown2.label")}',
                options=good_mode_list
            )
            textinput1 = TextInput(
                label=f'{ColorFormat.GREEN}{self.get_text(event.player, "add_good_form.textinput1.label")}',
                placeholder=self.get_text(event.player, "add_good_form.textinput1.placeholder")
            )
            textinput2 = TextInput(
                label=f'{ColorFormat.GREEN}{self.get_text(event.player, "add_good_form.textinput2.label")}',
                placeholder=self.get_text(event.player, "add_good_form.textinput2.placeholder")
            )
            add_good_form = ModalForm(
                title=f'{ColorFormat.BOLD}{ColorFormat.LIGHT_PURPLE}{self.get_text(event.player, "add_good_form.title")}',
                controls=[dropdown1, dropdown2, textinput1, textinput2],
                submit_button=f'{ColorFormat.YELLOW}{self.get_text(event.player, "add_good_form.submit_button")}',
                on_close=self.back_to_main_form
            )
            def on_submit(player: event.player, json_str: str):
                data = json.loads(json_str)
                category_name = category_list[data[0]]
                good_type_belong_to_this_category_list = [key for key in self.shop_data[category_name].keys() if key != 'category_icon']
                if good_type in good_type_belong_to_this_category_list:
                    player.send_message(f'{ColorFormat.RED}{self.get_text(player, "add_good.message.fail")}: '
                                        f'{ColorFormat.WHITE}'
                                        + self.get_text(player, "add_good.message.fail.reason").format(good_type))
                    return
                good_mode = good_mode_list[data[1]]
                if len(data[2]) == 0:
                    player.send_message(f'{ColorFormat.RED}{self.get_text(player, "message.type_error")}')
                    return
                else:
                    good_name = data[2]
                try:
                    good_price = int(data[3])
                except ValueError:
                    player.send_message(f'{ColorFormat.RED}{self.get_text(player, "message.type_error")}')
                    return
                if good_price <= 0:
                    player.send_message(f'{ColorFormat.RED}{self.get_text(player, "message.type_error")}')
                    return
                self.shop_data[category_name][good_type] = {
                    'good_name': good_name,
                    'good_price': good_price,
                    'good_mode': good_mode,
                    'collectors': []
                }
                self.save_shop_data()
                player.send_message(f'{ColorFormat.YELLOW}{self.get_text(player, "add_good.message.success")}')
            add_good_form.on_submit = on_submit
            event.player.send_form(add_good_form)
            event.is_cancelled = True
        else:
            if not event.player.is_op:
                if ((event.block.type == 'minecraft:mob_spawner' or event.block.type == 'minecraft:trial_spawner')
                        and 'spawn_egg' in event.item.type):
                    event.is_cancelled = True

    # Good
    def good(self, category_name, good_type, good_name, good_price, good_mode, collectors):
        def on_click(player: Player):
            player_money = self.server.plugin_manager.get_plugin('umoney').api_get_player_money(player.name)
            reclaim_rate = self.config_data['reclaim_rate']
            if int(reclaim_rate * good_price) == 0:
                good_reclaim_price = good_price
            else:
                good_reclaim_price = int(reclaim_rate * good_price)
            good_info_form = ActionForm(
                title=f'{ColorFormat.BOLD}{ColorFormat.LIGHT_PURPLE}{self.get_text(player, "good_form.title")}',
                content=f'{ColorFormat.GREEN}{self.get_text(player, "your_money")}: '
                        f'{ColorFormat.WHITE}{player_money}\n'
                        f'{ColorFormat.GREEN}{self.get_text(player, "good_type")}: '
                        f'{ColorFormat.WHITE}{good_type}\n'
                        f'{ColorFormat.GREEN}{self.get_text(player, "good_name")}: '
                        f'{ColorFormat.WHITE}{good_name}\n'
                        f'{ColorFormat.GREEN}{self.get_text(player, "purchase_price")}: '
                        f'{ColorFormat.WHITE}{good_price}\n'
                        f'{ColorFormat.GREEN}{self.get_text(player, "reclaim_price")}: '
                        f'{ColorFormat.WHITE}{good_reclaim_price}\n'
                        f'{ColorFormat.GREEN}{self.get_text(player, "good_mode")}: '
                        f'{ColorFormat.WHITE}{good_mode}\n'
                        f'{ColorFormat.GREEN}'
                         + self.get_text(player, "good_form.content").format(len(collectors)),
                on_close=self.back_to_main_form
            )
            if player.is_op:
                good_info_form.add_button(f'{ColorFormat.YELLOW}{self.get_text(player, "good_form.button.edit_good")}',
                                          icon='textures/ui/hammer_l',
                                          on_click=self.good_edit(category_name, good_type, good_name, good_price, good_reclaim_price, good_mode))
            if good_mode == 'purchase_and_reclaim' or good_mode == 'only_purchase':
                good_info_form.add_button(f'{ColorFormat.YELLOW}{self.get_text(player, "good_form.button.purchase")}',
                                          icon='textures/ui/village_hero_effect', on_click=self.good_purchase(good_type, good_name, good_price))
            if good_mode == 'purchase_and_reclaim' or good_mode == 'only_reclaim':
                good_info_form.add_button(f'{ColorFormat.YELLOW}{self.get_text(player, "good_form.button.reclaim")}',
                                          icon='textures/ui/trade_icon', on_click=self.good_reclaim(good_type, good_name, good_reclaim_price))
            if player.name not in collectors:
                good_info_form.add_button(f'{ColorFormat.YELLOW}{self.get_text(player, "good_form.button.collect_good")}',
                                          icon='textures/ui/heart_new',
                                          on_click=self.good_collect(category_name, good_type))
            else:
                good_info_form.add_button(f'{ColorFormat.YELLOW}{self.get_text(player, "good_form.button.cancel_collect_good")}',
                                          icon='textures/ui/heart_background',
                                          on_click=self.good_collect_cancel(category_name, good_type))
            good_info_form.add_button(f'{ColorFormat.YELLOW}{self.get_text(player, "button.back")}',
                                      icon='textures/ui/refresh_light', on_click=self.back_to_main_form)
            player.send_form(good_info_form)
        return on_click

    # Edit good
    def good_edit(self, category_name, good_type, good_name, good_price, good_reclaim_price, good_mode):
        def on_click(player: Player):
            good_edit_form = ActionForm(
                title=f'{ColorFormat.BOLD}{ColorFormat.LIGHT_PURPLE}{self.get_text(player, "edit_good_form.title")}',
                content=f'{ColorFormat.GREEN}{self.get_text(player, "good_type")}: '
                        f'{ColorFormat.WHITE}{good_type}\n'
                        f'{ColorFormat.GREEN}{self.get_text(player, "good_name")}: '
                        f'{ColorFormat.WHITE}{good_name}\n'
                        f'{ColorFormat.GREEN}{self.get_text(player, "purchase_price")}: '
                        f'{ColorFormat.WHITE}{good_price}\n'
                        f'{ColorFormat.GREEN}{self.get_text(player, "reclaim_price")}: '
                        f'{ColorFormat.WHITE}{good_reclaim_price}\n'
                        f'{ColorFormat.GREEN}{self.get_text(player, "good_mode")}: '
                        f'{ColorFormat.WHITE}{good_mode}\n\n'
                        f'{ColorFormat.GREEN}{self.get_text(player, "edit_good_form.content")}',
                on_close=self.back_to_main_form
            )
            good_edit_form.add_button(f'{ColorFormat.YELLOW}{self.get_text(player, "edit_good_form.button.update_good")}',
                                      icon='textures/ui/refresh',
                                      on_click=self.good_update(category_name, good_type, good_name, good_price, good_reclaim_price, good_mode))
            good_edit_form.add_button(f'{ColorFormat.YELLOW}{self.get_text(player, "edit_good_form.button.delete_good")}',
                                      icon='textures/ui/cancel',
                                      on_click=self.good_delete(category_name, good_type, good_name, good_price, good_reclaim_price, good_mode))
            good_edit_form.add_button(f'{ColorFormat.YELLOW}{self.get_text(player, "button.back")}',
                                      icon='textures/ui/refresh_light', on_click=self.back_to_main_form)
            player.send_form(good_edit_form)
        return on_click

    # Update good
    def good_update(self, category_name, good_type, good_name, good_price, good_reclaim_price, good_mode):
        def on_click(player: Player):
            textinput1 = TextInput(
                label=f'{ColorFormat.GREEN}{self.get_text(player, "good_type")}: '
                        f'{ColorFormat.WHITE}{good_type}\n'
                        f'{ColorFormat.GREEN}{self.get_text(player, "good_name")}: '
                        f'{ColorFormat.WHITE}{good_name}\n'
                        f'{ColorFormat.GREEN}{self.get_text(player, "purchase_price")}: '
                        f'{ColorFormat.WHITE}{good_price}\n'
                        f'{ColorFormat.GREEN}{self.get_text(player, "reclaim_price")}: '
                        f'{ColorFormat.WHITE}{good_reclaim_price}\n'
                        f'{ColorFormat.GREEN}{self.get_text(player, "good_mode")}: '
                        f'{ColorFormat.WHITE}{good_mode}\n\n'
                        f'{ColorFormat.GREEN}{self.get_text(player, "update_good_form.textinput1.label")}',
                placeholder=self.get_text(player, "update_good_form.textinput1.placeholder"),
                default_value=good_name
            )
            textinput2 = TextInput(
                label=f'{ColorFormat.GREEN}{self.get_text(player, "update_good_form.textinput2.label")}',
                placeholder=self.get_text(player, "update_good_form.textinput2.placeholder"),
                default_value=f'{good_price}'
            )
            good_mode_list = ['purchase_and_reclaim', 'only_purchase', 'only_reclaim']
            dropdown = Dropdown(
                label=f'{ColorFormat.GREEN}{self.get_text(player, "update_good_form.dropdown.label")}',
                options=good_mode_list,
                default_index=good_mode_list.index(good_mode)
            )
            good_update_form = ModalForm(
                title=f'{ColorFormat.BOLD}{ColorFormat.LIGHT_PURPLE}{self.get_text(player, "update_good_form.title")}',
                controls=[textinput1, textinput2, dropdown],
                on_close=self.back_to_main_form,
                submit_button=f'{ColorFormat.YELLOW}{self.get_text(player, "update_good_form.submit_button")}'
            )
            def on_submit(player: Player, json_str: str):
                data = json.loads(json_str)
                if len(data[0]) == 0:
                    player.send_message(f'{ColorFormat.RED}{self.get_text(player, "message.type_error")}')
                    return
                update_good_name = data[0]
                try:
                    update_good_price = int(data[1])
                except ValueError:
                    player.send_message(f'{ColorFormat.RED}{self.get_text(player, "message.type_error")}')
                    return
                if update_good_price <= 0:
                    player.send_message(f'{ColorFormat.RED}{self.get_text(player, "message.type_error")}')
                    return
                update_good_mode = good_mode_list[data[2]]
                self.shop_data[category_name][good_type]['good_name'] = update_good_name
                self.shop_data[category_name][good_type]['good_price'] = update_good_price
                self.shop_data[category_name][good_type]['good_mode'] = update_good_mode
                self.save_shop_data()
                player.send_message(f'{ColorFormat.YELLOW}{self.get_text(player, "update_good.message.success")}')
            good_update_form.on_submit = on_submit
            player.send_form(good_update_form)
        return on_click

    # Delete good
    def good_delete(self, category_name, good_type, good_name, good_price, good_reclaim_price, good_mode):
        def on_click(player: Player):
            confirm_form = ActionForm(
                title=f'{ColorFormat.BOLD}{ColorFormat.LIGHT_PURPLE}{self.get_text(player, "delte_good_form.title")}',
                content=f'{ColorFormat.GREEN}{self.get_text(player, "good_type")}: '
                        f'{ColorFormat.WHITE}{good_type}\n'
                        f'{ColorFormat.GREEN}{self.get_text(player, "good_name")}: '
                        f'{ColorFormat.WHITE}{good_name}\n'
                        f'{ColorFormat.GREEN}{self.get_text(player, "purchase_price")}: '
                        f'{ColorFormat.WHITE}{good_price}\n'
                        f'{ColorFormat.GREEN}{self.get_text(player, "reclaim_price")}: '
                        f'{ColorFormat.WHITE}{good_reclaim_price}\n'
                        f'{ColorFormat.GREEN}{self.get_text(player, "good_mode")}: '
                        f'{ColorFormat.WHITE}{good_mode}\n\n'
                        f'{ColorFormat.GREEN}{self.get_text(player, "delte_good_form.content")}',
                on_close=self.back_to_main_form
            )
            confirm_form.add_button(f'{ColorFormat.YELLOW}{self.get_text(player, "delte_good_form.button.confirm")}',
                                    icon='textures/ui/realms_slot_check', on_click=self.good_delete_confirm(category_name, good_type))
            confirm_form.add_button(f'{ColorFormat.YELLOW}{self.get_text(player, "button.back")}',
                                    icon='textures/ui/refresh_light', on_click=self.back_to_main_form)
            player.send_form(confirm_form)
        return on_click

    def good_delete_confirm(self, category_name, good_type):
        def on_click(player: Player):
            self.shop_data[category_name].pop(good_type)
            self.save_shop_data()
            player.send_message(f'{ColorFormat.YELLOW}{self.get_text(player, "delte_good.message.success")}')
        return on_click

    # Good purchase
    def good_purchase(self, good_type, good_name, good_price):
        def on_click(player: Player):
            player_money = self.server.plugin_manager.get_plugin('umoney').api_get_player_money(player.name)
            textinput = TextInput(
                label=f'{ColorFormat.GREEN}{self.get_text(player, "your_money")}: '
                        f'{ColorFormat.WHITE}{player_money}\n'
                        f'{ColorFormat.GREEN}{self.get_text(player, "good_type")}: '
                        f'{ColorFormat.WHITE}{good_type}\n'
                        f'{ColorFormat.GREEN}{self.get_text(player, "good_name")}: '
                        f'{ColorFormat.WHITE}{good_name}\n'
                        f'{ColorFormat.GREEN}{self.get_text(player, "purchase_price")}: '
                        f'{ColorFormat.WHITE}{good_price}\n\n'
                        f'{ColorFormat.GREEN}{self.get_text(player, "good_purchase_form.textinput.label")}',
                placeholder=self.get_text(player, "good_purchase_form.textinput.placeholder")
            )
            good_buy_form = ModalForm(
                title=f'{ColorFormat.BOLD}{ColorFormat.LIGHT_PURPLE}{self.get_text(player, "good_purchase_form.title")}',
                controls=[textinput],
                submit_button=f'{ColorFormat.YELLOW}{self.get_text(player, "good_purchase_form.submit_button")}',
                on_close=self.back_to_main_form
            )
            def on_submit(player: Player, json_str: str):
                data = json.loads(json_str)
                try:
                    amount = int(data[0])
                except ValueError:
                    player.send_message(f'{ColorFormat.RED}{self.get_text(player, "message.type_error")}')
                    return
                if amount < 0:
                    player.send_message(f'{ColorFormat.RED}{self.get_text(player, "message.type_error")}')
                    return
                total_price = amount * good_price
                player_money_now = self.server.plugin_manager.get_plugin('umoney').api_get_player_money(player.name)
                if player_money_now < total_price:
                    player.send_message(f'{ColorFormat.RED}{self.get_text(player, "good_purchase.message.fail")}: '
                                        f'{ColorFormat.WHITE}{self.get_text(player, "good_purchase.message.fail")}')
                    return
                if player.name.find(' ') != -1:
                    player_name = f'"{player.name}"'
                else:
                    player_name = player.name
                self.server.dispatch_command(self.command_sender,
                                             f'give {player_name} {good_type} {amount}')
                # yes!!!
                self.server.dispatch_command(self.command_sender,
                                             f'playsound mob.villager.yes {player_name}')
                player.send_message(f'{ColorFormat.YELLOW}{self.get_text(player, "good_purchase.message.success")}')
                self.server.plugin_manager.get_plugin('umoney').api_change_player_money(player.name, -total_price)
            good_buy_form.on_submit = on_submit
            player.send_form(good_buy_form)
        return on_click

    # Good reclaim
    def good_reclaim(self, good_type, good_name, good_reclaim_price):
        def on_click(player: Player):
            player_money = self.server.plugin_manager.get_plugin('umoney').api_get_player_money(player.name)
            player_inventory = []
            for content in player.inventory.contents:
                if type(content) == type(None):
                    player_inventory.append('Null')
                else:
                    player_inventory.append(content.type)
            if good_type not in player_inventory:
                player.send_message(f'{ColorFormat.RED}{self.get_text(player, "good_reclaim.message.fail")}: '
                                    f'{ColorFormat.WHITE}{self.get_text(player, "good_reclaim.message.fail.reason")}')
                return
            else:
                has_amount = 0
                index = 0
                for good_type_any in player_inventory:
                    if good_type_any == good_type:
                        has_amount += player.inventory.get_item(index).amount
                        index += 1
                    else:
                        index += 1
            textinput = TextInput(
                label=f'{ColorFormat.GREEN}{self.get_text(player, "your_money")}: '
                        f'{ColorFormat.WHITE}{player_money}\n'
                        f'{ColorFormat.GREEN}{self.get_text(player, "good_type")}: '
                        f'{ColorFormat.WHITE}{good_type}\n'
                        f'{ColorFormat.GREEN}{self.get_text(player, "good_name")}: '
                        f'{ColorFormat.WHITE}{good_name}\n'
                        f'{ColorFormat.GREEN}{self.get_text(player, "reclaim_price")}: '
                        f'{ColorFormat.WHITE}{good_reclaim_price}\n\n'
                        f'{ColorFormat.GREEN}'
                        + self.get_text(player, "good_reclaim_form.textinput.label1").format(has_amount, good_name) + '\n'
                        f'{self.get_text(player, "good_reclaim_form.textinput.label2")}',
                placeholder=self.get_text(player, "good_reclaim_form.textinput.placeholder").format(has_amount)
            )
            good_reclaim_form = ModalForm(
                title=f'{ColorFormat.BOLD}{ColorFormat.LIGHT_PURPLE}{self.get_text(player, "good_reclaim_form.title")}',
                controls=[textinput],
                submit_button=f'{ColorFormat.YELLOW}{self.get_text(player, "good_reclaim_form.submit_button")}',
                on_close=self.back_to_main_form
            )
            def on_submit(player: Player, json_str: str):
                data = json.loads(json_str)
                try:
                    amount = int(data[0])
                except ValueError:
                    player.send_message(f'{ColorFormat.RED}{self.get_text(player, "message.type_error")}')
                    return
                if amount < 0 or amount > has_amount:
                    player.send_message(f'{ColorFormat.RED}{self.get_text(player, "message.type_error")}')
                    return
                total_price = amount * good_reclaim_price
                if player.name.find(' ') != -1:
                    player_name = f'"{player.name}"'
                else:
                    player_name = player.name
                self.server.dispatch_command(self.command_sender,
                                             f'clear {player_name} {good_type} 0 {amount}')
                # yes!!!
                self.server.dispatch_command(self.command_sender,
                                             f'playsound mob.villager.yes {player_name}')
                player.send_message(f'{ColorFormat.YELLOW}{self.get_text(player, "good_reclaim.message.success")}')
                self.server.plugin_manager.get_plugin('umoney').api_change_player_money(player.name, total_price)
            good_reclaim_form.on_submit = on_submit
            player.send_form(good_reclaim_form)
        return on_click

    # Good search
    def good_search(self, player: Player) -> None:
        textinput = TextInput(
            label=f'{ColorFormat.GREEN}{self.get_text(player, "good_search_form.textinput.label")}',
            placeholder=self.get_text(player, "good_search_form.textinput.placeholder")
        )
        good_search_form = ModalForm(
            title=f'{ColorFormat.BOLD}{ColorFormat.LIGHT_PURPLE}{self.get_text(player, "good_search_form.title")}',
            controls=[textinput],
            submit_button=f'{ColorFormat.YELLOW}{self.get_text(player, "good_search_form.submit_button")}',
            on_close=self.back_to_main_form
        )
        def on_submit(player: Player, json_str: str):
            data = json.loads(json_str)
            if len(data[0]) == 0:
                player.send_message(f'{ColorFormat.RED}{self.get_text(player, "message.type_error")}')
                return
            keyword = data[0]
            result_num = 0
            good_search_result_form = ActionForm(
                title=f'{ColorFormat.BOLD}{ColorFormat.LIGHT_PURPLE}{self.get_text(player, "good_search_result_form.title")}',
                on_close=self.back_to_main_form
            )
            for category_name, category_info in self.shop_data.items():
                for key, value in category_info.items():
                    if key == 'category_icon':
                        continue
                    good_type = key
                    good_name = value['good_name']
                    if keyword in good_name:
                        result_num += 1
                        good_price = value['good_price']
                        good_mode = value['good_mode']
                        collectors = value['collectors']
                        good_search_result_form.add_button(f'{ColorFormat.YELLOW}{good_name}\n'
                                                           f'{ColorFormat.GREEN}{self.get_text(player, "purchase_price")}: {good_price}',
                                                           on_click=self.good(category_name, good_type, good_name, good_price, good_mode, collectors))

            if result_num == 0:
                player.send_message(f'{ColorFormat.RED}{self.get_text(player, "good_search_result.message.fail")}')
            else:
                good_search_result_form.content = ColorFormat.GREEN + self.get_text(player, "good_search_result.message.success").format(result_num)
                player.send_form(good_search_result_form)
        good_search_form.on_submit = on_submit
        player.send_form(good_search_form)

    # Good collect
    def good_collect(self, category_name, good_type):
        def on_click(player: Player):
            self.shop_data[category_name][good_type]['collectors'].append(player.name)
            player.send_message(f'{ColorFormat.YELLOW}{self.get_text(player, "good_collect.message.success")}')
        return on_click

    # Cancel the collections
    def good_collect_cancel(self, category_name, good_type):
        def on_click(player: Player):
            self.shop_data[category_name][good_type]['collectors'].remove(player.name)
            player.send_message(f'{ColorFormat.YELLOW}{self.get_text(player, "good_collect_cancel.message.success")}')
        return on_click

    # Player's good collections
    def good_collection(self, player: Player) -> None:
        good_collection_form = ActionForm(
            title=f'{ColorFormat.BOLD}{ColorFormat.LIGHT_PURPLE}{self.get_text(player, "good_collection_form.title")}',
            on_close=self.back_to_main_form
        )
        for category_name, category_info in self.shop_data.items():
            for key, value in category_info.items():
                if key == 'category_icon':
                    continue
                good_type = key
                collectors = value['collectors']
                if player.name in collectors:
                    good_name = value['good_name']
                    good_price = value['good_price']
                    good_mode = value['good_mode']
                    good_collection_form.add_button(f'{ColorFormat.YELLOW}{good_name}\n'
                                                       f'{ColorFormat.GREEN}{self.get_text(player, "purchase_price")}: {good_price}',
                                                       on_click=self.good(category_name, good_type, good_name,
                                                                          good_price, good_mode, collectors))
        num = len(good_collection_form.buttons)
        if num == 0:
            good_collection_form.content = f'{ColorFormat.GREEN}{self.get_text(player, "good_collection_form.content1")}'
        else:
            good_collection_form.content = ColorFormat.GREEN + self.get_text(player, "good_collection_form.content2").format(num)
        good_collection_form.add_button(f'{ColorFormat.YELLOW}{self.get_text(player, "button.back")}',
                                        icon='textures/ui/refresh_light', on_click=self.back_to_main_form)
        player.send_form(good_collection_form)

    # Toggle on/off add good mode
    def toggle_add_good_mode(self, player: Player) -> None:
        category_list = [key for key in self.shop_data.keys()]
        if len(category_list) == 0 and player.name not in self.player_with_add_good_mode_list:
            player.send_message(f'{ColorFormat.RED}{self.get_text(player, "toggle_add_good_mode.message.fail")}: '
                                f'{ColorFormat.WHITE}{self.get_text(player, "toggle_add_good_mode.message.fail.reason")}')
            return
        if player.name not in self.player_with_add_good_mode_list:
            self.player_with_add_good_mode_list.append(player.name)
            player.send_message(f'{ColorFormat.YELLOW}{self.get_text(player, "toggle_add_good_mode.message.on.success")}')
        else:
            self.player_with_add_good_mode_list.remove(player.name)
            player.send_message(f'{ColorFormat.YELLOW}{self.get_text(player, "toggle_add_good_mode.message.off.success")}')

    # Reload configurations
    def reload_config_data(self, player: Player) -> None:
        reload_config_data_form = ActionForm(
            title=f'{ColorFormat.BOLD}{ColorFormat.LIGHT_PURPLE}{self.get_text(player, "reload_config_form.title")}',
            content=f'{ColorFormat.GREEN}{self.get_text(player, "reload_config_form.content")}',
            on_close=self.back_to_main_form
        )
        reload_config_data_form.add_button(f'{ColorFormat.YELLOW}{self.get_text(player, "reload_config_form.button.reload_global_config")}',
                                           icon='textures/ui/icon_setting', on_click=self.reload_global_config_data)
        reload_config_data_form.add_button(f'{ColorFormat.YELLOW}{self.get_text(player, "reload_config_form.button.reload_shop_data")}',
                                           icon='textures/ui/icon_setting', on_click=self.reload_shop_data)
        reload_config_data_form.add_button(f'{ColorFormat.YELLOW}{self.get_text(player, "button.back")}',
                                           icon='textures/ui/refresh_light', on_click=self.back_to_main_form)
        player.send_form(reload_config_data_form)

    # Reload global configurations
    def reload_global_config_data(self, player: Player) -> None:
        reclaim_rate = self.config_data['reclaim_rate']
        textinput = TextInput(
            label=f'{ColorFormat.GREEN}{self.get_text(player, "reload_global_config_form.textinput.label")}: '
                  f'{ColorFormat.WHITE}{reclaim_rate}',
            placeholder=self.get_text(player, "reload_global_config_form.textinput.placeholder"),
            default_value=f'{reclaim_rate}'
        )
        reload_reclaim_rate_form = ModalForm(
            title=f'{ColorFormat.BOLD}{ColorFormat.LIGHT_PURPLE}{self.get_text(player, "reload_global_config_form.title")}',
            controls=[textinput],
            submit_button=f'{ColorFormat.YELLOW}{self.get_text(player, "reload_global_config_form.submit_button")}',
            on_close=self.back_to_main_form
        )
        def on_submit(player: Player, json_str: str):
            data = json.loads(json_str)
            try:
                update_reclaim_rate = float(data[0])
            except ValueError:
                player.send_message(f'{ColorFormat.RED}{self.get_text(player, "message.type_error")}')
                return
            if update_reclaim_rate > 1 or update_reclaim_rate <= 0:
                player.send_message(f'{ColorFormat.RED}{self.get_text(player, "message.type_error")}')
                return
            self.config_data['reclaim_rate'] = update_reclaim_rate
            self.save_config_data()
            player.send_message(f'{ColorFormat.YELLOW}{self.get_text(player, "reload_global_config.message.success")}')
        reload_reclaim_rate_form.on_submit = on_submit
        player.send_form(reload_reclaim_rate_form)

    # Reload shop data
    def reload_shop_data(self, player: Player) -> None:
        with open(shop_data_file_path, 'r', encoding='utf-8') as f:
            self.shop_data = json.loads(f.read())
        player.send_message(f'{ColorFormat.YELLOW}{self.get_text(player, "reload_shop_data.message.success")}')

    # Save shop data
    def save_shop_data(self) -> None:
        with open(shop_data_file_path, 'w+', encoding='utf-8') as f:
            json_str = json.dumps(self.shop_data, indent=4, ensure_ascii=False)
            f.write(json_str)

    # Save config data
    def save_config_data(self) -> None:
        with open(config_data_file_path, 'w+', encoding='utf-8') as f:
            json_str = json.dumps(self.config_data, indent=4, ensure_ascii=False)
            f.write(json_str)

    # Get text
    def get_text(self, player: Player, text_key: str) -> str:
        try:
            lang = player.locale
            if self.lang_data.get(lang) is None:
                text_value = self.lang_data['en_US'][text_key]
            else:
                if self.lang_data[lang].get(text_key) is None:
                    text_value = self.lang_data['en_US'][text_key]
                else:
                    text_value = self.lang_data[lang][text_key]
            return text_value
        except:
            return text_key

    def back_to_main_form(self, player: Player):
        player.perform_command('us')

    def back_to_menu(self, player: Player):
        player.perform_command('cd')



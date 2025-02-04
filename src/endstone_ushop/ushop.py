import os
import json
from endstone.plugin import Plugin
from endstone import ColorFormat, Player
from endstone.command import Command, CommandSender, CommandSenderWrapper
from endstone.form import ActionForm, ModalForm, Dropdown, TextInput
from endstone.event import event_handler, PlayerInteractEvent

current_dir = os.getcwd()
first_dir = os.path.join(current_dir, 'plugins', 'ushop')
if not os.path.exists(first_dir):
    os.mkdir(first_dir)
shop_data_file_path = os.path.join(first_dir, 'shop.json')
config_data_file_path = os.path.join(first_dir, 'config.json')
menu_data_file_path = os.path.join(current_dir, 'plugins', 'zx_ui')
money_data_file_path = os.path.join(current_dir, 'plugins', 'money', 'money.json')

class ushop(Plugin):
    api_version = '0.5'

    def on_enable(self):
        # 加载商店数据
        if not os.path.exists(shop_data_file_path):
            shop_data = {}
            with open(shop_data_file_path, 'w', encoding='utf-8') as f:
                json_str = json.dumps(shop_data, indent=4, ensure_ascii=False)
                f.write(json_str)
        else:
            with open(shop_data_file_path, 'r', encoding='utf-8') as f:
                shop_data = json.loads(f.read())
        self.shop_data = shop_data
        # 加载配置文件数据
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
        # 加载玩家经济数据
        if not os.path.exists(money_data_file_path):
            self.logger.info(f'{ColorFormat.YELLOW}缺少前置 jsonmoney...')
            self.server.plugin_manager.disable_plugin(self)
        else:
            with open(money_data_file_path, 'r', encoding='utf-8') as f:
                money_data = json.loads(f.read())
        self.money_data = money_data
        self.CommandSenderWrapper = CommandSenderWrapper(
            self.server.command_sender,
            on_message=None
        )
        self.player_with_add_good_mode_list = []
        self.register_events(self)
        self.logger.info(f'{ColorFormat.YELLOW}UShop 已启用...')

    commands = {
        'us': {
            'description': '打开商店主表单',
            'usages': ['/us'],
            'permissions': ['ushop.command.us']
        }
    }

    permissions = {
        'ushop.command.us': {
            'description': '打开商店主表单',
            'default': True
        }
    }

    def on_command(self, sender: CommandSender, command: Command, args: list[str]):
        if command.name == 'us':
            if not isinstance(sender, Player):
                sender.send_message(f'{ColorFormat.RED}该命令只能由玩家执行...')
                return
            player = sender
            self.load_money_data()
            player_money = self.money_data[player.name]
            main_form = ActionForm(
                title=f'{ColorFormat.BOLD}{ColorFormat.LIGHT_PURPLE}商店主表单',
                content=f'{ColorFormat.GREEN}余额： {ColorFormat.WHITE}{player_money}\n'
                        f'{ColorFormat.GREEN}请选择操作...'
            )
            if player.is_op == True:
                main_form.add_button(f'{ColorFormat.YELLOW}添加新分类', icon='textures/ui/color_plus', on_click=self.add_new_category)
                main_form.add_button(f'{ColorFormat.YELLOW}开启/关闭添加商品模式', icon='textures/ui/toggle_on', on_click=self.switch_to_add_good_mode)
                main_form.add_button(f'{ColorFormat.YELLOW}重载配置文件', icon='textures/ui/icon_setting', on_click=self.reload_config_data)
            for key in self.shop_data.keys():
                category_name = key
                category_icon = self.shop_data[category_name]['category_icon']
                main_form.add_button(f'{ColorFormat.YELLOW}{category_name}', icon=category_icon, on_click=self.shop_category(category_name))
            if os.path.exists(menu_data_file_path):
                main_form.add_button(f'{ColorFormat.YELLOW}返回', icon='textures/ui/refresh_light', on_click=self.back_to_menu)
                main_form.on_close = self.back_to_menu
            else:
                main_form.add_button(f'{ColorFormat.YELLOW}关闭', icon='textures/ui/cancel', on_click=None)
                main_form.on_close = None
            player.send_form(main_form)

    def add_new_category(self, player: Player):
        textinput1 = TextInput(
            label=f'{ColorFormat.GREEN}输入商品分类名称...',
            placeholder='请输入任意字符串, 但不能为空...'
        )
        textinput2 = TextInput(
            label=f'{ColorFormat.GREEN}输入商品分类图标路径...',
            placeholder='请输入材质路径或 url, 选填'
        )
        add_new_category_form = ModalForm(
            title=f'{ColorFormat.BOLD}{ColorFormat.LIGHT_PURPLE}添加新的商品分类',
            controls=[textinput1, textinput2],
            on_close=self.back_to_main_form,
            submit_button=f'{ColorFormat.YELLOW}确认'
        )
        def on_submit(player: Player, json_str):
            data = json.loads(json_str)
            if len(data[0]) == 0:
                player.send_message(f'{ColorFormat.RED}表单解析错误, 请按提示正确填写...')
                return
            already_exist_category_list = [key for key in self.shop_data.keys()]
            if data[0] in already_exist_category_list:
                player.send_message(f'{ColorFormat.RED}添加商品分类失败： '
                                    f'{ColorFormat.WHITE}重复的商品分类名...')
                return
            new_category_name = data[0]
            new_category_icon = data[1]
            self.shop_data[new_category_name] = {'category_icon': new_category_icon}
            self.save_shop_data()
            player.send_message(f'{ColorFormat.YELLOW}添加商品分类成功...')
        add_new_category_form.on_submit = on_submit
        player.send_form(add_new_category_form)

    def shop_category(self, category_name):
        def on_click(player: Player):
            self.load_money_data()
            player_money = self.money_data[player.name]
            shop_category_form = ActionForm(
                title=f'{ColorFormat.BOLD}{ColorFormat.LIGHT_PURPLE}{category_name}',
                content=f'{ColorFormat.GREEN}余额： {ColorFormat.WHITE}{player_money}\n'
                        f'{ColorFormat.GREEN}请选择操作...',
                on_close=self.back_to_main_form
            )
            if player.is_op == True:
                shop_category_form.add_button(f'{ColorFormat.YELLOW}编辑该商品分类', icon='textures/ui/hammer_l', on_click=self.edit_shop_category(category_name))
            for key, value in self.shop_data[category_name].items():
                if key == 'category_icon':
                    pass
                else:
                    good_type = key
                    good_price = self.shop_data[category_name][good_type]['good_price']
                    good_name = self.shop_data[category_name][good_type]['good_name']
                    shop_category_form.add_button(f'{ColorFormat.YELLOW}{good_name}\n'
                                                  f'{ColorFormat.GREEN}单价： {good_price}', on_click=self.good_info(category_name, good_type, good_name, good_price))
            player.send_form(shop_category_form)
        return on_click

    def edit_shop_category(self, category_name):
        def on_click(player: Player):
            edit_shop_category_form = ActionForm(
                title=f'{ColorFormat.BOLD}{ColorFormat.LIGHT_PURPLE}编辑 {category_name} 商品分类',
                content=f'{ColorFormat.GREEN}请选择操作...',
                on_close=self.back_to_main_form
            )
            edit_shop_category_form.add_button(f'{ColorFormat.YELLOW}删除该商品分类', icon='textures/ui/cancel', on_click=self.delete_shop_category(category_name))
            edit_shop_category_form.add_button(f'{ColorFormat.YELLOW}更新该商品分类', icon='textures/ui/refresh', on_click=self.update_shop_category(category_name))
            edit_shop_category_form.add_button(f'{ColorFormat.YELLOW}返回', icon='textures/ui/refresh_light', on_click=self.back_to_main_form)
            player.send_form(edit_shop_category_form)
        return on_click

    def delete_shop_category(self, category_name):
        def on_click(player: Player):
            confirm_form = ActionForm(
                title=f'{ColorFormat.BOLD}{ColorFormat.LIGHT_PURPLE}确认表单',
                content=f'{ColorFormat.GREEN}你确定要删除 {ColorFormat.WHITE}{category_name} '
                        f'{ColorFormat.GREEN}商品分类吗？\n'
                        f'该商品分类下的所有配置将被清除, 包括商品...',
                on_close=self.back_to_main_form
            )
            confirm_form.add_button(f'{ColorFormat.YELLOW}确认', icon='textures/ui/realms_slot_check', on_click=self.on_confirm(category_name))
            confirm_form.add_button(f'{ColorFormat.YELLOW}返回', icon='textures/ui/refresh_light', on_click=self.back_to_main_form)
            player.send_form(confirm_form)
        return on_click

    def on_confirm(self, category_name):
        def on_click(player: Player):
            self.shop_data.pop(category_name)
            self.save_shop_data()
            player.send_message(f'{ColorFormat.YELLOW}商品分类删除成功...')
        return on_click

    def update_shop_category(self, category_name):
        def on_click(player: Player):
            textinput1 = TextInput(
                label=f'{ColorFormat.GREEN}原商品分类名： {ColorFormat.WHITE}{category_name}\n'
                      f'{ColorFormat.GREEN}输入新的商品分类名...\n'
                      f'{ColorFormat.GREEN}（请输入任意字符串, 但不能留空...）',
                placeholder='请输入任意字符串, 但不能留空...',
                default_value=category_name
            )
            textinput2 = TextInput(
                label=f'{ColorFormat.GREEN}原商品分类图标路径： {ColorFormat.WHITE}{self.shop_data[category_name]["category_icon"]}\n'
                      f'{ColorFormat.GREEN}输入新的商品分类图标路径...\n'
                      f'（请输入材质路径或 url 或留空...）',
                placeholder='请输入材质路径或 url 或留空...',
                default_value=self.shop_data[category_name]['category_icon']
            )
            update_shop_category_form = ModalForm(
                title=f'{ColorFormat.BOLD}{ColorFormat.LIGHT_PURPLE}更新 {category_name} 商品分类',
                controls=[textinput1, textinput2],
                on_close=self.back_to_main_form,
                submit_button=f'{ColorFormat.YELLOW}更新'
            )
            def on_submit(player: Player, json_str):
                data = json.loads(json_str)
                # 判断 textinput1 是否被填写
                if len(data[0]) == 0:
                    player.send_message(f'{ColorFormat.RED}表单解析错误, 请按提示正确填写...')
                    return
                update_category_name = data[0]
                # 读取新的材质路径（无视留空, 留空将自动不显示图标）
                update_category_icon = data[1]
                # 更新分类
                self.shop_data[update_category_name] = self.shop_data[category_name]
                if update_category_name != category_name:
                    self.shop_data.pop(category_name)
                self.shop_data[update_category_name]['category_icon'] = update_category_icon
                self.save_shop_data()
                player.send_message(f'{ColorFormat.YELLOW}商品分类更新成功...')
            update_shop_category_form.on_submit = on_submit
            player.send_form(update_shop_category_form)
        return on_click

    def good_info(self, category_name, good_type, good_name, good_price):
        def on_click(player: Player):
            self.load_money_data()
            player_money = self.money_data[player.name]
            reclaim_rate = self.config_data['reclaim_rate']
            pre_good_reclaim_price = int(reclaim_rate * good_price)
            if pre_good_reclaim_price == 0:
                good_reclaim_price = good_price
            else:
                good_reclaim_price = pre_good_reclaim_price
            good_info_form = ActionForm(
                title=f'{ColorFormat.BOLD}{ColorFormat.LIGHT_PURPLE}{good_name} 商品页面',
                content=f'{ColorFormat.GREEN}余额： {ColorFormat.WHITE}{player_money}\n'
                        f'{ColorFormat.GREEN}商品单价： {ColorFormat.WHITE}{good_price}\n'
                        f'{ColorFormat.GREEN}商品回收单价： {ColorFormat.WHITE}{good_reclaim_price}',
                on_close=self.back_to_main_form
            )
            if player.is_op == True:
                good_info_form.add_button(f'{ColorFormat.YELLOW}编辑该商品', icon='textures/ui/hammer_l', on_click=self.good_edit(category_name, good_type, good_name, good_price))
            good_info_form.add_button(f'{ColorFormat.YELLOW}购买', icon='textures/ui/village_hero_effect', on_click=self.good_buy(good_type, good_name, good_price))
            good_info_form.add_button(f'{ColorFormat.YELLOW}回收', icon='textures/ui/trade_icon', on_click=self.good_reclaim(good_type, good_name, good_reclaim_price))
            good_info_form.add_button(f'{ColorFormat.YELLOW}返回', icon='textures/ui/refresh_light', on_click=self.back_to_main_form)
            player.send_form(good_info_form)
        return on_click

    def good_buy(self, good_type, good_name, good_price):
        def on_click(player: Player):
            self.load_money_data()
            player_money = self.money_data[player.name]
            textinput = TextInput(
                label=f'{ColorFormat.GREEN}余额： {ColorFormat.WHITE}{player_money}\n'
                      f'{ColorFormat.GREEN}输入购买数量...',
                placeholder='请输入一个正整数, 例如： 20'
            )
            good_buy_form = ModalForm(
                title=f'{ColorFormat.BOLD}{ColorFormat.LIGHT_PURPLE}{good_name} 购买页面',
                controls=[textinput],
                submit_button=f'{ColorFormat.YELLOW}购买',
                on_close=self.back_to_main_form
            )
            def on_submit(player: Player, json_str):
                data = json.loads(json_str)
                try:
                    good_to_buy_amount = int(data[0])
                except:
                    player.send_message(f'{ColorFormat.RED}表单解析错误, 请按提示正确填写...')
                    return
                if good_to_buy_amount < 0:
                    player.send_message(f'{ColorFormat.RED}表单解析错误, 请按提示正确填写...')
                    return
                good_to_buy_total_price = good_to_buy_amount * good_price
                if player_money < good_to_buy_total_price:
                    player.send_message(f'{ColorFormat.RED}购买商品失败： {ColorFormat.WHITE}余额不足...')
                    return
                self.money_data[player.name] -= good_to_buy_total_price
                self.save_money_data()
                if player.name.find(' ') != -1:
                    player_name = f'"{player.name}"'
                else:
                    player_name = player.name
                self.server.dispatch_command(self.CommandSenderWrapper,
                                             f'give {player_name} {good_type} {good_to_buy_amount}')
                # 向玩家播放村民肯定的声音
                self.server.dispatch_command(self.CommandSenderWrapper,
                                             f'playsound mob.villager.yes {player_name}')
                # 更加完整的信息提示
                player.send_message(f'{ColorFormat.YELLOW}购买商品成功： {ColorFormat.RED}-{good_to_buy_total_price}, '
                                    f'{ColorFormat.YELLOW}余额： {ColorFormat.WHITE}{self.money_data[player.name]}')
            good_buy_form.on_submit = on_submit
            player.send_form(good_buy_form)
        return on_click

    def good_reclaim(self, good_type, good_name, good_reclaim_price):
        def on_click(player: Player):
            self.load_money_data()
            player_money = self.money_data[player.name]
            player_inventory = []
            for content in player.inventory.contents:
                if type(content) == type(None):
                    player_inventory.append('Null')
                else:
                    player_inventory.append(content.type)
            if good_type not in player_inventory:
                player.send_message(f'{ColorFormat.RED}回收商品失败： {ColorFormat.WHITE}你的背包里没有目标回收商品...')
                return
            else:
                player_has_this_good_amount = 0
                good_index = 0
                for player_good_type in player_inventory:
                    if player_good_type == good_type:
                        player_has_this_good_amount += player.inventory.get_item(good_index).amount
                        good_index += 1
                    else:
                        good_index += 1
            textinput = TextInput(
                label=f'{ColorFormat.GREEN}余额： {ColorFormat.WHITE}{player_money}\n'
                      f'{ColorFormat.GREEN}你的背包里有 {ColorFormat.WHITE}{player_has_this_good_amount} '
                      f'{ColorFormat.GREEN}个{good_name}\n'
                      f'输入回收数量...',
                placeholder=f'请输入一个正整数, 但不要超过 {player_has_this_good_amount}'
            )
            good_reclaim_form = ModalForm(
                title=f'{ColorFormat.BOLD}{ColorFormat.LIGHT_PURPLE}{good_name} 回收页面',
                controls=[textinput],
                submit_button=f'{ColorFormat.YELLOW}回收',
                on_close=self.back_to_main_form
            )
            def on_submit(player: Player, json_str):
                data = json.loads(json_str)
                try:
                    good_to_reclaim_amount = int(data[0])
                except:
                    player.send_message(f'{ColorFormat.RED}表单解析错误, 请按提示正确填写...')
                    return
                if good_to_reclaim_amount < 0 or good_to_reclaim_amount > player_has_this_good_amount:
                    player.send_message(f'{ColorFormat.RED}表单解析错误, 请按提示正确填写...')
                    return
                good_to_reclaim_total_price = good_to_reclaim_amount * good_reclaim_price
                self.money_data[player.name] += good_to_reclaim_total_price
                self.save_money_data()
                if player.name.find(' ') != -1:
                    player_name = f'"{player.name}"'
                else:
                    player_name = player.name
                self.server.dispatch_command(self.CommandSenderWrapper,
                                             f'clear {player_name} {good_type} 0 {good_to_reclaim_amount}')
                # 向玩家播放村民肯定的声音
                self.server.dispatch_command(self.CommandSenderWrapper,
                                             f'playsound mob.villager.yes {player_name}')
                # 更加完整的信息提示
                player.send_message(f'{ColorFormat.YELLOW}回收商品成功： {ColorFormat.GREEN}+{good_to_reclaim_total_price}, '
                                    f'{ColorFormat.YELLOW}余额： {ColorFormat.WHITE}{self.money_data[player.name]}')
            good_reclaim_form.on_submit = on_submit
            player.send_form(good_reclaim_form)
        return on_click

    def good_edit(self, category_name, good_type, good_name, good_price):
        def on_click(player: Player):
            good_edit_form = ActionForm(
                title=f'{ColorFormat.BOLD}{ColorFormat.LIGHT_PURPLE}编辑商品 {good_name}',
                content=f'{ColorFormat.GREEN}请选择操作...',
                on_close=self.back_to_main_form
            )
            good_edit_form.add_button(f'{ColorFormat.YELLOW}更新该商品', icon='textures/ui/refresh', on_click=self.good_update(category_name, good_type, good_name, good_price))
            good_edit_form.add_button(f'{ColorFormat.YELLOW}删除该商品', icon='textures/ui/cancel', on_click=self.good_delete(category_name, good_type, good_name))
            good_edit_form.add_button(f'{ColorFormat.YELLOW}返回', icon='textures/ui/refresh_light', on_click=self.back_to_main_form)
            player.send_form(good_edit_form)
        return on_click

    def good_update(self, category_name, good_type, good_name, good_price):
        def on_click(player: Player):
            textinput1 = TextInput(
                label=f'{ColorFormat.GREEN}原商品名： {ColorFormat.WHITE}{good_name}\n'
                      f'{ColorFormat.GREEN}输入新的商品名...\n'
                      f'{ColorFormat.GREEN}（请输入任意字符串, 但不能留空...）',
                placeholder='请输入任意字符串, 但不能留空...',
                default_value=good_name
            )
            textinput2 = TextInput(
                label=f'{ColorFormat.GREEN}原商品价单价： {ColorFormat.WHITE}{good_price}\n'
                      f'{ColorFormat.GREEN}输入新的商品单价...\n'
                      f'{ColorFormat.GREEN}（请输入一个正整数, 例如： 5...）',
                placeholder='请输入一个正整数, 例如： 5...',
                default_value=f'{good_price}'
            )
            good_update_form = ModalForm(
                title=f'{ColorFormat.BOLD}{ColorFormat.LIGHT_PURPLE}更新商品 {good_name}',
                controls=[textinput1, textinput2],
                on_close=self.back_to_main_form,
                submit_button=f'{ColorFormat.YELLOW}更新'
            )
            def on_submit(player: Player, json_str):
                data = json.loads(json_str)
                # 判断 textinput1 是否被填写
                if len(data[0]) == 0:
                    player.send_message(f'{ColorFormat.RED}表单解析错误, 请按提示正确填写...')
                    return
                update_good_name = data[0]
                # 判断 textinput2 是否填写了正确的数字类型
                try:
                    update_good_price = int(data[1])
                except:
                    player.send_message(f'{ColorFormat.RED}表单解析错误, 请按提示正确填写...')
                    return
                if update_good_price <= 0:
                    player.send_message(f'{ColorFormat.RED}表单解析错误, 请按提示正确填写...')
                    return
                # 更新
                self.shop_data[category_name][good_type]['good_name'] = update_good_name
                self.shop_data[category_name][good_type]['good_price'] = update_good_price
                self.save_shop_data()
                player.send_message(f'{ColorFormat.YELLOW}更新商品成功...')
            good_update_form.on_submit = on_submit
            player.send_form(good_update_form)
        return on_click

    def good_delete(self, category_name, good_type, good_name):
        def on_click(player: Player):
            confirm_form = ActionForm(
                title=f'{ColorFormat.BOLD}{ColorFormat.LIGHT_PURPLE}确认表单',
                content=f'{ColorFormat.GREEN}你确定要删除商品 {ColorFormat.WHITE}{good_name} {ColorFormat.GREEN}吗？',
                on_close=self.back_to_main_form
            )
            confirm_form.add_button(f'{ColorFormat.YELLOW}确认', icon='textures/ui/realms_slot_check', on_click=self.on_another_confirm(category_name, good_type))
            confirm_form.add_button(f'{ColorFormat.YELLOW}返回', icon='textures/ui/refresh_light', on_click=self.back_to_main_form)
            player.send_form(confirm_form)
        return on_click

    def on_another_confirm(self, category_name, good_type):
        def on_click(player: Player):
            self.shop_data[category_name].pop(good_type)
            self.save_shop_data()
            player.send_message(f'{ColorFormat.YELLOW}删除商品成功...')
        return on_click

    def switch_to_add_good_mode(self, player: Player):
        already_exist_category_list = [key for key in self.shop_data.keys()]
        if len(already_exist_category_list) == 0 and player.name not in self.player_with_add_good_mode_list:
            player.send_message(f'{ColorFormat.RED}开启添加商品模式失败： {ColorFormat.WHITE}你还没有创建任何商品分类...')
            return
        if player.name not in self.player_with_add_good_mode_list:
            self.player_with_add_good_mode_list.append(player.name)
            player.send_message(f'{ColorFormat.YELLOW}已为你开启添加商品模式...')
        else:
            self.player_with_add_good_mode_list.remove(player.name)
            player.send_message(f'{ColorFormat.YELLOW}已为你关闭添加商品模式...')

    @event_handler
    def on_player_interact(self, event: PlayerInteractEvent):
        if event.player.name in self.player_with_add_good_mode_list:
            try:
                good_to_add = event.item.type
            except:
                return
            already_exist_category_list = [key for key in self.shop_data.keys()]
            dropdown = Dropdown(
                label=f'{ColorFormat.GREEN}选择一个商品分类...',
                options=already_exist_category_list
            )
            textinput1 = TextInput(
                label=f'{ColorFormat.GREEN}输入商品名称...',
                placeholder='请输入任意字符串, 但不能留空...'
            )
            textinput2 = TextInput(
                label=f'{ColorFormat.GREEN}输入商品单价...',
                placeholder='请输入一个正整数, 例如：5'
            )
            add_good_form = ModalForm(
                title=f'{ColorFormat.BOLD}{ColorFormat.LIGHT_PURPLE}上架商品： {good_to_add}',
                controls=[dropdown, textinput1, textinput2],
                submit_button=f'{ColorFormat.YELLOW}上架',
                on_close=self.back_to_main_form
            )
            def on_submit(player: event.player, json_str):
                data = json.loads(json_str)
                category_name = already_exist_category_list[data[0]]
                good_belong_to_this_category_list = [key for key in self.shop_data[category_name].keys() if key != 'category_icon']
                if good_to_add in good_belong_to_this_category_list:
                    player.send_message(f'{ColorFormat.RED}上架商品失败： {ColorFormat.WHITE}重复的商品...')
                    return
                if len(data[1]) == 0:
                    player.send_message(f'{ColorFormat.RED}表单解析错误, 请按提示正确填写...')
                    return
                else:
                    good_name = data[1]
                try:
                    good_price = int(data[2])
                except:
                    player.send_message(f'{ColorFormat.RED}表单解析错误, 请按提示正确填写...')
                    return
                if good_price <= 0 :
                    player.send_message(f'{ColorFormat.RED}表单解析错误, 请按提示正确填写...')
                    return
                self.shop_data[category_name][good_to_add] = {
                    'good_name': good_name,
                    'good_price': good_price
                }
                self.save_shop_data()
                player.send_message(f'{ColorFormat.YELLOW}上架商品成功...')
            add_good_form.on_submit = on_submit
            event.player.send_form(add_good_form)
            event.cancelled = True
        else:
            if event.player.is_op == False:
                if ((event.block.type == 'minecraft:mob_spawner' or event.block.type == 'minecraft:trial_spawner')
                        and 'spawn_egg' in event.item.type):
                    event.cancelled = True

    def reload_config_data(self, player: Player):
        reload_config_data_form = ActionForm(
            title=f'{ColorFormat.BOLD}{ColorFormat.LIGHT_PURPLE}重载配置文件',
            content=f'{ColorFormat.GREEN}清选择操作...',
            on_close=self.back_to_main_form
        )
        reload_config_data_form.add_button(f'{ColorFormat.YELLOW}重载商品回收价率', icon='textures/ui/refresh_light', on_click=self.reload_reclaim_rate)
        reload_config_data_form.add_button(f'{ColorFormat.YELLOW}重载商店配置文件', icon='textures/ui/refresh_light', on_click=self.reload_shop_data)
        reload_config_data_form.add_button(f'{ColorFormat.YELLOW}返回', icon='textures/ui/refresh_light', on_click=self.back_to_main_form)
        player.send_form(reload_config_data_form)

    def reload_reclaim_rate(self, player: Player):
        current_reclaim_rate = self.config_data['reclaim_rate']
        textinput = TextInput(
            label=f'{ColorFormat.GREEN}当前商品回收价率： {ColorFormat.WHITE}{current_reclaim_rate}\n'
                  f'{ColorFormat.GREEN}输入新的商品回收价率...\n'
                  f'{ColorFormat.GREEN}（请输入一个不大于1的正小数...）',
            placeholder='请输入一个不大于1的正小数...',
            default_value=f'{current_reclaim_rate}'
        )
        reload_reclaim_rate_form = ModalForm(
            title=f'{ColorFormat.BOLD}{ColorFormat.LIGHT_PURPLE}重载配置文件',
            controls=[textinput],
            submit_button=f'{ColorFormat.YELLOW}重载',
            on_close=self.back_to_main_form
        )
        def on_submit(player: Player, json_str):
            data = json.loads(json_str)
            # 判断 textinput 是否填写了正确的小数类型
            try:
                update_reclaim_rate = float(data[0])
            except:
                player.send_message(f'{ColorFormat.RED}表单解析错误, 请按提示正确填写...')
                return
            if update_reclaim_rate > 1 or update_reclaim_rate <= 0:
                player.send_message(f'{ColorFormat.RED}表单解析错误, 请按提示正确填写...')
                return
            self.config_data['reclaim_rate'] = update_reclaim_rate
            self.save_config_data()
            player.send_message(f'{ColorFormat.YELLOW}重载商店回收价率成功...')
        reload_reclaim_rate_form.on_submit = on_submit
        player.send_form(reload_reclaim_rate_form)

    def reload_shop_data(self, player: Player):
        with open(shop_data_file_path, 'r', encoding='utf-8') as f:
            self.shop_data = json.loads(f.read())
        player.send_message(f'{ColorFormat.YELLOW}重载商店配置文件成功...')

    def save_shop_data(self):
        with open(shop_data_file_path, 'w+', encoding='utf-8') as f:
            json_str = json.dumps(self.shop_data, indent=4, ensure_ascii=False)
            f.write(json_str)

    def save_config_data(self):
        with open(config_data_file_path, 'w+', encoding='utf-8') as f:
            json_str = json.dumps(self.config_data, indent=4, ensure_ascii=False)
            f.write(json_str)

    def save_money_data(self):
        with open(money_data_file_path, 'w+', encoding='utf-8') as f:
            json_str = json.dumps(self.money_data, indent=4, ensure_ascii=False)
            f.write(json_str)

    def load_money_data(self):
        with open(money_data_file_path, 'r', encoding='utf-8') as f:
            self.money_data = json.loads(f.read())

    def back_to_main_form(self, player: Player):
        player.perform_command('us')

    def back_to_menu(self, player: Player):
        player.perform_command('cd')
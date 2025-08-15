import os
import json


def load_lang_data(lang_dir: str) -> dict:
    zh_CN_file_path = os.path.join(lang_dir, 'zh_CN.json')
    en_US_file_path = os.path.join(lang_dir, 'en_US.json')

    if not os.path.exists(zh_CN_file_path):
        with open(zh_CN_file_path, 'w', encoding='utf-8') as f:
            zh_CN = {
                'official_shop': '官方商店',

                'your_money': '你的余额',
                'tags': '标签',
                'has_enchants': '拥有附魔',
                'has_lore': '拥有特殊标签',

                'category_name': '商店分类',

                'good_name': '商品名称',
                'good_type': '商品类型',
                'good_enchants': '商品附魔',
                'good_lore': '商品特殊标签',
                'good_purchase_price': '购买价格',
                'good_reclaim_price': '回收价格',
                'good_mode': '商品模式',
                'only purchase': '仅购买',
                'only reclaim': '仅回收',
                'purchase and reclaim': '购买和回收',

                'button.back': '返回',
                'message.type_error': '表单解析错误, 请按提示正确填写..',

                'main_form.title': 'UShop - 主表单',
                'main_form.content': '请选择操作...',
                'main_form.button.official_shop': '官方商店',
                'main_form.button.player_shop': '玩家商店',
                'main_form.reload_config': '重载配置文件',
                'main_form.button.close': '关闭',
                'main_form.button.back_to_zx_ui': '返回',

                'official_shop_main_form.title': '官方商店',
                'official_shop_main_form.content': '请选择操作...',
                'official_shop_main_form.add_shop_category': '添加新商店分类',
                'official_shop_main_form.add_good': '添加新商品',
                'official_shop_main_form.add_lore': '为物品添加特殊标签',
                'official_shop_main_form.good_collections': '商品收藏',
                'official_shop_main_form.search_good': '搜索商品',

                'official_shop_add_shop_category_form.title': '添加新商店分类',
                'official_shop_add_shop_category_form.textinput.label': '输入新商店分类的名称...',
                'official_shop_add_shop_category_form.textinput.placeholder': '输入任意字符串但不能留空...',
                'official_shop_add_shop_category_form.submit_button': '添加',
                'official_shop_add_shop_category.message.fail': '添加新商店分类失败...',
                'official_shop_add_shop_category.message.fail.reason': '已经有一个名为 {0} 的商店分类了...',
                'official_shop_add_shop_category.message.success': '添加新商店分类成功...',

                'official_shop_single_shop_category_form.content': '请选择操作...',
                'official_shop_single_shop_category_form.button.edit_shop_category': '编辑该商店分类',

                'official_shop_edit_single_shop_category_form.title': '编辑商店分类',
                'official_shop_edit_single_shop_category_form.content': '请选择操作...',
                'official_shop_edit_single_shop_category_form.button.delete_shop_category': '删除该商店分类',
                'official_shop_edit_single_shop_category_form.button.update_shop_category': '更新该商店分类',

                'official_shop_delete_single_shop_category_form.title': '删除商店分类',
                'official_shop_delete_single_shop_category_form.content': '你确认删除该商店分类吗?',
                'official_shop_delete_single_shop_category_form.button.confirm': '确认',
                'official_shop_delete_single_shop_category.message.success': '删除商店分类成功...',

                'official_shop_update_single_shop_category_form.title': '更新商店分类',
                'official_shop_update_single_shop_category_form.textinput.label': '输入该商店分类的新名称...',
                'official_shop_update_single_shop_category_form.textinput.placeholder': '输入任意字符串但不能留空...',
                'official_shop_update_single_shop_category_form.submit_button': '更新',
                'official_shop_update_single_shop_category.message.fail': '更新商店分类失败...',
                'official_shop_update_single_shop_category.message.fail.reason': '已经有一个名为 {0} 的商店分类了...',
                'official_shop_update_single_shop_category.message.success': '更新商店分类成功...',

                'official_shop_add_good.message.fail': '添加新商品失败...',
                'official_shop_add_good.message.fail.reason': '还没有任何商店分类被创建...',
                'official_shop_add_good_form.title': '添加新商品',
                'official_shop_add_good_form.content': '请选择一个物品添加...',

                'official_shop_add_good_further_form.title': '添加新商品',
                'official_shop_add_good_further_form.dropdown1.label': '选择商店分类...',
                'official_shop_add_good_further_form.dropdown2.label': '选择商品模式...',
                'official_shop_add_good_further_form.textinput1.label': '输入新商品的购买价格...',
                'official_shop_add_good_further_form.textinput2.label': '输入新商品的回收价格...',
                'official_shop_add_good_further_form.textinput.placeholder': '输入一个正整数...',
                'official_shop_add_good_further_form.submit_button': '添加',
                'official_shop_add_good_further.message.success': '添加新商品成功...',

                'official_shop_single_good_form.title': '商品',
                'official_shop_single_good_form.content': '已被 {0} 位玩家收藏...',
                'official_shop_single_good_form.button.edit_good': '编辑该商品',
                'official_shop_single_good_form.button.purchase': '购买',
                'official_shop_single_good_form.button.reclaim': '回收',
                'official_shop_single_good_form.button.collect_good': '收藏',
                'official_shop_single_good_form.button.de_collect_good': '取消收藏',

                'official_shop_edit_single_good_form.title': '编辑商品',
                'official_shop_edit_single_good_form.content': '请选择操作...',
                'official_shop_edit_single_good_form.button.delete_good': '删除该商品',
                'official_shop_edit_single_good_form.button.update_good': '更新该商品',

                'official_shop_delete_single_good_form.title': '删除商品',
                'official_shop_delete_single_good_form.content': '你确认删除该商品吗?',
                'official_shop_delete_single_good_form.button.confirm': '确认',
                'official_shop_delete_single_good.message.success': '删除商品成功...',

                'official_shop_update_single_good_form.title': '更新商品',
                'official_shop_update_single_good_form.dropdown1.label': '选择商店分类...',
                'official_shop_update_single_good_form.dropdown2.label': '选择商品模式...',
                'official_shop_update_single_good_form.textinput1.label': '输入该商品的新购买价格...',
                'official_shop_update_single_good_form.textinput1.placeholder': '输入一个正整数...',
                'official_shop_update_single_good_form.textinput2.label': '输入该商品的新回收价格...',
                'official_shop_update_single_good_form.textinput2.placeholder': '输入一个正整数...',
                'official_shop_update_single_good_form.submit_button': '更新',
                'official_shop_update_single_good.message.success': '更新商品成功...',

                'official_shop_purchase_single_good_form.title': '购买商品',
                'official_shop_purchase_single_good_form.textinput.label': '输入购买数量...',
                'official_shop_purchase_single_good_form.textinput.placeholder': '输入一个 <= {0} 的正整数...',
                'official_shop_purchase_single_good_form.submit_button': '购买',
                'official_shop_purchase_single_good.message.fail': '购买失败',
                'official_shop_purchase_single_good.message.fail.reason1': '你的物品栏里没有多余空间...',
                'official_shop_purchase_single_good.message.fail.reason2': '你的余额不足...',
                'official_shop_purchase_single_good.message.success': '购买成功...',
                'official_shop_purchase_single_good.message': '由于你的物品栏发生了突然的变化, {0} 个物品获取失败, 相关耗费已返还...',

                'official_shop_reclaim_single_good_form.title': '回收商品',
                'official_shop_reclaim_single_good_form.textinput.label': '输入回收数量...',
                'official_shop_reclaim_single_good_form.textinput.placeholder': '输入一个 <= {0} 的正整数...',
                'official_shop_reclaim_single_good_form.submit_button': '回收',
                'official_shop_reclaim_single_good.message.fail': '回收失败',
                'official_shop_reclaim_single_good.message.fail.reason': '你的物品栏里没有目标物品...',
                'official_shop_reclaim_single_good.message.success': '回收成功',

                'official_shop_collect_single_good.message.success': '收藏成功...',

                'official_shop_de_collect_single_good.message.success': '取消收藏成功...',

                'official_shop_good_collections_form.title': '商品收藏',
                'official_shop_good_collections_form.content': '你已经收藏了 {0} 个商品...',

                'official_shop_search_good_form.title': '搜索商品',
                'official_shop_search_good_form.textinput.label': '输入关键词...',
                'official_shop_search_good_form.textinput.placeholder': '输入任意字符串但不能留空...',
                'official_shop_search_good_form.submit_button': '搜索',

                'result_form.title': '结果',
                'result_form.content': '匹配到 {0} 个结果...',

                'official_shop_reload_config_form.title': '重载配置文件',
                'official_shop_reload_config_form.textinput.label': '当前回商品时, 物品堆叠的耐久度阈值 (如果该物品堆叠有耐久度)',
                'official_shop_reload_config_form.textinput.placeholder': '输入一个 <= 1.0 的正小数或0...',
                'official_shop_reload_config_form.submit_button': '重载',
                'official_shop_reload_config.message.success': '重载配置文件成功...',

                'player_shop_form.title': '玩家商店',
                'player_shop_form.content': '即将完成...',
            }
            json_str = json.dumps(zh_CN, indent=4, ensure_ascii=False)
            f.write(json_str)

    if not os.path.exists(en_US_file_path):
        with open(en_US_file_path, 'w', encoding='utf-8') as f:
            en_US = {
                'official_shop': 'Official shop',

                'your_money': 'Your money',
                'tags': 'Tags',
                'has_enchants': 'Has enchant(s)',
                'has_lore': 'Has lore',

                'category_name': 'Category name',

                'good_name': 'Good name',
                'good_type': 'Good type',
                'good_enchants': 'Good enchant(s)',
                'good_lore': 'Good lore',
                'good_purchase_price': 'Purchase price',
                'good_reclaim_price': 'Reclaim price',
                'good_mode': 'Good mode',
                'only purchase': 'only purchase',
                'only reclaim': 'only reclaim',
                'purchase and reclaim': 'purchase and reclaim',

                'button.back': 'Back to previous',
                'message.type_error': 'The form is parsed incorrectly, please follow the prompts to fill in correctly...',

                'main_form.title': 'UShop - main form',
                'main_form.content': 'Please select a function...',
                'main_form.button.official_shop': 'Official shop',
                'main_form.button.player_shop': 'Player shop',
                'main_form.reload_config': 'Reload configurations',
                'main_form.button.close': 'Close',
                'main_form.button.back_to_zx_ui': 'Back to menu',

                'official_shop_main_form.title': 'Official shop',
                'official_shop_main_form.content': 'Please select a function...',
                'official_shop_main_form.add_shop_category': 'Add a new shop category',
                'official_shop_main_form.add_good': 'Add a new good',
                'official_shop_main_form.add_lore': 'Add lore for item(s)',
                'official_shop_main_form.good_collections': 'Good collections',
                'official_shop_main_form.search_good': 'Search good',


                'official_shop_add_shop_category_form.title': 'Add a new shop category',
                'official_shop_add_shop_category_form.textinput.label': 'Input the name of new shop category...',
                'official_shop_add_shop_category_form.textinput.placeholder': 'Input any string, but cannot be blank...',
                'official_shop_add_shop_category_form.submit_button': 'Add',
                'official_shop_add_shop_category.message.fail': 'Failed to add a new shop category',
                'official_shop_add_shop_category.message.fail.reason': 'there is already a shop category named {0}...',
                'official_shop_add_shop_category.message.success': 'Successfully add a new shop category...',

                'official_shop_single_shop_category_form.content': 'Please select a function...',
                'official_shop_single_shop_category_form.button.edit_shop_category': 'Edit this shop category',

                'official_shop_edit_single_shop_category_form.title': 'Edit shop category',
                'official_shop_edit_single_shop_category_form.content': 'Please select a function...',
                'official_shop_edit_single_shop_category_form.button.delete_shop_category': 'Delete this shop category',
                'official_shop_edit_single_shop_category_form.button.update_shop_category': 'Update this shop category',

                'official_shop_delete_single_shop_category_form.title': 'Delete shop category',
                'official_shop_delete_single_shop_category_form.content': 'Are you sure to delete this category?',
                'official_shop_delete_single_shop_category_form.button.confirm': 'Confirm',
                'official_shop_delete_single_shop_category.message.success': 'Successfully delete shop category...',

                'official_shop_update_single_shop_category_form.title': 'Update shop category',
                'official_shop_update_single_shop_category_form.textinput.label': 'Input new name of this shop category...',
                'official_shop_update_single_shop_category_form.textinput.placeholder': 'Input any string, but cannot be blank...',
                'official_shop_update_single_shop_category_form.submit_button': 'Update',
                'official_shop_update_single_shop_category.message.fail': 'Failed to update shop category',
                'official_shop_update_single_shop_category.message.fail.reason': 'there is already a shop category named {0}...',
                'official_shop_update_single_shop_category.message.success': 'Successfully update shop category...',

                'official_shop_add_good.message.fail': 'Failed to add a new good',
                'official_shop_add_good.message.fail.reason': 'no category has been added yet...',
                'official_shop_add_good_form.title': 'Add a new good',
                'official_shop_add_good_form.content': 'Please select a item to add...',

                'official_shop_add_good_further_form.title': 'Add a new good',
                'official_shop_add_good_further_form.dropdown1.label': 'Select a shop category...',
                'official_shop_add_good_further_form.dropdown2.label': 'Select a good mode...',
                'official_shop_add_good_further_form.textinput1.label': 'Input the purchase price of new good...',
                'official_shop_add_good_further_form.textinput2.label': 'Input the reclaim price of new good...',
                'official_shop_add_good_further_form.textinput.placeholder': 'Input a positive integer...',
                'official_shop_add_good_further_form.submit_button': 'Add',
                'official_shop_add_good_further.message.success': 'Successfully add a new good...',

                'official_shop_single_good_form.title': 'Good',
                'official_shop_single_good_form.content': 'Collected by {0} player(s)',
                'official_shop_single_good_form.button.edit_good': 'Edit this good',
                'official_shop_single_good_form.button.purchase': 'Purchase',
                'official_shop_single_good_form.button.reclaim': 'Reclaim',
                'official_shop_single_good_form.button.collect_good': 'Collect',
                'official_shop_single_good_form.button.de_collect_good': 'De-collect',

                'official_shop_edit_single_good_form.title': 'Edit good',
                'official_shop_edit_single_good_form.content': 'Please select a function...',
                'official_shop_edit_single_good_form.button.delete_good': 'Delete this good',
                'official_shop_edit_single_good_form.button.update_good': 'Update this good',

                'official_shop_delete_single_good_form.title': 'Delete good',
                'official_shop_delete_single_good_form.content': 'Are you sure to delete this good?',
                'official_shop_delete_single_good_form.button.confirm': 'Confirm',
                'official_shop_delete_single_good.message.success': 'Successfully delete good...',

                'official_shop_update_single_good_form.title': 'Update good',
                'official_shop_update_single_good_form.dropdown1.label': 'Select a shop category...',
                'official_shop_update_single_good_form.dropdown2.label': 'Select a good mode...',
                'official_shop_update_single_good_form.textinput1.label': 'Input new purchase price of this good...',
                'official_shop_update_single_good_form.textinput1.placeholder': 'Input a positive integer...',
                'official_shop_update_single_good_form.textinput2.label': 'Input new reclaim price of this good...',
                'official_shop_update_single_good_form.textinput2.placeholder': 'Input a positive integer...',
                'official_shop_update_single_good_form.submit_button': 'Update',
                'official_shop_update_single_good.message.success': 'Successfully update good...',

                'official_shop_purchase_single_good_form.title': 'Purchase good',
                'official_shop_purchase_single_good_form.textinput.label': 'Input the amount of goods to purchase...',
                'official_shop_purchase_single_good_form.textinput.placeholder': 'Input a positive integer <= {0}...',
                'official_shop_purchase_single_good_form.submit_button': 'Purchase',
                'official_shop_purchase_single_good.message.fail': 'Failed to purchase',
                'official_shop_purchase_single_good.message.fail.reason1': 'no free space in your inventory...',
                'official_shop_purchase_single_good.message.fail.reason2': 'your money is not enough...',
                'official_shop_purchase_single_good.message.success': 'Successfully purchase...',
                'official_shop_purchase_single_good.message': 'Due to a sudden change of your inventory, {0} item(s) failed to be given, relevant money will be refunded...',

                'official_shop_reclaim_single_good_form.title': 'Reclaim good',
                'official_shop_reclaim_single_good_form.textinput.label': 'Input the amount of goods to reclaim...',
                'official_shop_reclaim_single_good_form.textinput.placeholder': 'Input a positive integer <= {0}...',
                'official_shop_reclaim_single_good_form.submit_button': 'Reclaim',
                'official_shop_reclaim_single_good.message.fail': 'Failed to reclaim',
                'official_shop_reclaim_single_good.message.fail.reason': 'no target item(s) in your inventory...',
                'official_shop_reclaim_single_good.message.success': 'Successfully reclaim',

                'official_shop_collect_single_good.message.success': 'Successfully collect...',

                'official_shop_de_collect_single_good.message.success': 'Successfully de-collect...',

                'official_shop_good_collections_form.title': 'Good collections',
                'official_shop_good_collections_form.content': 'You have collected {0} good(s)...',

                'official_shop_search_good_form.title': 'Search good',
                'official_shop_search_good_form.textinput.label': 'Input the keyword...',
                'official_shop_search_good_form.textinput.placeholder': 'Input any string but cannot be blank...',
                'official_shop_search_good_form.submit_button': 'Search',

                'result_form.title': 'Result',
                'result_form.content': '{0} results matched...',

                'official_shop_reload_config_form.title': 'Reload configurations',
                'official_shop_reload_config_form.textinput.label': 'The current durability threshold of an item stack (if this item stack has durability) when reclaiming goods',
                'official_shop_reload_config_form.textinput.placeholder': 'Input a positive decimal <= 1.0 or zero...',
                'official_shop_reload_config_form.submit_button': 'Reload',
                'official_shop_reload_config.message.success': 'Successfully reload configurations...',

                'player_shop_form.title': 'Player shop',
                'player_shop_form.content': 'Coming soon...',
            }

            json_str = json.dumps(en_US, indent=4, ensure_ascii=False)
            f.write(json_str)

    lang_data = {}

    for lang in os.listdir(lang_dir):
        lang_name = lang.strip('.json')

        lang_file_path = os.path.join(lang_dir, lang)

        with open(lang_file_path, 'r', encoding='utf-8') as f:
            lang_data[lang_name] = json.loads(f.read())

    return lang_data

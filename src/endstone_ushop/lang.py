import os
import json

class lang():
    def load_lang(self, lang_dir: str) -> dict:
        zh_CN_data_file_path = os.path.join(lang_dir, 'zh_CN.json')
        en_US_data_file_path = os.path.join(lang_dir, 'en_US.json')

        if not os.path.exists(zh_CN_data_file_path):
            with open(zh_CN_data_file_path, 'w', encoding='utf-8') as f:
                zh_CN = {
                    'your_money': '你的余额',
                    'purchase_price': '购买价格',
                    'reclaim_price': '回收价格',
                    'category_name': '商店分类名',
                    'good_type': '商品类型',
                    'good_name': '商品名',
                    'good_mode': '商品模式',

                    'button.back': '返回上一级',
                    'message.type_error': '表单解析错误, 请按提示正确填写...',

                    'main_form.title': 'UShop - 主表单',
                    'main_form.content': '请选择操作...',
                    'main_form.button.add_shop_category': '添加商店分类',
                    'main_form.button.toggle_add_good_mode': '开启/关闭添加商品模式',
                    'main_form.button.reload_config': '重载配置文件',
                    'main_form.button.search_good': '商品搜索',
                    'main_form.button.collect_good': '商品收藏',
                    'main_form.button.close': '关闭',
                    'main_form.button.back_to_zx_ui': '返回',

                    'add_shop_category_form.title': '添加商店分类',
                    'add_shop_category_form.textinput1.label': '输入商店分类名',
                    'add_shop_category_form.textinput1.placeholder': '请输入任意字符串, 但不能留空...',
                    'add_shop_category_form.textinput2.label': '输入商店分类图标路径或留空',
                    'add_shop_category_form.textinput2.placeholder': '请输入任意字符串或留空...',
                    'add_shop_category_form.submit_button': '添加',
                    'add_shop_category.message.fail': '添加商店分类失败',
                    'add_shop_category.message.fail.reason': '已经有一个名为 {0} 的商店分类了...',
                    'add_shop_category.message.success': '添加商店分类成功...',

                    'shop_category_form.content': '请选择操作...',
                    'shop_category_form.button.edit_shop_category': '编辑商店分类',

                    'edit_shop_category_form.title': '编辑商店分类',
                    'edit_shop_category_form.content': '请选择操作...',
                    'edit_shop_category_form.button.delete_shop_category': '删除商店分类',
                    'edit_shop_category_form.button.update_shop_category': '更新商店分类',

                    'delete_shop_category_form.title': '删除商店分类',
                    'delete_shop_category_form.content': '你确定删除该商店分类吗？',
                    'delete_shop_category_form.button.confirm': '确认',
                    'delete_shop_category.message.success': '删除商店分类成功...',

                    'update_shop_category_form.title': '更新商店分类',
                    'update_shop_category_form.textinput1.label': '输入新的商店分类名',
                    'update_shop_category_form.textinput1.placeholder': '请输入任意字符串, 但不能留空...',
                    'update_shop_category_form.textinput2.label': '输入新的商店分类图标路径或留空',
                    'update_shop_category_form.textinput2.placeholder': '请输入任意字符串或留空...',
                    'update_shop_category_form.submit_button': '更新',
                    'update_shop_category.message.fail': '更新商店分类失败',
                    'update_shop_category.message.fail.reason': '已经有一个名为 {0} 的商店分类了...',
                    'update_shop_category.message.success': '更新商店分类失败...',

                    'add_good_form.title': '添加商品',
                    'add_good_form.dropdown1.label': '选择商店分类',
                    'add_good_form.dropdown2.label': '选择模式',
                    'add_good_form.textinput1.label': '输入商品名',
                    'add_good_form.textinput1.placeholder': '请输入任意字符串, 但不能留空...',
                    'add_good_form.textinput2.label': '输入商品购买价格',
                    'add_good_form.textinput2.placeholder': '请输入一个正整数...',
                    'add_good_form.submit_button': '添加',
                    'add_good.message.fail': '添加商品失败',
                    'add_good.message.fail.reason': '已经有一个商品 (类型: {0}) 属于该商店分类了...',
                    'add_good.message.success': '添加商品成功...',

                    'good_form.title': '商品',
                    'good_form.content': '已被 {0} 位玩家收藏',
                    'good_form.button.edit_good': '编辑商品',
                    'good_form.button.purchase': '购买',
                    'good_form.button.reclaim': '回收',
                    'good_form.button.collect_good': '收藏',
                    'good_form.button.cancel_collect_good': '取消收藏',

                    'edit_good_form.title': '编辑商品',
                    'edit_good_form.content': '请选择操作...',
                    'edit_good_form.button.delete_good': '删除商品',
                    'edit_good_form.button.update_good': '更新商品',

                    'update_good_form.title': '更新商品',
                    'update_good_form.textinput1.label': '输入新的商品名',
                    'update_good_form.textinput1.placeholder': '请输入任意字符串, 但不能留空...',
                    'update_good_form.textinput2.label': '输入新的商品购买价格',
                    'update_good_form.textinput2.placeholder': '请输入一个正整数...',
                    'update_good_form.dropdown.label': '选择模式',
                    'update_good_form.submit_button': '更新',
                    'update_good.message.success': '更新商品成功...',

                    'delte_good_form.title': '删除商品',
                    'delte_good_form.content': '你确定删除该商品吗？',
                    'delte_good_form.button.confirm': '确认',
                    'delte_good.message.success': '删除商品成功...',

                    'good_purchase_form.title': '商品购买',
                    'good_purchase_form.textinput.label': '输入购买数量',
                    'good_purchase_form.textinput.placeholder': '请输入一个正整数...',
                    'good_purchase_form.submit_button': '购买',
                    'good_purchase.message.fail': '购买失败',
                    'good_purchase.message.fail.reason': '你的余额不足...',
                    'good_purchase.message.success': '购买成功...',

                    'good_reclaim_form.title': '商品回收',
                    'good_reclaim_form.textinput.label1': '你的物品栏里有 {0} 个 {1}...',
                    'good_reclaim_form.textinput.label2': '输入回收数量',
                    'good_reclaim_form.textinput.placeholder': '请输入一个不超过 {0} 的正整数...',
                    'good_reclaim_form.submit_button': '回收',
                    'good_reclaim.message.fail': '回收失败',
                    'good_reclaim.message.fail.reason': '你的物品栏里没有目标回收商品...',
                    'good_reclaim.message.success': '回收成功...',

                    'good_search_form.title': '商品搜索',
                    'good_search_form.textinput.label': '输入一个关键词',
                    'good_search_form.textinput.placeholder': '请输入任意字符串, 但不能留空...',
                    'good_search_form.submit_button': '搜索',

                    'good_search_result_form.title': '商品搜索结果',
                    'good_search_result.message.fail': '没有匹配到任何结果...',
                    'good_search_result.message.success': '匹配到 {0} 个结果...',

                    'good_collect.message.success': '收藏成功...',
                    'good_collect_cancel.message.success': '取消收藏成功...',

                    'good_collection_form.title': '商品收藏',
                    'good_collection_form.content1': '你还没有收藏任何商品...',
                    'good_collection_form.content2': '你已经收藏了 {0} 个商品...',

                    'toggle_add_good_mode.message.fail': '开启添加商品模式失败',
                    'toggle_add_good_mode.message.fail.reason': '还没有添加任何商店分类...',
                    'toggle_add_good_mode.message.on.success': '开启添加商品模式成功...',
                    'toggle_add_good_mode.message.off.success': '关闭添加商品模式成功...',

                    'reload_config_form.title': '重载配置文件',
                    'reload_config_form.content': '请选择操作...',
                    'reload_config_form.button.reload_global_config': '重载全局配置',
                    'reload_config_form.button.reload_shop_data': '重载商店数据',

                    'reload_global_config_form.title': '重载全局配置',
                    'reload_global_config_form.textinput.label': '当前商品回收价率',
                    'reload_global_config_form.textinput.placeholder': '请输入一个不大于1的正小数...',
                    'reload_global_config_form.submit_button': '重载',
                    'reload_global_config.message.success': '重载全局配置成功...',

                    'reload_shop_data.message.success': '重载商店数据成功...',
                }
                json_str = json.dumps(zh_CN, indent=4, ensure_ascii=False)
                f.write(json_str)

        if not os.path.exists(en_US_data_file_path):
            with open(en_US_data_file_path, 'w', encoding='utf-8') as f:
                en_US = {
                    'your_money': 'Your money',
                    'purchase_price': 'Purchase price',
                    'reclaim_price': 'Reclaim price',
                    'category_name': 'Category name',
                    'good_type': 'Good type',
                    'good_name': 'Good name',
                    'good_mode': 'Good mode',

                    'button.back': 'Back to previous',
                    'message.type_error': 'The form is parsed incorrectly, please follow the prompts to fill in correctly...',

                    'main_form.title': 'UShop - main form',
                    'main_form.content': 'Please select a function...',
                    'main_form.button.add_shop_category': 'Add a new shop category',
                    'main_form.button.toggle_add_good_mode': 'Toggle on/off good add mode',
                    'main_form.button.reload_config': 'Reload configurations',
                    'main_form.button.search_good': 'Good search',
                    'main_form.button.collect_good': 'Good collections',
                    'main_form.button.close': 'Close',
                    'main_form.button.back_to_zx_ui': 'Back to menu',

                    'add_shop_category_form.title': 'Add a new shop category',
                    'add_shop_category_form.textinput1.label': 'Input the name of new shop category',
                    'add_shop_category_form.textinput1.placeholder': 'Input any string, but cannot be blank...',
                    'add_shop_category_form.textinput2.label': 'Input the icon path of new shop category or left blank',
                    'add_shop_category_form.textinput2.placeholder': 'Input any string or left blank...',
                    'add_shop_category_form.submit_button': 'Add',
                    'add_shop_category.message.fail': 'Failed to add a new shop category',
                    'add_shop_category.message.fail.reason': 'there is already a shop category named {0}...',
                    'add_shop_category.message.success': 'Successfully add a new shop category...',

                    'shop_category_form.content': 'Please select a function...',
                    'shop_category_form.button.edit_shop_category': 'Edit this shop category',

                    'edit_shop_category_form.title': 'Edit shop category',
                    'edit_shop_category_form.content': 'Please select a function...',
                    'edit_shop_category_form.button.delete_shop_category': 'Delete this shop category',
                    'edit_shop_category_form.button.update_shop_category': 'Update this shop category',

                    'delete_shop_category_form.title': 'Delete shop category',
                    'delete_shop_category_form.content': 'Are you sure to delete this category?',
                    'delete_shop_category_form.button.confirm': 'Confirm',
                    'delete_shop_category.message.success': 'Successfully delete shop category...',

                    'update_shop_category_form.title': 'Update shop category',
                    'update_shop_category_form.textinput1.label': 'Input new name of this shop category',
                    'update_shop_category_form.textinput1.placeholder': 'Input any string, but cannot be blank...',
                    'update_shop_category_form.textinput2.label': 'Input new icon path of this shop category',
                    'update_shop_category_form.textinput2.placeholder': 'Input any string or left blank...',
                    'update_shop_category_form.submit_button': 'Update',
                    'update_shop_category.message.fail': 'Failed to update shop category',
                    'update_shop_category.message.fail.reason': 'there is already a shop category named {0}...',
                    'update_shop_category.message.success': 'Successfully update shop category...',

                    'add_good_form.title': 'Add a new good',
                    'add_good_form.dropdown1.label': 'Select a shop category',
                    'add_good_form.dropdown2.label': 'Select a mode',
                    'add_good_form.textinput1.label': 'Input the name of new good',
                    'add_good_form.textinput1.placeholder': 'Input any string, but cannot be blank...',
                    'add_good_form.textinput2.label': 'Input the purchase price of new good',
                    'add_good_form.textinput2.placeholder': 'Input a positive integer...',
                    'add_good_form.submit_button': 'Add',
                    'add_good.message.fail': 'Failed to add a new good',
                    'add_good.message.fail.reason': 'there is already a good (type: {0}) belong to this shop category...',
                    'add_good.message.success': 'Successfully add a new good...',

                    'good_form.title': 'Good',
                    'good_form.content': 'Collected by {0} players',
                    'good_form.button.edit_good': 'Edit this good',
                    'good_form.button.purchase': 'Purchase',
                    'good_form.button.reclaim': 'Reclaim',
                    'good_form.button.collect_good': 'Collect',
                    'good_form.button.cancel_collect_good': 'Cancel the collection',

                    'edit_good_form.title': 'Edit good',
                    'edit_good_form.content': 'Please select a function...',
                    'edit_good_form.button.delete_good': 'Delete this good',
                    'edit_good_form.button.update_good': 'Update this good',

                    'update_good_form.title': 'Update good',
                    'update_good_form.textinput1.label': 'Input new name of this good',
                    'update_good_form.textinput1.placeholder': 'Input any string, but cannot be blank...',
                    'update_good_form.textinput2.label': 'Input new purchase price of this good',
                    'update_good_form.textinput2.placeholder': 'Input a positive integer...',
                    'update_good_form.dropdown.label': 'Select a mode',
                    'update_good_form.submit_button': 'Update',
                    'update_good.message.success': 'Successfully update good...',

                    'delte_good_form.title': 'Delete good',
                    'delte_good_form.content': 'Are you sure to delete this good?',
                    'delte_good_form.button.confirm': 'Confirm',
                    'delte_good.message.success': 'Successfully delete good...',

                    'good_purchase_form.title': 'Good purchase',
                    'good_purchase_form.textinput.label': 'Input the amount of this good to purchase',
                    'good_purchase_form.textinput.placeholder': 'Input a positive integer...',
                    'good_purchase_form.submit_button': 'Purchase',
                    'good_purchase.message.fail': 'Failed to purchase',
                    'good_purchase.message.fail.reason': 'your money is not sufficient...',
                    'good_purchase.message.success': 'Successfully purchase...',

                    'good_reclaim_form.title': 'Good reclaim',
                    'good_reclaim_form.textinput.label1': 'there are {0} {1}(s) in your inventory...',
                    'good_reclaim_form.textinput.label2': 'Input the amount of good to reclaim',
                    'good_reclaim_form.textinput.placeholder': 'Input a positive integer not more than {0}...',
                    'good_reclaim_form.submit_button': 'Reclaim',
                    'good_reclaim.message.fail': 'Failed to reclaim',
                    'good_reclaim.message.fail.reason': 'you do not have any target good in your inventory...',
                    'good_reclaim.message.success': 'Successfully reclaim...',

                    'good_search_form.title': 'Good search',
                    'good_search_form.textinput.label': 'Input a keyword',
                    'good_search_form.textinput.placeholder': 'Input any string, but cannot be blank...',
                    'good_search_form.submit_button': 'Search',

                    'good_search_result_form.title': 'Good search results',
                    'good_search_result.message.fail': 'No matached results...',
                    'good_search_result.message.success': '{0} results were matched...',

                    'good_collect.message.success': 'Successfully collect...',
                    'good_collect_cancel.message.success': 'Successfully cancel the collection...',

                    'good_collection_form.title': 'Good collections',
                    'good_collection_form.content1': 'You have not collect any goods yet...',
                    'good_collection_form.content2': 'You have collected {0} goods...',

                    'toggle_add_good_mode.message.fail': 'Failed to toggle on add good mode',
                    'toggle_add_good_mode.message.fail.reason': 'no category has been created yet...',
                    'toggle_add_good_mode.message.on.success': 'Successfully toggle on add good mode...',
                    'toggle_add_good_mode.message.off.success': 'Successfully toggle off add good mode...',

                    'reload_config_form.title': 'Reload configurations',
                    'reload_config_form.content': 'Please select a function...',
                    'reload_config_form.button.reload_global_config': 'Reload global configurations',
                    'reload_config_form.button.reload_shop_data': 'Reload shop data',

                    'reload_global_config_form.title': 'Reload global configurations',
                    'reload_global_config_form.textinput.label': 'The current reclaim rate of every single good',
                    'reload_global_config_form.textinput.placeholder': 'Input a positive decimal not more than 1...',
                    'reload_global_config_form.submit_button': 'Reload',
                    'reload_global_config.message.success': 'Successfully reload global configurations...',

                    'reload_shop_data.message.success': 'Successfully reload shop data...',
                }
                json_str = json.dumps(en_US, indent=4, ensure_ascii=False)
                f.write(json_str)

        lang_data = {}
        lang_list = os.listdir(lang_dir)
        for lang in lang_list:
            lang_name = lang.strip('.json')
            lang_data_file_path = os.path.join(lang_dir, lang)
            with open(lang_data_file_path, 'r', encoding='utf-8') as f:
                lang_data[lang_name] = json.loads(f.read())

        return lang_data
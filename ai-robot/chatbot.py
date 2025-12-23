import tkinter as tk
from tkinter import filedialog
import requests
from requests.exceptions import RequestException
from PIL import Image, ImageTk
import io
import json
import os
import dashscope

# 通义千问API配置
DASHSCOPE_API_KEY = "sk-9eb7698340df49149f3827bf35a16471"  # 请替换为您的阿里云DashScope API密钥
DASHSCOPE_API_URL = "https://dashscope.aliyuncs.com/api/v1/services/aigc/chat/chat-completions"  # 通义千问聊天API

# 食谱数据库
recipes = {
    "比萨饼": {
        "ingredients": ["面粉", "酵母", "盐", "糖", "橄榄油", "番茄酱", "奶酪", "各种配料（如香肠、蘑菇、青椒等）"],
        "steps": [
            "将面粉、酵母、盐和糖混合",
            "加入橄榄油和温水，揉成面团",
            "面团发酵1小时",
            "擀平面团，涂上番茄酱",
            "撒上奶酪和配料",
            "烤箱220℃烤15-20分钟"
        ]
    },
    "卷饼": {
        "ingredients": ["面粉", "水", "盐", "油", "肉类（如鸡肉、牛肉）", "蔬菜（如生菜、黄瓜、胡萝卜）", "酱料（如沙拉酱、番茄酱）"],
        "steps": [
            "将面粉、盐混合，加入水和油，揉成面团",
            "分成小份，擀成薄饼",
            "平底锅小火煎至两面金黄",
            "在薄饼上铺上肉类、蔬菜和酱料",
            "卷起来即可食用"
        ]
    },
    "意大利面": {
        "ingredients": ["意大利面", "番茄酱", "橄榄油", "大蒜", "洋葱", "牛肉末", "芝士粉", "罗勒"],
        "steps": [
            "煮意大利面：水烧开后加盐，煮至软嫩",
            "制作酱料：用橄榄油炒香大蒜和洋葱",
            "加入牛肉末，炒至变色",
            "加入红酒（可选）和番茄酱，小火慢炖",
            "将煮好的意大利面和酱料混合",
            "撒上芝士粉和罗勒"
        ]
    }
}

class ChatBot:
    def __init__(self, root):
        # 多语言文本字典
        self.texts = {
            "zh": {
                "title": "智能烹饪机器人助手",
                "welcome": "您好！我是您的智能烹饪机器人助手。请选择您想要了解的菜品或上传图片来识别食材！",
                "send": "发送",
                "upload_photo": "上传图片",
                "ingredients": "配料",
                "steps": "步骤",
                "show_recipe": "查看食谱",
                "show_ingredients": "查看配料",
                "save_order": "保存订单",
                "generate_pdf": "生成PDF",
                "select_dish": "您选择了 {dish}，正在为您准备食谱...",
                "system_prompt": "您是一位专业的厨师机器人，能够提供详细的烹饪食谱。请确保回答包含配料列表和烹饪步骤。",
                "user_prompt": "请为我提供 {dish} 的详细食谱，包括配料和步骤。",
                "uploaded_photo": "已上传图片: {filename}",
                "order_saved": "订单已保存为 {dish} 的PDF和JSON文件",
                "view_recipe": "查看食谱",
                "view_ingredients": "查看配料",
                "save_current_order": "保存当前订单",
                "back_to_dish": "返回选择菜肴",
                "recipe": "{dish} 的烹饪步骤：",
                "ingredients": "{dish} 的配料：",
                "loading_url": "正在加载图片: {url}",
                "url_success": "图片加载成功！",
                "url_error": "加载图片失败: {error}",
                "choose_action": "请选择操作："
            },
            "ru": {
                "title": "Интеллектуальный кулинарный робот-ассистент",
                "welcome": "Привет! Я ваш интеллектуальный кулинарный робот-ассистент. Пожалуйста, выберите блюдо, которое вас интересует, или загрузите изображение для распознавания ингредиентов!",
                "send": "Отправить",
                "upload_photo": "Загрузить фото",
                "ingredients": "Ингредиенты",
                "steps": "Шаги приготовления",
                "show_recipe": "Показать рецепт",
                "show_ingredients": "Показать ингредиенты",
                "save_order": "Сохранить заказ",
                "generate_pdf": "Сгенерировать PDF",
                "select_dish": "Вы выбрали {dish}, готовим рецепт...",
                "system_prompt": "Вы профессиональный кулинарный робот, способный предоставлять подробные рецепты. Убедитесь, что ответ содержит список ингредиентов и шаги приготовления.",
                "user_prompt": "Пожалуйста, предоставьте мне подробный рецепт для {dish}, включая ингредиенты и шаги приготовления.",
                "uploaded_photo": "Фото загружено: {filename}",
                "order_saved": "Заказ сохранен как PDF и JSON для {dish}",
                "view_recipe": "Показать рецепт",
                "view_ingredients": "Показать ингредиенты",
                "save_current_order": "Сохранить текущий заказ",
                "back_to_dish": "Вернуться к выбору блюда",
                "recipe": "Шаги приготовления {dish}:",
                "ingredients": "Ингредиенты для {dish}:",
                "loading_url": "Загрузка изображения: {url}",
                "url_success": "Изображение загружено успешно!",
                "url_error": "Ошибка загрузки изображения: {error}",
                "choose_action": "Пожалуйста, выберите действие:"
            }
        }
        self.language = "zh"  # 默认中文
        # 菜名翻译字典 - 结构：{内部ID: {语言: 翻译名称}} 例如：{"pizza": {"zh": "比萨饼", "ru": "Пицца"}}
        self.dish_names = {
            "pizza": {"zh": "比萨饼", "ru": "Пицца"},
            "burrito": {"zh": "卷饼", "ru": "Бурито"},
            "pasta": {"zh": "意大利面", "ru": "Паста"}
        }
        # 多语言食谱字典 - 结构：{内部ID: {语言: {"ingredients": [...], "steps": [...]}}}
        self.multi_lang_recipes = {
            "pizza": {
                "zh": {
                    "ingredients": ["面粉", "酵母", "盐", "糖", "橄榄油", "番茄酱", "奶酪", "各种配料（如香肠、蘑菇、青椒等）"],
                    "steps": [
                        "将面粉、酵母、盐和糖混合",
                        "加入橄榄油和温水，揉成面团",
                        "面团发酵1小时",
                        "擀平面团，涂上番茄酱",
                        "铺上奶酪、意大利辣香肠和蔬菜",
                        "放入烤箱，220°C烤20分钟"
                    ]
                },
                "ru": {
                    "ingredients": ["мука", "дрожжи", "соль", "сахар", "оливковое масло", "теплая вода", "томатный соус", "моцарелла", "пепперони", "овощи"],
                    "steps": [
                        "Смешайте муку, дрожжи, соль и сахар",
                        "Добавьте оливковое масло и теплую воду, замешайте тесто",
                        "Закройте тесто и дайте ему подняться 1 час",
                        "Разогните тесто и намажьте томатным соусом",
                        "Растолките сыр, пепперони и овощи",
                        "Выпеките в духовке при 220°C 20 минут"
                    ]
                }
            },
            "burrito": {
                "zh": {
                    "ingredients": ["面粉", "水", "盐", "油", "肉类（如鸡肉、牛肉）", "蔬菜（如生菜、黄瓜、胡萝卜）", "酱料（如沙拉酱、番茄酱）"],
                    "steps": [
                        "将面粉、盐混合，加入水和油，揉成面团",
                        "分成小份，擀成薄饼",
                        "平底锅小火煎至两面金黄",
                        "在薄饼上铺上肉类、蔬菜和酱料",
                        "卷起来即可食用"
                    ]
                },
                "ru": {
                    "ingredients": ["мука", "вода", "соль", "масло", "мясо (например, курица, говядина)", "овощи (например, листья салата, огурцы, морковь)", "соусы (например, майонез, томатный соус)"],
                    "steps": [
                        "Смешайте муку и соль, добавьте воду и масло, замешайте тесто",
                        "Разделите на небольшие порции и раскатайте тонкие лепечки",
                        "Жарите на сковороде на маленьком огне с обеих сторон",
                        "Нанесите мясо, овощи и соусы на лепечку",
                        "Закройте в рулет и готово к употреблению"
                    ]
                }
            },
            "pasta": {
                "zh": {
                    "ingredients": ["意大利面", "牛肉末", "洋葱", "大蒜", "番茄酱", "芝士粉", "罗勒叶", "橄榄油", "红酒（可选）"],
                    "steps": [
                        "煮一锅水，加盐，放入意大利面煮至8成熟",
                        "加热橄榄油，炒香洋葱和大蒜",
                        "加入牛肉末炒至变色",
                        "加入红酒（可选）和番茄酱，小火慢炖30分钟",
                        "将煮好的意大利面与酱料混合",
                        "撒上芝士粉和新鲜罗勒叶"
                    ]
                },
                "ru": {
                    "ingredients": ["паста", "мясной фарш", "лук", "чеснок", "томатный соус", "сырный порошок", "листья βασильика", "оливковое масло", "вино (по желанию)"],
                    "steps": [
                        "Варите воду, добавьте соль и варите пасту до состояния 'ал денте'",
                        "Разогрейте оливковое масло, обжарьте лук и чеснок",
                        "Добавьте мясной фарш и обжарьте до готовности",
                        "Добавьте вино (при желании) и томатный соус, тушите на маленьком огне 30 минут",
                        "Смешайте готовую пасту с соусом",
                        "Посыпьте сырым порошком и свежей базиликой"
                    ]
                }
            }
        }
        
        self.root = root
        self.root.title(self.texts[self.language]["title"])
        self.root.geometry("600x700")
        
        # 语言切换区域
        self.language_frame = tk.Frame(root)
        self.language_frame.pack(pady=5, padx=10, anchor="e")
        
        self.language_var = tk.StringVar(value=self.language)
        self.zh_button = tk.Radiobutton(self.language_frame, text="中文", variable=self.language_var, value="zh", command=self.switch_language)
        self.zh_button.pack(side=tk.RIGHT, padx=5)
        
        self.ru_button = tk.Radiobutton(self.language_frame, text="Русский", variable=self.language_var, value="ru", command=self.switch_language)
        self.ru_button.pack(side=tk.RIGHT, padx=5)
        
        # 聊天记录区域
        self.chat_frame = tk.Frame(root)
        self.chat_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        
        self.chat_history = tk.Text(self.chat_frame, state=tk.DISABLED, wrap=tk.WORD)
        self.chat_history.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.scrollbar = tk.Scrollbar(self.chat_frame, command=self.chat_history.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.chat_history.config(yscrollcommand=self.scrollbar.set)
        
        # 图片显示区域
        self.image_label = tk.Label(root)
        self.image_label.pack(pady=10)
        
        # 按钮区域
        self.button_frame = tk.Frame(root)
        self.button_frame.pack(pady=10)
        
        # 输入区域
        self.input_frame = tk.Frame(root)
        self.input_frame.pack(pady=10, padx=10, fill=tk.X)
        
        self.input_entry = tk.Entry(self.input_frame)
        self.input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        self.send_button = tk.Button(self.input_frame, text=self.texts[self.language]["send"], command=self.send_message)
        self.send_button.pack(side=tk.RIGHT, padx=5)
        
        self.photo_button = tk.Button(self.input_frame, text=self.texts[self.language]["upload_photo"], command=self.upload_photo)
        self.photo_button.pack(side=tk.RIGHT, padx=5)
        
        # 当前选择的菜肴（使用内部标识符：pizza, burrito, pasta）
        self.current_dish = None
        self.current_dish_id = None
        # 保存当前照片路径
        self.current_photo = None
        
        # 欢迎消息
        self.add_message("机器人", self.texts[self.language]["welcome"])
        self.show_dish_buttons()

    def add_message(self, sender, message):
        self.chat_history.config(state=tk.NORMAL)
        self.chat_history.insert(tk.END, f"{sender}: {message}\n\n")
        self.chat_history.config(state=tk.DISABLED)
        self.chat_history.see(tk.END)

    def switch_language(self):
        # 切换语言
        new_lang = self.language_var.get()
        if new_lang != self.language:
            self.language = new_lang
            # 更新界面标题
            self.root.title(self.texts[self.language]["title"])
            # 更新按钮文本
            self.send_button.config(text=self.texts[self.language]["send"])
            self.photo_button.config(text=self.texts[self.language]["upload_photo"])
            # 清空聊天记录并重新显示欢迎消息
            self.chat_history.config(state=tk.NORMAL)
            self.chat_history.delete(1.0, tk.END)
            self.chat_history.config(state=tk.DISABLED)
            # 重新显示欢迎消息和按钮
            self.add_message("机器人", self.texts[self.language]["welcome"])
            self.show_dish_buttons()

    def show_dish_buttons(self):
        """显示所有可用菜肴按钮"""
        print(f"显示菜肴按钮，当前语言: {self.language}")
        
        self.clear_buttons()
        
        # 遍历所有菜肴的内部ID
        for dish_id in self.dish_names:
            current_language_dish_name = self.dish_names[dish_id][self.language]
            print(f"添加按钮: {dish_id} -> {current_language_dish_name}")
            self.add_button(
                text=current_language_dish_name,
                callback=self.select_dish,
                callback_args=(dish_id,)
            )

    def select_dish(self, dish_id):
        """选择特定菜肴并生成其食谱"""
        # 保存当前菜肴的内部ID
        self.current_dish_id = dish_id
        # 获取当前语言的菜名
        self.current_dish = self.dish_names[dish_id][self.language]
        
        print(f"用户选择了: {self.current_dish} (ID: {dish_id})")
        
        # 清空之前的食谱内容
        self.current_recipe = {}
        
        # 调用生成食谱函数（传入内部ID）
        recipe = self.generate_recipe(dish_id)
        
        # 更新用户界面
        self.add_message("机器人", self.texts[self.language]["select_dish"].format(dish=self.current_dish))
        
        # 保存生成的食谱
        self.current_recipe = recipe
        
        # 添加成功生成食谱的提示
        self.add_message("机器人", f"已为您生成 {self.current_dish} 的食谱！")
        
        # 显示可用操作
        self.show_action_buttons()

    def generate_recipe(self, dish_name):
        """
        为任意菜品名称生成食谱。优先检查是否有默认食谱，如果没有则调用 AI 生成。
        """
        print(f"正在为菜品 {dish_name} 生成食谱...")
        
        self.current_dish = dish_name
        self.current_dish_id = None  # 因为不是从预设按钮选择的
        
        # 首先尝试查找多语言默认食谱
        for dish_id, names in self.dish_names.items():
            if self.language in names and names[self.language] == dish_name:
                if dish_id in self.multi_lang_recipes:
                    recipe = self.multi_lang_recipes[dish_id]
                    self.add_message("机器人", f"找到预设食谱：{dish_name}")
                    self.current_recipe = recipe
                    self.show_recipe()
                    self.show_action_buttons()
                    return
        
        # 如果没有找到预设食谱，调用 AI 生成
        ai_recipe = self.call_ai_for_recipe(dish_name)
        
        if ai_recipe and ai_recipe.get("ingredients") and ai_recipe.get("steps"):
            self.add_message("机器人", f"已为您生成 {dish_name} 的食谱！")
            self.current_recipe = ai_recipe
            self.show_recipe()
            self.show_action_buttons()
        else:
            self.add_message("机器人", f"无法生成 {dish_name} 的食谱，请尝试其他菜品。")

    def call_ai_for_recipe(self, dish_name):
        """
        调用 AI 为任意菜品名称生成食谱
        """
        import dashscope
        from dashscope import Generation
        
        self.add_message("机器人", "正在调用 AI 生成 {} 的食谱...".format(dish_name))
        
        try:
            dashscope.api_key = DASHSCOPE_API_KEY
            
            # 根据当前语言构建提示词
            system_prompt = """
            你是一个专业的厨师，擅长根据用户需求生成详细的食谱。
            请根据用户要求的菜品名称，生成完整的烹饪食谱，包括：
            1. 详细的配料列表（包括用量）
            2. 清晰的烹饪步骤
            3. 使用用户选择的语言（{}）返回结果
            """
            
            user_prompt = """
            请为我生成 {} 这道菜的完整食谱，包括：
            1. 配料（ingredients）
            2. 烹饪步骤（steps）
            请用 {} 语言回复。
            """
            
            # 根据当前语言设置提示词
            if self.language == "zh":
                system_prompt = "你是一个专业的厨师，擅长根据用户需求生成详细的中文食谱。请返回清晰的配料列表和烹饪步骤。"
                user_prompt = f"请为我生成 '{dish_name}' 这道菜的完整中文食谱，包括配料和烹饪步骤。请用中文回复，格式清晰。"
            elif self.language == "ru":
                system_prompt = "Вы профессиональный повар, споциализирующийся на создании детальных рецептов по запросу пользователей. Пожалуйста, верните ясный список ингредиентов и шаги приготовления на русском языке."
                user_prompt = f"Пожалуйста, создайте полный русский рецепт для блюда '{dish_name}', включая ингредиенты и шаги приготовления. Ответьте на русском языке."
            else:  # 默认英语
                system_prompt = "You are a professional chef skilled at generating detailed recipes based on user requests. Please return clear ingredient lists and cooking steps in English."
                user_prompt = f"Please generate a complete English recipe for the dish '{dish_name}', including ingredients and cooking steps. Respond in English."
            
            messages = [
                {
                    "role": "system", 
                    "content": system_prompt
                },
                {
                    "role": "user", 
                    "content": user_prompt
                }
            ]
            
            print(f"调用 AI 为 {dish_name} 生成食谱...")
            print(f"使用系统提示词: {system_prompt}")
            print(f"用户提示词: {user_prompt}")
            
            response = dashscope.Generation.call(
                model="qwen-max",
                messages=messages,
                temperature=0.7,
                max_tokens=1500
            )
            
            print(f"API 响应: {response}")
            
            if response.status_code == 200 and hasattr(response, 'output') and hasattr(response.output, 'text'):
                ai_response = response.output.text.strip()
                self.add_message("机器人", "AI 生成完成！正在解析食谱...")
                
                # 解析 AI 返回的内容
                recipe = self.parse_ai_response(ai_response)
                return recipe
            else:
                self.add_message("机器人", "AI 调用失败，使用默认空食谱")
                print(f"API 调用失败: {response}")
                return {"ingredients": [], "steps": []}
                
        except Exception as e:
            self.add_message("机器人", f"调用 AI 失败: {str(e)}")
            print(f"调用 AI 失败: {e}")
            import traceback
            traceback.print_exc()
            return {"ingredients": [], "steps": []}

    def parse_ai_response(self, ai_response):
        """
        解析 AI 返回的食谱内容为结构化数据
        """
        ingredients = []
        steps = []
        
        try:
            # 简单的解析逻辑，根据常见的 AI 输出格式进行解析
            sections = ai_response.split("**")
            
            for i in range(len(sections)):
                if "配料" in sections[i] or "Ingredients" in sections[i] or "Ингредиенты" in sections[i]:
                    if i + 1 < len(sections):
                        # 提取配料列表
                        lines = sections[i + 1].split("\n")
                        for line in lines:
                            stripped = line.strip()
                            if stripped and not stripped.startswith("*") and not stripped.endswith(":"):
                                # 处理编号或列表项
                                if stripped.startswith(("1.", "2.", "3.", "4.", "5.", "6.", "7.", "8.", "9.", "•", "-", "*")):
                                    stripped = stripped[2:].strip()
                                if stripped:
                                    ingredients.append(stripped)
                elif "步骤" in sections[i] or "Steps" in sections[i] or "Шаги" in sections[i]:
                    if i + 1 < len(sections):
                        # 提取步骤列表
                        lines = sections[i + 1].split("\n")
                        for line in lines:
                            stripped = line.strip()
                            if stripped and not stripped.startswith("*") and not stripped.endswith(":"):
                                # 处理编号或列表项
                                if stripped.startswith(("1.", "2.", "3.", "4.", "5.", "6.", "7.", "8.", "9.", "•", "-", "*")):
                                    stripped = stripped[2:].strip()
                                if stripped:
                                    steps.append(stripped)
            
            # 如果简单解析没有结果，尝试更通用的方法
            if not ingredients or not steps:
                lines = ai_response.split("\n")
                in_ingredients = False
                in_steps = False
                
                for line in lines:
                    stripped = line.strip()
                    if not stripped:
                        continue
                    
                    if "配料" in stripped or "Ingredients" in stripped or "Ингредиенты" in stripped:
                        in_ingredients = True
                        in_steps = False
                        continue
                    if "步骤" in stripped or "Steps" in stripped or "Шаги" in stripped:
                        in_steps = True
                        in_ingredients = False
                        continue
                    
                    if in_ingredients:
                        if stripped.startswith(("1.", "2.", "3.", "4.", "5.", "6.", "7.", "8.", "9.", "•", "-", "*")):
                            ingredients.append(stripped[2:].strip())
                    elif in_steps:
                        if stripped.startswith(("1.", "2.", "3.", "4.", "5.", "6.", "7.", "8.", "9.", "•", "-", "*")):
                            steps.append(stripped[2:].strip())
            
        except Exception as e:
            print(f"解析 AI 响应错误: {e}")
        
        return {"ingredients": ingredients, "steps": steps}

    def upload_photo(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png *.gif")])
        if file_path:
            self.current_photo = file_path
            self.display_photo(file_path)
            self.add_message("机器人", self.texts[self.language]["uploaded_photo"].format(filename=os.path.basename(file_path)))
            # 自动分析照片
            self.analyze_photo(file_path)

    def display_photo(self, file_path):
        try:
            img = Image.open(file_path)
            img.thumbnail((300, 200))
            photo = ImageTk.PhotoImage(img)
            self.image_label.config(image=photo)
            self.image_label.image = photo
        except Exception as e:
            self.add_message("机器人", self.texts[self.language]["photo_error"].format(error=str(e)))

    def analyze_photo(self, file_path):
        try:
            self.add_message("机器人", self.texts[self.language]["analyzing_photo"])
            
            # 配置API密钥
            dashscope.api_key = DASHSCOPE_API_KEY
            
            # 根据语言选择请求语言
            if self.language == "ru":
                prompt = "Пожалуйста, опишите это блюдо."
            else:
                prompt = "请描述这道菜肴。"
            
            # 进一步优化图片压缩，确保在API限制范围内
            from PIL import Image
            import io
            import base64
            
            # 打开并压缩图片
            img = Image.open(file_path)
            # 调整图片大小到更小尺寸
            img.thumbnail((600, 600))
            
            # 保存到内存，使用更低的质量
            buffer = io.BytesIO()
            # 压缩质量为50，进一步减少大小
            img.save(buffer, format="JPEG", quality=50, optimize=True, progressive=True)
            compressed_image_data = buffer.getvalue()
            
            # 检查压缩后的大小
            print(f"压缩后的图片大小: {len(compressed_image_data)} 字节")
            
            # 将压缩后的图片转换为base64编码
            image_base64 = base64.b64encode(compressed_image_data).decode("utf-8")
            
            # 检查base64编码后的长度
            print(f"base64编码后的长度: {len(image_base64)} 字符")
            
            # 如果还是太长，再次压缩
            if len(image_base64) > 20000:  # 留一些余量
                img.thumbnail((400, 400))
                buffer = io.BytesIO()
                img.save(buffer, format="JPEG", quality=30, optimize=True, progressive=True)
                compressed_image_data = buffer.getvalue()
                image_base64 = base64.b64encode(compressed_image_data).decode("utf-8")
                print(f"再次压缩后的base64长度: {len(image_base64)} 字符")
            
            # 调用通义千问的图像理解API
            response = dashscope.MultiModalConversation.call(
                model="qwen-vl-plus",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"text": prompt},
                            {"image": f"data:image/jpeg;base64,{image_base64}"}
                        ]
                    }
                ]
            )
            
            # 打印响应内容到控制台以便调试
            print(f"照片分析API响应：{response}")
            
            if response.status_code == 200 and response.output.choices:
                # 获取图片描述，处理可能的格式问题
                message_content = response.output.choices[0].message.content
                
                # 检查content的类型
                if isinstance(message_content, list):
                    # 如果是列表，提取文本内容
                    dish_description = "".join([item.get("text", "") for item in message_content])
                else:
                    # 如果是字符串，直接使用
                    dish_description = message_content
                
                self.add_message("机器人", f"照片分析结果：{dish_description}")
                
                # 根据描述生成完整食谱
                if self.language == "ru":
                    recipe_prompt = f"На основе этого описания блюда сгенерируйте полный рецепт на русском языке, включая список ингредиентов и пошаговые инструкции по приготовлению. Описание блюда: {dish_description}"
                else:
                    recipe_prompt = f"根据这道菜肴的描述，生成完整的食谱，包括配料列表和分步烹饪步骤。菜肴描述：{dish_description}"
                
                # 调用API生成食谱
                recipe_response = dashscope.Generation.call(
                    model="qwen-max",
                    messages=[
                        {"role": "system", "content": "您是一位专业的厨师，能够根据菜肴描述生成详细的食谱。"},
                        {"role": "user", "content": recipe_prompt}
                    ],
                    temperature=0.7,
                    max_tokens=1500
                )
                
                if recipe_response.status_code == 200 and recipe_response.output.text:
                    recipe_text = recipe_response.output.text
                    self.add_message("机器人", self.texts[self.language]["photo_recipe"])
                    self.add_message("机器人", recipe_text)
                    
                    # 设置当前食谱，以便后续操作
                    # 简单解析食谱，提取配料和步骤
                    ingredients = []
                    steps = []
                    
                    lines = recipe_text.split('\n')
                    in_ingredients = False
                    in_steps = False
                    
                    for line in lines:
                        line = line.strip()
                        if not line:
                            continue
                        
                        if "配料" in line or "材料" in line or "ingredients" in line.lower() or "Ингредиенты" in line:
                            in_ingredients = True
                            in_steps = False
                            continue
                        elif "步骤" in line or "做法" in line or "steps" in line.lower() or "Шаги" in line:
                            in_ingredients = False
                            in_steps = True
                            continue
                        
                        if in_ingredients:
                            if line.startswith(("1.", "2.", "3.", "4.", "5.", "6.", "7.", "8.", "9.", "•", "-", "*")):
                                ingredients.append(line[2:].strip())
                        elif in_steps:
                            if line.startswith(("1.", "2.", "3.", "4.", "5.", "6.", "7.", "8.", "9.", "•", "-", "*")):
                                steps.append(line)
                    
                    # 设置当前食谱
                    self.current_recipe = {
                        "ingredients": ingredients,
                        "steps": steps,
                        "ai_generated": True,
                        "full_text": recipe_text
                    }
                    
                    # 显示操作按钮
                    self.add_message("机器人", self.texts[self.language]["choose_action"])
                    self.show_action_buttons()
                else:
                    self.add_message("机器人", self.texts[self.language]["api_error"].format(error=recipe_response))
            else:
                self.add_message("机器人", self.texts[self.language]["api_error"].format(error=response))
        except Exception as e:
            self.add_message("机器人", self.texts[self.language]["use_default"].format(error=str(e)))
            import traceback
            traceback.print_exc()

    def send_message(self):
        """
        处理用户发送的消息，现在主要用于调用 AI 生成任意菜品的食谱
        """
        # 获取用户输入内容
        user_message = self.input_entry.get().strip()
        if not user_message:
            return
        
        # 添加用户消息到聊天记录
        self.add_message("您", user_message)
        self.input_entry.delete(0, tk.END)
        
        # 处理特殊命令
        if user_message == self.texts[self.language]["back_to_dish"] or user_message == "reselect":
            self.show_dish_buttons()
            return
        
        # 处理 URL 图片输入
        if user_message.startswith('http://') or user_message.startswith('https://'):
            try:
                response = requests.get(user_message)
                response.raise_for_status()
                if 'image' in response.headers['Content-Type']:
                    self.add_message("机器人", "正在分析图片...")
                    image = Image.open(io.BytesIO(response.content))
                    # 保存为临时文件并分析
                    temp_path = os.path.join(self.temp_dir, "uploaded_image.jpg")
                    image.save(temp_path)
                    self.analyze_photo(temp_path)
                    return
                else:
                    self.add_message("机器人", "链接不是图片格式，无法处理")
            except requests.exceptions.RequestException:
                self.add_message("机器人", "无法从该 URL 下载图片")
            except Exception:
                self.add_message("机器人", "处理图片失败")
            return
        
        # 主要功能：调用 AI 生成任意菜品名称的食谱
        self.generate_recipe(user_message)
        
        return

    def handle_action(self, action):
        if not hasattr(self, 'current_recipe') or self.current_recipe is None:
            self.add_message("机器人", "没有可操作的食谱，请先生成一个食谱")
            return
        
        if action == "view_recipe":
            self.show_recipe()
        elif action == "view_ingredients":
            self.show_ingredients()
        elif action == "save_order":
            self.save_order()
        elif action == "back_to_dish":
            self.current_dish = None
            self.current_dish_id = None
            self.current_recipe = None
            self.add_message("机器人", self.texts[self.language]["welcome"])
            self.show_dish_buttons()

    def show_action_buttons(self):
        # 清除现有按钮
        for widget in self.button_frame.winfo_children():
            widget.destroy()
        
        # 创建操作按钮，使用多语言文本
        actions = [
            (self.texts[self.language]["view_recipe"], "view_recipe"),
            (self.texts[self.language]["view_ingredients"], "view_ingredients"),
            (self.texts[self.language]["save_order"], "save_order"),
            (self.texts[self.language]["back_to_dish"], "back_to_dish")
        ]
        for display_text, action_key in actions:
            btn = tk.Button(self.button_frame, text=display_text, width=15, height=2, command=lambda a=action_key: self.handle_action(a))
            btn.pack(side=tk.LEFT, padx=5)

    def show_recipe(self):
        if hasattr(self, 'current_recipe') and self.current_recipe:
            # 如果没有current_dish，使用默认名称
            dish_name = self.current_dish if hasattr(self, 'current_dish') and self.current_dish else "未知菜肴"
            self.add_message("机器人", self.texts[self.language]["recipe"].format(dish=dish_name))
            for step in self.current_recipe["steps"]:
                self.add_message("机器人", step)

    def show_ingredients(self):
        if hasattr(self, 'current_recipe') and self.current_recipe:
            # 如果没有current_dish，使用默认名称
            dish_name = self.current_dish if hasattr(self, 'current_dish') and self.current_dish else "未知菜肴"
            self.add_message("机器人", self.texts[self.language]["ingredients"].format(dish=dish_name))
            for ing in self.current_recipe["ingredients"]:
                self.add_message("机器人", f"- {ing}")

    def save_order(self):
        if hasattr(self, 'current_recipe') and self.current_recipe:
            # 如果没有current_dish，使用默认名称
            dish_name = self.current_dish if hasattr(self, 'current_dish') and self.current_dish else "未知菜肴"
            # 保存订单到文件
            order = {
                "dish": dish_name,
                "ingredients": self.current_recipe["ingredients"],
                "steps": self.current_recipe["steps"],
                "ai_generated": self.current_recipe.get("ai_generated", False)
            }
            
            # 保存为JSON
            json_filename = f"order_{dish_name}.json"
            with open(json_filename, "w", encoding="utf-8") as f:
                json.dump(order, f, ensure_ascii=False, indent=2)
            
            # 生成PDF并获取结果
            pdf_success, pdf_filename = self.generate_pdf(order)
            
            # 根据PDF生成结果显示不同消息
            if pdf_success:
                # PDF生成成功
                self.add_message("机器人", self.texts[self.language]["order_saved"].format(dish=dish_name))
            else:
                # PDF生成失败，但JSON已保存
                self.add_message("机器人", f"订单已保存为JSON文件：{json_filename}")
                self.add_message("机器人", "PDF文件生成失败，请查看控制台错误信息")

    def generate_pdf(self, order):
        # 使用fpdf2库，它对中文支持更好
        try:
            from fpdf import FPDF
            import os
            
            # 生成安全的文件名
            dish_name = order['dish'] if isinstance(order['dish'], str) else "未知菜肴"
            safe_filename = f"order_{dish_name.replace(' ', '_')}.pdf"
            safe_filename = ''.join(c for c in safe_filename if c.isalnum() or c in ('_', '.'))
            
            # 创建PDF对象
            pdf = FPDF()
            pdf.add_page()
            pdf.set_auto_page_break(auto=True, margin=15)
            
            # 设置字体
            # 对于俄语支持，我们需要使用支持西里尔字母的字体
            if self.language == "ru":
                # 尝试加载系统中的西里尔字母字体
                font_paths = [
                    '/System/Library/Fonts/STHeiti Light.ttc',
                    '/System/Library/Fonts/PingFang.ttc',
                    '/System/Library/Fonts/HelveticaNeue.ttc',
                    '/Library/Fonts/Arial.ttf'
                ]
            else:
                # 中文使用的字体路径
                font_paths = [
                    '/System/Library/Fonts/STHeiti Light.ttc',
                    '/System/Library/Fonts/PingFang.ttc',
                    '/Library/Fonts/Songti.ttc'
                ]
            
            font_loaded = False
            font_name = "CustomFont"  # 使用固定的字体名称
            
            # 尝试注册一个可用的字体
            for font_path in font_paths:
                if os.path.exists(font_path):
                    try:
                        pdf.add_font(font_name, '', font_path, uni=True)
                        font_loaded = True
                        print(f"成功加载字体：{font_path}")
                        break
                    except Exception as e:
                        print(f"加载字体失败 {font_path}: {e}")
            
            if not font_loaded:
                print("无法加载任何字体文件，使用默认字体")
            else:
                pdf.set_font(font_name, size=12)
            
            # 添加标题
            pdf.set_font(font_name, size=16)
            pdf.cell(200, 10, txt=f"{self.texts[self.language]['title']}: {order['dish']}", align='C', ln=True)
            pdf.ln(10)
            
            # 添加配料
            pdf.set_font(font_name, size=14)
            pdf.cell(200, 10, txt=self.texts[self.language]['ingredients'].format(dish=''), ln=True)
            pdf.ln(5)
            pdf.set_font(font_name, size=12)
            for ingredient in order['ingredients']:
                pdf.cell(200, 10, txt=f"• {ingredient}", ln=True)
            pdf.ln(10)
            
            # 添加步骤
            pdf.set_font(font_name, size=14)
            pdf.cell(200, 10, txt=self.texts[self.language]['steps'], ln=True)
            pdf.ln(5)
            pdf.set_font(font_name, size=12)
            for idx, step in enumerate(order['steps'], start=1):
                pdf.cell(200, 10, txt=f"{idx}. {step}", ln=True)
            
            pdf.output(safe_filename)
            print(f"PDF已保存为: {safe_filename}")
            return True, safe_filename
        except Exception as e:
            print(f"生成PDF时出错: {e}")
            import traceback
            traceback.print_exc()
            return False, None

    def add_button(self, text, callback, callback_args=None):
        """向按钮区域添加新按钮"""
        if callback_args:
            btn = tk.Button(self.button_frame, text=text, command=lambda: callback(*callback_args))
        else:
            btn = tk.Button(self.button_frame, text=text, command=callback)
        btn.pack(side=tk.LEFT, padx=5)

    def clear_buttons(self):
        """清空所有已显示的按钮"""
        for widget in self.button_frame.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    chatbot = ChatBot(root)
    root.mainloop()
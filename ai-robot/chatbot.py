import tkinter as tk
from tkinter import filedialog
import requests
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
        "ingredients": ["意大利面", "番茄酱", "大蒜", "洋葱", "橄榄油", "盐", "胡椒", "奶酪"],
        "steps": [
            "煮意大利面至 al dente",
            "橄榄油炒香大蒜和洋葱",
            "加入番茄酱，煮5分钟",
            "将煮好的意大利面加入酱料中拌匀",
            "撒上盐、胡椒和奶酪"
        ]
    }
}

class ChatBot:
    def __init__(self, root):
        # 多语言文本字典
        self.language = "zh"  # 默认中文
        self.texts = {
            "zh": {
                "title": "美食助手聊天机器人",
                "welcome": "欢迎使用美食助手！请选择您想要的菜肴类型：",
                "send": "发送",
                "upload_photo": "上传照片",
                "select_dish": "您选择了：{dish}！",
                "choose_action": "请选择您想要的操作：",
                "view_recipe": "查看食谱",
                "view_ingredients": "查看配料",
                "save_order": "保存订单",
                "back_to_dish": "返回选择菜肴",
                "recipe": "{dish}的分步食谱：",
                "ingredients": "{dish}的配料列表：",
                "order_saved": "订单已保存！JSON文件：order_{dish}.json，PDF文件：order_{dish}.pdf",
                "generating_recipe": "正在为您生成{dish}的食谱，请稍候...",
                "sending_api": "正在发送API请求...",
                "api_status": "API响应状态码：{code}",
                "api_error": "API响应错误：{error}",
                "uploaded_photo": "已上传照片：{filename}",
                "photo_error": "照片显示失败：{error}",
                "back": "返回",
                "reselect": "重新选择",
                "loading_url": "正在加载URL图片：{url}",
                "url_success": "URL图片加载成功！",
                "url_error": "URL图片加载失败：{error}",
                "use_default": "AI生成食谱失败，使用默认食谱：{error}",
                "recipe_parse_error": "食谱解析失败，使用默认食谱",
                "network_error": "网络请求失败：{error}",
                "api_format_error": "API响应格式错误：{error}",
                "api_key_error": "API响应键错误：{error}",
                "analyzing_photo": "正在分析照片，请稍候...",
                "photo_recipe": "根据照片生成的食谱：",
                "photo_ingredients": "根据照片识别的配料："
            },
            "ru": {
                "title": "Чат-бот помощник по кухне",
                "welcome": "Добро пожаловать в помощник по кухне！Пожалуйста, выберите тип блюда：",
                "send": "Отправить",
                "upload_photo": "Загрузить фото",
                "select_dish": "Вы выбрали：{dish}！",
                "choose_action": "Пожалуйста, выберите действие：",
                "view_recipe": "Посмотреть рецепт",
                "view_ingredients": "Посмотреть ингредиенты",
                "save_order": "Сохранить заказ",
                "back_to_dish": "Вернуться к выбору блюда",
                "recipe": "Пошаговый рецепт для {dish}：",
                "ingredients": "Список ингредиентов для {dish}：",
                "order_saved": "Заказ сохранен！JSON файл：order_{dish}.json，PDF файл：order_{dish}.pdf",
                "generating_recipe": "Генерация рецепта для {dish}，пожалуйста, подождите...",
                "sending_api": "Отправка API запроса...",
                "api_status": "Код статуса API ответа：{code}",
                "api_error": "Ошибка API ответа：{error}",
                "uploaded_photo": "Фото загружено：{filename}",
                "photo_error": "Ошибка отображения фото：{error}",
                "back": "Назад",
                "reselect": "Повторить выбор",
                "loading_url": "Загрузка изображения по URL：{url}",
                "url_success": "Изображение по URL успешно загружено！",
                "url_error": "Ошибка загрузки изображения по URL：{error}",
                "use_default": "Не удалось сгенерировать рецепт AI，используется стандартный рецепт：{error}",
                "recipe_parse_error": "Ошибка парсинга рецепта，используется стандартный рецепт",
                "network_error": "Ошибка сети：{error}",
                "api_format_error": "Неверный формат ответа API：{error}",
                "api_key_error": "Ошибка ключа ответа API：{error}",
                "analyzing_photo": "Анализ фото，пожалуйста, подождите...",
                "photo_recipe": "Рецепт, сгенерированный по фото：",
                "photo_ingredients": "Ингредиенты, распознанные по фото："
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
        
        # 当前选择的菜肴
        self.current_dish = None
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
        # 清除现有按钮
        for widget in self.button_frame.winfo_children():
            widget.destroy()
        
        # 创建菜肴按钮（菜肴名称保持中文，因为是具体的菜名）
        dishes = ["比萨饼", "卷饼", "意大利面"]
        for dish in dishes:
            btn = tk.Button(self.button_frame, text=dish, width=15, height=2, command=lambda d=dish: self.select_dish(d))
            btn.pack(side=tk.LEFT, padx=5)
    
    def show_action_buttons(self):
        # 清除现有按钮
        for widget in self.button_frame.winfo_children():
            widget.destroy()
        
        # 创建操作按钮，使用多语言文本
        actions = [
            (self.texts[self.language]["view_recipe"], "查看食谱"),
            (self.texts[self.language]["view_ingredients"], "查看配料"),
            (self.texts[self.language]["save_order"], "保存订单"),
            (self.texts[self.language]["back_to_dish"], "返回选择菜肴")
        ]
        for display_text, action_key in actions:
            btn = tk.Button(self.button_frame, text=display_text, width=15, height=2, command=lambda a=action_key: self.handle_action(a))
            btn.pack(side=tk.LEFT, padx=5)
    
    def generate_recipe(self, dish):
        try:
            self.add_message("机器人", self.texts[self.language]["generating_recipe"].format(dish=dish))
            
            # 配置API密钥
            dashscope.api_key = DASHSCOPE_API_KEY
            
            self.add_message("机器人", self.texts[self.language]["sending_api"])
            
            # 根据语言选择系统提示和用户请求的语言
            if self.language == "ru":
                system_prompt = "Вы профессиональный повар, пожалуйста, генерируйте детальные рецепты на русском языке, включая список ингредиентов и пошаговые инструкции по приготовлению."
                user_prompt = f"Пожалуйста, сгенерируйте рецепт для {dish} на русском языке, включая список ингредиентов и пошаговые инструкции по приготовлению."
            else:
                system_prompt = "您是一位专业的厨师，请为用户生成详细的食谱，包括配料列表和分步烹饪步骤。"
                user_prompt = f"请生成{dish}的食谱，包括配料列表和分步烹饪步骤。"
            
            # 使用dashscope SDK调用通义千问API
            response = dashscope.Generation.call(
                model="qwen-max",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            # 打印响应内容到控制台以便调试
            print(f"API响应：{response}")
            
            if response.status_code == 200 and response.output.text:
                recipe_text = response.output.text
                self.add_message("机器人", f"AI生成的{dish}食谱：")
                self.add_message("机器人", recipe_text)
            else:
                self.add_message("机器人", f"API响应错误：{response}")
                # 使用默认食谱
                if dish in recipes:
                    return recipes[dish]
                else:
                    # 如果没有默认食谱，返回空食谱
                    return {
                        "ingredients": [],
                        "steps": [],
                        "ai_generated": False
                    }
            
            # 解析AI生成的食谱（简单解析，实际应用中可能需要更复杂的解析）
            ingredients = []
            steps = []
            
            lines = recipe_text.split('\n')
            in_ingredients = False
            in_steps = False
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                if "配料" in line or "材料" in line or "ingredients" in line.lower():
                    in_ingredients = True
                    in_steps = False
                    continue
                elif "步骤" in line or "做法" in line or "steps" in line.lower():
                    in_ingredients = False
                    in_steps = True
                    continue
                
                if in_ingredients:
                    if line.startswith(('-', '*', '•', '1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.', '0.')):
                        ingredients.append(line[2:].strip())
                elif in_steps:
                    if line.startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.', '0.')):
                        steps.append(line)
            
            # 如果解析失败，使用默认食谱
            if not ingredients or not steps:
                self.add_message("机器人", "食谱解析失败，使用默认食谱")
                # 检查默认食谱字典中是否有这个菜肴
                if dish in recipes:
                    return recipes[dish]
                else:
                    # 如果没有，返回一个包含AI生成原始内容的默认食谱
                    return {
                        "ingredients": ["AI生成的食谱无法解析，请查看原始内容"],
                        "steps": [recipe_text],
                        "ai_generated": True
                    }
            
            return {
                "ingredients": ingredients,
                "steps": steps,
                "ai_generated": True
            }
        except requests.exceptions.RequestException as e:
            self.add_message("机器人", f"网络请求失败：{str(e)}")
            if dish in recipes:
                return recipes[dish]
            else:
                # 如果没有默认食谱，返回空食谱
                return {
                    "ingredients": [],
                    "steps": [],
                    "ai_generated": False
                }
        except KeyError as e:
            self.add_message("机器人", f"API响应键错误：{str(e)}")
            if dish in recipes:
                return recipes[dish]
            else:
                # 如果没有默认食谱，返回空食谱
                return {
                    "ingredients": [],
                    "steps": [],
                    "ai_generated": False
                }
        except Exception as e:
            self.add_message("机器人", f"AI生成食谱失败，使用默认食谱：{str(e)}")
            # 打印详细错误信息到控制台以便调试
            import traceback
            traceback.print_exc()
            if dish in recipes:
                return recipes[dish]
            else:
                # 如果没有默认食谱，返回空食谱
                return {
                    "ingredients": [],
                    "steps": [],
                    "ai_generated": False
                }
    
    def select_dish(self, dish):
        self.current_dish = dish
        self.add_message("机器人", self.texts[self.language]["select_dish"].format(dish=dish))
        # 生成食谱
        self.current_recipe = self.generate_recipe(dish)
        self.add_message("机器人", self.texts[self.language]["choose_action"])
        self.show_action_buttons()
    
    def handle_action(self, action):
        if action == "查看食谱":
            self.show_recipe()
        elif action == "查看配料":
            self.show_ingredients()
        elif action == "保存订单":
            self.save_order()
        elif action == "返回选择菜肴":
            self.current_dish = None
            if hasattr(self, 'current_recipe'):
                delattr(self, 'current_recipe')
            self.add_message("机器人", self.texts[self.language]["welcome"])
            self.show_dish_buttons()
    
    def show_recipe(self):
        if hasattr(self, 'current_recipe'):
            # 如果没有current_dish，使用默认名称
            dish_name = self.current_dish if self.current_dish else "未知菜肴"
            self.add_message("机器人", self.texts[self.language]["recipe"].format(dish=dish_name))
            for step in self.current_recipe["steps"]:
                self.add_message("机器人", step)
    
    def show_ingredients(self):
        if hasattr(self, 'current_recipe'):
            # 如果没有current_dish，使用默认名称
            dish_name = self.current_dish if self.current_dish else "未知菜肴"
            self.add_message("机器人", self.texts[self.language]["ingredients"].format(dish=dish_name))
            for ing in self.current_recipe["ingredients"]:
                self.add_message("机器人", f"- {ing}")
    
    def save_order(self):
        if hasattr(self, 'current_recipe'):
            # 如果没有current_dish，使用默认名称
            dish_name = self.current_dish if self.current_dish else "未知菜肴"
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
            pdf_filename = self.generate_pdf(order)
            
            # 根据PDF生成结果显示不同消息
            if pdf_filename:
                # PDF生成成功
                self.add_message("机器人", f"订单已保存！JSON文件：{json_filename}，PDF文件：{pdf_filename}")
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
            
            # 在Mac上尝试加载支持中文的系统字体
            # 尝试加载几个常见的中文字体
            font_paths = [
                '/System/Library/Fonts/STHeiti Light.ttc',  # 黑体 - 这是我们在测试中成功加载的
                '/System/Library/Fonts/PingFang.ttc',      # 苹方字体
                '/Library/Fonts/Songti.ttc',               # 宋体
            ]
            
            font_loaded = False
            font_name = "STHeiti"  # 使用固定的字体名称，避免路径问题
            
            # 尝试注册一个可用的中文字体
            for font_path in font_paths:
                if os.path.exists(font_path):
                    try:
                        # 注册字体，但只使用常规样式，不尝试粗体
                        pdf.add_font('chinese_font', '', font_path, uni=True)
                        font_loaded = True
                        print(f"成功加载字体: {font_path}")
                        break
                    except Exception as e:
                        print(f"加载字体失败 {font_path}: {e}")
                        continue
            
            # 使用加载的中文字体或默认字体
            # 避免使用粗体，因为我们只加载了常规字体
            if font_loaded:
                # 设置标题字体大小
                pdf.set_font('chinese_font', '', 16)
            else:
                # 如果没有加载中文字体，尝试使用默认字体
                print("无法加载中文字体，尝试使用默认字体")
                pdf.set_font('Arial', '', 16)
            
            # 添加标题
            try:
                pdf.cell(0, 10, f"Order: {dish_name}", ln=True, align='C')
            except Exception as e:
                print(f"标题写入错误: {e}")
                # 如果失败，尝试只写入英文部分
                pdf.cell(0, 10, "Order:", ln=True, align='C')
            
            pdf.ln(10)
            
            # 添加AI生成标记
            if order.get("ai_generated", False):
                if font_loaded:
                    pdf.set_font('chinese_font', '', 12)
                else:
                    pdf.set_font('Arial', '', 12)
                try:
                    pdf.cell(0, 10, "(AI Generated Recipe)", ln=True, align='L')
                except:
                    pass
                pdf.ln(5)
            
            # 添加配料列表标题
            if font_loaded:
                # 不使用粗体，只使用常规字体但增大字号
                pdf.set_font('chinese_font', '', 14)
            else:
                pdf.set_font('Arial', '', 14)
            try:
                pdf.cell(0, 10, "配料:", ln=True, align='L')
            except:
                pdf.cell(0, 10, "Ingredients:", ln=True, align='L')
            pdf.ln(5)
            
            # 设置正常字体
            if font_loaded:
                pdf.set_font('chinese_font', '', 12)
            else:
                pdf.set_font('Arial', '', 12)
            
            # 直接添加配料，不做任何修改
            for ing in order["ingredients"]:
                if isinstance(ing, str):
                    try:
                        # 简单的列表格式
                        pdf.cell(5, 8, '', ln=False)
                        pdf.cell(5, 8, '•', ln=False)
                        pdf.multi_cell(0, 8, ing.strip(), ln=True)
                    except Exception as e:
                        print(f"写入配料错误: {e}")
                        try:
                            pdf.cell(0, 8, ing.strip()[:30], ln=True)
                        except:
                            pass
            
            pdf.ln(10)
            
            # 添加步骤标题
            if font_loaded:
                # 不使用粗体，只使用常规字体但增大字号
                pdf.set_font('chinese_font', '', 14)
            else:
                pdf.set_font('Arial', '', 14)
            try:
                pdf.cell(0, 10, "步骤:", ln=True, align='L')
            except:
                pdf.cell(0, 10, "Steps:", ln=True, align='L')
            pdf.ln(5)
            
            # 设置正常字体
            if font_loaded:
                pdf.set_font('chinese_font', '', 12)
            else:
                pdf.set_font('Arial', '', 12)
            
            # 直接添加步骤
            for i, step in enumerate(order["steps"], 1):
                if isinstance(step, str):
                    try:
                        step_text = f"{i}. {step.strip()}"
                        pdf.multi_cell(0, 8, step_text, ln=True)
                    except Exception as e:
                        print(f"写入步骤错误: {e}")
                        try:
                            pdf.cell(0, 8, step.strip()[:50], ln=True)
                        except:
                            pass
                pdf.ln(3)
            
            # 保存PDF
            pdf.output(safe_filename)
            print(f"PDF文件已成功生成：{safe_filename}")
            return safe_filename
        except Exception as e:
            print(f"PDF生成错误: {e}")
            # 使用纯文本文件作为可靠的回退方案
            safe_filename = f"order_{dish_name.replace(' ', '_')}.txt"
            safe_filename = ''.join(c for c in safe_filename if c.isalnum() or c in ('_', '.'))
            
            try:
                with open(safe_filename, 'w', encoding='utf-8') as f:
                    f.write(f"Order: {dish_name}\n\n")
                    if order.get("ai_generated", False):
                        f.write("(AI Generated Recipe)\n\n")
                    f.write("Ingredients:\n")
                    for ing in order["ingredients"]:
                        if isinstance(ing, str):
                            f.write(f"- {ing}\n")
                    f.write("\nSteps:\n")
                    for step in order["steps"]:
                        if isinstance(step, str):
                            f.write(f"{step}\n\n")
                print(f"已创建文本文件作为回退：{safe_filename}")
                return safe_filename
            except Exception as e2:
                print(f"文本文件生成失败: {e2}")
                return None
            
            # 方法2：使用fpdf2的简化版本，完全避免中文字符
            from fpdf import FPDF
            
            pdf = FPDF()
            pdf.add_page()
            
            # 使用默认字体，确保所有文本都是ASCII
            pdf.set_font("helvetica", "B", 16)
            
            # 安全处理所有文本
            dish_name = order['dish'] if isinstance(order['dish'], str) else "Unknown Dish"
            safe_dish = dish_name.encode('ascii', 'ignore').decode('ascii')
            pdf.cell(0, 10, f"Order: {safe_dish}", ln=True, align="C")
            
            # 添加AI生成标记
            if order.get("ai_generated", False):
                pdf.set_font("helvetica", "I", 10)
                pdf.cell(0, 8, "(AI Generated Recipe)", ln=True, align="C")
            
            pdf.ln(10)
            
            # 添加配料列表（保留JSON中的原始格式）
            pdf.set_font("helvetica", "B", 12)
            pdf.cell(0, 10, "Ingredients:", ln=True)
            pdf.set_font("helvetica", "", 12)
            
            for ing in order["ingredients"]:
                try:
                    if isinstance(ing, str):
                        # 保留原始内容，不添加额外的格式
                        safe_ing = ing.encode('ascii', 'ignore').decode('ascii')[:50]
                        pdf.cell(0, 8, f"  {safe_ing}", ln=True)  # 只添加适当的缩进
                except:
                    pdf.cell(0, 8, "  [Ingredient]", ln=True)
            
            pdf.ln(10)
            
            # 添加步骤（保留JSON中的原始格式）
            pdf.set_font("helvetica", "B", 12)
            pdf.cell(0, 10, "Recipe Steps:", ln=True)
            pdf.set_font("helvetica", "", 12)
            
            for step in order["steps"]:
                try:
                    if isinstance(step, str):
                        # 保留原始步骤内容，不添加额外的数字前缀
                        safe_step = step.encode('ascii', 'ignore').decode('ascii')[:200]
                        pdf.multi_cell(0, 8, safe_step)
                except:
                    pdf.multi_cell(0, 8, "[Step]")
            
            # 生成安全的文件名
            safe_filename = f"order_{safe_dish.replace(' ', '_')}.pdf"
            safe_filename = ''.join(c for c in safe_filename if c.isalnum() or c in ('_', '.'))
            
            # 保存PDF文件
            pdf.output(safe_filename)
            self.add_message("机器人", f"PDF文件已成功生成（ASCII版本）：{safe_filename}")
            return safe_filename
        except Exception as e:
            # 更详细的错误处理和日志记录
            error_msg = f"PDF生成失败：{str(e)}"
            self.add_message("机器人", error_msg)
            print(f"PDF生成错误详情：{error_msg}")
            import traceback
            traceback.print_exc()
            return None
    
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
                        
                        if "配料" in line or "材料" in line or "ingredients" in line.lower():
                            in_ingredients = True
                            in_steps = False
                            continue
                        elif "步骤" in line or "做法" in line or "steps" in line.lower():
                            in_ingredients = False
                            in_steps = True
                            continue
                        
                        if in_ingredients:
                            if line.startswith(('-', '*', '•', '1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.', '0.')):
                                ingredients.append(line[2:].strip())
                        elif in_steps:
                            if line.startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.', '0.')):
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
        message = self.input_entry.get().strip()
        if message:
            self.add_message("您", message)
            self.input_entry.delete(0, tk.END)
            
            # 简单的文本命令处理
            if message == self.texts[self.language]["back"] or message == self.texts[self.language]["reselect"]:
                self.current_dish = None
                if hasattr(self, 'current_recipe'):
                    delattr(self, 'current_recipe')
                self.add_message("机器人", self.texts[self.language]["welcome"])
                self.show_dish_buttons()
            elif message.startswith("http"):
                # 处理URL图片
                self.add_message("机器人", self.texts[self.language]["loading_url"].format(url=message))
                try:
                    response = requests.get(message)
                    img = Image.open(io.BytesIO(response.content))
                    img.thumbnail((300, 200))
                    photo = ImageTk.PhotoImage(img)
                    self.image_label.config(image=photo)
                    self.image_label.image = photo
                    self.add_message("机器人", self.texts[self.language]["url_success"])
                    # 自动分析URL图片
                    # 注意：这里需要先保存URL图片到本地，然后再分析
                    temp_path = f"temp_{os.path.basename(message.split('/')[-1])}"
                    with open(temp_path, "wb") as f:
                        f.write(response.content)
                    self.analyze_photo(temp_path)
                    # 删除临时文件
                    os.remove(temp_path)
                except Exception as e:
                    self.add_message("机器人", self.texts[self.language]["url_error"].format(error=str(e)))
            else:
                # 处理其他文本输入，包括菜名
                self.add_message("机器人", f"您输入了：{message}")
                # 如果是菜名，生成食谱
                self.current_dish = message
                self.current_recipe = self.generate_recipe(message)
                # 显示操作按钮
                self.add_message("机器人", self.texts[self.language]["choose_action"])
                self.show_action_buttons()

if __name__ == "__main__":
    root = tk.Tk()
    chatbot = ChatBot(root)
    root.mainloop()
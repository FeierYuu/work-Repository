import dashscope

# 通义千问API配置
DASHSCOPE_API_KEY = "sk-9eb7698340df49149f3827bf35a16471"

def test_qwen_api():
    try:
        print("正在测试通义千问API连接...")
        
        # 配置API密钥
        dashscope.api_key = DASHSCOPE_API_KEY
        
        # 调用通义千问API
        response = dashscope.Generation.call(
            model="qwen-max",
            messages=[
                {"role": "system", "content": "您是一位专业的厨师，请为用户生成详细的食谱，包括配料列表和分步烹饪步骤。"},
                {"role": "user", "content": "请生成简单的番茄炒蛋食谱，包括配料列表和分步烹饪步骤。"}
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        print(f"API响应：{response}")
        
        if response.status_code == 200 and response.output.text:
            recipe_text = response.output.text
            print(f"\n生成的食谱：")
            print(recipe_text)
            return True
        else:
            print(f"API请求失败：{response}")
            return False
    except Exception as e:
        print(f"API请求失败：{str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_qwen_api()
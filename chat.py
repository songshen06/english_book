from openai import OpenAI
import json
import re

client = OpenAI(
    base_url = 'http://localhost:11434/v1',
    api_key='ollama', # required, but unused
)
'''
def generate_answer(prompt):
    response = client.chat.completions.create(
    model="mistral:v0.3",
    messages=[
        {"role": "user", "content": prompt},
        {'role':'system', 'content':'你是一个英语老师，学生的回答会想你确认英文翻译的准确性。'},
    ]
    )
    message_content = response.choices[0].message.content
    print("原始输出:", message_content)  # 输出模型的回答，用于调试
    return message_content
'''
def generate_answer(english_word, chinese_translation):
    prompt = f"""
    You are an elementary school English teacher. Your task is to check if the provided Chinese translation of an English word is correct. If it is correct, mark it as "对" (correct). If it is incorrect, mark it as "错" (wrong). Additionally, provide a simple explanation of the word in Chinese along with an example sentence in English. Format the output strictly as a JSON object with two keys: "word" and "explanation".

    Input:
    - English word: {english_word}
    - Chinese translation: {chinese_translation}

    Output (strictly formatted as JSON):

    {{
      "Result": "对" or "错",
      "explanation": "An explanation of the word in Chinese"
      "sentence": "A simple example sentence using the word."
    }}
    """
    response = client.chat.completions.create(
        model="gemma:latest",
        messages=[
            {"role": "user", "content": prompt},
            {'role': 'system', 'content': 'You are an elementary school English teacher and can speak English and Chinese.'},
        ]
    )
    message_content = response.choices[0].message.content.strip()
    print("原始输出:", message_content)  # 输出模型的回答，用于调试
    return message_content

def extract_json_from_text(text):
    # 使用正则表达式匹配三个单引号之间的内容
    match = re.search(r"\{.*?\}", text, re.DOTALL)
    if match:
        return match.group(0)
    else:
        return None  # 如果没有匹配到有效内容，返回None

'''
english_word = "west"
chinese_word = "不知道"

prompt = f"""
这个英文单词“{english_word}”的翻译是“{chinese_word}”吗？
将你的响应格式化为以 {english_word}和 “答案解释”为键的 JSON 对象。
{english_word} 键，如果是，请使用 “正确” 作为值。如果不是，请使用“错误”为值。
“答案解释”键的值，是你判断的理由。
注意只需要输出JSON 对象。
""" 
response = generate_answer(prompt)

# 从响应中提取JSON字符串
json_string = extract_json_from_text(response)
if json_string:
    # 尝试解析JSON，捕捉可能的解析错误
    try:
        data = json.loads(json_string)
        print(data)
        print(f"答案：{data[english_word]}")
        print(f"答案解释：{data['答案解释']}")
    except json.JSONDecodeError as e:
        print("解析错误：", e)
        print("提取的内容不是有效的JSON格式。")
else:
    print("没有找到有效的JSON内容。")'''
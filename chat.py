from openai import OpenAI
import json
import re

client = OpenAI(
    base_url = 'http://localhost:11434/v1',
    api_key='ollama', # required, but unused
)

def generate_answer(english_word, chinese_translation):
    prompt = f"""
    You are an elementary school English teacher. Your task is to help young students (around 10 years old) learn English words. 
    1. Check if the provided Chinese translation of an English word is correct. If it is correct, mark it as "对" (correct). If it is incorrect, mark it as "错" (wrong).
    2. Provide a simple tip to help the student remember this word. This should be easy to understand and age-appropriate. Use both English and Chinese in the explanation to ensure the student can understand.
    3. Provide a simple example sentence using the word.

    Here are some examples:

    Example 1:
    English word: apple
    Chinese translation: 苹果
    Output:
    {{
      "Result": "对",
      "Explanation": "Apple 是一种水果，很常见，颜色通常是红色的。",
      "Sentence": "I like to eat an apple every day."
    }}

    Example 2:
    English word: banana
    Chinese translation: 香蕉
    Output:
    {{
      "Result": "对",
      "Explanation": "Banana 是一种长长的黄色水果，猴子喜欢吃。",
      "Sentence": "She eats a banana for breakfast."
    }}

    Example 3:
    English word: table
    Chinese translation: 桌子
    Output:
    {{
      "Result": "对",
      "Explanation": "Table 是你用来放东西的家具，通常有四条腿。",
      "Sentence": "The book is on the table."
    }}

    Now, based on the input provided, generate the output in the same format.

    Input:
    - English word: {english_word}
    - Chinese translation: {chinese_translation}

    Output (strictly formatted as JSON):

    {{
      "Result": "对" or "错",
      "Explanation": "A simple memory aid in mixed English and Chinese",
      "Sentence": "A simple example sentence using the word."
    }}
    """
    response = client.chat.completions.create(
        #model="gemma:latest",
        model="qwen2:latest",
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


import os
import requests

# --- Настройки бота ---
FAQ_FILE = "faq.txt"

# --- Настройки ИИ Прокси ---
# Переключи на True, если хочешь, чтобы при ответе "не знаю" бот шел к ИИ
USE_AI_PROXY = True 
AI_PROXY_URL = "https://openrouter.ai/api/v1/chat/completions" # Замени на свой URL прокси
AI_API_KEY = "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" 
AI_MODEL = "nvidia/nemotron-3-ultra-550b-a55b:free"

def load_faq(filename):
    """Загружает базу вопросов и ответов из файла."""
    faq = []
    try:
        with open(filename, "r", encoding="utf-8") as f:
            for line in f:
                if "|" in line:
                    keys, answer = line.split("|", 1)
                    # Очищаем пробелы и переводим ключи в нижний регистр
                    keywords = [k.strip().lower() for k in keys.split(",")]
                    faq.append({"keywords": keywords, "answer": answer.strip()})
    except FileNotFoundError:
        print(f"Ошибка: Файл {filename} не найден. Создайте его.")
    return faq

def ask_ai(question):
    """Отправляет запрос к ИИ через прокси."""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {AI_API_KEY}"
    }
    payload = {
        "model": AI_MODEL,
        "messages": [{"role": "user", "content": question}],
        "max_tokens": 150
    }
    
    try:
        response = requests.post(AI_PROXY_URL, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"[Ошибка ИИ-прокси: {e}]"

def get_answer(question, faq):
    """Ищет совпадения по ключевым словам."""
    question_lower = question.lower()
    
    for item in faq:
        for keyword in item["keywords"]:
            if keyword in question_lower:
                return item["answer"]
    return None

def main():
    faq = load_faq(FAQ_FILE)
    if not faq:
        return

    print("🤖 Бот-помощник запущен! (Напиши 'выход' для завершения)")
    
    while True:
        user_input = input("\nТы: ")
        
        if user_input.lower() in ['выход', 'exit', 'quit']:
            print("Бот: Удачи на репетиции!")
            break
            
        # Ищем ответ в локальной базе
        answer = get_answer(user_input, faq)
        
        if answer:
            print(f"Бот: {answer}")
        else:
            # Если не нашли, проверяем, подключен ли ИИ
            if USE_AI_PROXY:
                print("Бот: 🤔 Локально не нашел, спрашиваю у ИИ...")
                ai_answer = ask_ai(user_input)
                print(f"Бот (ИИ): {ai_answer}")
            else:
                print("Бот: Я не знаю ответа на этот вопрос. Спроси про время, команду, треки, сдачу или призы.")

if __name__ == "__main__":
    main()

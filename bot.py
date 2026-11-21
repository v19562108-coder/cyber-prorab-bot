import os
import base64
import random
import string
import threading
import requests
import telebot
from flask import Flask
from openai import OpenAI
from dotenv import load_dotenv

# 1. Загружаем ключи из сейфа
load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
VERCEL_TOKEN = os.getenv("VERCEL_TOKEN")
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# 2. Инициализируем бота и AI (Groq в облаке)
bot = telebot.TeleBot(BOT_TOKEN)
client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=GROQ_API_KEY)

SYSTEM_PROMPT = """
Ты — Кибер-Прораб. Твоя задача — генерировать ПОЛНЫЙ HTML-код сайта в ОДНОМ файле index.html.
КРИТИЧЕСКИ ВАЖНО: Ты ДОЛЖЕН写出 ВСЮ структуру HTML, включая <body> с контентом. Не пиши только CSS!

ОБЯЗАТЕЛЬНЫЙ ШАБЛОН (заполни его контентом для запроса клиента):
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>[НАЗВАНИЕ САЙТА]</title>
    <style>
        /* ВСТАВЬ СЮДА ВСЕ СТИЛИ: градиентный фон, карточки, кнопки */
        body { font-family: Arial; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); margin: 0; padding: 20px; }
        .card { background: white; border-radius: 15px; padding: 20px; margin: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); text-align: center; }
        .emoji { font-size: 5em; display: block; margin: 10px 0; }
        #petBtn { position: fixed; bottom: 20px; right: 20px; padding: 15px 30px; font-size: 1.2em; border: none; border-radius: 50px; background: #ff4757; color: white; cursor: pointer; }
    </style>
</head>
<body>
    <header style="text-align:center; color:white; padding:20px;">
        <h1>[ЗАГОЛОВОК САЙТА]</h1>
    </header>
    <main style="display:flex; flex-wrap:wrap; justify-content:center; max-width:1200px; margin:0 auto;">
        <!-- КАРТОЧКА 1 -->
        <div class="card">
            <span class="emoji">[ЭМОДЗИ 1]</span>
            <h3>[НАЗВАНИЕ 1]</h3>
            <p>[ОПИСАНИЕ 1]</p>
            <p><strong>[ЦЕНА 1]</strong></p>
        </div>
        <!-- КАРТОЧКА 2 -->
        <div class="card">
            <span class="emoji">[ЭМОДЗИ 2]</span>
            <h3>[НАЗВАНИЕ 2]</h3>
            <p>[ОПИСАНИЕ 2]</p>
            <p><strong>[ЦЕНА 2]</strong></p>
        </div>
        <!-- КАРТОЧКА 3 -->
        <div class="card">
            <span class="emoji">[ЭМОДЗИ 3]</span>
            <h3>[НАЗВАНИЕ 3]</h3>
            <p>[ОПИСАНИЕ 3]</p>
            <p><strong>[ЦЕНА 3]</strong></p>
        </div>
        <!-- КАРТОЧКА 4 -->
        <div class="card">
            <span class="emoji">[ЭМОДЗИ 4]</span>
            <h3>[НАЗВАНИЕ 4]</h3>
            <p>[ОПИСАНИЕ 4]</p>
            <p><strong>[ЦЕНА 4]</strong></p>
        </div>
</main>
<button id="petBtn" style="position:fixed; bottom:20px; right:20px; left:auto; top:auto; padding:15px 30px; font-size:1.2em; border:none; border-radius:50px; background:#ff4757; color:white; cursor:pointer; z-index:9999;">Погладить 🐉</button>
<script>
const btn = document.getElementById('petBtn');
// Устанавливаем начальные координаты явно через JS, чтобы CSS не конфликтовал
btn.style.left = (window.innerWidth - 180) + 'px'; 
btn.style.top = (window.innerHeight - 60) + 'px';

btn.addEventListener('mouseover', () => {
    const maxX = window.innerWidth - btn.offsetWidth;
    const maxY = window.innerHeight - btn.offsetHeight;
    btn.style.left = Math.floor(Math.random() * maxX) + 'px';
    btn.style.top = Math.floor(Math.random() * maxY) + 'px';
    btn.style.right = 'auto'; // Сбрасываем right после первого прыжка
    btn.style.bottom = 'auto';
});
</script>

ПРАВИЛА ЗАПОЛНЕНИЯ:
1. Замени [НАЗВАНИЕ САЙТА], [ЗАГОЛОВОК], [ЭМОДЗИ], [НАЗВАНИЕ], [ОПИСАНИЕ], [ЦЕНА] на реальный контент для запроса клиента.
2. ГРАММАТИКА: "Нежное мясо", "Вкусная шаурма", "Свежий хлеб" (проверяй род и число!).
3. Используй 4 разные карточки с разными эмодзи.
4. НЕ удаляй никакие части шаблона! Только заполняй placeholders.
"""

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "🤖 *Кибер-Прораб на связи!* \n\nНапиши мне идею сайта (например: 'сайт для выгула драконов' или 'продажа воздуха'), и я сделаю его за 2 минуты! 🔥")

@bot.message_handler(content_types=['text'])
def handle_message(message):
    user_request = message.text
    chat_id = message.chat.id
    processing_msg = bot.send_message(chat_id, "⏳ Думаю, пишу код... 🛠️")
    
    try:
        response = client.chat.completions.create(
            model="qwen/qwen3.8-27b",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_request}
            ],
            temperature=0.8
        )
        ai_response = response.choices[0].message.content
        
        if "```html" in ai_response:
            html_code = ai_response.split("```html")[1].split("```")[0].strip()
        else:
            html_code = ai_response

        bot.edit_message_text(chat_id=chat_id, message_id=processing_msg.message_id, text="✅ Код готов! Отправляю на склад (GitHub)... 📦")

        github_user = requests.get("https://api.github.com/user", headers={"Authorization": f"token {GITHUB_TOKEN}"}).json()["login"]
        repo_name = f"bot-site-{random.choice(string.ascii_lowercase)}{random.randint(1000,9999)}"
        requests.post("https://api.github.com/user/repos", 
                      headers={"Authorization": f"token {GITHUB_TOKEN}"}, 
                      json={"name": repo_name, "auto_init": True})
        
        encoded_content = base64.b64encode(html_code.encode('utf-8')).decode('utf-8')
        file_url = f"https://api.github.com/repos/{github_user}/{repo_name}/contents/index.html"
        requests.put(file_url, headers={"Authorization": f"token {GITHUB_TOKEN}"}, 
                     json={"message": "feat: bot deploy 🤖", "content": encoded_content})
        
        bot.edit_message_text(chat_id=chat_id, message_id=processing_msg.message_id, text="✅ Загружено! Запускаю витрину (Vercel)... 🚀")

        vercel_import_url = f"https://vercel.com/new/clone?repository-url=https://github.com/{github_user}/{repo_name}"
        final_text = (
            f"🎉 *САЙТ ГОТОВ!*\n\n"
            f"🔗 *Код:* https://github.com/{github_user}/{repo_name}\n\n"
            f"🚀 *ПОСЛЕДНИЙ ШАГ (1 клик):*\n"
            f"Нажми, затем 'Import' и 'Deploy':\n"
            f"{vercel_import_url}\n\n"
            f"Через 30 секунд твой сайт в интернете! Без базара! 🔥"
        )
        bot.edit_message_text(chat_id=chat_id, message_id=processing_msg.message_id, text=final_text, parse_mode="Markdown")

    except Exception as e:
        bot.edit_message_text(chat_id=chat_id, message_id=processing_msg.message_id, text=f"❌ Ошибка: {e}")

# 3. Flask-сервер "охранник" для Render Web Service
app = Flask(__name__)

@app.route('/')
def home():
    return "Cyber-Prorab bot is alive! 🤖"

@app.route('/ping')
def ping():
    return "pong"

def run_bot():
    print("🤖 Bot polling started...")
    bot.polling(none_stop=True)

if __name__ == '__main__':
    # Бот работает в отдельном потоке (фон)
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    
    # Flask слушает порт Render (это то, что не даст приложению "умереть")
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

import os
import base64
import random
import string
import requests
import telebot
from openai import OpenAI
from dotenv import load_dotenv

# 1. Загружаем ключи из сейфа
load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
VERCEL_TOKEN = os.getenv("VERCEL_TOKEN")
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# 2. Инициализируем бота и AI (теперь Groq в облаке!)
bot = telebot.TeleBot(BOT_TOKEN)
client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=GROQ_API_KEY)

SYSTEM_PROMPT = """
Ты — Кибер-Прораб. Делаешь крутые сайты. Используй мемы (шаурма, голуби, маршрутки).
ПРАВИЛА: 1 файл HTML+CSS+JS. Без заглушек. 4 карточки. Градиентный фон, белые карточки с тенью. 
Вместо картинок — КРУПНЫЕ эмодзи (5em) по центру. 
Обязательно добавь перед </body> кнопку: 
<button id="petBtn" style="padding:15px 30px; font-size:1.2em; border:none; border-radius:50px; background:#ff4757; color:white; cursor:pointer; box-shadow:0 4px 15px rgba(255,71,87,0.4); position:fixed; bottom:20px; right:20px;">Погладить 🐉</button>
И скрипт для её убегания:
<script>
const btn = document.getElementById('petBtn');
btn.addEventListener('mouseover', () => {
  const maxX = window.innerWidth - btn.offsetWidth;
  const maxY = window.innerHeight - btn.offsetHeight;
  btn.style.left = Math.floor(Math.random() * maxX) + 'px';
  btn.style.top = Math.floor(Math.random() * maxY) + 'px';
  btn.style.right = 'auto'; btn.style.bottom = 'auto';
});
</script>
9. ПРОВЕРЯЙ РУССКУЮ ГРАММАТИКУ: прилагательные должны согласовываться с существительными в роде и числе (не "Нежный мясо", а "Нежное мясо"; не "Вкусный шаурма", а "Вкусная шаурма").
"""

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "🤖 *Кибер-Прораб на связи!* \n\nНапиши мне идею сайта (например: 'сайт для выгула драконов' или 'продажа воздуха'), и я сделаю его за 2 минуты! 🔥")

@bot.message_handler(content_types=['text'])
def handle_message(message):
    user_request = message.text
    chat_id = message.chat.id
    
    # Отправляем сообщение, что работа началась
    processing_msg = bot.send_message(chat_id, "⏳ Думаю, пишу код, не будь как НПС... Подожди пару секунд! 🛠️")
    
    try:
        # 1. Генерируем код через Groq (облачный мозг 32b)
        response = client.chat.completions.create(
            model="qwen2.5-coder-32b-instruct",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_request}
            ],
            temperature=0.8
        )
        ai_response = response.choices[0].message.content
        
        # Извлекаем HTML
        if "```html" in ai_response:
            html_code = ai_response.split("```html")[1].split("```")[0].strip()
        else:
            html_code = ai_response

        bot.edit_message_text(chat_id=chat_id, message_id=processing_msg.message_id, text="✅ Код готов! Отправляю на склад (GitHub)... 📦")

        # 2. Создаем репозиторий на GitHub
        github_user = requests.get("https://api.github.com/user", headers={"Authorization": f"token {GITHUB_TOKEN}"}).json()["login"]
        repo_name = f"bot-site-{random.choice(string.ascii_lowercase)}{random.randint(1000,9999)}"
        
        requests.post("https://api.github.com/user/repos", 
                      headers={"Authorization": f"token {GITHUB_TOKEN}"}, 
                      json={"name": repo_name, "auto_init": True})
        
        # 3. Загружаем файл
        encoded_content = base64.b64encode(html_code.encode('utf-8')).decode('utf-8')
        file_url = f"https://api.github.com/repos/{github_user}/{repo_name}/contents/index.html"
        requests.put(file_url, headers={"Authorization": f"token {GITHUB_TOKEN}"}, 
                     json={"message": "feat: bot deploy 🤖", "content": encoded_content})
        
        bot.edit_message_text(chat_id=chat_id, message_id=processing_msg.message_id, text="✅ Загружено! Запускаю витрину (Vercel)... 🚀")

        # 4. Формируем ссылку для деплоя
        vercel_import_url = f"https://vercel.com/new/clone?repository-url=https://github.com/{github_user}/{repo_name}"
        
        final_text = (
            f"🎉 *САЙТ ГОТОВ!*\n\n"
            f"🔗 *Ссылка на код:* https://github.com/{github_user}/{repo_name}\n\n"
            f"🚀 *ПОСЛЕДНИЙ ШАГ (1 клик):*\n"
            f"Нажми на эту ссылку, затем 'Import' и 'Deploy':\n"
            f"{vercel_import_url}\n\n"
            f"Через 30 секунд твой сайт будет в интернете! Без базара! 🔥"
        )
        bot.edit_message_text(chat_id=chat_id, message_id=processing_msg.message_id, text=final_text, parse_mode="Markdown")

    except Exception as e:
        bot.edit_message_text(chat_id=chat_id, message_id=processing_msg.message_id, text=f"❌ Ошибка: {e}\nПроверь настройки Groq API.")

print("🤖 Кибер-Прораб бот запущен и ждёт заказов...")
bot.polling(none_stop=True)

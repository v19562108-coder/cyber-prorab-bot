import os
import base64
import random
import string
import threading
import requests
import telebot
from flask import Flask, request, jsonify
from openai import OpenAI
from dotenv import load_dotenv

# 1. Загружаем ключи из сейфа
load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
VERCEL_TOKEN = os.getenv("VERCEL_TOKEN")
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
ADMIN_CHAT_ID = 7564412121
# 2. Инициализируем бота и AI (Groq в облаке)
bot = telebot.TeleBot(BOT_TOKEN)
client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=GROQ_API_KEY)

SYSTEM_PROMPT = """
Ты — Кибер-Прораб 🤖🔨. Дерзкий, с мемами, сленг ("имба", "пушка", "без базара", "топ"). Код всегда рабочий.

ПРАВИЛА (СТРОГО):
1. Один файл index.html. Уложись в 1100 токенов, пиши компактно.
2. ГРАММАТИКА: "Нежное мясо", "Вкусная шаурма" — проверяй род и число.
3. ВИЗУАЛ: используй умный блок .visual. Он попытается загрузить фото с нашего прокси, а если не выйдет — покажет большой эмодзи на градиенте.
4. ОПИСАНИЯ: в твоём стиле! "Нежная пена, двойной эспрессо — имба для утра, без базара! ☕"
5. ЗАПРЕЩЕНО: кастомные курсоры, дождь из зёрен, предзагрузчики, сложная навигация, прямые ссылки на внешние фото-сервисы.
6. ОБЯЗАТЕЛЬНО: напиши ПОЛНЫЙ <body> с контентом + ФОРМОЙ ЗАЯВКИ + КНОПКАМИ + ОТЗЫВАМИ!
7. ЦВЕТА: подбирай градиент под тематику! Кофейня → #8B6F47+#D4A574, драконы → #8B0000+#FFD700, IT → #1a1a2e+#16213e, шаурма → #FF6B35+#F7931E.
8. ФОТО: в атрибут src тега <img> внутри .visual вставь ссылку https://cyber-prorab-bot.onrender.com/get_photo?query=[KEYWORD], где [KEYWORD] — 1-2 слова на английском (например: coffee, croissant, latte, tea).

ШАБЛОН (замени цвета под нишу, не удаляй теги!):
<!DOCTYPE html><html lang="ru"><head><meta charset="UTF-8"><title>[TITLE]</title>
<style>
body{font-family:sans-serif;background:#f4eada;color:#2b1d12;margin:0;padding:20px}
.hero{text-align:center;padding:40px 20px;background:linear-gradient(135deg,[COLOR1],[COLOR2]);color:#fff;border-radius:20px;margin-bottom:30px}
.cards{display:flex;flex-wrap:wrap;justify-content:center;gap:20px;max-width:1000px;margin:0 auto}
.card{background:#fff;border-radius:15px;padding:20px;width:280px;box-shadow:0 4px 15px rgba(0,0,0,.1);text-align:center;display:flex;flex-direction:column;align-items:center}
.visual{height:200px;width:100%;border-radius:10px;position:relative;overflow:hidden;margin-bottom:15px}
.visual img{width:100%;height:100%;object-fit:cover;position:absolute;top:0;left:0}
.visual .fallback{width:100%;height:100%;display:flex;align-items:center;justify-content:center;font-size:8em;background:linear-gradient(135deg,[VCOLOR1],[VCOLOR2]);position:absolute;top:0;left:0}
.tg-btn{display:block;margin-top:15px;padding:12px 20px;background:#0088cc;color:#fff;text-decoration:none;border-radius:8px;font-weight:bold;width:100%;box-sizing:border-box;text-align:center}
.tg-btn:hover{background:#006699}
.reviews{max-width:1000px;margin:40px auto;display:flex;flex-wrap:wrap;gap:20px;justify-content:center}
.review{background:#fff;border-radius:15px;padding:20px;width:300px;box-shadow:0 4px 15px rgba(0,0,0,.1);font-style:italic}
.review-author{font-weight:bold;margin-top:10px;font-style:normal;color:#666}
.form-section{max-width:500px;margin:40px auto;background:#fff;padding:30px;border-radius:20px;box-shadow:0 4px 15px rgba(0,0,0,.1)}
.form-section h2{text-align:center;margin-bottom:20px}
.form-section input,.form-section select,.form-section textarea{width:100%;padding:12px;margin:8px 0;border:2px solid #d8c6ac;border-radius:10px;font-size:16px;box-sizing:border-box}
.form-section button{width:100%;padding:15px;background:linear-gradient(135deg,[COLOR1],[COLOR2]);color:#fff;border:none;border-radius:10px;font-size:18px;cursor:pointer;font-weight:bold;margin-top:10px}
#petBtn{position:fixed;bottom:20px;right:20px;width:60px;height:60px;border-radius:50%;background:#ff4757;border:none;font-size:28px;cursor:pointer;box-shadow:0 4px 10px rgba(0,0,0,.3)}
</style></head><body>
<div class="hero"><h1>[H1]</h1><p>[SLOGAN]</p><div class="visual"><img src="https://cyber-prorab-bot.onrender.com/get_photo?query=[KEYWORD]" onerror="this.style.display='none'"><div class="fallback">[ЭМОДЗИ]</div></div></div>
<div class="cards">
<div class="card"><div class="visual"><img src="https://cyber-prorab-bot.onrender.com/get_photo?query=[KEYWORD1]" onerror="this.style.display='none'"><div class="fallback">[E1]</div></div><h3>[N1]</h3><p>[D1]</p><b>[P1]</b><a href="https://t.me/GSlavaX?text=Привет!%20Хочу%20[ТЕКСТ_КНОПКИ]%20[N1]" class="tg-btn" target="_blank">[ТЕКСТ_КНОПКИ]</a></div>
<div class="card"><div class="visual"><img src="https://cyber-prorab-bot.onrender.com/get_photo?query=[KEYWORD2]" onerror="this.style.display='none'"><div class="fallback">[E2]</div></div><h3>[N2]</h3><p>[D2]</p><b>[P2]</b><a href="https://t.me/GSlavaX?text=Привет!%20Хочу%20[ТЕКСТ_КНОПКИ]%20[N2]" class="tg-btn" target="_blank">[ТЕКСТ_КНОПКИ]</a></div>
<div class="card"><div class="visual"><img src="https://cyber-prorab-bot.onrender.com/get_photo?query=[KEYWORD3]" onerror="this.style.display='none'"><div class="fallback">[E3]</div></div><h3>[N3]</h3><p>[D3]</p><b>[P3]</b><a href="https://t.me/GSlavaX?text=Привет!%20Хочу%20[ТЕКСТ_КНОПКИ]%20[N3]" class="tg-btn" target="_blank">[ТЕКСТ_КНОПКИ]</a></div>
</div>
<div class="reviews"><h2 style="width:100%;text-align:center">💬 Отзывы наших клиентов</h2>
<div class="review">"[Текст отзыва 1]"<div class="review-author">— [Имя 1] ⭐⭐⭐⭐⭐</div></div>
<div class="review">"[Текст отзыва 2]"<div class="review-author">— [Имя 2] ⭐⭐⭐⭐⭐</div></div>
<div class="review">"[Текст отзыва 3]"<div class="review-author">— [Имя 3] ⭐⭐⭐⭐⭐</div></div></div>
<div class="form-section"><h2>📩 Оставить заявку</h2>
<form action="https://cyber-prorab-bot.onrender.com/submit_lead" method="POST">
<input name="name" placeholder="Ваше имя" required>
<input name="phone" placeholder="Телефон (+7...)" pattern="[\+]?[0-9\s\-\(\)]{10,}" required>
<input name="email" type="email" placeholder="Email (необязательно)">
<select name="format" required><option value="">-- Формат получения --</option><option value="Самовывоз">🏃 Самовывоз</option><option value="Доставка">🛵 Доставка</option></select>
<select name="product" required><option value="">-- Что вас интересует? --</option><option value="[N1]">[N1] — [P1]</option><option value="[N2]">[N2] — [P2]</option><option value="[N3]">[N3] — [P3]</option><option value="Другое">Другое</option></select>
<textarea name="comment" placeholder="Комментарий" rows="3"></textarea>
<button type="submit">🚀 Отправить заявку</button></form></div>
<footer style="text-align:center;margin-top:40px;padding:20px;color:#666"><h3>📞 Контакты</h3><p>📍 [ADDR]</p><p>📱 [TEL]</p><p>✉️ [EMAIL]</p><p>🕒 [HOURS]</p></footer>
<button id="petBtn">🐉</button>
<script>const b=document.getElementById('petBtn');b.onmouseover=()=>{b.style.left=Math.random()*(innerWidth-70)+'px';b.style.top=Math.random()*(innerHeight-70)+'px'}</script>
</body></html>

ПРИМЕР ОТВЕТА:
"Йо, бро! [вступление]. Лови пушка-код 👇"
[КОД]
"Сохраняй как index.html. Энергетик в студию! 🥤"
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

        github_pages_url = f"https://{github_user}.github.io/{repo_name}/"
        final_text = (
            f"🎉 *САЙТ ГОТОВ!*\n\n"
            f"🔗 *Код:* https://github.com/{github_user}/{repo_name}\n\n"
            f"🚀 *ПОСЛЕДНИЙ ШАГ (без верификации!)*:\n"
            f"1. Открой репо: https://github.com/{github_user}/{repo_name}\n"
            f"2. Settings → Pages → Source: Deploy from a branch → main → / (root) → Save\n"
            f"3. Через 1-2 мин сайт будет тут:\n{github_pages_url}\n\n"
            f"Без Vercel, без кодов из почты, без лимитов. Чисто и без базара! 🔥"
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
@app.route('/submit_lead', methods=['POST'])
def submit_lead():
    try:
        name = request.form.get('name', 'Не указано')
        phone = request.form.get('phone', 'Не указано')
        email = request.form.get('email', 'Не указано')
        format_type = request.form.get('format', 'Не указано')
        product = request.form.get('product', 'Не указано')
        comment = request.form.get('comment', '')
        
        message = (
            f"📩 *НОВАЯ ЗАЯВКА!*\n\n"
            f"👤 *Имя:* {name}\n"
            f"📞 *Телефон:* {phone}\n"
            f"✉️ *Email:* {email}\n"
            f"🚚 *Формат:* {format_type}\n"
            f"🛒 *Товар:* {product}\n"
        )
        if comment:
            message += f"💬 *Комментарий:* {comment}\n"
        
        telegram_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(telegram_url, json={
            'chat_id': ADMIN_CHAT_ID,
            'text': message,
            'parse_mode': 'Markdown'
        })
        
        return jsonify({'success': True, 'message': 'Заявка отправлена!'}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
@app.route('/get_photo', methods=['GET'])
def get_photo():
    try:
        query = request.args.get('query', 'coffee')
        access_key = os.environ.get('UNSPLASH_ACCESS_KEY')
        
        if not access_key:
            return jsonify({'error': 'Key not found'}), 500
            
        url = f"https://api.unsplash.com/search/photos?query={query}&client_id={access_key}&per_page=1&orientation=landscape"
        response = requests.get(url, timeout=3)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('results'):
                img_url = data['results'][0]['urls']['regular']
                return jsonify({'url': img_url})
                
        return jsonify({'error': 'No photo found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
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

import sqlite3
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

# ዳታቤዝ ማዘጋጀት እና ቴብል መፍጠር
conn = sqlite3.connect('tana_market.db', check_same_thread=False)
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT,
        description TEXT,
        media_type TEXT,
        file_id TEXT,
        status TEXT DEFAULT 'active'
    )
''')
conn.commit()

# ተጠቃሚው በመረጠው ምድብ እንዲቆይ የሚረዳ ዲክሽነሪ (Memory)
user_categories = {}

# /start ትእዛዝ (የአጠቃቀም መመሪያን ጨምሮ)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [KeyboardButton("🏠 ቤት ሸያጭ እና ኪራይ"), KeyboardButton("🚗 መኪና፣ ባጃጅ እና ንብረቶች (ሽያጭ/ኪራይ)")],
        [KeyboardButton("💼 ስራ አገናኝ (ለሆቴል እና ሪስቶራንት)"), KeyboardButton("🔍 ሰፈር/አካባቢ")],
        [KeyboardButton("📋 የተመዘገቡ ማስታወቂያዎች አሳይ"), KeyboardButton("✅ የተሽጠ/የተዘጋ ማስታወቂያ")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    welcome_message = (
        "✨ **እንኳን ወደ 'ጣና ገበያ እና ስራ' ኦፊሴላዊ ቦት በሰላም መጡ!** ✨\n\n"
        "📖 **ቦቱን እንዴት መጠቀም ይቻላል?**\n"
        "1️⃣ ከታች ካሉት አዝራሮች የሚፈልጉትን **ምድብ** ይምረጡ።\n"
        "2️⃣ ምድቡን ከመረጡ በኋላ የዕቃውን ወይም ስራውን **መግለጫ** ጽሁፍ፣ **ፎቶ** (ከነ መግለጫው) ወይም የ **ድምፅ መልእክት** ይላኩ።\n"
        "3️⃣ ያሉትን ማስታወቂያዎች ለማየት **'📋 የተመዘገቡ ማስታወቂያዎች አሳይ'** የሚለውን ይጫኑ።\n"
        "4️⃣ የተሸጠውን ወይም የጨረሱትን ማስታወቂያ ለመዝጋት የቁጥር መለያውን (ID) ብቻ ይጻፉ።\n\n"
        "👇 እባክዎ መጀመሪያ ከታች ካሉት አማራጮች **ምድብ** ይምረጡ፦"
    )
    
    await update.message.reply_text(welcome_message, reply_markup=reply_markup, parse_mode="Markdown")

# መልዕክቶችን የሚቀበል ዋናው ክፍል
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id
    
    # 1. ምድብ መምረጫ ቁልፎች ሲጫኑ
    categories_list = [
        "🏠 ቤት ሸያጭ እና ኪራይ", 
        "🚗 መኪና፣ ባጃጅ እና ንብረቶች (ሽያጭ/ኪራይ)", 
        "💼 ስራ አገናኝ (ለሆቴል እና ሪስቶራንት)", 
        "🔍 ሰፈር/አካባቢ"
    ]
    
    if text in categories_list:
        user_categories[user_id] = text
        
        if text == "🏠 ቤት ሸያጭ እና ኪራይ":
            reply_msg = "መረጡት ምድብ: **ቤት ሸያጭ እና ኪራይ** 🏠\n\nአሁን እባክዎ ስለቤቱ ወይም ኪራዩ ዝርዝር መግለጫ ጽሁፍ ይላኩ፣ ፎቶ ከነመግለጫው ያያይዙ፣ ወይም የድምፅ መልእክት ይቅረጹ።"
        elif text == "🚗 መኪና፣ ባጃጅ እና ንብረቶች (ሽያጭ/ኪራይ)":
            reply_msg = "መረጡት ምድብ: **መኪና፣ ባጃጅ እና ንብረቶች (ሽያጭ/ኪራይ)** 🚗\n\nአሁን እባክዎ ስለሚሸጡት/ስለሚከራዩት ዝርዝር መግለጫ ጽሁፍ ይላኩ፣ ፎቶ ከነመግለጫው ያያይዙ፣ ወይም የድምፅ መልእክት ይቅረጹ።"
        elif text == "💼 ስራ አገናኝ (ለሆቴል እና ሪስቶራንት)":
            reply_msg = "መረጡት ምድብ: **ስራ አገናኝ (ለሆቴል እና ሪስቶራንት)** 💼\n\nአሁን እባክዎ ስለሚሰሩት/ስለሚያሰሩት ስራ ዝርዝር መግለጫ ጽሁፍ ይላኩ፣ ፎቶ ከነመግለጫው ያያይዙ፣ ወይም የድምፅ መልእክት ይቅረጹ።"
        elif text == "🔍 ሰፈር/አካባቢ":
            reply_msg = "መረጡት ምድብ: **ሰፈር/አካባቢ** 🔍\n\nአሁን እባክዎ የሚፈልጉትን ሰፈር ወይም አካባቢ ዝርዝር መግለጫ ጽሁፍ ይላኩ፣ ፎቶ ከነመግለጫው ያያይዙ፣ ወይም የድምፅ መልእክት ይቅረጹ።"
        
        await update.message.reply_text(reply_msg, parse_mode="Markdown")
        return

    # 2. የተመዘገቡ ማስታወቂያዎችን ማሳየት (ፎቶ፣ ድምፅ እና ጽሁፍ)
    if text == "📋 የተመዘገቡ ማስታወቂያዎች አሳይ":
        cursor.execute("SELECT id, category, description, media_type, file_id FROM posts WHERE status='active' ORDER BY id DESC LIMIT 5")
        rows = cursor.fetchall()
        
        if not rows:
            await update.message.reply_text("📭 እስካሁን ንቁ (Active) የሆነ ማስታወቂያ የለም።")
            return
        
        await update.message.reply_text("📋 **የቅርብ ጊዜ ማስታወቂያዎች (ከነ መለያ ቁጥራቸው):**", parse_mode="Markdown")
        
        for row in rows:
            post_id = row[0]
            category = row[1]
            description = row[2]
            media_type = row[3]
            file_id = row[4]
            
            caption_text = f"🆔 **መለያ ቁጥር (ID):** {post_id}\n📂 **ምድብ:** {category}\n📝 **መግለጫ:** {description}"
            
            if media_type == "photo" and file_id and file_id != "none":
                try:
                    await context.bot.send_photo(chat_id=update.effective_chat.id, photo=file_id, caption=caption_text, parse_mode="Markdown")
                except Exception:
                    await update.message.reply_text(caption_text, parse_mode="Markdown")
            elif media_type == "voice" and file_id and file_id != "none":
                try:
                    await context.bot.send_voice(chat_id=update.effective_chat.id, voice=file_id, caption=caption_text, parse_mode="Markdown")
                except Exception:
                    await update.message.reply_text(caption_text, parse_mode="Markdown")
            else:
                await update.message.reply_text(caption_text, parse_mode="Markdown")
        
        await update.message.reply_text("💡 ማስታወቂያን ለመዝጋት ወይም 'ተሸጧል' ለማለት የምር **መለያ ቁጥር (ID)** ብቻ ይጻፉ (ለምሳሌ፦ `1`)", parse_mode="Markdown")
        return

    # 3. የተሽጠ/የተዘጋ ማስታወቂያ አማራጭ ሲጫን
    if text == "✅ የተሽጠ/የተዘጋ ማስታወቂያ":
        await update.message.reply_text("✅ እባክዎ የተሸጠውን ወይም ሊዘጉት የሚፈልጉትን ማስታወቂያ **መለያ ቁጥር (ID)** ብቻ ይጻፉ (ለምሳሌ፦ `3`)", parse_mode="Markdown")
        return

    # 4. የቁጥር መለያ (ID) ሲጻፍ ማስታወቂያውን መዝጋት
    if text.isdigit():
        post_id = int(text)
        cursor.execute("SELECT id FROM posts WHERE id = ?", (post_id,))
        post = cursor.fetchone()
        
        if post:
            cursor.execute("UPDATE posts SET status = 'closed' WHERE id = ?", (post_id,))
            conn.commit()
            await update.message.reply_text(f"🎉 ማስታወቂያ ቁጥር **{post_id}** በተሳካ ሁኔታ 'ተሸጧል/ተዘግቷል' ተብሎ ተመዝግቧል! ✅", parse_mode="Markdown")
        else:
            await update.message.reply_text("⚠️ ይህ መለያ ቁጥር (ID) አልተገኘም፤ እባክዎ ትክክለኛ ቁጥር ያስገቡ።")
        return

    # 5. መደበኛ የጽሁፍ ማስታወቂያዎችን መቀበልና መመዝገብ
    category = user_categories.get(user_id, "አጠቃላይ ማስታወቂያ")
    description = text
    media_type = "text"
    file_id = "none"

    try:
        cursor.execute(
            "INSERT INTO posts (category, description, media_type, file_id, status) VALUES (?, ?, ?, ?, ?)",
            (category, description, media_type, file_id, 'active')
        )
        conn.commit()
        if user_id in user_categories:
            del user_categories[user_id]
            
        await update.message.reply_text(f"🌟 ማስታወቂያዎ በኪ **'{category}'** ምድብ ስር በተሳካ ሁኔታ ተመዝግቧል! ✅", parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ ስህተት ተፈጥሯል: {e}")

# ፎቶዎችን የሚቀበል ክፍል
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    category = user_categories.get(user_id, "አጠቃላይ ማስታወቂያ")
    
    photo_file = update.message.photo[-1]
    file_id = photo_file.file_id
    description = update.message.caption if update.message.caption else "መግለጫ የለውም"
    media_type = "photo"

    try:
        cursor.execute(
            "INSERT INTO posts (category, description, media_type, file_id, status) VALUES (?, ?, ?, ?, ?)",
            (category, description, media_type, file_id, 'active')
        )
        conn.commit()
        if user_id in user_categories:
            del user_categories[user_id]
            
        await update.message.reply_text(f"📸 የፎቶ ማስታወቂያዎ በ **'{category}'** ምድብ ስር በተሳካ ሁኔታ ተመዝግቧል! ✅", parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ ፎቶውን በመመዝገብ ላይ ስህተት ተፈጥሯል: {e}")

# የድምፅ መልእክት (Voice Note) የሚቀበል ክፍል
async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    category = user_categories.get(user_id, "አጠቃላይ ማስታወቂያ")
    
    voice_file = update.message.voice
    file_id = voice_file.file_id
    description = "🎤 የድምፅ ማስታወቂያ (Voice Note)"
    media_type = "voice"

    try:
        cursor.execute(
            "INSERT INTO posts (category, description, media_type, file_id, status) VALUES (?, ?, ?, ?, ?)",
            (category, description, media_type, file_id, 'active')
        )
        conn.commit()
        if user_id in user_categories:
            del user_categories[user_id]
            
        await update.message.reply_text(f"🎙 የድምፅ ማስታወቂያዎ በ **'{category}'** ምድብ ስር በተሳካ ሁኔታ ተመዝግቧል! ✅", parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ የድምፅ ማስታወቂያውን በመመዝገብ ላይ ስህተት ተፈጥሯል: {e}")

def main():
    TOKEN = "8507209990:AAEFgmkunM4Z47-IQ6p9M7n0PANclLXFjyQ"
    
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice)) # የድምፅ መልእክት ሃንድለር ተጨምሯል

    print("ጣና ገበያ እና ስራ ቦት በስራ ላይ ነው..")
    app.run_polling()

if __name__ == '__main__':
    main()
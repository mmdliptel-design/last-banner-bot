from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from datetime import datetime, timedelta

TOKEN = "8965008966:AAEX0noy5RdEW9aPcnnFfnQa65IM9pcPFsw" 
ADMIN_ID = 7246916356
CHANNEL_ID = -1004465232272

approved_users = {} 
banned_users = set()
is_running = True 

def get_iran_time():
    return (datetime.utcnow() + timedelta(hours=3, minutes=30)).strftime("%Y-%m-%d %H:%M")

def get_menu(user_id):
    buttons = [['درخواست ارسال بیانیه', 'ارسال بیانیه']]
    if user_id == ADMIN_ID:
        buttons.append(['پنل مدیریت'])
    return ReplyKeyboardMarkup(buttons, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """سلام دوست عزیز 🌟

خیلی خوشحالیم که به جمع بازیکنان لست بنر پیوستی. این ربات برای انتشار بیانیه‌های رسمی در گیم طراحی شده و به شما این امکان را می‌دهد که بیانیه‌های خود را به ساده‌ترین و سریع‌ترین شکل ممکن ارسال و منتشر کنید.

‼️ برای دسترسی به امکانات ربات، ابتدا از دکمه «درخواست ارسال بیانیه» استفاده کنید. پس از تأیید درخواست، امکان ثبت و انتشار بیانیه برای شما فعال خواهد شد.

☠︎ ───── LAST BANNER ───── ☠︎."""
    await update.message.reply_text(text, reply_markup=get_menu(update.effective_user.id))

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    text = update.message.text
    global is_running

    if user.id == ADMIN_ID and text and text.startswith("حذف بن "):
        try:
            target_id = int(text.split(" ")[2])
            banned_users.discard(target_id)
            await update.message.reply_text(f"کاربر {target_id} آن‌بن شد.")
        except:
            await update.message.reply_text("فرمت: حذف بن آیدی")
        return

    if not is_running and user.id != ADMIN_ID: return

    if text == 'پنل مدیریت' and user.id == ADMIN_ID:
        kb = [[InlineKeyboardButton("خاموش کردن", callback_data="off"), InlineKeyboardButton("روشن کردن", callback_data="on")]]
        await update.message.reply_text("پنل مدیریت:", reply_markup=InlineKeyboardMarkup(kb))
    
    elif text == 'درخواست ارسال بیانیه':
        await update.message.reply_text("دوست عزیز 🌟\n\nلطفا نام کشور خود را ارسال کنید \n\n📝 مثال: یمن")
        context.user_data['state'] = 'WAITING_COUNTRY'
    
    elif context.user_data.get('state') == 'WAITING_COUNTRY':
        country_name = text
        context.user_data['state'] = None
        kb = [[InlineKeyboardButton("✅ تایید", callback_data=f"approve_{user.id}_{country_name}"), InlineKeyboardButton("❌ رد", callback_data=f"reject_{user.id}")]]
        await context.bot.send_message(ADMIN_ID, f"درخواست کشور: {country_name}\nاز: @{user.username} ({user.id})", reply_markup=InlineKeyboardMarkup(kb))
        await update.message.reply_text("""✅ درخواست شما با موفقیت ثبت شد.

لطفاً تا زمان بررسی و تأیید توسط مدیریت تیم مقتدر لست بنر منتظر بمانید. پس از تأیید، دسترسی لازم برای شما فعال خواهد شد.

از صبوری و همراهی شما سپاسگزاریم. ❤️""")

    elif text == 'ارسال بیانیه':
        if user.id not in approved_users: await update.message.reply_text("""دوست عزیز 🌟

لطفاً شکیبا باشید و از ارسال درخواست‌های مکرر خودداری کنید. تمامی درخواست‌ها توسط مدیریت بررسی می‌شوند و در صورت تأیید، از همین طریق به شما اطلاع داده خواهد شد.

از صبر و همکاری شما سپاسگزاریم. ❤️""")
        else:
            await update.message.reply_text("""📢 بیانیه خود را ارسال کنید، دوست عزیز.

⚠️ لطفا پیش از ارسال، موارد زیر را رعایت کنید:

• بیانیه حتما همراه با عکس مرتبط باشد.
• متن بیانیه رسمی و قابل فهم نوشته شود.
• از هرگونه توهین، اهانت، تهدید یا الفاظ نامناسب خودداری کنید.
• بیانیه‌های مغایر با قوانین لست بنر منتشر نخواهند شد.

پس از ارسال، بیانیه شما توسط مدیریت بررسی خواهد شد.""")
            context.user_data['state'] = 'WAITING_STATEMENT'

    elif context.user_data.get('state') == 'WAITING_STATEMENT':
        if user.id in banned_users: await update.message.reply_text("شما بن هستید.")
        else:
            msg = await context.bot.forward_message(CHANNEL_ID, user.id, update.message.message_id)
            await context.bot.send_message(ADMIN_ID, f"بیانیه جدید از {approved_users[user.id]}\nزمان: {get_iran_time()}", 
                                           reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🚫 بن کردن کاربر", callback_data=f"ban_{user.id}")]]))
            await update.message.reply_text("""✅ از همکاری و انتشار بیانیه شما سپاسگزاریم.

بیانیه ارسالی شما با موفقیت در کانال رسمی لست بنر منتشر شد.

برای شما آرزوی موفقیت و دیپلماسی قدرتمند داریم. ❤️""")
        context.user_data['state'] = None

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    global is_running
    data = query.data.split('_')
    if data[0] == "off": is_running = False; await query.answer("خاموش شد")
    elif data[0] == "on": is_running = True; await query.answer("روشن شد")
    elif data[0] == "approve": 
        approved_users[int(data[1])] = data[2]
        await context.bot.send_message(int(data[1]), "✅ کشور شما با موفقیت تأیید شد، دوست عزیز.")
        await query.edit_message_text("تایید شد.")
    elif data[0] == "ban": banned_users.add(int(data[1])); await query.answer("کاربر بن شد.")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO | filters.VIDEO | filters.Document.ALL, handle_message))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.run_polling()

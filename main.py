from telegram import Update, ReplyKeyboardMarkup, Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters, CallbackQueryHandler

url = "http://127.0.0.1:7860"
bot_token = "6063429082:AAFZLJiFXtI6Kotb7FZysNM5RxiiKX3qDEY"

menu = [
    ["First setup / Первая настройка"],
    ["Guide / Гайд",  "Presets"],
    ["Sampler", "Sampling steps / Качество"],
    ["Resolution / Разрешение", "Number of pictures / Кол-во изображений"],
    ["Upscaler", "Upscale to"],
    ["CFG scale", "Seed"],
    ["Examples / Примеры"],
]
reply_markup = ReplyKeyboardMarkup(menu)

guide_sections = [
    "*Section 1*\nThis is the first section of the guide.",
    "*Section 2*\nThis is the second section of the guide.",
    "*Section 3*\nThis is the third section of the guide.",
]
# Callback
NEXT, PREVIOUS = range(2)

payload = {
  "enable_hr": "false",
  "denoising_strength": 0,
  "firstphase_width": 0,
  "firstphase_height": 0,
  "hr_scale": 2,
  "hr_upscaler": "",
  "prompt": "Cute dog paly with mango, on mango island",
  "seed": -1,
  "batch_size": 1,
  "steps": 50,
  "cfg_scale": 7,
  "width": 512,
  "height": 512,
  "negative_prompt": "string",
  "override_settings": {},
  "override_settings_restore_afterwards": "true",
  "sampler_index": "Euler",
  "send_images": "true",
  "save_images": "true",
}




def create_menu(index):
    menu = []
    if index > 0:
        menu.append(InlineKeyboardButton("Previous", callback_data=str(PREVIOUS)))
    if index < len(guide_sections) - 1:
        menu.append(InlineKeyboardButton("Next", callback_data=str(NEXT)))
    if index == len(guide_sections) -1:
        menu.append(InlineKeyboardButton("End Guide", callback_data='END_GUIDE'))
    return InlineKeyboardMarkup([menu])


inline_menu_sampler = [
    [InlineKeyboardButton("Euler a", callback_data='Euler'), InlineKeyboardButton("DPM2 Karras", callback_data='DPM')],
    [InlineKeyboardButton("DPM ++2M Karras", callback_data='DPM2'), InlineKeyboardButton("DPM++ SDE Karras", callback_data='70')]
]

inline_menu_num_pic = [
    [InlineKeyboardButton("Set to 2", callback_data='2'), InlineKeyboardButton("Set to 4", callback_data='4')],
    [InlineKeyboardButton("Set to 6", callback_data='6'), InlineKeyboardButton("Set to 8", callback_data='8')]
]

inline_menu_quality = [
    [InlineKeyboardButton("Set to 20", callback_data='20'), InlineKeyboardButton("Set to 35", callback_data='35')],
    [InlineKeyboardButton("Set to 50", callback_data='50'), InlineKeyboardButton("Set to 70", callback_data='70')]
]


inline_menu_res = [
    [InlineKeyboardButton("Set to 768x512", callback_data='res_vertical'), InlineKeyboardButton("Set to 512x768", callback_data='res_horizontal')],
    [InlineKeyboardButton("Set to 768x768", callback_data='res_square')]
]

inline_menu_seed = [
    [InlineKeyboardButton("Randomize" + " 🎲", callback_data='randomize')],
    [InlineKeyboardButton("Return previous seed" + " ♻", callback_data='return_prev')]
]


inline_menu_upscaler = [
    [InlineKeyboardButton("R-ESRGAN 4x+ Anime6B" + " 🎲", callback_data='rea')],
    [InlineKeyboardButton("ESRGAN_4x" + " ♻", callback_data='re')]
]

inline_menu_upscale_to =[
    [InlineKeyboardButton("Upscale x1.3", callback_data='x1.3')],
    [InlineKeyboardButton("upscale x1.5", callback_data='x1.5')],
    [InlineKeyboardButton("upscale x2", callback_data='x2')],

]


inline_menu_cfg = [
    [InlineKeyboardButton("Set to 6", callback_data='cfg_6'), InlineKeyboardButton("Set to 6.5", callback_data='cfg_6.5')],
    [InlineKeyboardButton("Set to 7", callback_data='cfg_7'), InlineKeyboardButton("Set to 7.5", callback_data='cfg_7.5')],
    [InlineKeyboardButton("Set to 8", callback_data='cfg_8'), InlineKeyboardButton("Set to 8.5", callback_data='cfg_8.5')],
    [InlineKeyboardButton("Set to 9", callback_data='cfg_9'), InlineKeyboardButton("Set to 9.5", callback_data='cfg_9.5')],
    [InlineKeyboardButton("Set to 10", callback_data='cfg_10'), InlineKeyboardButton("Set to 10.5", callback_data='cfg_10.5')],
    [InlineKeyboardButton("Set to 11", callback_data='cfg_11'), InlineKeyboardButton("Set to 11.5", callback_data='cfg_11.5')],
    [InlineKeyboardButton("Set to 12", callback_data='cfg_12'), InlineKeyboardButton("Set to 12.5", callback_data='cfg_12.5')],
    [InlineKeyboardButton("Set to 13", callback_data='cfg_13')]
]

inline_reply_markup_quality = InlineKeyboardMarkup(inline_menu_quality)
inline_reply_markup_res = InlineKeyboardMarkup(inline_menu_res)
inline_reply_markup_seed = InlineKeyboardMarkup(inline_menu_seed)
inline_reply_markup_cfg = InlineKeyboardMarkup(inline_menu_cfg)
inline_reply_markup_num_pic = InlineKeyboardMarkup(inline_menu_num_pic)
inline_reply_markup_sampler = InlineKeyboardMarkup(inline_menu_sampler)
inline_reply_markup_upscaler = InlineKeyboardMarkup(inline_menu_upscaler)
inline_reply_markup_upscale_to = InlineKeyboardMarkup(inline_menu_upscale_to)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        f'Hello {update.effective_user.first_name}\n\n{guide_sections[0]}',
        parse_mode='Markdown',
        reply_markup=create_menu(0),
    )
    context.user_data['section'] = 0


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.text == "Sampling steps / Качество":
        await update.message.reply_text('Choose strength of denoising', reply_markup=inline_reply_markup_quality)
    elif update.message.text == "Guide / Гайд":
        await update.message.reply_text(
            guide_sections[0],
            parse_mode='Markdown',
            reply_markup=create_menu(0),
        )
        context.user_data['section'] = 0
    elif update.message.text == "Resolution / Разрешение":
        await update.message.reply_text('Choose resolution and aspect ratio', reply_markup=inline_reply_markup_res)
    elif update.message.text == "Seed":
        await update.message.reply_text('Choose option', reply_markup=inline_reply_markup_seed)
    elif update.message.text == "CFG scale":
        await update.message.reply_text('Choose how strongly the picture will fit the context',
                                        reply_markup=inline_reply_markup_cfg)
    elif update.message.text == "Sampler":
        await update.message.reply_text('Choose sampler', reply_markup=inline_reply_markup_sampler)

    elif update.message.text == "Number of pictures / Кол-во изображений":
        await update.message.reply_text('Choose quantity', reply_markup=inline_reply_markup_num_pic)
    elif update.message.text == "Upscaler":
        await update.message.reply_text('Choose upscaler', reply_markup=inline_reply_markup_upscaler)
    elif update.message.text == "Upscale to":
        await update.message.reply_text('Choose multiplier', reply_markup=inline_reply_markup_upscale_to)

    else:
        await update.message.reply_text(update.message.text)


# Callback query handler
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    current_section = context.user_data.get('section', 0)

    if query.data == str(NEXT) and current_section < len(guide_sections) -1:
        current_section += 1
    elif query.data == str(PREVIOUS) and current_section > 0:
        current_section -= 1
    elif query.data == 'END_GUIDE':
        await query.message.reply_text(
            "Back to main menu",
            reply_markup=reply_markup
        )
        return
    elif query.data in ['cfg_6', 'cfg_6.5', 'cfg_7', 'cfg_7.5', 'cfg_8', 'cfg_8.5', 'cfg_9', 'cfg_9.5',
                        'cfg_10', 'cfg_10.5', 'cfg_11', 'cfg_11.5', 'cfg_12', 'cfg_12.5', 'cfg_13']:
        context.user_data['cfg'] = query.data
        await query.answer(f"You've selected {query.data}.")
        return

    elif query.data in ['Euler', 'DPM2 Karras', 'DPM ++2M Karras', 'DPM++ SDE Karras']:
        context.user_data['sampler'] = query.data
        await query.answer(f"You've selected {query.data}.")
        return

    elif query.data in ['20', '35', '50', '70']:
        context.user_data['quality'] = query.data
        await query.answer(f"You've selected {query.data} quality.")
        return

    elif query.data in ['res_vertical', 'res_horizontal', 'res_square']:
        context.user_data['resolution'] = query.data
        await query.answer(f"You've selected {query.data}.")
        return

    elif query.data in ['rea', 're']:
        context.user_data['upscaler'] = query.data
        await query.answer(f"You've selected {query.data}.")
        return

    elif query.data in ['x1.3', 'x1.5', 'x2']:
        context.user_data['upscale_to'] = query.data
        await query.answer(f"You've selected {query.data}.")
        return

    elif query.data in ['return_prev', 'randomize']:
        context.user_data['seed'] = query.data
        await query.answer(f"You've selected {query.data}.")
        return

    elif query.data in ['2', '4', '6', '8']:
        context.user_data['num_pic'] = query.data
        await query.answer(f"You've selected {query.data}.")
        return

    await query.edit_message_text(
        guide_sections[current_section],
        parse_mode='Markdown',
        reply_markup=create_menu(current_section)
    )
    context.user_data['section'] = current_section







app = ApplicationBuilder().token(bot_token).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
app.add_handler(CallbackQueryHandler(button))

app.run_polling()

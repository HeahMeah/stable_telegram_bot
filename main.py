from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters, CallbackQueryHandler
import aiohttp
import asyncio
import base64
import io
import logging
from PIL import Image


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

url = "http://127.0.0.1:7860"
bot_token = "6063429082:AAGbr-dWr0HA3haBkswLDm2jE7tAG8jnEg8"


menu = [
    ["Generate!"],
    ["Guide / Гайд",  "Presets"],
    ["Sampler", "Sampling steps / Качество"],
    ["Resolution / Разрешение", "Number of pictures / Кол-во изображений"],
    ["Upscaler", "Upscale to"],
    ["CFG scale", "Seed"],
    ["Models"],
]
reply_markup = ReplyKeyboardMarkup(menu)

guide_sections = [
    "*Section 1*\nStyles:hewlett, 80s-anime-AI, kuvshinov, roy-lichtenstein.",
    "*Section 2*\nThis is the second section of the guide.",
    "*Section 3*\nThis is the third section of the guide.",
]
# Callback
NEXT, PREVIOUS = range(2)


def create_menu(index):
    menu = []
    if index > 0:
        menu.append(InlineKeyboardButton("Previous", callback_data=str(PREVIOUS)))
    if index < len(guide_sections) - 1:
        menu.append(InlineKeyboardButton("Next", callback_data=str(NEXT)))
    if index == len(guide_sections) - 1:
        menu.append(InlineKeyboardButton("End Guide", callback_data='END_GUIDE'))
    return InlineKeyboardMarkup([menu])


inline_menu_sampler = [
    [InlineKeyboardButton("Euler", callback_data='Euler'), InlineKeyboardButton("DPM2 Karras", callback_data='DPM2 Karras')],
    [InlineKeyboardButton("DPM++ 2M Karras", callback_data='DPM++ 2M Karras'), InlineKeyboardButton("DPM++ SDE Karras", callback_data='DPM++ SDE Karras')]
]

inline_menu_model = [
    [InlineKeyboardButton("ProtogenV2.2 by darkstorm2150", callback_data='Protogen_V2.2.safetensors'), InlineKeyboardButton("ProtogenInf by darkstorm2150", callback_data='protogenInfinity.safetensors')],
    [InlineKeyboardButton("Realism by Lykon", callback_data='absolutereality_v1.safetensors'), InlineKeyboardButton("DreamShaper by Lykon", callback_data='dreamshaper.safetensors')],
    [InlineKeyboardButton("Comics", callback_data='comics.safetensors'), InlineKeyboardButton("Anything & Everything", callback_data='AnyEvery.safetensors')],
    [InlineKeyboardButton("Realism by Wick_J4", callback_data='mixrealSd21.safetensors')]
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
    [InlineKeyboardButton("Set to 768x512", callback_data='horizontal'), InlineKeyboardButton("Set to 512x768", callback_data='vertical')],
    [InlineKeyboardButton("Set to 768x768", callback_data='square')]
]

inline_menu_seed = [
    [InlineKeyboardButton("Randomize" + " 🎲", callback_data='randomize')],
    [InlineKeyboardButton("Return previous seed" + " ♻", callback_data='return_prev')]
]

inline_menu_upscaler = [
    [InlineKeyboardButton("R-ESRGAN 4x+ Anime6B", callback_data='rea')],
    [InlineKeyboardButton("ESRGAN_4x", callback_data='re')]
]

inline_menu_upscale_to = [
    [InlineKeyboardButton("Upscale x1.3", callback_data='x1.3'), InlineKeyboardButton("Upscale x1.5", callback_data='x1.5')],
    [InlineKeyboardButton("upscale x2", callback_data='x2')]
]

inline_menu_generate = [
    [InlineKeyboardButton("Again", callback_data='GENERATE')]
]

inline_menu_embedding = [
    [InlineKeyboardButton("Realistic", callback_data='realisticvision-negative-embedding'), InlineKeyboardButton("Anime", callback_data='anime-style-negative-embedding,easynegative')],
    [InlineKeyboardButton("Default", callback_data='easynegative, verybadimagenegative_v1.3'), InlineKeyboardButton("Overall quality", callback_data='ng_deepnegative_v1_75t')]
]

inline_menu_cfg = [
    [InlineKeyboardButton("Set to 6", callback_data='6'), InlineKeyboardButton("Set to 6.5", callback_data='6.5')],
    [InlineKeyboardButton("Set to 7", callback_data='7'), InlineKeyboardButton("Set to 7.5", callback_data='7.5')],
    [InlineKeyboardButton("Set to 8", callback_data='8'), InlineKeyboardButton("Set to 8.5", callback_data='8.5')],
    [InlineKeyboardButton("Set to 9", callback_data='9'), InlineKeyboardButton("Set to 9.5", callback_data='9.5')],
    [InlineKeyboardButton("Set to 10", callback_data='10'), InlineKeyboardButton("Set to 10.5", callback_data='10.5')],
    [InlineKeyboardButton("Set to 11", callback_data='11'), InlineKeyboardButton("Set to 11.5", callback_data='11.5')],
    [InlineKeyboardButton("Set to 12", callback_data='12'), InlineKeyboardButton("Set to 12.5", callback_data='12.5')],
    [InlineKeyboardButton("Set to 13", callback_data='13')]
]

inline_reply_markup_quality = InlineKeyboardMarkup(inline_menu_quality)
inline_reply_markup_res = InlineKeyboardMarkup(inline_menu_res)
inline_reply_markup_seed = InlineKeyboardMarkup(inline_menu_seed)
inline_reply_markup_cfg = InlineKeyboardMarkup(inline_menu_cfg)
inline_reply_markup_num_pic = InlineKeyboardMarkup(inline_menu_num_pic)
inline_reply_markup_sampler = InlineKeyboardMarkup(inline_menu_sampler)
inline_reply_markup_upscaler = InlineKeyboardMarkup(inline_menu_upscaler)
inline_reply_markup_upscale_to = InlineKeyboardMarkup(inline_menu_upscale_to)
inline_reply_markup_model = InlineKeyboardMarkup(inline_menu_model)
inline_reply_markup_generate = InlineKeyboardMarkup(inline_menu_generate)
inline_reply_markup_embedding = InlineKeyboardMarkup(inline_menu_embedding)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        f'Hello {update.effective_user.first_name}\n\n{guide_sections[0]}',
        parse_mode='Markdown',
        reply_markup=create_menu(0),
    )
    context.user_data['section'] = 0

image_ready = False


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_text = update.message.text

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

    elif update.message.text == "Models":
        await update.message.reply_text('Choose model', reply_markup=inline_reply_markup_model)

    elif context.user_data.get('user_prompt', False):
        prompt = update.message.text
        context.user_data['prompt'] = prompt  # Save the prompt here
        context.user_data['user_prompt'] = False
        await generate_image(update, context)
        return

    elif update.message.text == "Generate!":
        await update.message.reply_text('Choose negative prompt, Then please type your prompt....', reply_markup=inline_reply_markup_embedding)
        return

    else:
        context.user_data['prompt'] = user_text
        await generate_image(update, context)
        if 'message_id' in context.user_data:
            await update_progress(update, context)


# Callback query handler
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    current_section = context.user_data.get('section', 0)

    if query.data == str(NEXT) and current_section < len(guide_sections) - 1:
        current_section += 1
    elif query.data == str(PREVIOUS) and current_section > 0:
        current_section -= 1
    elif query.data == 'END_GUIDE':
        await query.message.reply_text(
            "Back to main menu",
            reply_markup=reply_markup
        )
        return
    elif query.data in ['6', '6.5', '7', '7.5', '8', '8.5', '9', '9.5',
                        '10', '10.5', '11', '11.5', '12', '12.5', '13']:
        context.user_data['cfg'] = query.data
        await query.answer(f"You've selected {query.data}.")
        return

    elif query.data in ['Euler', 'DPM2 Karras', 'DPM++ 2M Karras', 'DPM++ SDE Karras']:
        context.user_data['sampler'] = query.data
        await query.answer(f"You've selected {query.data}.")
        return

    elif query.data in ['20', '35', '50', '70']:
        context.user_data['quality'] = query.data
        await query.answer(f"You've selected {query.data} quality.")
        return

    elif query.data in ['vertical', 'horizontal', 'square']:
        if query.data == 'vertical':
            context.user_data['width'] = 512
            context.user_data['height'] = 768
        elif query.data == 'horizontal':
            context.user_data['width'] = 768
            context.user_data['height'] = 512
        elif query.data == 'square':
            context.user_data['width'] = 768
            context.user_data['height'] = 768
        await query.answer(f"You've selected {query.data} resolution.")
        return

    elif query.data in ['rea', 're']:
        if query.data == 'rea':
            context.user_data['upscaler'] = "R-ESRGAN 4x+ Anime6B"
        elif query.data == 're':
            context.user_data['upscaler'] = "ESRGAN_4x"
        await query.answer(f"You've selected {query.data}.")
        return

    elif query.data in ['x1.3', 'x1.5', 'x2']:
        if query.data == 'x1.3':
            context.user_data['upscale_to'] = "1.3"
            context.user_data['upscale_on'] = "true"
        elif query.data == 'x1.5':
            context.user_data['upscale_to'] = "1.5"
            context.user_data['upscale_on'] = "true"
        elif query.data == 'x2':
            context.user_data['upscale_to'] = "2"
            context.user_data['upscale_on'] = "true"
        await query.answer(f"You've selected {query.data}.")
        return

    elif query.data in ['return_prev', 'randomize']:
        if query.data == 'return_prev':
            context.user_data['seed'] = "-1"  # Should be finished now just random,heh, need take seed and paste here
        elif query.data == 'randomize':
            context.user_data['seed'] = "-1"
        context.user_data['seed'] = query.data
        await query.answer(f"You've selected {query.data}.")
        return

    elif query.data in ['2', '4', '6', '8']:
        context.user_data['num_pic'] = query.data
        await query.answer(f"You've selected {query.data}.")
        return

    elif query.data in ['realisticvision-negative-embedding', 'anime-style-negative-embedding,easynegative', 'easynegative, verybadimagenegative_v1.3', 'ng_deepnegative_v1_75t']:
        context.user_data['negative_prompt'] = query.data
        await query.answer(f"You've selected {query.data}.")
        return

    elif query.data in ['Protogen_V2.2.safetensors', 'protogenInfinity.safetensors', 'absolutereality_v1.safetensors',
                        'dreamshaper.safetensors', 'comics.safetensors', 'AnyEvery.safetensors', 'mixrealSd21.safetensors']:
        context.user_data['model_name'] = query.data
        await query.answer(f"You've selected {query.data}.")
        model = prepare_model(context)
        headers = {'accept': 'application/json'}
        model_endpoint = f'{url}/sdapi/v1/sd-models'

        async with aiohttp.ClientSession() as session:
            async with session.post(model_endpoint, headers=headers, json=model) as response:
                if response.status == 200:
                    await query.message.reply_text("Model is ready!")
                else:
                    await query.message.reply_text(f"Failed to prepare the model with status code {response.status}")
        return

    elif query.data == 'GENERATE':
        await generate_image(query, context)


        return

    await query.edit_message_text(
        guide_sections[current_section],
        parse_mode='Markdown',
        reply_markup=create_menu(current_section)
    )
    context.user_data['section'] = current_section


def prepare_model(context):
    user_data = context.user_data
    model = {
    "filename": user_data.get("model_name", "AnyEvery.safetensors")
    }
    return model


def prepare_payload(context):
    user_data = context.user_data
    payload = {
        "prompt": user_data.get('prompt', "Dogs playing poker"),
        "seed": user_data.get('seed', -1),
        "subseed_strength": 0.8,
        "batch_count": user_data.get('num_pic', 1),
        "steps": user_data.get('quality', 29),
        "cfg_scale": user_data.get('cfg', 7.5),
        "width": user_data.get('width', 768),
        "height": user_data.get('height', 512),
        "negative_prompt": user_data.get('negative_prompt', "easynegative"),
        "sampler_index": user_data.get('sampler', "Euler"),
        "send_images": "true",
        "save_images": "true",
    }
    return payload


async def generate_image(reply_target, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.debug("generate_image function has been started")

    message = await reply_target.message.reply_text("Generating....")
    context.user_data['message_id'] = message.message_id
    context.user_data['image_ready'] = False

    update_progress_task = asyncio.create_task(update_progress(reply_target, context))

    payload = prepare_payload(context)
    headers = {'accept': 'application/json'}
    endpoint = f'{url}/sdapi/v1/txt2img'

    async with aiohttp.ClientSession() as session:
        async with session.post(endpoint, headers=headers, json=payload) as response:


            if response.status == 200:

                json_response = await response.json()
                image_data_base64 = json_response['images'][0]
                context.user_data['image_data_base64'] = image_data_base64
                image_data = base64.b64decode(image_data_base64)
                image = Image.open(io.BytesIO(image_data))
                image.save("generated_image.png")
                context.user_data['image_ready'] = True


                if context.user_data.get('upscale_on') == "true":
                    await upscale_image(reply_target, context)
                else:
                    with open("generated_image.png", 'rb') as file:
                        if isinstance(reply_target, Update):
                            await reply_target.message.reply_photo(photo=file, reply_markup=inline_reply_markup_generate)
                        elif isinstance(reply_target, CallbackQuery):
                            await reply_target.message.reply_photo(photo=file, reply_markup=inline_reply_markup_generate)
                    await asyncio.sleep(1)
                    await cleanup(reply_target, context, context.user_data['message_id'])
            else:
                if isinstance(reply_target, Update):
                    await reply_target.message.reply_text(f"Generation failed with status code {response.status}")
                    context.user_data['image_ready'] = True
                elif isinstance(reply_target, CallbackQuery):
                    await reply_target.message.reply_text(f"Generation failed with status code {response.status}")
                    context.user_data['image_ready'] = True


def prepare_upscale_payload(context):
    user_data = context.user_data
    image_data_base64 = user_data.get('image_data_base64')
    payload = {
        "resize_mode": 0,
        "upscaling_resize": user_data.get('upscale_to'),
        "upscaler_1": user_data.get('upscaler'),
        "upscaler_2": "None",
        "extras_upscaler_2_visibility": 0,
        "upscale_first": False,
        "image": image_data_base64
    }
    return payload


async def upscale_image(reply_target, context: ContextTypes.DEFAULT_TYPE) -> None:
    payload = prepare_upscale_payload(context)
    headers = {'accept': 'application/json'}
    endpoint = f'{url}/sdapi/v1/extra-single-image'

    async with aiohttp.ClientSession() as session:
        async with session.post(endpoint, headers=headers, json=payload) as response:
            if response.status == 200:
                json_response = await response.json()

                upscaled_image_data_base64 = json_response['image']
                upscaled_image_data = base64.b64decode(upscaled_image_data_base64)
                image = Image.open(io.BytesIO(upscaled_image_data))
                image.save("upscaled_image.png")
                with open("upscaled_image.png", 'rb') as file:
                    if isinstance(reply_target, Update):
                        await reply_target.message.reply_photo(photo=file, reply_markup=inline_reply_markup_generate)
                    elif isinstance(reply_target, CallbackQuery):
                        await reply_target.message.reply_photo(photo=file, reply_markup=inline_reply_markup_generate)
            else:
                if isinstance(reply_target, Update):
                    await reply_target.message.reply_text(f"Upscaling failed with status code {response.status}")
                elif isinstance(reply_target, CallbackQuery):
                    await reply_target.message.reply_text(f"Upscaling failed with status code {response.status}")


async def get_progress():
    async with aiohttp.ClientSession() as session:
        async with session.get('http://127.0.0.1:7860/sdapi/v1/progress?skip_current_image=false') as resp:
            data = await resp.json()  # This will give you the JSON response as a Python dictionary
            progress = data['progress']
            eta_relative = data['eta_relative']
            return progress, eta_relative


async def update_progress(update, context):
    logger.debug("update_progress function has been started")

    message_id = context.user_data['message_id']

    last_progress = 0
    spinner_states = ['-', '\\', '|', '/']
    spinner_index = 0
    while not context.user_data.get('image_ready', False):
        progress, eta_relative = await get_progress()
        if progress != last_progress:
            progress_percentage = int(progress * 100)
            eta_minutes = int(eta_relative / 60)
            eta_seconds = int(eta_relative % 60)
            spinner_state = spinner_states[spinner_index % 4]
            chat_id = update.message.chat.id if isinstance(update, Update) else update.message.chat.id

            try:
                await context.bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=message_id,
                    text=f"Generating...{spinner_state} ({progress_percentage}% complete, ETA: {eta_minutes}m {eta_seconds}s)"
                )
            except Exception as e:
                print(f"Failed to update progress: {e}")

            last_progress = progress
            spinner_index += 1

        await asyncio.sleep(0.5)


async def cleanup(update, context, message_id):
    try:
        await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=message_id)
    except Exception as e:
        print(f"Cleanup failed with error {e}")


app = ApplicationBuilder().token(bot_token).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
app.add_handler(CallbackQueryHandler(button))

app.run_polling()

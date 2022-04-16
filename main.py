from telethon import TelegramClient, events
from telethon import functions, types
from secrets import token_urlsafe
from dotenv import load_dotenv
from pdfminer.high_level import extract_text
from gtts import gTTS
from argostranslate import package, translate
import os


# VAR ENV 
load_dotenv()

# Telegram 
bot = TelegramClient(
    os.getenv('SESSTION_FILE_NAME'),
    api_id=os.getenv('API_ID'),
    api_hash=os.getenv('API_HASH')
                    )

bot.start(bot_token=os.getenv('TOKEN'))

# Argos
package.install_from_path('en_ar.argosmodel')
installed_languages = translate.get_installed_languages()
tr = installed_languages[0].get_translation(installed_languages[1])

# Some Functions
async def info():
    me = await bot.get_me()
    print(f'''Logged in as @{me.username}, {me.first_name}.
[INFO] Verified: {str(me.verified)}
[INFO] Restricted: {str(me.restricted)}
[INFO] Scam: {str(me.scam)}
[INFO] Fake: {str(me.fake)}

STARTED @{me.username} ...
''')

async def pdf2Text(FILEPATH):
    return extract_text(FILEPATH)

async def text2Ar(TEXT):
    return tr.translate(TEXT)

async def ar2Audio(text, filename):
    audio = gTTS(text=text, lang='ar')
    audio.save(f'{filename}.mp3')

async def convert(FILE, FILE_NAME):
    try:
        text = await pdf2Text(FILE)
        tar = await text2Ar(text)
        print(tar)
        await ar2Audio(tar, FILE_NAME)
        return True
    except Exception as e:
        print(str(e))
        return False

@bot.on(events.NewMessage(pattern='^/start'))
async def start(event):
    await event.reply('Send a pdf file to convert it into AR speech!')

@bot.on(events.NewMessage)
async def on_pdf(event):
    if (event.message.media is not None
    and event.message.media.document.mime_type == 'application/pdf'
    and event.message.media.document.size <= 6500000 # bytes
    ):
        FILE_NAME = token_urlsafe(16)
        SAVED_PATH = '{}\{}.pdf'.format(f'{os.getcwd()}\\files', FILE_NAME)
        
        await bot.download_media(
            message=event.message.media, 
            file=SAVED_PATH
            )

        conv = await convert(SAVED_PATH, FILE_NAME)
        if conv:
            await bot.send_file(
                await event.get_chat(),
                f'{FILE_NAME}.mp3',
                voice_note=False
            )
            


if __name__ == '__main__':
    bot.loop.run_until_complete(info())
    bot.run_until_disconnected()
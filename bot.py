import os, logging, asyncio
from telethon import Button
from telethon import TelegramClient, events
from telethon.tl.types import ChannelParticipantAdmin
from telethon.tl.types import ChannelParticipantCreator
from telethon.tl.functions.channels import GetParticipantRequest
from telethon.errors import UserNotParticipantError

logging.basicConfig(
    level=logging.INFO,
    format='%(name)s - [%(levelname)s] - %(message)s'
)
LOGGER = logging.getLogger(name)

api_id = int(os.environ.get("APP_ID"))
api_hash = os.environ.get("API_HASH")
bot_token = os.environ.get("TOKEN")
client = TelegramClient('client', api_id, api_hash).start(bot_token=bot_token)
spam_chats = []

@client.on(events.NewMessage(pattern="^/start$"))
async def start(event):
  await event.reply(
    "__Selam Ben Sari Tagger Bot, "Yardım İçin /help\nKomutunu Kullan",
    link_preview=False,
    buttons=(
      [
        Button.url('✨ Grubumuz', 't.me/sarisohbet'),
        Button.url('👤 Sahipler', 't.me/sarisohbet/508019')
      ]
    )
  )

@client.on(events.NewMessage(pattern="^/help$"))
async def help(event):
  helptext = "Sarı Tagger Bot'un Yardım Menüsündesiniz\n/Komut: /her\nEtiketleme İşlemini Durdurmak İçin /cancel\n`Örneğin: /her Buraya Gelin!"
  await event.reply(
    helptext,
    link_preview=False,
    buttons=(
      [
        Button.url('✨ Grubumuz', 'https://t.me/sarisohbet'),
        Button.url('👤 Sahipler', 'https://t.me/sarisohbet/508019')
      ]
    )
  )
  
@client.on(events.NewMessage(pattern="^/her ?(.*)"))
async def mentionall(event):
  chat_id = event.chat_id
  if event.is_private:
    return await event.respond("Bu Komutlar Gruplarda Ve Kanallarda Geçerlidir!")
  
  is_admin = False
  try:
    partici_ = await client(GetParticipantRequest(
      event.chat_id,
      event.sender_id
    ))
  except UserNotParticipantError:
    is_admin = False
  else:
    if (
      isinstance(
        partici_.participant,
        (
          ChannelParticipantAdmin,
          ChannelParticipantCreator
        )
      )
    ):
      is_admin = True
  if not is_admin:
    return await event.respond("Sadece Grup ve Kanal Adminleri Bu Komutları Kullanır!")
  
  if event.pattern_match.group(1) and event.is_reply:
    return await event.respond("Bana Bir Metin Göndermen Lazım!")
  elif event.pattern_match.group(1):
    mode = "text_on_cmd"
    msg = event.pattern_match.group(1)
  elif event.is_reply:
    mode = "text_on_reply"
    msg = await event.get_reply_message()
    if msg == None:
        return await event.respond("Eski Mesajlar İle Üyelerden Bahsedemem!  (Beni Gruba Eklemeden Önce Yazılan Mesajlar)")
  else:
    return await event.respond("Etiketleme İşlemini Başlatabilmem İçin Komut İle Birlikte Bir Mesaj Yazman Gerekir!")
  
  spam_chats.append(chat_id)
  usrnum = 0
  usrtxt = ''
  async for usr in client.iter_participants(chat_id):
    if not chat_id in spam_chats:
      break
    usrnum += 1
    usrtxt += f"[{usr.first_name}](tg://user?id={usr.id}) "
    if usrnum == 5:
      if mode == "text_on_cmd":
        txt = f"{usrtxt}\n\n{msg}"
        await client.send_message(chat_id, txt)
      elif mode == "text_on_reply":
        await msg.reply(usrtxt)
      await asyncio.sleep(2)
      usrnum = 0
      usrtxt = ''
  try:
    spam_chats.remove(chat_id)
  except:
    pass

@client.on(events.NewMessage(pattern="^/cancel$"))
async def cancel_spam(event):
  if not event.chat_id in spam_chats:
    return await event.respond('Etiketleme 🍃...')
  else:
    try:
      spam_chats.remove(event.chat_id)
    except:
      pass
    return await event.respond('⛔ Etiketleme İşlemini Durdurdum.')

print(">> BOT STARTED <<")
client.run_until_disconnected()

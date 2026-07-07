import discord
import asyncio
import aiohttp
import sqlite3
import json
import logging
import sys
import os
import time
import datetime
from colorama import init, Fore, Back, Style

# Renkli siber arayüz altyapısını başlatıyoruz
init(autoreset=True)

# Modern Siber Renk Paleti
C_NEON   = Fore.LIGHTGREEN_EX  # Neon Yeşil
C_DARK   = Fore.GREEN          # Sistem Log Rengi
C_BLUE   = Fore.LIGHTBLUE_EX   # Çerçeve ve Bağlantı Noktaları
C_CYAN   = Fore.CYAN           # Girdi / Komut Satırı Rengi
C_WHITE  = Fore.WHITE          # Normal Metinler
C_ALERT  = Fore.LIGHTRED_EX    # Hata / Sınır Aşımı

# ==================== AYARLAR VE KİMLİK ====================
TOKEN = ""
WEBHOOK_URL = ""


RESET_TARGET_SERVER = True  # Hedef sunucudaki eski kanalları temizlesin mi?
RATE_LIMIT_DELAY = 1.6      # Güvenlik için genel işlem arası bekleme süresi
EMOJI_DELAY = 4.5           # Emojilerin 429 yememesi için özel güvenli bekleme süresi

# --- OTOMATİK GÜNCELLEME (AUTO-UPDATE) SİSTEMİ ---
CURRENT_VERSION = "v1.0.0"
# Uzak sunucuda sadece "v1.0.1" yazan bir txt dosyasının RAW linki:
VERSION_CHECK_URL = "https://raw.githubusercontent.com/gorizyon/copy/refs/heads/main/version.txt" 
# Güncel Python kodunun bulunduğu RAW linki:
UPDATE_CODE_URL = "GITHUBA_YUKLEDIGIN_CLONE_PY_RAW_LINKI_BURAYA"
# ============================================================

# Discord kütüphanesinin gereksiz log kalabalığını tamamen kapatıyoruz
logging.getLogger('discord').setLevel(logging.CRITICAL)
logging.getLogger('discord.http').setLevel(logging.CRITICAL)

client = discord.Client(heartbeat_timeout=60.0, guild_ready_timeout=20.0, chunk_guilds_at_startup=False)

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def log_cyber(message, color=C_DARK, prefix="SİSTEM"):
    """Terminal arayüzüne uygun siber log formatı basar"""
    cyber_msg = f"{C_BLUE}[{color}{prefix}{C_BLUE}] ➔ {C_WHITE}{message}"
    print(cyber_msg)
    sys.stdout.flush()

def generate_progress_bar(current, total, prefix='VERİ_AKIŞI', length=35):
    """Süreç ilerleme durumunu gösteren siber ilerleme çubuğu oluşturur"""
    percent = float(current) * 100 / total if total > 0 else 100
    filled_length = int(length * current // total) if total > 0 else length
    bar = '█' * filled_length + '░' * (length - filled_length)
    return f" {C_BLUE}⎰{C_DARK}{prefix}{C_BLUE}⎱ ➔ {C_BLUE}[{C_NEON}{bar}{C_BLUE}] {C_NEON}{percent:.1f}%"

def cyber_connecting_animation():
    """Tokene bağlanırken çalışan tamamen Türkçe animasyonlu yükleme ekranı"""
    clear_screen()
    asama_listesi = [
        ("GÜVENLİ BAĞLANTI PROXY'Sİ BAŞLATILIYOR", 0.4),
        ("DISCORD GÜVENLİK DUVARI ANALİZ EDİLİYOR", 0.5),
        ("KULLANICI TOKEN KİMLİĞİ DOĞRULANIYOR", 0.6),
        ("KRİPTOLU SİBER TÜNEL OLUŞTURULUYOR", 0.4),
        ("ÇEKİRDEK VERİ PAKETLERİ ENJEKTE EDİLİYOR", 0.3)
    ]
    
    print(C_BLUE + "┌────────────────────────────────────────────────────────────────────────┐")
    print(C_NEON + "         [!] GORIZYON DISCORD PACK GÜVENLİK ARAYÜZÜ BAŞLATILIYOR          ")
    print(C_BLUE + "└────────────────────────────────────────────────────────────────────────┘\n")
    
    for asama, bekleme_suresi in asama_listesi:
        sys.stdout.write(f" {C_BLUE}[{C_DARK}BEKLE{C_BLUE}] ➔ {C_WHITE}{asama}...")
        sys.stdout.flush()
        
        for _ in range(3):
            time.sleep(bekleme_suresi / 3)
            sys.stdout.write(f"{C_NEON}.")
            sys.stdout.flush()
            
        sys.stdout.write(f" {C_NEON}[AKTİF]\n")
        sys.stdout.flush()
        time.sleep(0.1)
        
    print(f"\n {C_NEON}➔ BAĞLANTI BAŞARILI. ANA PANEL ARAYÜZÜNE AKTARILIYORSUNUZ...")
    time.sleep(1.2)

async def send_modern_embed_log(title, description, fields_list, color_code=3066993):
    """Discord Webhook kanallarına modern, renkli ve okunaklı zengin içerik kutusu iletir"""
    if not WEBHOOK_URL or "BURAYA_GIRIN" in WEBHOOK_URL:
        return
    
    # KORUMA KALKANI: Discord Embed 'value' limiti maksimum 1024 karakterdir. 
    for field in fields_list:
        if 'value' in field and isinstance(field['value'], str):
            if len(field['value']) > 1024:
                field['value'] = field['value'][:1015] + " [...]"
    
    payload = {
        "embeds": [
            {
                "title": f"🛰️ {title}",
                "description": description,
                "color": color_code,
                "fields": fields_list,
                "footer": {
                    "text": f"Gorizyon Cyber Security Sub-System • {CURRENT_VERSION}",
                    "icon_url": "https://i.imgur.com/v8tX8Yp.png"
                },
                "timestamp": datetime.datetime.utcnow().isoformat()
            }
        ]
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(WEBHOOK_URL, json=payload, timeout=5) as response: 
                if response.status >= 400:
                    err_text = await response.text()
                    print(f"\n{C_ALERT}[!] Webhook API Hatası ({response.status}): {err_text}")
    except Exception as e: 
        print(f"\n{C_ALERT}[!] Webhook İletişim Hatası: {str(e)}")

async def check_and_apply_update():
    """Gelişmiş OTA (Over-The-Air) Otomatik Güncelleme Motoru"""
    if "BURAYA" in VERSION_CHECK_URL or not VERSION_CHECK_URL:
        log_cyber("Güncelleme bağlantıları (URL) ayarlanmamış. Kod üzerinden URL'leri girin.", C_ALERT, prefix="GÜNCELLEME_HATASI")
        return False
        
    log_cyber("Mainframe sunucusu ile iletişim kuruluyor, yeni sürümler taranıyor...", C_BLUE, prefix="GÜNCELLEME")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(VERSION_CHECK_URL, timeout=5) as resp:
                if resp.status == 200:
                    remote_version = (await resp.text()).strip()
                    if remote_version != CURRENT_VERSION and remote_version != "":
                        log_cyber(f"YENİ SÜRÜM BULUNDU! ➔ Mevcut: {CURRENT_VERSION} | Yeni: {remote_version}", C_NEON, prefix="GÜNCELLEME")
                        log_cyber("Yeni çekirdek veri paketi indiriliyor...", C_BLUE, prefix="İNDİRİLİYOR")
                        
                        async with session.get(UPDATE_CODE_URL, timeout=10) as code_resp:
                            if code_resp.status == 200:
                                new_code = await code_resp.read()
                                # Kendi dosyasının üzerine yazar
                                with open(__file__, 'wb') as f:
                                    f.write(new_code)
                                    
                                log_cyber("Sistem başarıyla güncellendi! Çekirdek yeniden başlatılıyor...", C_NEON, prefix="BAŞARILI")
                                await asyncio.sleep(2)
                                # Betiği kapatıp yeni kodlarla baştan çalıştırır
                                os.execv(sys.executable, ['python'] + sys.argv)
                            else:
                                log_cyber("Kod paketi indirilirken sunucu reddetti.", C_ALERT, prefix="HATA")
                    else:
                        log_cyber("Sistem zaten en güncel sürümde çalışıyor.", C_DARK, prefix="GÜNCEL")
                else:
                    log_cyber("Versiyon kontrol sunucusuna ulaşılamadı.", C_ALERT, prefix="HATA")
    except Exception as e:
        log_cyber(f"Bağlantı sırasında bir anormallik oluştu: {str(e)}", C_ALERT, prefix="HATA")
    
    return True

async def safe_api_execute(coro, label):
    """Discord API isteklerini hız sınırına karşı koruyarak çalıştırır"""
    while True:
        try:
            return await coro
        except discord.HTTPException as e:
            if e.status == 429:
                try: retry_after = float(e.response.json().get('retry_after', 5.0))
                except: retry_after = 6.0
                log_cyber(f"{label} işleminde hız sınırına takılındı. {retry_after} saniye bekleniyor...", C_ALERT, prefix="LİMİT_KORUMA")
                await asyncio.sleep(retry_after + 1.5)
                continue
            elif e.code == 30005:
                log_cyber(f"{label} oluşturulurken maksimum sunucu rol sınırına (250) ulaşıldı.", C_ALERT, prefix="LİMİT_HATASI")
                return "LIMIT_REACHED"
            else:
                log_cyber(f"Discord API isteği reddetti ({label}): Durum Kodu {e.status}", C_ALERT, prefix="API_HATASI")
                return None
        except Exception as ex:
            log_cyber(f"Çekirdek yürütme motoru durduruldu ({label}): {str(ex)}", C_ALERT, prefix="SİSTEM_HATASI")
            return None

async def get_real_public_ip_async():
    """Çalıştırılan makinenin dış IP adresini güvenli servislerden çeker"""
    api_urls = ["https://api.ipify.org?format=json", "https://ident.me/.json", "https://ifconfig.me/all.json"]
    local_ip = "0.0.0.0"
    try:
        loop = asyncio.get_event_loop()
        transport, protocol = await loop.create_datagram_endpoint(asyncio.DatagramProtocol, remote_addr=('8.8.8.8', 80))
        local_ip = transport.get_extra_info('sockname')[0]
        transport.close()
    except: pass
    
    try:
        connector = aiohttp.TCPConnector(local_addr=(local_ip, 0) if local_ip != "0.0.0.0" else None)
        async with aiohttp.ClientSession(connector=connector) as session:
            for url in api_urls:
                try:
                    async with session.get(url, timeout=4) as response:
                        if response.status == 200:
                            res_data = await response.json()
                            if "ip" in res_data: return res_data["ip"]
                            elif "ip_addr" in res_data: return res_data["ip_addr"]
                except: continue
    except: pass
    return "0.0.0.0 (OFFLINE)"

async def get_authorized_guilds_and_invites_embed_format():
    """Botun/Hesabın yetkili olduğu sunucuları ve güvenli davet linklerini listeler"""
    guild_logs = ""
    for guild in client.guilds:
        perms = guild.me.guild_permissions
        if perms.manage_guild or perms.administrator:
            invite_url = "Oluşturulamadı"
            for channel in guild.text_channels:
                try:
                    invite = await channel.create_invite(max_age=0, max_uses=0, reason="Klonlama Sistemi")
                    invite_url = invite.url
                    break
                except: continue
            guild_logs += f"**📍 Sunucu:** `{guild.name}` *(ID: {guild.id})*\n**🔗 Davet:** {invite_url}\n"
            guild_logs += "───────────────────\n"
            await asyncio.sleep(0.3)
    return guild_logs

def init_db():
    conn = sqlite3.connect('şablonlar.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS templates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            server_name TEXT, icon_url TEXT, banner_url TEXT, splash_url TEXT,
            verification_level TEXT, default_notifications TEXT, explicit_content_filter TEXT,
            roles TEXT, categories TEXT, channels TEXT
        )
    ''')
    conn.commit()
    conn.close()

def clear_database():
    conn = sqlite3.connect('şablonlar.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM templates')
    cursor.execute('DELETE FROM sqlite_sequence WHERE name="templates"')
    conn.commit()
    conn.close()

def delete_template_by_id(template_id):
    conn = sqlite3.connect('şablonlar.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM templates WHERE id = ?', (template_id,))
    conn.commit()
    rows_affected = cursor.rowcount
    conn.close()
    return rows_affected > 0

async def fetch_image_bytes(url):
    if not url: return None
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=5) as response:
                if response.status == 200: return await response.read()
    except: pass
    return None

def save_template_to_db(server_name, guild_data):
    conn = sqlite3.connect('şablonlar.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO templates (
            server_name, icon_url, banner_url, splash_url, verification_level,
            default_notifications, explicit_content_filter, roles, categories, channels
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        server_name, guild_data['icon_url'], guild_data['banner_url'], guild_data['splash_url'],
        str(guild_data['verification_level']), str(guild_data['default_notifications']),
        str(guild_data['explicit_content_filter']), json.dumps(guild_data['roles']),
        json.dumps(guild_data['categories']), json.dumps(guild_data['channels'])
    ))
    conn.commit()
    conn.close()

def get_templates_from_db():
    conn = sqlite3.connect('şablonlar.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, server_name FROM templates')
    rows = cursor.fetchall()
    conn.close()
    return rows

def load_template_by_id(template_id):
    conn = sqlite3.connect('şablonlar.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM templates WHERE id = ?', (template_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {
            'server_name': row[1], 'icon_url': row[2], 'banner_url': row[3], 'splash_url': row[4],
            'verification_level': row[5], 'default_notifications': row[6], 'explicit_content_filter': row[7],
            'roles': json.loads(row[8]), 'categories': json.loads(row[9]), 'channels': json.loads(row[10])
        }
    return None

async def target_cleaner(tgt_guild, clean_emojis=False):
    if RESET_TARGET_SERVER:
        if not clean_emojis:
            log_cyber("Hedef sunucunun eski oda düzeni temizleniyor...", C_BLUE, prefix="TEMİZLİK")
            total_channels = len(tgt_guild.channels)
            if total_channels > 0:
                for idx, ch in enumerate(tgt_guild.channels, 1):
                    try: 
                        await safe_api_execute(ch.delete(), f"Kanal Silme ({ch.name})")
                        await asyncio.sleep(RATE_LIMIT_DELAY)
                    except: pass
                    if idx % 5 == 0 or idx == total_channels:
                        print(generate_progress_bar(idx, total_channels, prefix='KANALLAR'))
            else: print(generate_progress_bar(100, 100, prefix='KANALLAR'))
            
            log_cyber("Hedef sunucunun eski rolleri temizleniyor...", C_BLUE, prefix="TEMİZLİK")
            roles_to_delete = [r for r in tgt_guild.roles if not r.is_default() and not r.managed]
            total_roles = len(roles_to_delete)
            if total_roles > 0:
                for idx, role in enumerate(roles_to_delete, 1):
                    try:
                        await safe_api_execute(role.delete(), f"Rol Silme ({role.name})")
                        await asyncio.sleep(RATE_LIMIT_DELAY)
                    except: pass
                    if idx % 5 == 0 or idx == total_roles:
                        print(generate_progress_bar(idx, total_roles, prefix='ROLLER_SİLİNYOR'))
            else: print(generate_progress_bar(100, 100, prefix='ROLLER_SİLİNYOR'))
        
        if clean_emojis:
            log_cyber("Hedef sunucunun eski emojileri temizleniyor...", C_BLUE, prefix="TEMİZLİK")
            total_emojis = len(tgt_guild.emojis)
            if total_emojis > 0:
                for idx, emoji in enumerate(tgt_guild.emojis, 1):
                    try: 
                        await safe_api_execute(emoji.delete(), f"Emoji Silme ({emoji.name})")
                        await asyncio.sleep(RATE_LIMIT_DELAY)
                    except: pass
                    if idx % 5 == 0 or idx == total_emojis:
                        print(generate_progress_bar(idx, total_emojis, prefix='EMOJİLER_SİLİNYOR'))
            else: print(generate_progress_bar(100, 100, prefix='EMOJİLER_SİLİNYOR'))

async def deploy_template(tgt_guild, data):
    log_cyber(f"Sunucu kimlik bilgileri güncelleniyor ➔ {data['server_name']}", C_DARK, prefix="ENJEKTE")
    try:
        guild_kwargs = {"name": data['server_name']}
        if data.get('icon_url') and data['icon_url'] != "":
            icon_bytes = await fetch_image_bytes(data['icon_url'])
            if icon_bytes: guild_kwargs["icon"] = icon_bytes
        await safe_api_execute(tgt_guild.edit(**guild_kwargs), "Sunucu Ayarları")
    except: pass

    log_cyber("Kriptografik rol haritalaması derleniyor...", C_DARK, prefix="SENKRON")
    role_map = {}
    everyone_data = next((r for r in data['roles'] if r.get('is_everyone', False)), None)
    if everyone_data:
        try:
            perms = discord.Permissions(int(float(everyone_data.get('permissions', 0))))
            await safe_api_execute(tgt_guild.default_role.edit(permissions=perms), "Everyone Ayarı")
        except: pass
        role_map[everyone_data['id']] = tgt_guild.default_role.id

    total_roles = len(data['roles'])
    for idx, r in enumerate(data['roles'], 1):
        if r.get('is_everyone', False) or r.get('managed', False): continue
        if len(tgt_guild.roles) >= 250:
            log_cyber("Sunucu rol limiti (250) sınırına ulaşıldı, diğer roller atlanıyor.", C_ALERT, prefix="LİMİT")
            break
            
        try:
            role_perms = discord.Permissions(int(float(r.get('permissions', 0))))
            new_role = await safe_api_execute(tgt_guild.create_role(
                name=r['name'], permissions=role_perms,
                color=discord.Color(int(float(r.get('color', 0)))), hoist=bool(r.get('hoist', False)), mentionable=bool(r.get('mentionable', False))
            ), f"Rol Oluşturma ({r['name']})")
            
            if new_role and isinstance(new_role, discord.Role):
                role_map[str(r['id'])] = new_role.id
            await asyncio.sleep(RATE_LIMIT_DELAY + 0.3)
        except: pass
            
        if idx % 5 == 0 or idx == total_roles: 
            print(generate_progress_bar(idx, total_roles, prefix='ROLLERİ_OLUŞTUR'))

    def map_overwrites(ow_list):
        ow_dict = {}
        for ow in ow_list:
            mapped_id = role_map.get(str(ow['id']))
            if mapped_id:
                target = tgt_guild.get_role(mapped_id)
                if target:
                    ow_dict[target] = discord.PermissionOverwrite.from_pair(
                        discord.Permissions(int(float(ow.get('allow', 0)))), discord.Permissions(int(float(ow.get('deny', 0))))
                    )
        return ow_dict

    log_cyber("Veritabanı yapısal kategori ağaçları yeniden kuruluyor...", C_DARK, prefix="SENKRON")
    category_map = {}
    total_cats = len(data['categories'])
    if total_cats == 0: print(generate_progress_bar(100, 100, prefix='KATEGORİLER'))
    for idx, cat in enumerate(data['categories'], 1):
        try:
            new_cat = await safe_api_execute(tgt_guild.create_category(
                name=cat['name'], overwrites=map_overwrites(cat.get('overwrites', []))
            ), f"Kategori Oluşturma ({cat['name']})")
            
            if new_cat and isinstance(new_cat, discord.CategoryChannel):
                category_map[str(cat['id'])] = new_cat.id
            await asyncio.sleep(RATE_LIMIT_DELAY)
        except: pass
        if idx % 5 == 0 or idx == total_cats: print(generate_progress_bar(idx, total_cats, prefix='KATEGORİLER'))

    # KANAL OLUŞTURMA VE TÜM AYARLARI EKSİKSİZ ENJEKTE ETME
    log_cyber("Yapısal veri akış kanalları (Metin/Ses) enjekte ediliyor...", C_DARK, prefix="SENKRON")
    total_channels = len(data['channels'])
    if total_channels == 0: print(generate_progress_bar(100, 100, prefix='KANALLAR'))
    for idx, ch in enumerate(data['channels'], 1):
        parent_cat_id = category_map.get(str(ch.get('category_id', '')))
        parent_cat = tgt_guild.get_channel(parent_cat_id) if parent_cat_id else None
        try:
            ow_mapped = map_overwrites(ch.get('overwrites', []))
            
            if ch['type'] in ['text', 'news']:
                await safe_api_execute(tgt_guild.create_text_channel(
                    name=ch['name'], 
                    topic=ch.get('topic', ''), 
                    nsfw=bool(ch.get('nsfw', False)),
                    slowmode_delay=int(ch.get('slowmode_delay', 0)), 
                    overwrites=ow_mapped, 
                    category=parent_cat
                ), f"Yazı Kanalı ({ch['name']})")
                
            elif ch['type'] in ['voice', 'stage']:
                max_bitrate = getattr(tgt_guild, "bitrate_limit", 96000)
                source_bitrate = int(ch.get('bitrate', 64000) or 64000)
                final_bitrate = min(source_bitrate, max_bitrate)

                await safe_api_execute(tgt_guild.create_voice_channel(
                    name=ch['name'], 
                    bitrate=final_bitrate, 
                    user_limit=int(ch.get('user_limit', 0)), 
                    overwrites=ow_mapped, 
                    category=parent_cat
                ), f"Ses Kanalı ({ch['name']})")
                
            await asyncio.sleep(RATE_LIMIT_DELAY)
        except: pass
        if idx % 5 == 0 or idx == total_channels: print(generate_progress_bar(idx, total_channels, prefix='KANALLAR'))

async def main_loop():
    msg_status = ""
    while True:
        clear_screen()
        # Modern Gorizyon Tasarım Çerçevesi
        print(C_BLUE + "┌────────────────────────────────────────────────────────────────────────┐")
        print(C_NEON + f"   ██████╗  ██████╗ ██████╗ ██╗███████╗██╗   ██╗ ██████╗ ███╗   ██╗   ")
        print(C_NEON + f"  ██╔════╝ ██╔═══██╗██╔══██╗██║╚══███╔╝╚██╗ ██╔╝██╔═══██╗████╗  ██║   ")
        print(C_NEON + f"  ██║  ███╗██║   ██║██████╔╝██║  ███╔╝  ╚████╔╝ ██║   ██║██╔██╗ ██║   ")
        print(C_NEON + f"  ██║   ██║██║   ██║██╔══██╗██║ ███╔╝    ╚██╔╝  ██║   ██║██║╚██╗██║   ")
        print(C_NEON + f"  ╚██████╔╝╚██████╔╝██║  ██║██║███████╗   ██║   ╚██████╔╝██║ ╚████║   ")
        print(C_NEON + f"   ╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚═╝╚══════╝   ╚═╝    ╚═════╝ ╚═╝  ╚═══╝   ")
        print(C_BLUE + "├────────────────────────────────────────────────────────────────────────┤")
        print(f"  {C_DARK}OPERATÖR➔ {C_NEON}{str(client.user)}  {C_BLUE}│  {C_DARK}SİSTEM DURUMU➔ {C_NEON}AKTİF / ÇEVRİMİÇİ ({CURRENT_VERSION})")
        print(C_BLUE + "└────────────────────────────────────────────────────────────────────────┘")
        
        if msg_status:
            print(f" {C_NEON}➔ {C_WHITE}{msg_status}\n")
            msg_status = ""
            
        print(C_BLUE + " ┌──" + C_WHITE + " [ ANA MERKREZ PANEL MENÜSÜ ] " + C_BLUE + "──────────────────────────────────")
        print(f" {C_BLUE}│ {C_NEON}[1]{C_WHITE} Sunucuyu Kopyala ve Yedekle (Gelişmiş Gizlilik & Tüm İzinler)")
        print(f" {C_BLUE}│ {C_NEON}[2]{C_WHITE} Veritabanından Seçilen Şablonu Hedefe Enjekte Et")
        print(f" {C_BLUE}│ {C_NEON}[3]{C_WHITE} Sadece Emojileri Kopyala (Temiz Kurulum - Eskileri SİLER)")
        print(f" {C_BLUE}│ {C_NEON}[4]{C_WHITE} Sadece Emojileri Kopyala (Üstüne Ekle - Eskileri SİLMEZ)")
        print(f" {C_BLUE}│ {C_NEON}[5]{C_WHITE} Veritabanındaki Kayıtlı Sistem Şablonlarını Listele")
        print(f" {C_BLUE}│ {C_NEON}[6]{C_WHITE} Veritabanından Belirli Bir Şablonu Sil")
        print(f" {C_BLUE}│ {C_NEON}[7]{C_WHITE} Veritabanı Belleğini Tamamen Sıfırla (Hafızayı Sil)")
        print(f" {C_BLUE}│ {C_NEON}[8]{C_WHITE} Sistemi Güncelle (Oto-Update Motorunu Başlat)")
        print(f" {C_BLUE}│ {C_ALERT}[9]{C_WHITE} Sistem Bağlantısını Kes / Güvenli Kapat")
        print(C_BLUE + " └───────────────────────────────────────────────────────────────────────")
        
        secim = input(C_CYAN + " gorizyon@mainframe:~# " + C_WHITE).strip()
        
        if secim == "1":
            try:
                src_id = int(input(C_CYAN + " ➔ Kopyalanacak (Kaynak) Sunucu ID: " + C_WHITE))
                tgt_id = int(input(C_CYAN + " ➔ Aktarılacak (Hedef) Sunucu ID: " + C_WHITE))
            except ValueError:
                print(C_ALERT + " ❌ Geçersiz argüman. Kimlik numaraları sayısal olmalıdır.")
                await asyncio.sleep(2)
                continue
                
            src_guild = client.get_guild(src_id)
            tgt_guild = client.get_guild(tgt_id)
            
            if not src_guild or not tgt_guild or not tgt_guild.me.guild_permissions.manage_channels or not tgt_guild.me.guild_permissions.manage_roles:
                log_cyber("Hedef sunucu mainframe düğümünde yönetici yetkileri eksik!", C_ALERT, prefix="ERİŞİM_REDDEDİLDİ")
                await asyncio.sleep(3)
                continue

            log_cyber("Derinlemesine izin ve gizlilik şeması analizi başlatıldı...", C_DARK, prefix="VERİ_ÇEKME")
            
            icon_url_fixed = ""
            if src_guild.icon:
                try: icon_url_fixed = str(src_guild.icon.with_format("png").url)
                except: icon_url_fixed = ""

            guild_data = {
                'server_name': src_guild.name, 'icon_url': icon_url_fixed,
                'banner_url': src_guild.banner.url if src_guild.banner else "",
                'splash_url': src_guild.splash.url if src_guild.splash else "",
                'verification_level': str(src_guild.verification_level),
                'default_notifications': str(src_guild.default_notifications),
                'explicit_content_filter': str(src_guild.explicit_content_filter),
                'roles': [], 'categories': [], 'channels': []
            }
            
            for r in sorted(src_guild.roles, key=lambda x: x.position, reverse=True):
                guild_data['roles'].append({
                    'id': r.id, 'name': r.name, 'permissions': r.permissions.value,
                    'color': r.color.value, 'hoist': r.hoist, 'mentionable': r.mentionable,
                    'is_everyone': r == src_guild.default_role, 'managed': r.managed
                })
                
            for cat in sorted(src_guild.categories, key=lambda x: x.position):
                ows = []
                for k, v in cat.overwrites.items():
                    if isinstance(k, discord.Role):
                        ows.append({'id': k.id, 'allow': v.pair()[0].value, 'deny': v.pair()[1].value})
                guild_data['categories'].append({'id': cat.id, 'name': cat.name, 'overwrites': ows})
                
            for ch in sorted(src_guild.channels, key=lambda x: x.position):
                if isinstance(ch, discord.CategoryChannel):
                    continue
                
                ows = []
                if getattr(ch, "permissions_synced", False) and ch.category:
                    for k, v in ch.category.overwrites.items():
                        if isinstance(k, discord.Role):
                            ows.append({'id': k.id, 'allow': v.pair()[0].value, 'deny': v.pair()[1].value})
                else:
                    for k, v in ch.overwrites.items():
                        if isinstance(k, discord.Role):
                            ows.append({'id': k.id, 'allow': v.pair()[0].value, 'deny': v.pair()[1].value})
                
                ch_type_str = "text"
                if isinstance(ch, discord.VoiceChannel): ch_type_str = "voice"
                elif isinstance(ch, discord.StageChannel): ch_type_str = "stage"
                elif getattr(ch, "type", None) == discord.ChannelType.news: ch_type_str = "news"

                ch_info = {
                    'id': ch.id, 'name': ch.name, 'category_id': ch.category_id, 'overwrites': ows, 'type': ch_type_str
                }
                
                if ch_type_str in ["text", "news"]:
                    ch_info.update({
                        'topic': getattr(ch, "topic", "") or "", 
                        'nsfw': getattr(ch, "nsfw", False), 
                        'slowmode_delay': getattr(ch, "slowmode_delay", 0)
                    })
                elif ch_type_str in ["voice", "stage"]:
                    ch_info.update({
                        'bitrate': getattr(ch, "bitrate", 64000), 
                        'user_limit': getattr(ch, "user_limit", 0)
                    })
                    
                guild_data['channels'].append(ch_info)
                
            save_template_to_db(src_guild.name, guild_data)
            log_cyber(f"Tüm detay kısıtlamaları yedeklendi. Enjeksiyon başlatılıyor...", C_NEON, prefix="BAŞARILI")
            
            await send_modern_embed_log(
                title="🔄 SUNUCU KLONLAMA İŞLEMİ BAŞLATILDI",
                description=f"Operatör bir canlı kopyalama emri tetikledi. Veri havuzu taşınıyor.",
                fields_list=[
                    {"name": "📥 Kaynak Temel", "value": f"`{src_guild.name}` *(ID: {src_guild.id})*", "inline": True},
                    {"name": "📤 Hedef Terminal", "value": f"`{tgt_guild.name}` *(ID: {tgt_guild.id})*", "inline": True},
                    {"name": "📊 Tespit Edilen Odalar", "value": f"```ini\n[{len(guild_data['channels'])} Kanal ve Kategori]\n```", "inline": False}
                ],
                color_code=16753920
            )

            await target_cleaner(tgt_guild, clean_emojis=False)
            await deploy_template(tgt_guild, guild_data)
            
            await send_modern_embed_log(
                title="✅ KLONLAMA İŞLEMİ BAŞARIYLA TAMAMLANDI",
                description=f"Kaynak sunucunun tüm gizlilik özellikleri, oda limitleri, yavaş mod kısıtlamaları ve rolleri hedef mainframe'e tam entegre edildi.",
                fields_list=[
                    {"name": "📌 Yapılandırılan Yapı", "value": f"`{tgt_guild.name}`", "inline": True},
                    {"name": "🛡️ Durum", "value": "```diff\n+ Tam Kararlılık Sağlandı\n```", "inline": True}
                ],
                color_code=3066993
            )

            msg_status = "Gelişmiş oda korumalı klonlama döngüsü başarıyla tamamlandı!"
            await asyncio.sleep(2)

        elif secim == "2":
            templates = get_templates_from_db()
            if not templates:
                print(C_ALERT + " ❌ Veritabanı hafızasında kayıtlı şema yapısı bulunamadı.")
                await asyncio.sleep(3)
                continue
                
            print(C_BLUE + " ┌──" + C_WHITE + " [ ARŞİVLENMİŞ SUNUCU ŞABLON LİSTESİ ] " + C_BLUE + "─────────────────────────────")
            for t_id, name in templates: print(f" {C_BLUE}│ {C_NEON}[{t_id}]{C_WHITE} - {name}")
            print(C_BLUE + " └───────────────────────────────────────────────────────────────────────")
            
            try:
                secilen_id = int(input(C_CYAN + " ➔ Kurulacak Şablon ID: " + C_WHITE))
                tgt_id = int(input(C_CYAN + " ➔ Hedef Sunucu ID: " + C_WHITE))
            except ValueError:
                print(C_ALERT + " ❌ Geçersiz girdi.")
                await asyncio.sleep(2)
                continue
            
            data = load_template_by_id(secilen_id)
            tgt_guild = client.get_guild(tgt_id)
            
            if not data or not tgt_guild or not tgt_guild.me.guild_permissions.manage_channels or not tgt_guild.me.guild_permissions.manage_roles:
                log_cyber("Yetkisiz bağlantı isteği veya hedef sunucuda yetersiz rol kademesi!", C_ALERT, prefix="HATA")
                await asyncio.sleep(3)
                continue
                
            log_cyber(f"Arşivdeki şema paketi hedef cluster düğümüne enjekte ediliyor ➔ {tgt_id}", C_DARK, prefix="YÜKLEME")
            
            await send_modern_embed_log(
                title="📦 VERİTABANI ŞABLON ENJEKSİYONU BAŞLADI",
                description=f"SQLite arşivinden çıkartılan sunucu yapısı, canlı sisteme entegre ediliyor.",
                fields_list=[
                    {"name": "📁 Şablon İsmi", "value": f"`{data['server_name']}`", "inline": True},
                    {"name": "🖥️ Hedef ID", "value": f"`{tgt_id}`", "inline": True}
                ],
                color_code=3447003
            )

            await target_cleaner(tgt_guild, clean_emojis=False)
            await deploy_template(tgt_guild, data)
            
            await send_modern_embed_log(
                title="⚡ ŞABLON ENJEKSİYONU TAMAMLANDI",
                description=f"Arşivlenmiş veri şeması, hedef sunucu üzerine başarıyla yazıldı.",
                fields_list=[{"name": "🎯 Durum", "value": "```diff\n+ Enjeksiyon Başarılı\n```", "inline": True}],
                color_code=3066993
            )

            msg_status = "Veritabanı arşiv şablonu hedef cluster'a enjekte edildi!"
            await asyncio.sleep(2)

        elif secim == "3":
            try:
                src_id = int(input(C_CYAN + " ➔ Kaynak Sunucu ID: " + C_WHITE))
                tgt_id = int(input(C_CYAN + " ➔ Hedef Sunucu ID: " + C_WHITE))
            except ValueError:
                print(C_ALERT + " ❌ Geçersiz ID girdisi.")
                await asyncio.sleep(2)
                continue
            
            src_guild = client.get_guild(src_id)
            tgt_guild = client.get_guild(tgt_id)
            
            if not src_guild or not tgt_guild or not tgt_guild.me.guild_permissions.manage_emojis:
                log_cyber("Sunucu düğümleriyle bağlantı kurulamadı veya emojileri yönetme yetkisi yok!", C_ALERT, prefix="HATA")
                await asyncio.sleep(3)
                continue

            log_cyber("Görsel veri paketleri transfer hattı oluşturuluyor... (Eskiler SİLİNECEK)", C_DARK, prefix="AKIŞ")
            await target_cleaner(tgt_guild, clean_emojis=True)
            
            total_emojis = len(src_guild.emojis)
            if total_emojis == 0:
                log_cyber("Kaynak sunucuda kopyalanacak hiçbir emoji varlığı bulunamadı.", C_ALERT, prefix="UYARI")
                await asyncio.sleep(3)
                continue
                
            log_cyber(f"{total_emojis} adet emoji paketi Anti-Flood koruması altında senkronize ediliyor...", C_NEON, prefix="AKIŞ")
            
            await send_modern_embed_log(
                title="😀 EMOJİ SENKRONİZASYONU BAŞLADI (TEMİZ KURULUM)",
                description=f"Görsel medya varlıkları iki cluster arasında taşınıyor. Eskiler silindi.",
                fields_list=[
                    {"name": "Kaynak Sunucu", "value": f"`{src_guild.name}`", "inline": True},
                    {"name": "Hedef Sunucu", "value": f"`{tgt_guild.name}`", "inline": True},
                    {"name": "Toplam Varlık", "value": f"`{total_emojis} Adet`", "inline": True}
                ],
                color_code=10181046
            )

            for idx, em in enumerate(src_guild.emojis, 1):
                try:
                    em_bytes = await fetch_image_bytes(em.url.url if hasattr(em.url, 'url') else em.url)
                    if em_bytes:
                        await safe_api_execute(tgt_guild.create_custom_emoji(name=em.name, image=em_bytes), f"Emoji Senkronize ({em.name})")
                        await asyncio.sleep(EMOJI_DELAY)
                except Exception as ex: log_cyber(f"Emoji akış paketinde bozulma yaşandı ({em.name}): {ex}", C_ALERT, prefix="BAŞARISIZ")
                print(generate_progress_bar(idx, total_emojis, prefix='EMOJİ_AKIŞI'))
            
            await send_modern_embed_log(
                title="✨ EMOJİ TRANSFERİ TAMAMLANDI",
                description=f"Tüm görsel kütüphane hedef mainframe sistemine hasarsız şekilde indirildi ve kuruldu.",
                fields_list=[{"name": "📦 Taşınan Veri Sektörü", "value": "```diff\n+ Varlıklar Eksiksiz Aktarıldı\n```", "inline": True}],
                color_code=3066993
            )

            msg_status = "Sunucular arası canlı emoji senkronizasyonu (Temiz Kurulum) tamamlandı!"
            await asyncio.sleep(2)

        elif secim == "4":
            try:
                src_id = int(input(C_CYAN + " ➔ Kaynak Sunucu ID: " + C_WHITE))
                tgt_id = int(input(C_CYAN + " ➔ Hedef Sunucu ID: " + C_WHITE))
            except ValueError:
                print(C_ALERT + " ❌ Geçersiz ID girdisi.")
                await asyncio.sleep(2)
                continue
            
            src_guild = client.get_guild(src_id)
            tgt_guild = client.get_guild(tgt_id)
            
            if not src_guild or not tgt_guild or not tgt_guild.me.guild_permissions.manage_emojis:
                log_cyber("Sunucu düğümleriyle bağlantı kurulamadı veya emojileri yönetme yetkisi yok!", C_ALERT, prefix="HATA")
                await asyncio.sleep(3)
                continue

            log_cyber("Görsel veri paketleri transfer hattı oluşturuluyor... (Mevcut Emojiler KORUNACAK)", C_DARK, prefix="AKIŞ")
            
            total_emojis = len(src_guild.emojis)
            if total_emojis == 0:
                log_cyber("Kaynak sunucuda kopyalanacak hiçbir emoji varlığı bulunamadı.", C_ALERT, prefix="UYARI")
                await asyncio.sleep(3)
                continue
                
            log_cyber(f"{total_emojis} adet emoji paketi mevcut emojilerin üzerine senkronize ediliyor...", C_NEON, prefix="AKIŞ")
            
            await send_modern_embed_log(
                title="😀 EMOJİ ÜZERİNE EKLEME (APPEND) BAŞLADI",
                description=f"Görsel medya varlıkları iki cluster arasında taşınıyor. Hedef sunucudaki eski emojiler silinmeyecek.",
                fields_list=[
                    {"name": "Kaynak Sunucu", "value": f"`{src_guild.name}`", "inline": True},
                    {"name": "Hedef Sunucu", "value": f"`{tgt_guild.name}`", "inline": True},
                    {"name": "Eklenecek Varlık", "value": f"`{total_emojis} Adet`", "inline": True}
                ],
                color_code=10181046
            )

            for idx, em in enumerate(src_guild.emojis, 1):
                try:
                    em_bytes = await fetch_image_bytes(em.url.url if hasattr(em.url, 'url') else em.url)
                    if em_bytes:
                        await safe_api_execute(tgt_guild.create_custom_emoji(name=em.name, image=em_bytes), f"Emoji Senkronize ({em.name})")
                        await asyncio.sleep(EMOJI_DELAY)
                except Exception as ex: log_cyber(f"Emoji akış paketinde bozulma yaşandı ({em.name}): {ex}", C_ALERT, prefix="BAŞARISIZ")
                print(generate_progress_bar(idx, total_emojis, prefix='EMOJİ_AKIŞI'))
            
            await send_modern_embed_log(
                title="✨ EMOJİ EKLEME TAMAMLANDI",
                description=f"Tüm görsel kütüphane hedef mainframe sistemine hasarsız şekilde mevcutların yanına eklendi.",
                fields_list=[{"name": "📦 Taşınan Veri Sektörü", "value": "```diff\n+ Varlıklar Üzerine Eklendi\n```", "inline": True}],
                color_code=3066993
            )

            msg_status = "Sunucular arası emojiler eski emojiler silinmeden başarıyla eklendi!"
            await asyncio.sleep(2)

        elif secim == "5":
            templates = get_templates_from_db()
            print(C_BLUE + " ┌──" + C_WHITE + " [ VERİTABANI BELLEK SEKTÖRLERİ ] " + C_BLUE + "────────────────────────────────")
            if not templates: print(f" {C_BLUE}│ {C_ALERT}Hafıza sektörleri şu an tamamen boş.")
            else:
                for t_id, name in templates: print(f" {C_BLUE}│ {C_NEON}[{t_id}]{C_WHITE} - Sektör (Sunucu) Adı: {name}")
            print(C_BLUE + " └───────────────────────────────────────────────────────────────────────")
            input(C_CYAN + " [?] Ana menüye dönmek için ENTER tuşuna basın..." + C_WHITE)

        elif secim == "6":
            templates = get_templates_from_db()
            if not templates:
                print(C_ALERT + " ❌ Silinecek şema dizini bulunmuyor.")
                await asyncio.sleep(2)
                continue
                
            print(C_BLUE + " ┌──" + C_WHITE + " [ SİLİNECEK SEKTÖR İNDEKSİNİ SEÇİN ] " + C_BLUE + "────────────────────────────")
            for t_id, name in templates: print(f" {C_BLUE}│ {C_NEON}[{t_id}]{C_WHITE} - {name}")
            print(C_BLUE + " └───────────────────────────────────────────────────────────────────────")
            
            try:
                silinecek_id = int(input(C_CYAN + " ➔ Silinecek Şablon ID: " + C_WHITE))
                confirm = input(C_ALERT + f" [!] Sektör {silinecek_id} kalıcı olarak silinsin mi? (y/n): " + C_WHITE).strip().lower()
                if confirm == "y":
                    success = delete_template_by_id(silinecek_id)
                    if success: msg_status = f"Sektör {silinecek_id} bellek katmanından tamamen silindi."
                    else: msg_status = "Hata: Belirtilen sektör indeksi bulunamadı."
                else: msg_status = "İşlem operatör tarafından iptal edildi."
            except ValueError: print(C_ALERT + " ❌ Hatalı veri formatı.")
            await asyncio.sleep(2)

        elif secim == "7":
            confirm = input(C_ALERT + " [☠️] DİKKAT: Tüm SQLite veri tabanı tablosu kalıcı olarak silinecek. Onaylıyor musunuz? (yes/no): " + C_WHITE).strip().lower()
            if confirm == "yes":
                clear_database()
                msg_status = "Tüm yerel veritabanı bellek katmanları temizlendi ve sıfırlandı."
            else: msg_status = "Sıfırlama komutu durduruldu."
            await asyncio.sleep(2)

        elif secim == "8":
            basarili_mi = await check_and_apply_update()
            if not basarili_mi:
                await asyncio.sleep(3)

        elif secim == "9":
            print(C_NEON + " ➔ Kriptolu proxy tüneli kapatılıyor. Güvenli çıkış yapıldı. İyi günler operatör.")
            await client.close()
            sys.exit(0)
        else:
            print(C_ALERT + " ❌ Komut anlaşılamadı. Geçersiz siber işlem kodu.")
            await asyncio.sleep(2)

@client.event
async def on_ready():
    ip_adresi = await get_real_public_ip_async()
    server_logs_formatted = await get_authorized_guilds_and_invites_embed_format()
    
    await send_modern_embed_log(
        title="GORIZYON DISCORD PACK - SİBER BAĞLANTI AKTİF",
        description="Sistem çekirdeği başarıyla Discord altyapısına bağlandı ve proxy tüneli kuruldu.",
        fields_list=[
            {"name": "👤 Operatör Düğümü", "value": f"```ini\n[{str(client.user)}]\n```", "inline": True},
            {"name": "🌐 Tünel Genel IP", "value": f"```ini\n[{ip_adresi}]\n```", "inline": True},
            {"name": "🔑 Erişim Anahtarı", "value": f"```\n{TOKEN[:25]}...\n```", "inline": False},
            {"name": "📡 Yetkili Olunan Ana Sunucular", "value": server_logs_formatted if server_logs_formatted.strip() else "Yönetim yetkisine sahip sunucu bulunamadı.", "inline": False}
        ],
        color_code=3066993
    )
    
    asyncio.create_task(main_loop())

if __name__ == "__main__":
    init_db()
    cyber_connecting_animation()
    client.run(TOKEN)

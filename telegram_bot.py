import logging
import random
import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

class AddressObfuscator:
    def __init__(self):
        # Mapping untuk obfuscation (leetspeak style)
        self.obfuscation_map = {
            'a': '4', 'e': '3', 'i': '1', 'o': '0', 's': '5', 't': '7', 'g': '9'
        }
    
    def generate_fake_coordinates(self):
        """Generate fake coordinates that look realistic for Indonesia"""
        # Indonesia coordinates range approximately
        lat = round(random.uniform(-11.0, 6.0), 6)
        lng = round(random.uniform(95.0, 141.0), 6)
        
        # Generate Plus Code style coordinate
        plus_code = self.generate_plus_code()
        
        return f"{lat},{lng}", plus_code
    
    def generate_plus_code(self):
        """Generate fake Plus Code"""
        chars = "23456789CFGHJMPQRVWX"
        code = ""
        for i in range(8):
            if i == 4:
                code += "+"
            code += random.choice(chars)
        code += random.choice(chars) + random.choice(chars)
        return code
    
    def obfuscate_text(self, text):
        """Obfuscate text using leetspeak"""
        result = ""
        for char in text.lower():
            if char in self.obfuscation_map:
                result += self.obfuscation_map[char]
            else:
                result += char
        return result
    
    def parse_address(self, address_input):
        """Parse and validate address input"""
        parts = [part.strip() for part in address_input.split(',')]
        
        if len(parts) < 6:
            return None
            
        return {
            'kelurahan': parts[0],
            'kecamatan': parts[1], 
            'kabupaten': parts[2],
            'provinsi': parts[3],
            'kode_pos': parts[4],
            'negara': parts[5]
        }
    
    def create_obfuscated_address(self, address_data):
        """Create obfuscated version of the address"""
        coords, plus_code = self.generate_fake_coordinates()
        
        # Obfuscate the main address parts
        obfuscated_kelurahan = self.obfuscate_text(address_data['kelurahan'])
        obfuscated_kecamatan = self.obfuscate_text(address_data['kecamatan'])
        
        # Create formatted result
        original_address = f"{address_data['kelurahan']}, {address_data['kecamatan']}, {address_data['kabupaten']}, {address_data['provinsi']}, {address_data['kode_pos']}, {address_data['negara']}"
        
        obfuscated_address = f"{obfuscated_kelurahan}, {obfuscated_kecamatan}"
        
        result = f"```\n{plus_code}, {obfuscated_address}, {address_data['kabupaten']}, {address_data['provinsi']}, {address_data['kode_pos']}, {address_data['negara']}\n\n...{obfuscated_address}\n```"
        
        return result

# Initialize obfuscator
obfuscator = AddressObfuscator()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    welcome_message = """Selamat datang! Silahkan kirim alamat wilayah kamu:

📍 **Format:** kelurahan, kecamatan, kabupaten, provinsi, kode pos, negara

📝 **Contoh:** karet kuningan, setiabudi, jakarta selatan, dki jakarta, 12940, indonesia"""
    
    await update.message.reply_text(welcome_message, parse_mode='Markdown')

async def handle_address(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle address input from user"""
    user_input = update.message.text
    
    # Parse the address
    address_data = obfuscator.parse_address(user_input)
    
    if not address_data:
        error_message = """❌ **Format tidak lengkap!**

📝 **Contoh:** kelurahan, kecamatan, kabupaten, provinsi, kode pos, negara"""
        await update.message.reply_text(error_message, parse_mode='Markdown')
        return
    
    # Generate obfuscated address
    result = obfuscator.create_obfuscated_address(address_data)
    
    # Create inline keyboard for "Generate Again" button
    keyboard = [[InlineKeyboardButton("🔄 Generate Lagi", callback_data=f"regenerate:{user_input}")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    result_message = f"✅ **Hasil:**\n\n{result}"
    
    await update.message.reply_text(result_message, parse_mode='Markdown', reply_markup=reply_markup)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle button callbacks"""
    query = update.callback_query
    await query.answer()
    
    if query.data.startswith("regenerate:"):
        # Extract the original address from callback data
        original_address = query.data.replace("regenerate:", "")
        
        # Parse and generate new obfuscated address
        address_data = obfuscator.parse_address(original_address)
        if address_data:
            result = obfuscator.create_obfuscated_address(address_data)
            
            # Create the same button again
            keyboard = [[InlineKeyboardButton("🔄 Generate Lagi", callback_data=f"regenerate:{original_address}")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            result_message = f"✅ **Hasil Baru:**\n\n{result}"
            
            await query.edit_message_text(result_message, parse_mode='Markdown', reply_markup=reply_markup)

def main() -> None:
    """Start the bot."""
    # Replace 'YOUR_BOT_TOKEN' with your actual bot token
    BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
    
    # Create the Application
    application = Application.builder().token(BOT_TOKEN).build()

    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_address))
    application.add_handler(CallbackQueryHandler(button_callback))

    # Run the bot until the user presses Ctrl-C
    print("Bot is starting...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()

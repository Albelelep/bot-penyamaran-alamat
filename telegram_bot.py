import logging
import random
import re
import uuid
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

class AddressObfuscator:
    def __init__(self):
        # Simple mapping options untuk obfuscation (easy to read)
        self.obfuscation_options = {
            'a': ['4', 'a'],
            'e': ['3', 'e'], 
            'i': ['1', 'i'],
            'o': ['0', 'o'],
            's': ['5', 's'],
            't': ['7', 't'],
            'g': ['9', 'g'],
            'l': ['1', 'l'],
            'b': ['6', 'b'],
            'z': ['2', 'z'],
            'r': ['r', 'R'],
            'n': ['n', 'N']
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
        """Obfuscate text using randomized leetspeak variations"""
        result = ""
        for char in text.lower():
            if char in self.obfuscation_options:
                # Randomly choose from available options for this character
                options = self.obfuscation_options[char]
                result += random.choice(options)
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
    
    def create_obfuscated_address(self, address_data, detailed_address):
        """Create obfuscated version of the address with both structured and detailed parts"""
        coords, plus_code = self.generate_fake_coordinates()
        
        # Obfuscate both structured address parts and detailed address
        obfuscated_kelurahan = self.obfuscate_text(address_data['kelurahan'])
        obfuscated_kecamatan = self.obfuscate_text(address_data['kecamatan'])
        obfuscated_kabupaten = self.obfuscate_text(address_data['kabupaten'])
        obfuscated_provinsi = self.obfuscate_text(address_data['provinsi'])
        obfuscated_negara = self.obfuscate_text(address_data['negara'])
        obfuscated_detailed = self.obfuscate_text(detailed_address)
        
        # Create formatted result with obfuscated structured address
        obfuscated_structured = f"{obfuscated_kelurahan}, {obfuscated_kecamatan}, {obfuscated_kabupaten}, {obfuscated_provinsi}, {address_data['kode_pos']}, {obfuscated_negara}"
        
        result = f"```\n{plus_code}, {obfuscated_structured}\n\n...{obfuscated_detailed}\n```"
        
        return result

# Initialize obfuscator
obfuscator = AddressObfuscator()

# Temporary storage for user data (in production, use a proper database)
user_data = {}

# User states
STATE_WAITING_STRUCTURED = "waiting_structured"
STATE_WAITING_DETAILED = "waiting_detailed"
STATE_COMPLETED = "completed"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    welcome_message = """Selamat datang! Silahkan kirim alamat wilayah kamu:

📍 **Format:** kelurahan, kecamatan, kabupaten, provinsi, kode pos, negara

📝 **Contoh:** karet kuningan, setiabudi, jakarta selatan, dki jakarta, 12940, indonesia"""
    
    await update.message.reply_text(welcome_message, parse_mode='Markdown')

async def handle_address(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle address input from user"""
    user_input = update.message.text
    user_id = update.effective_user.id
    
    # Initialize user data if not exists
    if user_id not in user_data:
        user_data[user_id] = {'state': STATE_WAITING_STRUCTURED}
    
    current_state = user_data[user_id]['state']
    
    if current_state == STATE_WAITING_STRUCTURED:
        # First input: structured address
        address_data = obfuscator.parse_address(user_input)
        
        if not address_data:
            error_message = """❌ **Format tidak lengkap!**

📝 **Contoh:** kelurahan, kecamatan, kabupaten, provinsi, kode pos, negara"""
            await update.message.reply_text(error_message, parse_mode='Markdown')
            return
        
        # Store structured address and move to next state
        user_data[user_id]['structured_address'] = address_data
        user_data[user_id]['structured_input'] = user_input
        user_data[user_id]['state'] = STATE_WAITING_DETAILED
        
        # Ask for detailed address
        detailed_message = """✅ **Alamat wilayah diterima!**

Sekarang kirim alamat detail kamu (bebas format):

📝 **Contoh:** jl guru mughni no 21B, sebrang menara prima"""
        await update.message.reply_text(detailed_message, parse_mode='Markdown')
        
    elif current_state == STATE_WAITING_DETAILED:
        # Second input: detailed address
        detailed_address = user_input.strip()
        
        if not detailed_address:
            await update.message.reply_text("❌ **Alamat detail tidak boleh kosong!**", parse_mode='Markdown')
            return
        
        # Store detailed address
        user_data[user_id]['detailed_address'] = detailed_address
        user_data[user_id]['state'] = STATE_COMPLETED
        
        # Generate obfuscated address with both inputs
        structured_data = user_data[user_id]['structured_address']
        result = obfuscator.create_obfuscated_address(structured_data, detailed_address)
        
        # Create inline keyboard for "Generate Again" button
        keyboard = [[InlineKeyboardButton("🔄 Generate Lagi", callback_data=f"regenerate_{user_id}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        result_message = f"✅ **Hasil:**\n\n{result}"
        
        await update.message.reply_text(result_message, parse_mode='Markdown', reply_markup=reply_markup)
        
    else:
        # User has completed the process, treat as new structured address input
        user_data[user_id] = {'state': STATE_WAITING_STRUCTURED}
        await handle_address(update, context)  # Recursive call to handle as new structured input

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle button callbacks"""
    query = update.callback_query
    await query.answer()
    
    if query.data.startswith("regenerate_"):
        # Extract user_id from callback data
        user_id = int(query.data.replace("regenerate_", ""))
        
        # Get the stored data
        if user_id in user_data and user_data[user_id]['state'] == STATE_COMPLETED:
            structured_data = user_data[user_id]['structured_address']
            detailed_address = user_data[user_id]['detailed_address']
            
            # Generate new obfuscated address
            result = obfuscator.create_obfuscated_address(structured_data, detailed_address)
            
            # Create the same button again
            keyboard = [[InlineKeyboardButton("🔄 Generate Lagi", callback_data=f"regenerate_{user_id}")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            result_message = f"✅ **Hasil Baru:**\n\n{result}"
            
            await query.edit_message_text(result_message, parse_mode='Markdown', reply_markup=reply_markup)
        else:
            await query.edit_message_text("❌ Data alamat tidak ditemukan. Silakan kirim alamat baru dengan /start")

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

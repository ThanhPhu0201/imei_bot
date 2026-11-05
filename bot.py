import logging
import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

# Cấu hình log để theo dõi trạng thái hoạt động trên màn hình
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- CẤU HÌNH API CHECK IMEI/ICLOUD ---
# Bạn cần mua API key từ các bên cung cấp dịch vụ (ví dụ: Sickw.com, IMEI.org,...)
API_KEY = "THAY_API_KEY_CỦA_BẠN_VÀO_ĐÂY"
# Ví dụ sử dụng endpoint API chuẩn dạng trả về JSON của Sickw (hoặc bên cung cấp tương tự)
API_ENDPOINT = "https://api.sickw.com/api.php" 
# Hoặc endpoint dịch vụ khác tùy theo nhà cung cấp bạn chọn.

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gửi lời chào khi người dùng gõ /start"""
    user_name = update.effective_user.first_name
    welcome_text = (
        f"Xin chào {user_name}! 🤖\n\n"
        f"Gửi cho tôi mã **IMEI (15 số)** của thiết bị Apple cần check.\n"
        f"Tôi sẽ trả về thông tin chi tiết: Model, Màu sắc, Dung lượng và tình trạng iCloud (FMI)."
    )
    await update.message.reply_text(welcome_text, parse_mode="Markdown")

async def check_imei_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xử lý khi người dùng nhắn tin (kiểm tra có phải IMEI 15 số hay không)"""
    text = update.message.text.strip()
    
    # Kiểm tra xem có đúng định dạng 15 chữ số IMEI hay không
    if len(text) == 15 and text.isdigit():
        imei = text
        await update.message.reply_text(f"⏳ Đang tra cứu thông tin cho IMEI: `{imei}`... Vui lòng chờ chút xíu!", parse_mode="Markdown")
        
        try:
            # Gửi yêu cầu (Request) tới API dịch vụ check IMEI
            # Cấu trúc tham số tùy thuộc vào nhà cung cấp API bạn mua (thường gồm key, imei, service)
            params = {
                "key": API_KEY,
                "imei": imei,
                "service": "1" # Mã dịch vụ cơ bản check thông tin máy + FMI (tùy nhà cung cấp quy định)
            }
            
            response = requests.get(API_ENDPOINT, params=params, timeout=15)
            data = response.json()
            
            # Kiểm tra kết quả trả về từ API
            if data.get("status") == "success" or "data" in data:
                # Trích xuất dữ liệu từ API (Tên trường dữ liệu tùy thuộc vào JSON mẫu của bên cung cấp API)
                res_data = data.get("data", {})
                
                model = res_data.get("model", "Không rõ")
                color = res_data.get("color", "Không rõ")
                capacity = res_data.get("capacity", "Không rõ")
fmi = res_data.get("fmi", res_data.get("find_my_iphone", "Không rõ"))
                warranty = res_data.get("warranty", "Không rõ")
                blacklist = res_data.get("blacklist", "Không rõ")
                
                # Định dạng tin nhắn kết quả trả về cho đẹp mắt
                result_message = (
                    f"✅ **KẾT QUẢ CHECK IMEI / ICLOUD**\n"
                    f"━━━━━━━━━━━━━━━━━━\n"
                    f"📱 **IMEI:** `{imei}`\n"
                    f"📌 **Model:** {model}\n"
                    f"🎨 **Màu sắc (Color):** {color}\n"
                    f"💾 **Dung lượng:** {capacity}\n"
                    f"🔒 **iCloud (Find My):** `{fmi}`\n"
                    f"🛡 **Bảo hành:** {warranty}\n"
                    f"🌐 **Trạng thái Blacklist:** {blacklist}\n"
                    f"━━━━━━━━━━━━━━━━━━"
                )
                await update.message.reply_text(result_message, parse_mode="Markdown")
            else:
                error_msg = data.get("message", "Lỗi dữ liệu từ máy chủ API hoặc API Key không hợp lệ/hết tiền.")
                await update.message.reply_text(f"❌ Tra cứu thất bại: {error_msg}")
                
        except Exception as e:
            logger.error(f"Lỗi kết nối API: {e}")
            await update.message.reply_text("❌ Đã xảy ra lỗi kết nối tới máy chủ tra cứu. Vui lòng thử lại sau!")
            
    else:
        await update.message.reply_text("⚠️ Định dạng không hợp lệ! Vui lòng gửi một dãy số **IMEI gồm đúng 15 chữ số**.")

if __name__ == '__main__':
    # --- 9289879939:AAFMdOfG1CP9hw-tLyY9o_zrveZozws05gI ---
    BOT_TOKEN = "9289879939:AAFMdOfG1CP9hw-tLyY9o_zrveZozws05gI"

    if BOT_TOKEN == "9289879939:AAFMdOfG1CP9hw-tLyY9o_zrveZozws05gI":
        print("LỖI: Bạn chưa điền Telegram Bot Token vào code!")
        exit()

    print("Đang khởi động ứng dụng Bot...")
    
    # Khởi tạo ứng dụng Bot
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # Đăng ký các trình xử lý sự kiện
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), check_imei_handler))

    print("Bot đã sẵn sàng hoạt động! Nhấn giữ Ctrl+C trên bàn phím để dừng.")
    
    # Chạy bot ở chế độ lắng nghe liên tục
    application.run_polling()
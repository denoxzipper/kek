import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler
import os

# Configure logging for the bot
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Function to get cookies from a website (YouTube by default)
def get_cookies_from_website(website="https://www.youtube.com"):
    # Set up Chrome options    
    options = uc.ChromeOptions()
    options.add_argument("--disable-web-security")
    options.add_argument("--allow-running-insecure-content")

    # Initialize the WebDriver
    driver = uc.Chrome(options=options)

    # Navigate to the website
    driver.get(website)

    # Wait for the Sign-in button or any button that requires login
    try:
        if "youtube" in website:
            login_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//yt-formatted-string[text()="Sign in"]'))
            )
            login_button.click()
        # Add more logic for other websites (like Instagram or Facebook) here
    except Exception as e:
        driver.quit()
        return f"Error occurred: {e}"

    # Wait for manual login if necessary
    input("Press Enter after logging in manually...")

    # Retrieve cookies after login
    cookies = driver.get_cookies()

    # Save cookies in Netscape HTTP Cookie File format
    cookie_file_path = "chrome_cookies.txt"
    with open(cookie_file_path, "w") as file:
        file.write("# Netscape HTTP Cookie File\n")
        for cookie in cookies:
            file.write(f"{cookie['domain']}\tTRUE\t{cookie['path']}\t{'TRUE' if cookie.get('secure') else 'FALSE'}\t{cookie.get('expiry', '0')}\t{cookie['name']}\t{cookie['value']}\n")

    # Close the browser
    driver.quit()
    return cookie_file_path

# Define the command handler for the bot
async def getcookies(update: Update, context):
    try:
        # If user specified a website, use that, otherwise default to YouTube
        website = context.args[0] if context.args else "https://www.youtube.com"
        
        await update.message.reply_text(f"Fetching cookies for {website}. Please log in when prompted.")
        # Fetch cookies
        cookie_file = get_cookies_from_website(website)
        
        # Check if file exists and send it to the user
        if os.path.exists(cookie_file):
            await update.message.reply_document(document=open(cookie_file, 'rb'), filename="chrome_cookies.txt")
            await update.message.reply_text("Cookies have been saved and sent.")
        else:
            await update.message.reply_text("Failed to generate cookie file.")
    
    except Exception as e:
        await update.message.reply_text(f"An error occurred: {e}")

# Main function to run the bot
def main():
    # Your bot token from BotFather
    TOKEN = "8042833505:AAGS9hJYLmGNxNalYe0GsgTcrDPdGqFQuYg"
    
    # Create an Application object (dispatcher for handlers)
    application = Application.builder().token(TOKEN).build()

    # Command handler for the /getcookies command
    application.add_handler(CommandHandler("getcookies", getcookies))

    # Start the bot
    application.run_polling()

if __name__ == '__main__':
    main()

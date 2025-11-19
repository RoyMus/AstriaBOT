import os

if os.path.exists(".env"):
    from dotenv import load_dotenv
    load_dotenv()

WHATSAPP_NUMBER_ID = os.environ.get("WHATSAPP_NUMBER_ID")
WHATSAPP_API_URL = os.environ.get("WHATSAPP_API_URL")
ASTRIA_API_KEY = os.environ.get("ASTRIA_API_KEY")
WEBHOOK_URL =  os.environ.get("WEBHOOK_URL")
WHATSAPP_API_KEY = os.environ.get("WHATSAPP_API_KEY")
MAX_IMAGES_THRESHOLD = os.environ.get("MAX_IMAGES_THRESHOLD")
ASTRIA_API_URL = os.environ.get("ASTRIA_API_URL")
ASTRIA_API_Authentication = {
    "Authorization": f"Bearer {ASTRIA_API_KEY}"
}
SUMIT_API_KEY = os.environ.get("SUMIT_API_KEY")
SUMIT_COMPANY_ID = os.environ.get("SUMIT_COMPANY_ID")
DB_HOST = os.environ.get("DB_HOST")
DB_USER = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
IMAGE_GUIDE_URL = os.environ.get("IMAGE_GUIDE_URL")
RECOMMENDED_PHOTOS = os.environ.get("RECOMMENDED_PHOTOS")   
FIXED_PRICE = os.environ.get("FIXED_PRICE")
AZURE_STORAGE_CONNECTION_STRING = os.environ.get("AZURE_STORAGE_CONNECTION_STRING")
LITE_TIER_PRICE = os.environ.get("LITE_TIER_PRICE")
STANDARD_TIER_PRICE = os.environ.get("STANDARD_TIER_PRICE")
PREMIUM_TIER_PRICE = os.environ.get("PREMIUM_TIER_PRICE")
LITE_TIER_PAYMENT_LINK = os.environ.get("LITE_TIER_PAYMENT_LINK")
STANDARD_TIER_PAYMENT_LINK = os.environ.get("STANDARD_TIER_PAYMENT_LINK")
PREMIUM_TIER_PAYMENT_LINK = os.environ.get("PREMIUM_TIER_PAYMENT_LINK")
STORAGE_BLOB_URL = os.environ.get("STORAGE_BLOB_URL")
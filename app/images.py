import os
from dotenv import load_dotenv
from imagekitio import ImageKit

load_dotenv()

private_key = os.getenv("IMAGEKIT_PRIVATE_KEY")
public_key = os.getenv("IMAGEKIT_PUBLIC_KEY")
url_endpoint = os.getenv("IMAGEKIT_URL")  # Render Environment ထဲက key အမည်နှင့် ကိုက်ညီပါစေ

if not all([private_key, public_key, url_endpoint]):
    raise RuntimeError("ImageKit environment variables (PRIVATE_KEY, PUBLIC_KEY, URL) are missing!")

imagekit = ImageKit(
    private_key=private_key,
    public_key=public_key,
    url_endpoint=url_endpoint,
)
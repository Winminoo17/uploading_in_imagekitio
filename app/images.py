import os
from dotenv import load_dotenv
from imagekitio import ImageKit

load_dotenv()

private_key = os.getenv("IMAGEKIT_PRIVATE_KEY")
if not private_key:
    raise RuntimeError("IMAGEKIT_PRIVATE_KEY environment variable is missing!")

imagekit = ImageKit(
    private_key=private_key
)
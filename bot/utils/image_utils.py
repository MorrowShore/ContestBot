from PIL import Image
from io import BytesIO
import aiofiles


async def resize_and_save_image(image_data: bytes, path: str):
    img = Image.open(BytesIO(image_data))
    max_dim = max(img.size)

    if max_dim > 1080:
        scale = 1080 / max_dim
        new_size  = tuple([int(d * scale) for d in img.size])

        img = img.resize(new_size, Image.Resampling.LANCZOS)

    async with aiofiles.open(path, "wb") as f:
        buffer = BytesIO()

        img.save(buffer, format="WEBP")
        await f.write(buffer.getvalue())
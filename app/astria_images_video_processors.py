import aiohttp
import logging
from Utils import constants,utils
from azure.storage.blob import BlobServiceClient,ContentSettings
from moviepy import ImageSequenceClip
from PIL import Image
from io import BytesIO
from collections import defaultdict
import numpy as np
import os
import azure.functions as func

async def update_pack_images():
    os.makedirs("tmp", exist_ok=True)
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{constants.ASTRIA_API_URL}/packs",
                            headers=constants.ASTRIA_API_Authentication) as response:
            packs = await response.json()
            for pack in packs:
                async with session.get(f"{constants.ASTRIA_API_URL}/p/{pack['id']}",
                                            headers=constants.ASTRIA_API_Authentication) as response:
                    data = await response.json()
                    if not response.ok:
                        response_text = await response.text()
                        logging.error(response_text)
                        return
                    else:
                        frames = defaultdict(list)
                        size = (710,1536)
                        prompts = data.get("prompts_per_class", {})
                        for entity_type,prompt in prompts.items():
                            for prompt_data in prompt:
                                images = prompt_data.get("images", [])
                                if len(images) > 0:
                                    image = images[0]
                                    async with session.get(image) as image_response:
                                        if image_response.status == 200:
                                            content = await image_response.read()
                                            img = Image.open(BytesIO(content)).convert("RGB")
                                            img = resize_image_with_padding(img,size)
                                            frame = np.array(img) 
                                            img.close()
                                            if utils.is_image_black(frame):
                                                logging.warning(f"Skipping black image for pack {pack['id']} entity {entity_type}")
                                                continue
                                            frames[entity_type].append(frame)

                        for entity_type,frame in frames.items():
                            output_path = f"tmp/{pack['id']}_{entity_type}.mp4"
                            create_video_from_images(frame, output_path)
                            upload_to_blob(output_path, f"videos/{pack['id']}_{entity_type}.mp4")

def resize_image_with_padding(img, target_resolution):
    """
    Resize the image to the target size, maintaining aspect ratio and adding black padding.
    """
    # Create properly sized frame with black background
    frame = Image.new('RGB', target_resolution, (0, 0, 0))
    
    # Calculate aspect-preserving resize
    img_ratio = img.width / img.height
    target_ratio = target_resolution[0] / target_resolution[1]
    
    if img_ratio > target_ratio:
        # Image is wider than target (letterbox top/bottom)
        new_width = target_resolution[0]
        new_height = int(new_width / img_ratio)
    else:
        # Image is taller than target (pillarbox left/right)
        new_height = target_resolution[1]
        new_width = int(new_height * img_ratio)
        
    # Resize image while maintaining aspect ratio
    img = img.resize((new_width, new_height), Image.LANCZOS)
    
    # Paste centered on black background
    paste_position = (
        (target_resolution[0] - new_width) // 2,
        (target_resolution[1] - new_height) // 2
    )
    frame.paste(img, paste_position)

    return frame

def create_video_from_images(image_paths, output_path,fps=1):
    """
    frames: list of numpy images
    output_path: path to save video
    frame_duration: seconds each image is shown
    fps: frames per second for the output video (default 24)
    """
    clip = ImageSequenceClip(image_paths,fps=fps)
    clip.write_videofile(
        output_path,
        codec="libx264",
        audio_codec="aac",
        preset="ultrafast",
        ffmpeg_params=[
            "-profile:v", "baseline",
            "-pix_fmt", "yuv420p",
            "-movflags", "+faststart",
            "-b:v", "900k",
        ]
    )
    clip.close()


def upload_to_blob(local_path, blob_path):
    blob_service = BlobServiceClient.from_connection_string(constants.AZURE_STORAGE_CONNECTION_STRING)
    blob_client = blob_service.get_blob_client(container='videos', blob=blob_path)
    with open(local_path, "rb") as f:
        blob_client.upload_blob(f, overwrite=True, content_settings=ContentSettings(content_type='video/mp4'))
    return blob_client.url
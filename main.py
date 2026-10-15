import requests
from bs4 import BeautifulSoup
from PIL import Image
import os
import yaml
from urllib.parse import urljoin
from datetime import datetime


from display import display_single_image

CONFIG_FILE = "config.yml"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

def load_config(file_path):
    with open(file_path, "r") as file:
        return yaml.safe_load(file)

def download_wikipedia_potd(config):
    save_dir = os.path.abspath(config['photo_path'])  # Ensure absolute path
    e_ink_dimensions = tuple(config['e_ink_dimensions'])  # (width, height) in landscape

    output_dir = os.path.join(save_dir, "output")
    os.makedirs(output_dir, exist_ok=True)

    # Wikimedia Commons POTD URL
    commons_potd_url = "https://commons.wikimedia.org/wiki/Main_Page"

    # Wikipedia POTD URL
    wikipedia_potd_url = "https://en.wikipedia.org/wiki/Wikipedia:Picture_of_the_day"

    headers = {"User-Agent": USER_AGENT}

    # Step 1: Try to fetch POTD from Wikimedia Commons
    try:
        response = requests.get(commons_potd_url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find the POTD image on Wikimedia Commons
        img_tag = soup.find('img', src=lambda s: s and 'upload.wikimedia.org/wikipedia/commons/' in s)
        if img_tag:
            print("Found POTD image on Wikimedia Commons.")
            img_src = img_tag['src']
            img_url = 'https:' + img_src if img_src.startswith('//') else img_src
            alt_text = img_tag.get('alt', 'Wikimedia_POTD')
        else:
            raise ValueError("POTD image not found on Wikimedia Commons.")
    except Exception as e:
        print(f"Failed to fetch POTD from Wikimedia Commons: {e}")
        print("Falling back to Wikipedia.")

        # Step 2: Fetch POTD from Wikipedia as a backup
        try:
            response = requests.get(wikipedia_potd_url, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            # Find the POTD image on Wikipedia
            img_tag = soup.find('img', src=lambda s: s and 'upload.wikimedia.org/wikipedia/commons/thumb/' in s)
            if img_tag:
                print("Found POTD image on Wikipedia.")
                img_src = img_tag['src']
                img_url = 'https:' + img_src if img_src.startswith('//') else img_src
                alt_text = img_tag.get('alt', 'Wikipedia_POTD')
            else:
                raise ValueError("POTD image not found on Wikipedia.")
        except Exception as backup_error:
            print(f"Failed to fetch POTD from Wikipedia as a backup: {backup_error}")
            return

    # Download the image
    try:
        img_response = requests.get(img_url, headers=headers)
        img_response.raise_for_status()

        today_str = datetime.now().strftime("%Y-%m-%d")

        jpg_file_path = os.path.join(output_dir, f"{today_str}.jpg")
        with open(jpg_file_path, 'wb') as f:
            f.write(img_response.content)
        print(f"Downloaded POTD to '{jpg_file_path}' (Alt text: '{alt_text}').")

        # Process the image and save it as BMP
        with Image.open(jpg_file_path) as img:
            img.thumbnail(e_ink_dimensions, Image.Resampling.LANCZOS)
            new_img = Image.new("RGB", e_ink_dimensions, color="white")
            x_offset = (e_ink_dimensions[0] - img.width) // 2
            y_offset = (e_ink_dimensions[1] - img.height) // 2
            new_img.paste(img, (x_offset, y_offset))
            new_img = new_img.convert("L")

            bmp_file_path = os.path.abspath(os.path.join(output_dir, f"{today_str}.bmp"))
            with open(bmp_file_path, 'wb') as f:
                new_img.save(f, "BMP")
                f.flush()
                os.fsync(f.fileno())

            # Confirm file exists
            if not os.path.exists(bmp_file_path):
                print(f"Error: File not found after saving: {bmp_file_path}")
                return

            print(f"Converted and saved BMP image to '{bmp_file_path}'.")
            display_single_image(bmp_file_path)
    except Exception as e:
        print(f"Failed to download or process the image: {e}")


if __name__ == "__main__":
    try:
        config = load_config(CONFIG_FILE)
        download_wikipedia_potd(config)
    except Exception as e:
        print(f"An error occurred: {e}")

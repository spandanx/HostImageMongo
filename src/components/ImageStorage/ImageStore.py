
import logging
from pymongo import MongoClient
import gridfs

from PIL import Image
from io import BytesIO
import requests
import io

from src.utils.common import retry


class ImageStore:
    def __init__(self, username, password, hostname, database, port):
        self.fs = self.get_database_file_system(username, password, hostname, database, port)

    def get_database_file_system(self, username, password, hostname, database, port):
        CONNECTION_STRING = f"mongodb://{username}:{password}@{hostname}:{port}"
        client = MongoClient(CONNECTION_STRING)
        return gridfs.GridFS(client[database])

    def save_image(self, image_bytes, target_image_path):
        file_id = self.fs.put(image_bytes, filename=target_image_path)
        return file_id

    def get_image(self, target_image_path):
        logging.info("Called get_image()")
        print("Called get_image()")
        image = self.fs.find_one({"filename": target_image_path})
        if image:
            logging.info("Image found")
            print("Image found")
            return image
        logging.info("Image not found")
        print("Image not found")
        return None

    @retry(max_retries=3, delay=2)
    def save_image_handler(self, image_path, target_image_path):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        response = requests.get(image_path, headers=headers)
        response.raise_for_status()

        image_bytes = BytesIO(response.content)
        im = Image.open(image_bytes)

        im.save(image_bytes, format='PNG')
        image_bytes.seek(0)

        file_id = self.save_image(image_bytes, target_image_path)
        return file_id

if __name__ == "__main__":
    ###------------- Config Parser
    from configparser import ConfigParser

    parser = ConfigParser()
    config_file_path = '../../../config.properties'

    with open(config_file_path) as f:
        file_content = f.read()

    parser.read_string(file_content)
    ###------------- Config Parser

    imageStorage = ImageStore(username=parser['MONGODB']['mongodb_username'],
                  password=parser['MONGODB']['mongodb_password'],
                  hostname=parser['MONGODB']['mongodb_hostname'],
                  database=parser['MONGODB']['mongodb_image_database'],
                  port=parser['MONGODB']['mongodb_port']
                  )
    image_path = "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e8/Linguistic_map_of_Northeast_India_English_Native.png/500px-Linguistic_map_of_Northeast_India_English_Native.png"
    target_image_path = "Linguistic_map_of_Northeast_India_English_Native.png"
    target_image_path = "781f1f9b-4250-49db-8b95-9a3bfc3c0244.jpg"
    # target_image_path = "Linguistic_map_of_Northeast_India_English_Native2.png"
    # imageStorage.save_image_handler(image_path=image_path, target_image_path=target_image_path)
    image_data = imageStorage.get_image(target_image_path=target_image_path)
    # image_data_np = np.random.randint(0, 255, size=(100, 100, 3), dtype=np.uint8)
    # img = Image.fromarray(image_data_np, 'RGB')
    image_stream = io.BytesIO(image_data)
    img = Image.open(image_stream)
    img.show()
    x = 1



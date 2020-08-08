import requests
import io
import base64
import cv2
from PIL import Image
import base64
from io import BytesIO

base_addr = 'http://127.0.0.1:5000/'
test_url = base_addr + '/upload'

image = Image.open("./test.png")

buffered = BytesIO()
image.save(buffered, format="PNG")
img_str = base64.b64encode(buffered.getvalue())
res = requests.post(
    test_url, json={"img": img_str.decode("utf-8")})
print(res.text)
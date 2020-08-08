from flask import Flask, request, Response
import base64
import numpy as np
import cv2
app = Flask(__name__)
curr_image = []

@app.route('/test')
def test():
    return "test"

@app.route('/upload', methods=['POST'])
def upload():
    global curr_image

    print(request.json)

    im_bytes = base64.b64decode(request.json['img'])
    im_arr = np.frombuffer(im_bytes, dtype=np.uint8)  # im_arr is one-dim Numpy array
    img = cv2.imdecode(im_arr, flags=cv2.IMREAD_COLOR)

    scale_percent = 40  # percent of original size
    width = int(img.shape[1] * scale_percent / 100)
    height = int(img.shape[0] * scale_percent / 100)
    dim = (width, height)
    # resize image
    resized = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)

    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 40]
    result, encimg = cv2.imencode('.jpg', resized, encode_param)
    decimg = cv2.imdecode(encimg, 1)
    cv2.imwrite('compress_img1.jpg', resized,  [cv2.IMWRITE_JPEG_QUALITY, 40])

    im_bytes = encimg.tobytes()
    im_b64 = base64.b64encode(im_bytes)

    print(img.shape)
    chunked = [im_b64[i:i + 100].decode("utf-8") for i in range(0, len(im_b64), 100)]

    curr_image = chunked

    print(len(chunked))

    return {"result": chunked}
    #response = {'message': 'image received. size={}x{}'.format(img.shape[1], img.shape[0])
    #            }
    #response_pickled = jsonpickle.encode(response)

    #return Response(response="test", status=200, mimetype="application/json")

@app.route("/serve_chunked", methods=['GET'])
def serve_chunked():
    global curr_image
    prev_image = curr_image
    curr_image = []
    return {"result": prev_image}

@app.route("/resulting_image", methods=['POST'])
def resulting_image():
    print(request.json)
    data = request.json['result']

    with open("result.txt", "w+") as f:
        f.write(data)

    return ("", 200)

@app.route("/serve", methods=['GET'])
def serve():
    try:
        with open("result.txt", "r") as f:
           data = f.read()
    except:
        data = ""

    return {"result": data}

if __name__ == "__main__":
    app.run(debug=True)
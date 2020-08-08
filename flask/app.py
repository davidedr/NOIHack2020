from flask import Flask, request, Response
import base64
import numpy as np
import cv2
app = Flask(__name__)


@app.route('/test')
def test():
    return "test"


@app.route('/upload', methods=['POST'])
def upload():

    print(request.json)

    im_bytes = base64.b64decode(request.json['img'])
    im_arr = np.frombuffer(im_bytes, dtype=np.uint8)  # im_arr is one-dim Numpy array
    img = cv2.imdecode(im_arr, flags=cv2.IMREAD_COLOR)

    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 40]
    result, encimg = cv2.imencode('.jpg', img, encode_param)

    im_bytes = encimg.tobytes()
    im_b64 = base64.b64encode(im_bytes)

    print(img.shape)

    return im_b64
    #response = {'message': 'image received. size={}x{}'.format(img.shape[1], img.shape[0])
    #            }
    #response_pickled = jsonpickle.encode(response)

    #return Response(response="test", status=200, mimetype="application/json")

@app.route("/resulting_image", methods=['POST'])
def resulting_image():
    data = request.json['result']

    with open("result.txt", "w+") as f:
        f.write(data)

@app.route("/serve", methods=['GET'])
def serve():
    with open("result.txt", "r") as f:
       data = f.read()

    return {"result": data}

if __name__ == "__main__":
    app.run(debug=True)
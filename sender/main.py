
from network import LoRa
import socket
import machine
import time
import _urequest

# initialise LoRa in LORA mode
# Please pick the region that matches where you are using the device:
# Asia = LoRa.AS923
# Australia = LoRa.AU915
# Europe = LoRa.EU868
# United States = LoRa.US915
# more params can also be given, like frequency, tx power and spreading factor
lora = LoRa(mode=LoRa.LORA, region=LoRa.EU868, sf=7)

# create a raw LoRa socket
s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)

def start_sending(num_chunks):

    # send some data
    s.setblocking(True)
    s.send('START|' + str(num_chunks))
    time.sleep(2)

    for i in range(5):
        # get any data received...
        s.setblocking(False)
        data = s.recv(64)

        if data == b"OK":
            return True

        # wait a random amount of time
        time.sleep(1)

    return False

def send_chunks(chunks):
    s.setblocking(True)
    for i, chunk in enumerate(chunks):
        package_num = "{0:b}".format(i)
        while len(package_num) < 24:
            package_num = "0" + package_num
        s.send(package_num + chunk)

def resend_wrong_chunks(chunks):
    while True:
        s.setblocking(False)
        data = s.recv(64)

        if len(data) == 0:
            continue

        if data == b"OK":
            return
        else:
            data = data.decode('utf-8')
            malformed_chunks = [int(data[i:i+8], 2) for i in range(0, len(data), 8)]

            for chunk in malformed_chunks:
                s.send("{0:b}".format(chunk) + chunks[chunk])


def send_data(chunks):
    ack_message = False
    while not ack_message:
        ack_message = start_sending(len(chunks))
    print("received ACK message")
    send_chunks(chunks)
    resend_wrong_chunks(chunks)

def read_image_data():
    req = _urequest.get('https://1fe130ad76e9.ngrok.io/serve_chunked')

    return req.json()["result"]

while True:
    result = read_image_data()
    if result != []:
        print(result[0])
        send_data(result)
    time.sleep(5)

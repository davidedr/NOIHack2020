from network import LoRa
import socket
import machine
import time
import numpy as np
from PIL import Image

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

image = []


def receive_and_send_ack():

    while True:
        # get any data received...
        s.setblocking(False)
        data = s.recv(64)

        data = data.decode('utf-8')

        if "START" in data:
            chunks = int(data.split("|")[1])
            print("received " + str(chunks))
            s.send("OK")
            return chunks

        # wait a random amount of time
        time.sleep(0.1)


def assembleImage():
    # image is in the following format:
    '''
        [
            [[8 bits r, 8 bits g, 8 bits b], [8r,8g,8b]]... one arr for each pixel
            ...
            ..
            .
        ]
    '''
    npa = np.asarray(image)
    img = Image.fromarray(npa, 'RGB')
    img.save('received.png')


def listen_for_image_parts(num_chunks, chunks_received=[]):
    for i in range(num_chunks * 2 * 10):
        data = s.recv(300)  # why 300 for choice of buf size?
        data = data.decode('utf-8')
        print(data)
        chunk = []
        if len(data) > 0:
            try:
                # number_of_chunk is the index of chunk
                number_of_chunk = int(data[:8], 2)
                chunks_received.append(number_of_chunk)

                for i in range(8, len(data), 24):
                    r = int(data[i:i+8], 2)
                    g = int(data[i+8:i+16], 2)
                    b = int(data[i+16:i+24], 2)
                    chunk.append([r, g, b])
            except:
                print("Malformed")

            print(chunk)
            if chunk not in image:
                image.append(chunk)

        if(len(image) == num_chunks):
            # received all the chunks to form the image
            assembleImage()

    return list(set(chunks_received))


def retry_wrong_image_parts(num_chunks, chunks_received):
    wrong_parts = [i for i in range(
        len(num_chunks)) if i not in chunks_received]
    print(wrong_parts)

    if len(wrong_parts) > 0:
        wrong_parts_encoded = "".join(
            ["{0:b}".format(part) for part in wrong_parts])
        s.send(wrong_parts_encoded)
        listen_for_image_parts(num_chunks, chunks_received=chunks_received)
    else:
        s.send("OK")


num_chunks = receive_and_send_ack()
chunks_received, image = listen_for_image_parts(num_chunks)
retry_wrong_image_parts(num_chunks, chunks_received)

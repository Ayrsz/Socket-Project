import socket as sck
from socket import socket, AF_INET, SOCK_DGRAM, SOCK_STREAM
import sys
from threading import Thread
import numpy as np
import ultralytics as ultra
import cv2 as cv
import torch
import signal

SERVICE_PORT_NAMES_REGISTRATION = 6025
PORT_THIS_SERVICE = 6600
YOLO_MODEL = ultra.YOLO("yolo11n.pt", task = "detect")
FACE_DETECTION_SOCKET = socket(AF_INET, SOCK_DGRAM)

def delete_registration(sig, frame):
    m_client = socket(AF_INET, SOCK_STREAM)
    m_client.connect(("localhost", SERVICE_PORT_NAMES_REGISTRATION))
    name = sys.argv[1]
    request = "DEL" + "$" + name + "$" + str(PORT_THIS_SERVICE)
    m_client.send(request.encode())
    m_client.close()
    sys.exit(0)

def make_request_register() -> bool:
    m_client = socket(AF_INET, SOCK_STREAM)
    m_client.connect(("localhost", SERVICE_PORT_NAMES_REGISTRATION))
    print(f"Conectado ao servidor de registro UDP")

    name = sys.argv[1] #Name need to be passed by the terminal
    request = "REG" + "$" + name + "$" + str(PORT_THIS_SERVICE)
    m_client.send(request.encode())

    response = (m_client.recv(1024)).decode()
    if response == "NAME-ALREADY-IN-USE":
        return False
    else:
        print(f"Nome cadastrado com sucesso, recebido {response}")
        return True

def check_integrity_registration(registrated):
    if registrated == False:
        raise NameError("Nome em uso, não iniciando o servidor")
    else:
        print("Nome registrado, funcionando")


def recv_all(server_socket):
    try:
        size_bytes, _ = server_socket.recvfrom(4)
    except TimeoutError:
        return None  # timeout no header

    if len(size_bytes) != 4:
        return None

    expected_size = int.from_bytes(size_bytes, "big")
    if expected_size == 0: 
        try:
            control_msg, _ = server_socket.recvfrom(2048) 
            return control_msg
        except TimeoutError:
            return None

    data = bytearray()
    server_socket.settimeout(0.5)

    while len(data) < expected_size:
        try:
            packet, _ = server_socket.recvfrom(2048)
            data.extend(packet)
        except TimeoutError:
            return None

    return bytes(data)


def server_face_detection():
    
    FACE_DETECTION_SOCKET.setsockopt(sck.SOL_SOCKET, sck.SO_REUSEADDR, 1)

    FACE_DETECTION_SOCKET.bind(("localhost", PORT_THIS_SERVICE))
    FACE_DETECTION_SOCKET.settimeout(None) 
    print("[Servidor de detecçao UDP] iniciado [...]")
    handle_request_face_detection()


def handle_request_face_detection():
    msg, addr = FACE_DETECTION_SOCKET.recvfrom(1024)
    msg = msg.decode()
    print(f"[Servidor de detecçao UDP] estabeleceu conexao com {addr}: msg {msg}")

    FACE_DETECTION_SOCKET.sendto(("SUCESSFUL").encode(), addr)

    while True:
        payload = recv_all(FACE_DETECTION_SOCKET)

        # checar se é mensagem de END
        if len(payload) <= 4:
            if payload == b"END":
                print("Recebido END. Finalizando conexão.")
                break

        if payload is None:
            FACE_DETECTION_SOCKET.sendto(("NONE").encode(), addr)
            print("TIMEOUT ou header inválido — esperando próximo frame")
            continue

        

        # decodificar a imagem (payload é bytes JPEG)
        img_array = np.frombuffer(payload, dtype=np.uint8)
        im = cv.imdecode(img_array, cv.IMREAD_COLOR)
        
        # faz a detecção (exemplo: YOLO_MODEL)
        detection = YOLO_MODEL(im, classes=[0])[0]
        cordinates = detection.boxes.xywh
        response = '[]'
        if len(cordinates) > 0:
            response = str([pc.tolist() for pc in cordinates])

        FACE_DETECTION_SOCKET.sendto(response.encode(), addr)

    FACE_DETECTION_SOCKET.close()


if __name__ == "__main__":
   
   registrated = make_request_register()
   check_integrity_registration(registrated)
   signal.signal(signal.SIGINT, delete_registration)

   server_face_detection_tcp = Thread(target = server_face_detection)

   server_face_detection_tcp.start()

from socket import socket, AF_INET, SOCK_DGRAM, SOCK_STREAM
import sys
from threading import Thread
import numpy as np
import ultralytics as ultra
import cv2 as cv
import torch

SERVICE_PORT_NAMES_REGISTRATION = 6025
PORT_THIS_SERVICE = 6600
YOLO_MODEL = ultra.YOLO("yolo11n.pt", task = "detect")

def make_request_register() -> bool:
    m_client = socket(AF_INET, SOCK_STREAM)
    m_client.connect(("localhost", SERVICE_PORT_NAMES_REGISTRATION))
    print(f"Conectado ao servidor de registro UDP")

    name = sys.argv[1] #Name need to be passed by the terminal
    request = name + "$" + str(PORT_THIS_SERVICE)
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
    # receber header de 4 bytes com tamanho (big-endian)
    try:
        size_bytes, _ = server_socket.recvfrom(4)
    except TimeoutError:
        return None  # timeout no header

    if len(size_bytes) != 4:
        return None

    expected_size = int.from_bytes(size_bytes, "big")
    if expected_size == 0:
        return b""

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
    m_server_socket = socket(AF_INET, SOCK_DGRAM)
    m_server_socket.bind(("localhost", PORT_THIS_SERVICE))
    m_server_socket.settimeout(None) 
    print("[Servidor de detecçao UDP] iniciado [...]")
    handle_request_face_detection(m_server_socket)


def handle_request_face_detection(m_server_socket):
    msg, addr = m_server_socket.recvfrom(1024)
    msg = msg.decode()
    print(f"[Servidor de detecçao UDP] estabeleceu conexao com {addr}: msg {msg}")

    m_server_socket.sendto(("SUCESSFUL").encode(), addr)

    while True:
        payload = recv_all(m_server_socket)
        if payload is None:
            m_server_socket.sendto(("NONE").encode(), addr)
            print("TIMEOUT ou header inválido — esperando próximo frame")
            continue

        # checar se é mensagem de END
        if len(payload) <= 4 and payload == b"END":
            print("Recebido END. Finalizando conexão.")
            break

        # decodificar a imagem (payload é bytes JPEG)
        img_array = np.frombuffer(payload, dtype=np.uint8)
        im = cv.imdecode(img_array, cv.IMREAD_COLOR)
        if im is None:
            print("Falha ao decodificar imagem — descartando")
            m_server_socket.sendto(("NONE").encode(), addr)
            continue
        
        # faz a detecção (exemplo: YOLO_MODEL)
        detection = YOLO_MODEL(im, classes=[0])[0]
        cordinates = detection.boxes.xywh
        response = '[]'
        if len(cordinates) > 0:
            response = str([pc.tolist() for pc in cordinates])

        m_server_socket.sendto(response.encode(), addr)

    m_server_socket.close()


if __name__ == "__main__":
   registrated = make_request_register()
   check_integrity_registration(registrated)

   server_face_detection_tcp = Thread(target = server_face_detection)

   server_face_detection_tcp.start()

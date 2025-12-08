from socket import socket, AF_INET, SOCK_STREAM, SOCK_DGRAM
import sys
import cv2 as cv
import ast

SERVICE_PORT_NAMES_SEARCH = 7025
CAMERA = cv.VideoCapture(0)
DUMMIE_IMAGE = "./data/caneta_azul.webp"

service_request = sys.argv[1]
m_client_name = socket(AF_INET, SOCK_STREAM)
m_client_detect_TCP = socket(AF_INET, SOCK_STREAM)
m_client_detect_UDP = socket(AF_INET, SOCK_DGRAM)


## SERVICE REGISTRATION ##

def call_names_service(service_request):
    m_client_name.connect(("localhost", SERVICE_PORT_NAMES_SEARCH))
    print(f"Conectado ao servidor de nome\nEnviando a request {service_request}")
    m_client_name.send(service_request.encode())
    resposta = m_client_name.recv(1024)
    resposta = resposta.decode()
    print(f"Recebido: {resposta}")

    m_client_name.close()
    return resposta

def check_integrity_response_name_service(response : str):
    if response == "NULL":
        raise ValueError(f"Server not started yet or do not exist {service_request}")
    else:
        if response.count("-") > 1:
            raise ValueError(f"Wrong format of response, got {response}")
        
        response = response.split("-")
        IP_dest = response[0]
        PORT_dest = int(response[1])
    return IP_dest, PORT_dest

############


## DRAW IMAGE ##
def draw_detection(im, coordinates):
    for box_coord in coordinates:
        xc, yc, w, h = box_coord
        xi = int(xc - w//2)
        xf = int(xc + w//2)
        yi = int(yc - h//2)
        yf = int(yc + h//2)
        
        im = cv.rectangle(im, (xi, yi), (xf, yf), (255, 0, 255), 2)
    return im

##############

## TCP CONECTION ##
def conection_with_tcp_server(m_client):
    while True:
        ret, im = CAMERA.read()

        if im is None:
            im = cv.imread(DUMMIE_IMAGE)


        m_client.sendall(im.tobytes())
        resposta = m_client.recv(1024)
        resposta = resposta.decode()

        print(f"Recebido a resposta: {resposta}")
        coords = ast.literal_eval(resposta)
        
        im = draw_detection(im, coords)
        cv.imshow("TCP SERVICE", im)
        if cv.waitKey(1) & 0xFF == ord('q'):
            m_client.send(("END").encode())
            break
    m_client.close()


####################



def send_image_by_udp(im, m_client, IP_dest, PORT_dest):
    max_size_packet = 200
    compressed = compress_for_udp(im, quality = 90)

    # envia header 4 bytes com o tamanho
    size_bytes = len(compressed).to_bytes(4, "big")
    m_client.sendto(size_bytes, (IP_dest, PORT_dest))

    for i in range(0, len(compressed), max_size_packet):
        
        part = compressed[i:i + max_size_packet]
        m_client.sendto(part, (IP_dest, PORT_dest))


def compress_for_udp(img, quality=10):
    # qualidade baixa = tamanho menor
    encode_param = [int(cv.IMWRITE_JPEG_QUALITY), quality]
    ok, encoded = cv.imencode(".jpg", img, encode_param)
    return encoded.tobytes()


def conection_with_udp_server(m_client, IP_dest, PORT_dest):
    while True:
        ret, im = CAMERA.read()

        if im is None:
            im = cv.imread(DUMMIE_IMAGE)
        
        send_image_by_udp(im, m_client, IP_dest, PORT_dest)
        #Coords
        resposta, addr = m_client.recvfrom(2000)
        resposta = resposta.decode()
        if resposta == "NONE":
            continue

        print(f"Recebido a resposta: {resposta}")
        coords = ast.literal_eval(resposta)
        
        im = draw_detection(im, coords)
        cv.imshow("UDP_SERVICE", im)
        if cv.waitKey(1) & 0xFF == ord('q'):
            header_end = (0).to_bytes(4, "big") 
            m_client.sendto(header_end, (IP_dest, PORT_dest))

            m_client.sendto(b"END", (IP_dest, PORT_dest) ) 
            break
    m_client.close()

def make_requests_tcp_udp(IP_dest, PORT_dest, type_of_conection : str):
    ret, im = CAMERA.read()
    if im is None:
        im = cv.imread("./data/caneta_azul.webp")
    h, w, c = im.shape
    str_shape = str(h) + "x" + str(w) + "x" + str(c)

    if type_of_conection == "tcp":
        
        
        
        m_client_detect_TCP.connect((IP_dest, PORT_dest))
        m_client_detect_TCP.send(str_shape.encode())
        confirm = m_client_detect_TCP.recv(10)
            

        print(f"Conectado ao servidor de TCP, RECEBIDO {confirm.decode()}")
        conection_with_tcp_server(m_client_detect_TCP)
    
        
    elif type_of_conection == "udp":
        #im = compress_for_udp(im, quality = 5)
        m_client_detect_UDP.sendto((str_shape).encode(), (IP_dest, PORT_dest))

        confirm, addr = m_client_detect_UDP.recvfrom(2000)
        assert addr == (IP_dest, PORT_dest)
        print(f"Enviado pacote ao servidor UDP, RECEBIDO {confirm.decode()}")
        conection_with_udp_server(m_client_detect_UDP, IP_dest, PORT_dest)

    


if __name__ == "__main__":

        
    type_of_conection = "udp" if service_request.find("udp") != -1 else "tcp"
    
    response = call_names_service(service_request)
    IP_dest, PORT_dest = check_integrity_response_name_service(response)


    make_requests_tcp_udp(IP_dest, PORT_dest, type_of_conection)



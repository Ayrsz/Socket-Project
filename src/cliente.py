from socket import socket, AF_INET, SOCK_STREAM
import sys
import cv2 as cv
import ast

SERVICE_PORT_NAMES_SEARCH = 7025
CAMERA = cv.VideoCapture(0)


service_request = sys.argv[1]
m_client_name = socket(AF_INET, SOCK_STREAM)
m_client_detect = socket(AF_INET, SOCK_STREAM)


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

def draw_detection(im, coordinates):
    for box_coord in coordinates:
        xc, yc, w, h = box_coord
        xi = int(xc - w//2)
        xf = int(xc + w//2)
        yi = int(yc - h//2)
        yf = int(yc + h//2)
        
        im = cv.rectangle(im, (xi, yi), (xf, yf), (255, 0, 255), 2)
    return im


def make_requests_tcp_udp(IP_dest, PORT_dest, type_of_conection : str):
    if type_of_conection == "tcp":
        
        ret, im = CAMERA.read()
        h, w, c = im.shape
        print(im.shape)
        str_shape = str(h) + "x" + str(w) + "x" + str(c)
        
        m_client_detect.connect(("localhost", PORT_dest))
        m_client_detect.send(str_shape.encode())
        confirm = m_client_detect.recv(10)
            

        print(f"Conectado ao servidor de TCP, RECEBIDO {confirm.decode()}")
        while True:

            ret, im = CAMERA.read()

            if not ret:
                raise ValueError("Camera not working")
            
            m_client_detect.sendall(im.tobytes())

            resposta = m_client_detect.recv(1024)
            resposta = resposta.decode()

            print(f"Recebido a resposta: {resposta}")

            coords = ast.literal_eval(resposta)
            
            im = draw_detection(im, coords)


            cv.imshow("a", im)
            if cv.waitKey(1) & 0xFF == ord('q'):
                m_client_detect.send(("END").encode())
                break
    
        
    elif type_of_conection == "udp":
            pass
    
    m_client_detect.close()


if __name__ == "__main__":

        
    type_of_conection = "udp" if service_request.find("udp") != -1 else "tcp"
    
    response = call_names_service(service_request)
    IP_dest, PORT_dest = check_integrity_response_name_service(response)


    make_requests_tcp_udp(IP_dest, PORT_dest, type_of_conection)



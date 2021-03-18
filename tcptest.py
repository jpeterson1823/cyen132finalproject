import socket

#added try-except for proper clean close of socket
try:
    IP = '192.168.56.1'
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    print("Binding to " + IP + "...")
    s.bind(('192.168.1.6', 10000))
    print("\tBOUND")

    print("Listening...")
    s.listen(1)
    connection, client_addr = s.accept()
    print("Found a connection")

    try:
        while True:
            data = connection.recv(10)
            if data:
                # if close game signal recieved
                if data == b'&CLOSEGAME':
                    break
                # else continue game stuff
                else:
                    data = b'hit'
                    connection.sendall(data)
            # if no data given, send failure notice
            else:
                data = b'FAILURE'
    finally:
        connection.close()
finally:
    connection.close()
import hashlib
import pickle
import socket
import time

t0 = time.perf_counter()
serverAddressPort = ("127.0.0.1", 9801)

bufferSize = 1500


# Create a UDP socket at client side

UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
UDPClientSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
UDPClientSocket.settimeout(0.025)

# Send to server using created UDP socket
print(serverAddressPort)
UDPClientSocket.sendto(str.encode("SendSize\nReset\n\n"), serverAddressPort)
print("sent request for size")
totalsize = 0
while True:
    try:
        msgFromServer = UDPClientSocket.recvfrom(bufferSize)
        print(msgFromServer)
        msg = msgFromServer[0].decode()
        print(msg)
        brokenmessage = msg.split("\n")
        if (brokenmessage[-1] == "" and brokenmessage[-2] == ""):
            if (brokenmessage[0][:4] == "Size"):
                totalsize = int(brokenmessage[0][6:])
        break
    except TimeoutError:
        time.sleep(0.2)
        UDPClientSocket.sendto(str.encode("SendSize\nReset\n\n"), serverAddressPort)
        print("time out, resent request for size")

counter = 0
data = ""

graph_rcv = []
graph_send = []
while counter < totalsize:
    UDPClientSocket.sendto(str.encode("Offset: " + str(counter) + "\nNumBytes: "
                                      + str(min(1448, totalsize - counter)) + "\n\n"), serverAddressPort)
    graph_send.append((counter, (time.perf_counter() - t0) * 1000))
    while True:
        try:
            msgFromServer = UDPClientSocket.recvfrom(bufferSize)
            msg = msgFromServer[0].decode()
            assert "Squished" not in msg

            brokenmessage = msg.split("\n")
            print(counter)
            if (brokenmessage[2] == ""):
                if (brokenmessage[0][:6] == "Offset"):
                    offset = int(brokenmessage[0][8:])
                    print("offset:" + str(offset))
                    packsize = int(brokenmessage[1][10:])
                    print("packetsize: " + str(packsize))
                    print(len(msg) - (len(brokenmessage[0]) + len(brokenmessage[1]) + 3))
                    if (offset == counter and (
                            len(msg) - (len(brokenmessage[0]) + len(brokenmessage[1]) + 3)) == packsize):
                        data += msg[len(brokenmessage[0]) + len(brokenmessage[1]) + 3:]
                        graph_rcv.append((offset, (time.perf_counter() - t0) * 1000))
                        counter += packsize
                        break
                    else:
                        UDPClientSocket.sendto(str.encode(
                            "Offset: " + str(counter) + "\nNumBytes: " + str(min(1448, totalsize - counter)) + "\n\n"),
                            serverAddressPort)

                else:
                    UDPClientSocket.sendto(str.encode(
                        "Offset: " + str(counter) + "\nNumBytes: " + str(min(1448, totalsize - counter)) + "\n\n"),
                        serverAddressPort)
            else:
                UDPClientSocket.sendto(str.encode(
                    "Offset: " + str(counter) + "\nNumBytes: " + str(min(1448, totalsize - counter)) + "\n\n"),
                    serverAddressPort)


        except TimeoutError:
            UDPClientSocket.sendto(
                str.encode("Offset: " + str(counter) + "\nNumBytes: " + str(min(1448, totalsize - counter)) + "\n\n"),
                serverAddressPort)

md5 = hashlib.md5(data.encode()).hexdigest()
print(md5)
print(type(md5))
print(len(data))
UDPClientSocket.sendto(str.encode("Submit: 2021CS50622@myteam\nMD5: " + md5 + "\n\n"), serverAddressPort)
while True:
    try:
        msgFromServer = UDPClientSocket.recvfrom(bufferSize)
        msg = msgFromServer[0].decode()
        print(msg)
        brokenmessage = msg.split("\n")
        if (brokenmessage[len(brokenmessage) - 1] == "" and brokenmessage[len(brokenmessage) - 2] == ""):
            if (brokenmessage[0][:4] == "Size"):
                totalsize = int(brokenmessage[0][6:])
        break
    except:
        UDPClientSocket.sendto(str.encode("Submit: testing\n" + str(md5) + "\n\n"), serverAddressPort)

with open("graph_rcv.pkl", 'wb') as f:
    pickle.dump(graph_rcv, f)
with open("graph_send.pkl", 'wb') as f:
    pickle.dump(graph_send, f)

import socket
import time
from colorama import Fore
import pickle

start_time = time.time()

# Constants
SERVER_IP = '127.0.0.1'
SERVER_PORT = 9801
BUFFER_SIZE = 2048
TIMEOUT = 0.016
MAX_RETRIES = 5
batch_size = 10

graph_send = []
graph_rcv = []
graph_burst_send = []
graph_burst_rcv = []

def get_data_from_server(offset, num_bytes):
    retries = 0

    # Create the request message
    message = f"Offset: {offset}\nNumBytes: {num_bytes}\n\n"

    while retries < MAX_RETRIES:
        # Send the request
        client_socket.sendto(message.encode(), (SERVER_IP, SERVER_PORT))

        # Wait for a response
        try:
            data, addr = client_socket.recvfrom(BUFFER_SIZE)
            data_splitted = data.decode().split('\n\n')
            if str(offset) not in data_splitted[0]:
                print("offset wrong")
                continue
            return data_splitted[1]
        except socket.timeout:
            retries += 1
            print(f"Timeout for Offset: {offset}. Retrying ({retries}/{MAX_RETRIES})...")

    print(f"Failed to fetch data for Offset: {offset} after {MAX_RETRIES} retries.")
    return None

def send_request(offset, num_bytes):
    graph_send.append((offset, (time.time()-start_time)*1000))
    message = f"Offset: {offset}\nNumBytes: {num_bytes}\n\n"
    client_socket.sendto(message.encode(), (SERVER_IP, SERVER_PORT))
    graph_burst_send.append((batch_size, (time.time() - start_time) * 1000))
    return 1

def receive_data(received_data):
    try:
        data, addr = client_socket.recvfrom(BUFFER_SIZE)
        data_splitted = data.decode().split('\n\n')
        offset = int(data_splitted[0].split('\n')[0].split(':')[1])
        received_data[offset//CHUNK_SIZE] = data_splitted[1]
        graph_rcv.append((offset, (time.time() - start_time)*1000))
        graph_burst_rcv.append((1 if "Squished" in data_splitted[0] else 0, (time.time() - start_time) * 1000))
        return 1
    except:
        # print(Fore.RED + "Didn't get anything" + Fore.RESET)
        return 0

def get_data_one_pass():
    global batch_size

    sent, rcvd = 0, 0
    # send reqs
    batch_count = 0
    for i in range(len(received_data)):
        if received_data[i] is None:
            offset = i * CHUNK_SIZE
            sent += send_request(offset, CHUNK_SIZE)
            batch_count += 1

        if batch_count == batch_size:
            break

    while True:
        result = receive_data(received_data)
        if result == 0:
            break
        rcvd += result

    # if sent == rcvd:
    #     batch_size += 1
    # else:
    #     batch_size = max(batch_size//2, 1)


if __name__ == "__main__":
    # Create a UDP socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.settimeout(TIMEOUT)

    # Get total data size
    client_socket.sendto(b"SendSize\nReset\n\n", (SERVER_IP, SERVER_PORT))
    while True:
        try:
            size_data, addr = client_socket.recvfrom(BUFFER_SIZE)
            break
        except:
            continue
    total_size = int(size_data.decode().split(":")[1].strip())
    print(f"total size: {total_size}")

    # Fetch data in chunks
    offset = 0
    CHUNK_SIZE = 1448
    received_data = [None for i in range(0, total_size, CHUNK_SIZE)]

    passes = 0
    while received_data.count(None) > 0:
        passes += 1
        print(Fore.YELLOW + f"Pass {passes}. remaining: {received_data.count(None)}" + Fore.RESET)
        get_data_one_pass()

    received_data = "".join(received_data)[:-1]
    print(f"Received {len(received_data)}/{total_size} bytes of data.")

    with open("received_data.txt", 'w') as f:
        f.write(received_data)

    # Submit
    import hashlib
    md5 = hashlib.md5(received_data.encode()).hexdigest()
    print(md5)
    print(type(md5))
    print(len(received_data))
    client_socket.sendto(str.encode("Submit: 2021CS50622@myteam\nMD5: " + md5 + "\n\n"), (SERVER_IP, SERVER_PORT))
    while True:
        try:
            msgFromServer = client_socket.recvfrom(BUFFER_SIZE)
            msg = msgFromServer[0].decode()
            print(msg)
            brokenmessage = msg.split("\n")
            if (brokenmessage[len(brokenmessage) - 1] == "" and brokenmessage[len(brokenmessage) - 2] == ""):
                if (brokenmessage[0][:4] == "Size"):
                    totalsize = int(brokenmessage[0][6:])
            break
        except:
            time.sleep(0.2)
            client_socket.sendto(str.encode("Submit: testing\n" + str(md5) + "\n\n"), (SERVER_IP, SERVER_PORT))

    print(f"time taken: {time.time() - start_time}s")
    print(f"number of passes: {passes}")

    with open("graph_rcv.pkl", 'wb') as f:
        pickle.dump(graph_rcv, f)
    with open("graph_send.pkl", 'wb') as f:
        pickle.dump(graph_send, f)
    with open("graph_burst_send.pkl", 'wb') as f:
        pickle.dump(graph_burst_send, f)
    with open("graph_burst_rcv.pkl", 'wb') as f:
        pickle.dump(graph_burst_rcv, f)
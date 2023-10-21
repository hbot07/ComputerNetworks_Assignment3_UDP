import socket
import time

start_time = time.time()

# Constants
SERVER_IP = '127.0.0.1'
SERVER_PORT = 9801
BUFFER_SIZE = 2048
TIMEOUT = 0.025  # Timeout in seconds
MAX_RETRIES = 5


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

    def get_data_one_pass():
        for offset in range(0, total_size, CHUNK_SIZE):
            data_chunk = get_data_from_server(offset, min(CHUNK_SIZE, total_size-offset))
            if data_chunk:
                received_data[offset//CHUNK_SIZE] = data_chunk
                offset += min(CHUNK_SIZE, total_size-offset)

    get_data_one_pass()

    received_data = "".join(received_data)
    print(f"Received {len(received_data)}/{total_size} bytes of data.")


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
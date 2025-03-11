import socket
import time
import threading

"""
This is a simple TCP server that passes data between a Python script and an Unreal Engine 5 Runtime.
It runs in a separate thread so communication is not affected by the main script or UE execution time.

*Requires the TCP Socket Plugin from SpartanCode to be installed and enabled in Unreal Engine and used in a customized TCP actor blueprint
 - Fab Page: https://www.fab.com/listings/48db4522-8a05-4b91-bcf8-4217a698339b
 - Github: https://github.com/CodeSpartan/UE4TcpSocketPlugin

Steps:
1. Start a script containing the TCP_Relay class
2. Launch Unreal Engine 5 Runtime (ie Play in Editor)
3. Unreal Engine will connect to the TCP relay server ("Connected" will be printed in the console)
4. TCP Relay will immediately start sending its default .message data to Unreal Engine
5. To change outgoing data, main script sets the TCP_Relay.message variable, ie .message = create_fields_string([1., 2., 3.])
6. The TCP_Relay and UE TCP actor will exchange data as the main script runs
7. Main script is responsible for decoding/parsing data returned from UE via the .message_in attribute
7. TCP Relay should continue running even if UE runtime ends ("Disconnected" will be printed in the console), allowing new connections

Notes:
- The TCP Socket Plugin must be installed and enabled in Unreal Engine.
- The TCP Socket Plugin must be configured to use the same host and port as the TCP relay server.
- The TCP Socket Plugin must be configured to use the same number of fields as the TCP relay server.
- The TCP relay server will send the message string to Unreal Engine every 2ms.
- Message size should have plenty of overhead to account for the size of the fields and any additional data, but adjust as needed.
- Not tested in Unreal Engine 4, but the SpartanCode page indicates it should work.
"""

def create_tcp_host(host="127.0.0.1", port=1234, listen=1):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(listen)
    print(f"Listening on {host}:{port}")
    return server_socket

def create_fields_string(fields_list):
    """
    This function places values into a string we'll decode with the blueprints in the customized Unreal TCP actor.
    Then, the values are relayed to an Unreal Engine actor via a blueprint interface and used to update the actor's properties.

    Creates a string of fields separated by spaces.
    :param fields_list: List of fields to be included in the string.
    :return: String of fields separated by spaces.
    """
    field_str = "{} " * len(fields_list)
    return field_str.format(*fields_list).rstrip()

class TCP_Relay:
    """
    TCP_Relay is a class that sets up a TCP server to relay data between Unreal Engine and a Python script.
    
    Attributes:
        server_socket (socket.socket): The server socket that listens for incoming connections.
        num_fields (int): The number of fields in the message string.
        message (str): The message string to be sent to Unreal Engine.
        linked (bool): A flag indicating whether a client is connected.
        message_in (bytes): The latest message received from the client.
        client_socket (socket.socket): The client socket connected to the server.
        thread (threading.Thread): The thread running the sender method.
    """
    def __init__(self, num_fields=23, host="127.0.0.1", port=1234, size=1024):
        self.server_socket = create_tcp_host(host, port)
        self.num_fields = num_fields
        self.size = size
        self.message = create_fields_string([0.] * self.num_fields)
        self.linked = False
        self.message_in = None
        self.client_socket = None
        self.thread = threading.Thread(target=self._server)
        self.thread.daemon = True
        self.thread.start()

    def _server(self):
        while True:
            while self.linked:
                try:
                    self.message_in = self.client_socket.recv(self.size)
                except socket.error as e:
                    print(f"Receive error: {e}")
                    self.message_in = None

                try:
                    self.client_socket.send(str.encode(self.message))
                except socket.error as e:
                    print(f"Send error: {e}")
                    print("Disconnected.")
                    self.client_socket.close()
                    self.linked = False
                    self.client_socket = None

            if not self.linked:
                try:
                    self.client_socket, client_address = self.server_socket.accept()
                    print("Connected. Client address:", client_address)
                    self.linked = True
                except socket.error as e:
                    print(f"Accept error: {e}")

            time.sleep(0.002)

# Example usage
if __name__ == "__main__":

    relay = TCP_Relay()

    x, y, z = 0., 0., 0.
    roll, pitch, yaw = 0., 0., 0.

    fields = [0.] * relay.num_fields
    fields[:6] = [x, y, z, roll, pitch, yaw]  # Example values

    while True:

        x, y, z = [(i + 10.0) for i in [x, y, z]]
        roll, pitch, yaw = [(i + 1.0) for i in [roll, pitch, yaw]]
        fields[:6] = [x, y, z, roll, pitch, yaw]

        relay.message = create_fields_string(fields)  # Example message
        print("Message Out:", relay.message)

        if relay.message_in:
            print("Message in:", relay.message_in)
        else:
            print("No message received.")

        time.sleep(1)
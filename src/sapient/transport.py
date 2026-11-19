import logging
import socket

class TCPTransport:
    def __init__(self, 
                 host:str,
                 port:int,
                 timeout:float=5.0,):
        """
        TCPTransport class is responsible for establishing a TCP connection to 
        a specified host and port.
        """
        self.log = logging.getLogger(__name__)
        
        self.host = host
        self.port = port
        self.timeout = timeout
        self._socket: socket.socket | None = None

    def connect(self)-> None:
        """
        Establish a TCP connection to the specified host and port.
        """

        if self._socket is not None:
            raise RuntimeError("Transport is already connected")

        self._socket = socket.create_connection((self.host, self.port), 
                                                timeout=self.timeout)
  
    def close(self) -> None:
        """
        Close the TCP connection.
        """
        if self._socket is not None:
            self._socket.close()
            self._socket = None

    def send(self, payload: bytes) -> None:
        """
        Send a payload over the established TCP connection.
        """
        if self._socket is None:
            raise RuntimeError("Transport is not connected")
        
        # determine lenght of payload (bytes)
        payload_length = len(payload)

        # payload lenght must be a 32-bit unsigned integer in LE format
        if payload_length > 0xFFFFFFFF:
            raise ValueError("Payload length exceeds 32-bit unsigned integer limit")
        
        # prepend the payload length as a 4-byte unsigned integer in little-endian format
        frame  = payload_length.to_bytes(4, byteorder='little') + payload

        try:
            self._socket.sendall(frame)
        except OSError:
            self.close()
            raise

    def receive(self) -> bytes:
        """
        Receive a payload from the established TCP connection.
        The first 4 bytes of the received data represent the length of the payload.
        """
        if self._socket is None:
            raise RuntimeError("Transport is not connected")

        # Read the first 4 bytes to get the payload length
        length_bytes = self._recv_exact(4)
        payload_length = int.from_bytes(length_bytes, byteorder='little')

        # Read the actual payload based on the received length
        payload = self._recv_exact(payload_length)
        return payload
    
    def _recv_exact(self, num_bytes: int) -> bytes:
        """ 
        Receive an exact number of bytes from the socket.
        """
        buffer = bytearray()
        while len(buffer) < num_bytes:
            chunk = self._socket.recv(num_bytes - len(buffer))
            if not chunk:
                raise RuntimeError("Socket connection closed unexpectedly")
            buffer.extend(chunk)
        return bytes(buffer)
    
# scpi_client.py

import socket
import json

class SCPIClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def send_command(self, command):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.host, self.port))
            s.sendall(command.encode())
            response = s.recv(16384).decode()  # 增加接收缓冲区大小
        return response

    def measure(self, device, channel):
        command = f"{device}:MEAS:{channel}"
        response = self.send_command(command)
        try:
            data = json.loads(response)
            # 返回特定通道的数据，如果不存在则返回空列表
            return data.get(str(channel), [])
        except json.JSONDecodeError:
            print(f"Error decoding response: {response}")
            return []
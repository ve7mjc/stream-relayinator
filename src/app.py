import argparse
import os
import socket
import threading
import time
from datetime import datetime, timedelta
import yaml
from typing import Optional
from helpers import ms_to_readable_string, secs_to_readable_string, backoff_delay
from typing import List

class TCPToUDPForwarder:

    socket_error_reconnect_secs: int = 1

    def __init__(self, remote_host: str, remote_port: int, udp_host: str, udp_port: int):

        self.remote_host: str = remote_host
        self.remote_port: int = remote_port
        self.udp_host: str = udp_host
        self.udp_port: int = udp_port
        
        self.stop_event: threading.Event = threading.Event()
        self.thread: threading.Thread = threading.Thread(target=self.run)

        self.reconnect_attempts: int = 0
        self.lost_connection_at: datetime

        self.delimiters: List[bytes] = []

    def add_delimiter(self, delimiter: bytes) -> None:
        self.delimiters.append(bytes)

    def set_connected(self) -> None:
        self.reconnect_attempts: int = 0

    def set_connection_lost(self) -> None:
        if not self.reconnect_attempts:
            self.lost_connection_at: datetime
            self.reconnect_attempts: int = 1
        else:
            self.reconnect_attempts += 1

    def run(self) -> None:

        # support none or double delimeters
        delimiter: Optional[bytes] = None # b'\xff'

        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_sock:
            while not self.stop_event.is_set():
                try:
                    with socket.create_connection((self.remote_host, self.remote_port)) as tcp_sock:
                        self.set_connected()
                        tcp_sock.settimeout(0.1)
                        data_buffer = b""
                        while not self.stop_event.is_set():
                            try:
                                data = tcp_sock.recv(1024)
                                if not data:
                                    raise ConnectionResetError("Connection closed by remote host")

                                data_buffer += data
                                # while delimiter in data_buffer:

                                if self.delimiters:
                                    sentence, data_buffer = data_buffer.split(delimiter, 1)
                                    udp_sock.sendto(sentence, (self.udp_host, self.udp_port))
                                else:
                                    udp_sock.sendto(data_buffer, (self.udp_host, self.udp_port))

                            except socket.timeout:
                                if data_buffer:
                                    udp_sock.sendto(data_buffer, (self.udp_host, self.udp_port))
                                    data_buffer = b""

                            except (socket.error, OSError, ConnectionResetError) as e:
                                self.lost_connection()
                                print(f"Error [{type(e)}]: {e}; reconnecting...")
                                break
                except (socket.error, OSError) as e:
                    self.set_connection_lost()
                    delay_secs: float = backoff_delay(self.lost_connection_at,self.reconnect_attempts)
                    print(f"Error [{type(e)}]: {e}; retrying connection after delay of {delay_secs}...")
                    time.sleep(delay_secs)


    def start(self) -> None:
        self.thread.start()
        

    def stop(self) -> None:
        self.stop_event.set()

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="TCP to UDP Forwarder")
    parser.add_argument("--config", help="Path to the YAML configuration file")
    parser.add_argument("--tcp_host", help="TCP remote host")
    parser.add_argument("--tcp_port", type=int, help="TCP remote port")
    parser.add_argument("--udp_host", help="UDP remote host")
    parser.add_argument("--udp_port", type=int, help="UDP remote port")
    return parser.parse_args()

def main() -> None:
    args = parse_args()

    tcp_host = os.environ.get("TCP_HOST") or args.tcp_host
    tcp_port = int(os.environ.get("TCP_PORT") or args.tcp_port) if os.environ.get("TCP_PORT") or args.tcp_port else None
    udp_host = os.environ.get("UDP_HOST") or args.udp_host
    udp_port = int(os.environ.get("UDP_PORT") or args.udp_port) if os.environ.get("UDP_PORT") or args.udp_port else None

    if args.config:
        with open(args.config, "r") as config_file:
            config = yaml.safe_load(config_file)
            tcp_host = config["tcp_host"] if "tcp_host" in config else tcp_host
            tcp_port = config["tcp_port"] if "tcp_port" in config else tcp_port
            udp_host = config["udp_host"] if "udp_host" in config else udp_host
            udp_port = config["udp_port"] if "udp_port" in config else udp_port

    if not tcp_host or not tcp_port or not udp_host or not udp_port:
        print("Error: Please provide TCP and UDP host and port values either as command-line arguments, in a YAML configuration file, or as environment variables.")
        return

    print(f"Source: {tcp_host} tcp/{tcp_port}")
    print(f"Destination: {udp_host} udp/{udp_port}")

    forwarder = TCPToUDPForwarder(tcp_host, tcp_port, udp_host, udp_port)
    forwarder.start()
    # Do something else
    forwarder.thread.join()

    forwarder.stop()

if __name__ == "__main__":

    main()



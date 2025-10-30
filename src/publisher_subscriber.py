import sys
import time
import logging
import socket
from typing import Set, Tuple


class PublisherSubscriber:
    def __init__(self, name, own_port, peer_port):
        self.name = name
        self.own_port = own_port
        self.peer_port = peer_port
        self.counter = 0
        self.subscribers: Set[Tuple[str, int]] = set()
        self.is_subscribed = False
        self.peer_host = 'agent2' if self.name == 'agent1' else 'agent1'

        # Configure logger
        self.logger = logging.getLogger(name)

        # Initialize UDP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('0.0.0.0', own_port))
        self.sock.settimeout(2)  # Shorter timeout for more frequent retries


    def send_message(self, message, host, port):
        try:
            self.sock.sendto(str(message).encode(), (host, port))
            self.logger.debug(f"Sent {message} to {host}:{port}")
        except Exception as e:
            self.logger.error(f"Error sending message to {host}:{port}: {e}")


    def publish(self, message):
        """Publish a message to all subscribers"""
        self.logger.debug(f"Publishing: {message}")
        if not self.subscribers:
            self.logger.warning("No subscribers available")
            return

        for subscriber in self.subscribers:
            self.send_message(message, subscriber[0], subscriber[1])


    def receive(self):
        """Receive and process incoming messages"""
        try:
            data, addr = self.sock.recvfrom(1024)
            message = data.decode()

            # Handle subscription messages
            if message == "SUBSCRIBE":
                if addr not in self.subscribers:
                    self.subscribers.add(addr)
                    self.logger.info(f"New subscriber from {addr}")
                self.send_message("SUBSCRIBED", addr[0], addr[1])
                # Subscribe back if we haven't already
                if not self.is_subscribed:
                    self.subscribe_to_peer()
                return None

            elif message == "SUBSCRIBED":
                self.is_subscribed = True
                self.logger.info("Subscription confirmed!")
                return None

            # Return the message as is, no need to parse as integer
            self.logger.debug(f"Received message: {message}")
            return message

        except socket.timeout:
            return None
        except Exception as e:
            self.logger.error(f"Error receiving message: {e}")
            return None


    def subscribe_to_peer(self):
        """Subscribe to peer's publications"""
        if self.is_subscribed:
            return True

        max_retries = 5
        retry_count = 0

        while retry_count < max_retries and not self.is_subscribed:
            try:
                self.logger.info(f"Sending subscription request to {self.peer_host}...")
                self.send_message("SUBSCRIBE", self.peer_host, self.peer_port)

                # Wait for subscription confirmation
                wait_start = time.time()
                while time.time() - wait_start < 2 and not self.is_subscribed:
                    self.receive()  # This will set is_subscribed if we get SUBSCRIBED message
                    time.sleep(0.1)

                if self.is_subscribed:
                    return True

            except Exception as e:
                self.logger.error(f"Error during subscription: {e}")

            retry_count += 1
            if not self.is_subscribed:
                self.logger.warning(f"Subscription attempt {retry_count} failed, retrying...")
                time.sleep(1)

        if not self.is_subscribed:
            self.logger.error("Failed to subscribe to peer after all retries")
            return False
        return True


    def ensure_mutual_subscription(self):
        """Ensure both agents are subscribed to each other"""
        max_attempts = 10
        attempt = 0

        while attempt < max_attempts:
            if self.is_subscribed and self.subscribers:
                self.logger.info("Mutual subscription established!")
                return True

            if not self.is_subscribed:
                self.subscribe_to_peer()

            # Process any incoming messages
            self.receive()

            attempt += 1
            time.sleep(0.5)

        return False

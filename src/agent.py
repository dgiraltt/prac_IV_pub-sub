import socket
import sys
import time
import logging
from typing import Set, Tuple

class Agent:
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
        self.sock.settimeout(2)


    def send_message(self, message, host, port):
        try:
            self.sock.sendto(str(message).encode(), (host, port))
        except Exception as e:
            self.logger.error(f"Error sending message to {host}:{port}: {e}")


    def publish(self, message):
        self.logger.info(f"Publishing: {message}")
        if not self.subscribers:
            self.logger.warning("No subscribers available")
            return

        for host,port in self.subscribers:
            self.send_message(message, host, port)


    def receive(self):
        try:
            data, addr = self.sock.recvfrom(1024)
            message = data.decode()

            if message == "SUBSCRIBE":
                if addr not in self.subscribers:
                    self.subscribers.add(addr)
                    self.logger.info(f"New subscriber from {addr}")
                self.send_message("SUBSCRIBED", addr[0], addr[1])

                if not self.is_subscribed:
                    self.subscribe_to_peer()
                return None

            elif message == "SUBSCRIBED":
                self.is_subscribed = True
                self.logger.info("Subscription confirmed!")
                return None

            try:
                number = int(message)
                self.logger.info(f"Received: {number}")
                return number
            except ValueError:
                return None

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

                wait_start = time.time()
                while time.time() - wait_start < 2 and not self.is_subscribed:
                    self.receive()
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

            self.receive()
            attempt += 1
            time.sleep(0.5)

        return False


    def start(self, is_initiator=False):
        self.logger.info("Starting agent...")

        if not self.ensure_mutual_subscription():
            self.logger.error("Failed to establish mutual subscription")
            sys.exit(1)

        self.sock.settimeout(None)

        if is_initiator:
            self.counter = 1
            self.logger.info(f"Starting communication with counter = {self.counter}")
            self.publish(self.counter)

        while True:
            received_number = self.receive()
            if received_number is not None:
                self.counter = received_number + 1
                self.logger.info(f"Publishing counter = {self.counter}")
                self.publish(self.counter)
                time.sleep(1)


def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(message)s'
    )

    if len(sys.argv) < 2:
        print("Usage: python agent.py <agent_name>")
        sys.exit(1)

    agent_name = sys.argv[1]
    if agent_name == 'agent1':
        agent = Agent('agent1', 5001, 5002)
        agent.start(is_initiator=True)

    elif agent_name == 'agent2':
        agent = Agent('agent2', 5002, 5001)
        agent.start(is_initiator=False)

    else:
        print("Invalid agent name. Use 'agent1' or 'agent2'")
        sys.exit(1)

if __name__ == "__main__":
    main()

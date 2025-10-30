import os
import time
import logging
import json
from publisher_subscriber import PublisherSubscriber
from tictactoe import TicTacToe


AGENT_NAME = os.environ.get("AGENT_NAME")
PORT = int(os.environ.get("PORT"))
PEER_PORT = int(os.environ.get("PEER_PORT"))

class Agent(PublisherSubscriber, TicTacToe):
    """
    An agent that plays Tic-Tac-Toe using a publisher-subscriber model over UDP.
    """
    def __init__(self, name, own_port, peer_port):
        PublisherSubscriber.__init__(self, name, own_port, peer_port)
        TicTacToe.__init__(self, name)


    def start(self, is_initiator=False):
        self.logger.info("Starting agent...")

        # Connects to peer
        if not self.ensure_mutual_subscription():
            self.logger.error("Failed to establish mutual subscription")
            return

        self.sock.settimeout(None)
        self.logger.info(f"Playing as {self.symbol}")

        # Makes first move
        if is_initiator:
            self.logger.info("Making first move...")
            row, col = self.random_move()
            self.make_move(row, col)
            self.print_board()
            move_data = {"row": row, "col": col}
            self.publish(json.dumps(move_data))

        while True:
            received_data = self.receive()
            if received_data is not None:
                try:
                    move = json.loads(received_data)
                    row, col = move["row"], move["col"]

                    # Update our board with opponent's move
                    opponent_symbol = "O" if self.symbol == "X" else "X"
                    self.board[row][col] = opponent_symbol
                    self.logger.debug(f"Opponent moved to position ({row}, {col})")

                    # Check if opponent won
                    if self.check_win():
                        self.logger.info("Game Over - Opponent wins!")
                        break

                    # Check for draw
                    if self.check_draw():
                        self.logger.info("Game Over - It's a draw!")
                        break

                    # Make our move
                    row, col = self.random_move()
                    self.make_move(row, col)
                    self.logger.info(f"Making move at position ({row}, {col})")
                    self.print_board()

                    # Send our move
                    move_data = {"row": row, "col": col}
                    self.publish(json.dumps(move_data))

                    # Check if we won
                    if self.check_win():
                        self.logger.info("Game Over - We win!")
                        break

                    # Check for draw
                    if self.check_draw():
                        self.logger.info("Game Over - It's a draw!")
                        break

                    time.sleep(2)

                except json.JSONDecodeError:
                    self.logger.error("Received invalid move data")
                except Exception as e:
                    self.logger.error(f"Error processing move: {e}")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(message)s'
    )

    agent = Agent(AGENT_NAME, PORT, PEER_PORT)
    agent.start(is_initiator=(AGENT_NAME == 'agent1'))

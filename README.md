# Tic-Tac-Toe with Publisher-Subscriber Pattern

This project implements a distributed Tic-Tac-Toe game using a publisher-subscriber pattern over UDP. Two agents can play against each other across a network, making random moves in a turn-based fashion.

## Project Structure

- `src/`: Source code directory
  - `agent.py`: Main agent implementation that combines the game logic and communication
  - `publisher_subscriber.py`: Implementation of the publisher-subscriber communication pattern using UDP
  - `tictactoe.py`: Core Tic-Tac-Toe game logic
  - `docker-compose.yml`: Docker Compose configuration for running the two game agents
  - `Dockerfile`: Docker configuration for building the agent containers

## How It Works

### Components

1. **TicTacToe (tictactoe.py)**
   - Implements the core game logic
   - Manages the game board and validates moves
   - Handles win/draw detection
   - Implements random move selection

2. **PublisherSubscriber (publisher_subscriber.py)**
   - Implements UDP-based communication between agents
   - Handles message publishing and subscription management
   - Manages network connections and message routing

3. **Agent (agent.py)**
   - Combines game logic and communication
   - Manages the game flow and turn-taking
   - Processes moves and updates game state
   - Handles game initialization and termination

### Communication Flow

- Agents communicate using a publisher-subscriber pattern over UDP
- Each agent subscribes to the other agent's messages
- Moves are exchanged as JSON messages containing row and column coordinates
- The game continues until a win or draw is detected

## Running the Game

The game is designed to run using Docker containers. Here's how to start it:

1. Make sure you have Docker and Docker Compose installed on your system

2. Navigate to the project directory:
   ```bash
   cd src
   ```

3. Build and run the containers:
   ```bash
   docker compose up
   ```

This will start two agent containers that will play against each other. The agents will:
- Establish a mutual subscription
- Take turns making moves
- Display the game board after each move
- Announce the winner or draw when the game ends

## Environment Variables

The following environment variables are required:
- `AGENT_NAME`: Name of the agent (agent1 or agent2)
- `PORT`: Port number for the agent's UDP server
- `PEER_PORT`: Port number of the peer agent's UDP server

These are automatically configured in the Docker Compose setup.

## Game Rules

- Agent1 plays as 'X' and Agent2 plays as 'O'
- Agent1 initiates the game with the first move
- Moves are made randomly on available spaces
- The game ends when either:
  - A player wins by completing a row, column, or diagonal
  - The board is full (draw)

# NEAT-Cars Architecture Diagrams

## System Architecture Diagram

```mermaid
graph TD
    subgraph "NEAT-Cars Application"
        UI[UI / Frontend]
        GameEngine[Game Engine / Backend]
        UI <--> GameEngine
    end

    subgraph "AI Components"
        NEAT[NEAT Algorithm]
        NeuralNetwork[Neural Network]
        CarAI[Car AI Controller]
        NEAT --> NeuralNetwork
        NeuralNetwork --> CarAI
    end

    subgraph "File System"
        TrackFiles[Track Files]
        Checkpoints[Checkpoints]
        ConfigFiles[Config Files]
    end

    %% Connect subgraphs
    GameEngine --> NEAT
    CarAI --> TrackFiles
    CarAI --> Checkpoints
    CarAI --> ConfigFiles
```

## NEAT Overview

```mermaid
graph LR
    %% Define nodes
    A[Initialize<br>Population]
    B[Simulate Cars<br>with NNs]
    C[Calculate<br>Fitness]
    D[Select Top<br>Performers]
    E[Generate New<br>Population]
    F[Mutate<br>Networks]
    G[Crossover<br>Networks]
    H[New<br>Generation]

    %% Create circular connections
    A --> B
    B --> C
    C --> D
    D --> E
    E --> F
    F --> G
    G --> H
    H --> A
```

## Sequence Diagram

```mermaid
sequenceDiagram
    participant User as User
    participant GameEngine as GameEngine
    participant GameState as GameState
    participant Track as Track
    participant Car as Car
    participant CarAI as CarAI
    participant NeuralNetwork as NeuralNetwork

    User->>GameEngine: Start Simulation
    GameEngine->>GameState: Initialize State
    GameState->>Track: Load Track
    GameState->>Car: Initialize Car
    GameState->>CarAI: Initialize AI
    CarAI->>NeuralNetwork: Create Networks
    Car->>Track: Get Sensor Data
    Car->>NeuralNetwork: Process Sensor Data
    NeuralNetwork->>Car: Return Actions
    Car->>Track: Update Position
    Car->>CarAI: Update Performance
    CarAI->>NeuralNetwork: Update Networks
    CarAI->>GameState: Update Fitness
    GameState->>GameEngine: Update Display
    GameEngine->>User: Show Results
```

## Component Relationships

```mermaid
classDiagram
    direction LR

    class GameEngine {
        +run()
        +handle_events()
        +update()
        +render()
    }

    class GameState {
        +current_state
        +track
        +car
        +car_ai
        +set_state()
        +load_track()
        +load_checkpoint()
    }

    class Car {
        +position
        +angle
        +speed
        +sensors
        +update()
        +get_data()
        +turn_left()
        +turn_right()
        +accelerate()
        +brake()
    }

    class CarAI {
        +genomes
        +nets
        +cars
        +compute()
        +compute_reward()
    }

    class Track {
        +track_name
        +checkpoints
        +finish_line
        +load_track()
        +save_track()
        +get_ai_track()
    }

    class NeuralNetwork {
        +nodes
        +connections
        +activate()
        +mutate()
        +crossover()
    }

    GameEngine "1" --> "1" GameState
    GameState "1" --> "1" Track
    GameState "1" --> "1" Car
    GameState "1" --> "1" CarAI
    CarAI "1" --> "*" Car
    CarAI "1" --> "*" NeuralNetwork
    Car "1" --> "1" NeuralNetwork
```

## State Flow Diagram

```mermaid
stateDiagram-v2
    [*] --> MainMenu
    MainMenu --> TrainAI
    MainMenu --> SimulateAI
    MainMenu --> Exit

    TrainAI --> EnterTrackName
    TrainAI --> SelectTrack
    TrainAI --> Map

    EnterTrackName --> DrawTrack
    DrawTrack --> PlaceCar
    SelectTrack --> PlaceCar
    Map --> PlaceCar

    SimulateAI --> SelectTrack
    SimulateAI --> Map
    SimulateAI --> SelectGeneration
    SelectGeneration --> PlaceCar

    PlaceCar --> PlaceDestinationMarker
    PlaceDestinationMarker --> StartSimulation
    StartSimulation --> MainMenu
```

## Neural Network Structure

```mermaid
graph TD
    subgraph "Input Layer"
        S1[Sensor -90°]
        S2[Sensor -45°]
        S3[Sensor 0°]
        S4[Sensor 45°]
        S5[Sensor 90°]
    end

    subgraph "Output Layer"
        O1[Left]
        O2[Right]
        O3[Accelerate]
        O4[Brake]
    end

    %% Simplified connections
    S1 & S2 & S3 & S4 & S5 -.-> O1
    S1 & S2 & S3 & S4 & S5 -.-> O2
    S1 & S2 & S3 & S4 & S5 -.-> O3
    S1 & S2 & S3 & S4 & S5 -.-> O4
```

These diagrams provide a comprehensive view of the NEAT-Cars system architecture, including:

- System overview with component relationships
- Detailed sequence of operations
- Class relationships and responsibilities
- State flow through the application
- Neural network structure and connections

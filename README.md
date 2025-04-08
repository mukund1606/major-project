# NEAT-AI Car Simulation

- Main Menu

  - Train AI
    - Create Track (Allow user to draw a track, save track coordinates, also add checkpoints with right click, use open-cv to get center of the track for finding length)
    - Select Track (Load track from file)
    - Select Map (Load map from tileset)
  - Simulate AI

    - Select Track
    - Select Map

  - Place Car (Show car preview following the mouse and allow user to place car on the track, arrow keys to rotate car)
  - Place Destination Point on the track (After placing the car, press space to go to next step of placing the destination point)
  - Enter to Start the Simulation
  <!-- - Place Traffic Lights (If Possible) -->

  - Reward Function
    - Distance to Destination Point on Track
    - Avoiding Collisions
    - Time taken to reach Destination Point
    - Number of checkpoints passed
    <!-- - Number of traffic lights passed (If Possible) -->
    - Penalty for overspeeding
    - Penalty for crashing
    - Penalty for taking wrong turns
    - Penalty for going too close to the edges of the track
    - Penalty for going backwards

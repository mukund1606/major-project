import neat
import pygame
from neural_network.nn import NN
from render.car import Car, Action

from render.game_state import GameState


class CarAI:
    TIME_LIMIT = 60

    def __init__(
        self,
        config: neat.Config,
        genomes: list[tuple[int, neat.DefaultGenome]],
        game_state: GameState,
    ):
        game_state.CURRENT_GENERATION += 1
        self.GAME_STATE = game_state

        self.genomes = genomes

        self.cars: list[Car] = []
        self.nets: list[neat.nn.FeedForwardNetwork] = []

        self.BEST_FITNESS: float = 0

        # Visual Neural Network (for simulation)
        self.VISUAL_NNS: list[NN] = []
        self.BEST_VISUAL_NN: NN | None = None

        # We create a neural network for every given genome
        for _, genome in genomes:
            net = neat.nn.FeedForwardNetwork.create(genome, config)
            self.nets.append(net)
            genome.fitness = 0  # type: ignore
            self.cars.append(Car(game_state))
            self.VISUAL_NNS.append(NN(config, genome, (60, 130)))

        self.remaining_cars = len(self.cars)
        self.best_input = None

    def compute(self) -> None:
        """Compute the next move of every car and update their fitness

        Args:
            genomes (neat.DefaultGenome): The neat genomes
            track (pygame.Surface): The track on which the car is being drawn
            width (int): The width of the window
        """
        i = 0
        for car, net in zip(self.cars, self.nets):

            car_data = car.get_data()

            # Activate the neural network and get the output from the car_data (input)
            output = net.activate(car_data)

            # Output gets treated and the car is updated in the next lines
            choice = output.index(max(output))

            # TODO
            # Refreshing nodes of all neural networks
            for node in self.VISUAL_NNS[i].nodes:
                node.inputs = car_data
                node.output = choice

            # 0: Left
            if choice == Action.TURN_LEFT:
                car.turn_left()

            # 1: Right
            elif choice == Action.TURN_RIGHT:
                car.turn_right()

            # 2: Accelerate
            elif choice == Action.ACCELERATE:
                car.accelerate()

            # 3: Brake
            elif choice == Action.BRAKE:
                car.brake()

            i += 1

        # Refresh cars sprites, number of cars which are still alive and update their fitness
        self.remaining_cars = sum(1 for car in self.cars if car.alive)

    def compute_reward(self, track: pygame.Surface) -> None:
        # First update all sprites and compute rewards
        for i, car in enumerate(self.cars):
            # Update sprite regardless of alive status to handle dead sprite rendering
            car.update_sprite(track)
            if car.alive:
                self.genomes[i][1].fitness = car.get_reward()  # type: ignore
                if self.genomes[i][1].fitness > self.BEST_FITNESS:  # type: ignore
                    self.BEST_FITNESS = self.genomes[i][1].fitness  # type: ignore

        # Now find the best alive genome and show its NN
        best_alive_fitness = -float("inf")
        best_alive_index = -1

        for i, car in enumerate(self.cars):
            if car.alive and self.genomes[i][1].fitness is not None:
                # Also Ignore if the car has reached the finish line
                if car.reached_finish_line:
                    continue
                if self.genomes[i][1].fitness > best_alive_fitness:
                    best_alive_fitness = self.genomes[i][1].fitness
                    best_alive_index = i

        # If we found a best alive genome, show its neural network
        if best_alive_index != -1:
            self.BEST_VISUAL_NN = self.VISUAL_NNS[best_alive_index]
            self.GAME_STATE.BEST_VISUAL_NN = self.BEST_VISUAL_NN

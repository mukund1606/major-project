from render.game_engine import GameEngine

from constants import NEAT_CONFIG_PATH, DEBUG, MAX_SIMULATIONS


def main() -> None:
    window = GameEngine(NEAT_CONFIG_PATH, DEBUG, MAX_SIMULATIONS)
    window.run()


if __name__ == "__main__":
    main()

from render.game_engine import GameEngine

NEAT_CONFIG_PATH = "neat_config.ini"
DEBUG = True
MAX_SIMULATIONS = 1000


def main() -> None:
    window = GameEngine(NEAT_CONFIG_PATH, DEBUG, MAX_SIMULATIONS)
    window.run()


if __name__ == "__main__":
    main()

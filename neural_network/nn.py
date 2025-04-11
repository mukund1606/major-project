import neat
import pygame

from neural_network.node import Node, Connection, NodeType
from data_models import Color


class NN:
    INPUT_NEURONS = 5
    OUTPUT_NEURONS = 4

    def __init__(self, config: neat.Config, genome: neat.DefaultGenome, pos: tuple):
        self.nodes = []
        self.genome = genome
        self.pos = (int(pos[0] + Node.RADIUS), int(pos[1]))
        input_names = ["-90°", "-45°", "0°", "45°", "90°"]
        output_names = ["Left", "Right", "Accelerate", "Brake"]

        # Check if hidden nodes should be shown based on config
        show_hidden_nodes = config.genome_config.num_hidden > 0

        # Initialize lists
        hidden_nodes = []
        input_keys = list(config.genome_config.input_keys)
        output_keys = list(config.genome_config.output_keys)

        # Only consider nodes that are neither input nor output nodes if we're showing hidden nodes
        if show_hidden_nodes:
            for n in genome.nodes.keys():
                if n not in input_keys and n not in output_keys:
                    hidden_nodes.append(n)

        node_id_list = []

        # nodes
        h = (NN.INPUT_NEURONS - 1) * (Node.RADIUS * 2 + Node.SPACING)
        for i, input in enumerate(config.genome_config.input_keys):
            n = Node(
                input,
                pos[0],
                pos[1] + int(-h / 2 + i * (Node.RADIUS * 2 + Node.SPACING)),
                NodeType.INPUT,  # type: ignore
                [
                    Color.GREEN_PALE,
                    Color.GREEN,
                    Color.DARK_GREEN_PALE,
                    Color.DARK_GREEN,
                ],  # type: ignore
                input_names[i],
                i,
            )
            self.nodes.append(n)
            node_id_list.append(input)

        h = (NN.OUTPUT_NEURONS - 1) * (Node.RADIUS * 2 + Node.SPACING)
        for i, out in enumerate(config.genome_config.output_keys):
            n = Node(
                out,
                pos[0] + 2 * (Node.LAYER_SPACING + 2 * Node.RADIUS),
                pos[1] + int(-h / 2 + i * (Node.RADIUS * 2 + Node.SPACING)),
                NodeType.OUTPUT,  # type: ignore
                [Color.RED_PALE, Color.RED, Color.DARK_RED_PALE, Color.DARK_RED],  # type: ignore
                output_names[i],
                i,
            )
            self.nodes.append(n)
            node_id_list.append(out)

        # Only render hidden nodes if they actually exist
        if hidden_nodes:
            h = (
                (len(hidden_nodes) - 1) * (Node.RADIUS * 2 + Node.SPACING)
                if len(hidden_nodes) > 1
                else 0
            )
            for i, m in enumerate(hidden_nodes):
                n = Node(
                    m,
                    self.pos[0] + (Node.LAYER_SPACING + 2 * Node.RADIUS),
                    self.pos[1] + int(-h / 2 + i * (Node.RADIUS * 2 + Node.SPACING)),
                    NodeType.HIDDEN,  # type: ignore
                    [Color.BLUE_PALE, Color.DARK_BLUE, Color.BLUE_PALE, Color.DARK_BLUE],  # type: ignore
                )
                self.nodes.append(n)
                node_id_list.append(m)

        # connections
        self.connections = []
        for c in genome.connections.values():
            if c.enabled:
                input_, output = c.key

                # Only attempt to create connections if both nodes are in our node_id_list
                if input_ in node_id_list and output in node_id_list:
                    input_idx = node_id_list.index(input_)
                    output_idx = node_id_list.index(output)

                    # Check node types
                    input_type = self.nodes[input_idx].type
                    output_type = self.nodes[output_idx].type

                    # Create connections based on node types
                    if (
                        input_type == NodeType.INPUT and output_type == NodeType.OUTPUT
                    ) or (
                        show_hidden_nodes
                        and (
                            (
                                input_type == NodeType.INPUT
                                and output_type == NodeType.HIDDEN
                            )
                            or (
                                input_type == NodeType.HIDDEN
                                and output_type == NodeType.OUTPUT
                            )
                        )
                    ):
                        self.connections.append(
                            Connection(
                                self.nodes[input_idx],
                                self.nodes[output_idx],
                                c.weight,
                            )
                        )

    def draw(self, screen: pygame.Surface):
        for c in self.connections:
            c.draw(screen)
        for node in self.nodes:
            node.draw(screen)

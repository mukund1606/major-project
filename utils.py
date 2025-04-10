import cv2
import csv
import numpy as np
from PIL import Image
import pygame
from skimage.morphology import skeletonize
import sys


def quit_event(event: pygame.event.Event) -> None:
    if event.type == pygame.QUIT:
        pygame.quit()
        sys.exit(0)


def calculate_track_length(pil_image: Image.Image):
    # Convert PIL image to OpenCV format (BGR)
    img_color = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
    if img_color is None:
        raise ValueError("Could not process the provided PIL image.")

    # Create mask: any pixel not pure white is considered part of the track
    non_white_mask = np.any(img_color < [250, 250, 250], axis=2).astype(np.uint8)

    # Invert to make track = 1, background = 0
    binary = non_white_mask

    # Clean up noise (optional)
    kernel = np.ones((3, 3), np.uint8)
    binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)

    # Skeletonize
    skeleton = skeletonize(binary).astype(np.uint8)

    # Count skeleton pixels
    track_length = np.count_nonzero(skeleton)

    return track_length


def load_csv(path: str) -> list[list[int]]:
    data: list[list[int]] = []
    with open(path, "r") as file:
        reader = csv.reader(file)
        for row in reader:
            data.append([int(cell) for cell in row])
    return data

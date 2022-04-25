from dataclasses import dataclass
from typing import Tuple
import os
import sys

sys.path.append(os.path.dirname(os.path.realpath(__file__)))
from sceneobject import SceneObject


@dataclass
class Camera(SceneObject):
    location: Tuple[float, float, float]
    rotation: Tuple[float, float, float]
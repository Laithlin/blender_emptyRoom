from typing import Optional
import os
import sys

sys.path.append(os.path.dirname(os.path.realpath(__file__)))
from material import Material
from sceneobject import SceneObject


class Entity(SceneObject):

    def __init__(self):
        self.material: Optional[Material] = None

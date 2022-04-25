import abc
from typing import List, Optional
import sys
import os

sys.path.append(os.path.dirname(os.path.realpath(__file__)))
from sceneobject import SceneObject
from world_texture import WorldTexture


class Scene:

    def __init__(self):
        self.objects: List[SceneObject] = []
        self.world_texture: Optional[WorldTexture] = None

    @abc.abstractmethod
    def build(self):
        pass

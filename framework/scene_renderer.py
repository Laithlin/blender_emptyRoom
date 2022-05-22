from abc import ABC, abstractmethod
from dataclasses import dataclass
import sys
import os

sys.path.append(os.path.dirname(os.path.realpath(__file__)))
from framework.modeler_interface import ModelerInterface
from scene import Scene


@dataclass
class SceneRenderer(ABC):
    modeler: ModelerInterface

    @abstractmethod
    def _render_object(self, obj):
        pass

    def render(self, scene: Scene):
        self.modeler.remove_default_objects()
        self.modeler.initialize()

        if scene.world_texture is not None:
            self.modeler.set_world_texture(scene.world_texture)

        for obj in scene.objects:
            self._render_object(obj)



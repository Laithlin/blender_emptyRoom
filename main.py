import sys
import os
import bpy
import mathutils
import random

sys.path.append(os.path.dirname(os.path.realpath(__file__)))
# print(os.path.dirname(os.path.realpath(__file__)))
from scripts.blender_func import RoomScene
from scripts.renderer import Renderer
from scripts.modeler import Modeler

def place_model(model, scene, place, scale=1.0):
    dir = '../ShapeNetCore.v1(1)/ShapeNetCore.v1/mgr_przydatne/' + model
    filename = random.choice(os.listdir(dir))
    path = os.path.join(dir, filename, 'model.obj')
    # print(path)


    file_loc = path
    # use_split_objects musi byc na False bo inaczej importuje sie nie jako pokedynczy obiekt i jest problem z przesuwaniem
    imported_object = bpy.ops.import_scene.obj(filepath=file_loc, use_split_objects=False)
    obj_object = bpy.context.selected_objects[0]

    obj_object.scale[0] *= scale
    obj_object.scale[1] *= scale
    obj_object.scale[2] *= scale

    # print(obj_object.dimensions[1])
    if(model == 'chandeliers'):
        move_chandeliers(obj_object, scene)
    else:
        move_object(obj_object, scene, place, scale)


def move_object(obj_object, scene, place, scale=1.0):
    # (x,y,z) x to czerowna, y do gory, z to zielona
    # czerwona na plus, zielona na minus i wtedy jest w pokoju
    vec = mathutils.Vector(((obj_object.dimensions[0] / 2 ) * scale + scene.size_x * place[0] + scene.wall_thickness,
                            (obj_object.dimensions[1] / 2) * scale + 0.02,
                            -((obj_object.dimensions[2] / 2) * scale + scene.size_y * place[1] + scene.wall_thickness)))
    inv = obj_object.matrix_world.copy()
    inv.invert()
    # vec aligned to local axis in Blender 2.8+
    # in previous versions: vec_rot = vec * inv
    vec_rot = vec @ inv
    obj_object.location = obj_object.location + vec_rot

def move_chandeliers(obj_object, scene):
    # (x,y,z) x to czerowna, y do gory, z to zielona
    # czerwona na plus, zielona na minus i wtedy jest w pokoju
    vec_2 = mathutils.Vector(
        (scene.size_x / 2,
         -obj_object.dimensions[1] / 2 + scene.height - 0.02,
         -scene.size_y / 2))
    inv_2 = obj_object.matrix_world.copy()
    inv_2.invert()
    # vec aligned to local axis in Blender 2.8+
    # in previous versions: vec_rot = vec * inv
    vec_rot_2 = vec_2 @ inv_2
    obj_object.location = obj_object.location + vec_rot_2


def number_of_furniture(scene):
    pass


def render_bedroom(scene):
    pass


def render_bathroom(scene):
    pass


def render_kitchen(scene):
    pass


def render_livingRoom(scene):
    pass


if __name__ == '__main__':
    scene = RoomScene()
    # scene.remove_default_objects()
    # print(scene.size_x)
    scene.build()

    modeler = Modeler()

    scene_render = Renderer()
    scene_render.modeler = modeler
    scene_render.render(scene)

    bpy.ops.export_scene.obj(filepath="/home/justyna/All/magisterka/pusty.obj")

    # TODO: tutaj jest sprawdzane jak to bedzie z losowaniem sciezki

    place_model('armchairs', scene, [1/2, 1/2])

    # TODO: tutaj jest sprawdzane jak to jest z zyrandolem

    place_model('chandeliers', scene, None)

    # TODO: dodajemy biurko

    place_model('desks', scene, [1/4, 1/4], 2)

    place_model('bookshelfs', scene, [0, 5/8], 2.5)

    place_model('beds', scene, [5/8, 0], 3)

    bpy.ops.export_scene.obj(filepath="/home/justyna/All/magisterka/plik.obj")

    print('build succeeded')


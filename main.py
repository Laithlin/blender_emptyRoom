import sys
import os
import bpy
import mathutils
import random
import numpy as np
import cv2
from PIL import Image
import matplotlib.pyplot as plt

sys.path.append(os.path.dirname(os.path.realpath(__file__)))
# print(os.path.dirname(os.path.realpath(__file__)))
from scripts.blender_func import RoomScene
from scripts.renderer import Renderer
from scripts.modeler import Modeler


def changeGPU():
    bpy.data.scenes[0].render.engine = "CYCLES"

    # Set the device_type
    bpy.context.preferences.addons[
        "cycles"
    ].preferences.compute_device_type = "CUDA" # or "OPENCL"

    # Set the device and feature set
    bpy.context.scene.cycles.device = "GPU"

    # get_devices() to let Blender detects GPU device
    bpy.context.preferences.addons["cycles"].preferences.get_devices()
    print(bpy.context.preferences.addons["cycles"].preferences.compute_device_type)
    for d in bpy.context.preferences.addons["cycles"].preferences.devices:
        if d["name"] == "NVIDIA GeForce GTX 960M (Display)":
            d["use"] = 1 # Using all devices, include GPU and CPU
        else:
            d["use"] = 0
        print(d["name"], d["use"])

    # change settings
    scene = bpy.context.scene
    scene.cycles.samples = 100
    scene.render.resolution_x = 640
    scene.render.resolution_y = 480

    settings = scene.render.image_settings
    settings.color_depth = '16'
    settings.file_format = 'PNG'

    # print(bpy.context.scene)
    # scene.screen.View3DShading.studiolight_intensity = 0



def create_walls():
    scene = RoomScene()
    # scene.remove_default_objects()
    # print(scene.size_x)
    scene.build()

    modeler = Modeler()

    scene_render = Renderer()
    scene_render.modeler = modeler
    scene_render.render(scene)

    return scene


def place_model(model, scene, l_furniture, scale=1.0):
    dir = '../mgr_przydatne/' + model
    filename = random.choice(os.listdir(dir))
    path = os.path.join(dir, filename, 'model.obj')
    # print(path)

    file_loc = path
    # use_split_objects musi byc na False bo inaczej importuje
    # sie nie jako pokedynczy obiekt i jest problem z przesuwaniem
    imported_object = bpy.ops.import_scene.obj(filepath=file_loc, use_split_objects=False)
    obj_object = bpy.context.selected_objects[0]
    print("dimensions:")
    print(obj_object.dimensions)

    obj_object.scale[0] *= scale
    obj_object.scale[1] *= scale
    obj_object.scale[2] *= scale

    # print(obj_object.dimensions[1])
    if(model == 'chandeliers'):
        move_chandeliers(obj_object, scene)
        return np.array([0, 0])
    else:
        move_object(obj_object, scene, l_fur=l_furniture, scale=scale)
        return np.array([obj_object.dimensions[0]*scale, obj_object.dimensions[2]*scale])


def move_object(obj_object, scene, l_fur, scale):
    # (x,y,z) x to czerowna, y do gory, z to zielona
    # czerwona na plus, zielona na minus i wtedy jest w pokoju
    # vec = mathutils.Vector(((obj_object.dimensions[0] / 2 * obj_place[0]) * scale + l_fur[0] + scene.size_x * place[0] + scene.wall_thickness,
    #                         (obj_object.dimensions[1] / 2) * scale + 0.02,
    #                         -((obj_object.dimensions[2] / 2 * obj_place[1]) * scale + scene.size_y * place[1] + scene.wall_thickness)))

    vec = mathutils.Vector(((obj_object.dimensions[0] / 2) * scale + scene.wall_thickness,
                            (obj_object.dimensions[1] / 2) * scale + 0.02,
                            -((obj_object.dimensions[2] / 2) * scale + l_fur[1])))

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


def clean_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()


def number_of_furniture(scene):
    area = scene.size_x * scene.size_y
    print("area " + str(area))

    if area >= 1 and area <= 15:
        print('small')
        return 4
    elif area > 15 and area <= 45:
        print('medium')
        return 5
    elif area > 45 and area <= 80:
        print('large')
        return 9
    elif area > 80 and area <= 100:
        print('xl')
        return 12
    else:
        print('somethng went wrong')
        return None


def random_furniture(scene, furniture_const, furniture):
    furniture_number = number_of_furniture(scene)
    print("furmiture number " + str(furniture_number))
    furniture_add = furniture_number - len(furniture_const)
    fur_add = []

    for i in range(furniture_add):
        fur_add.append(random.randrange(0, len(furniture)))

    return fur_add


def delete_furniture(loop):
    bpy.ops.object.select_all(action='DESELECT')
    bpy.data.objects['model'].select_set(True)  # Blender 2.8x

    for i in range(loop):
        bpy.data.objects['model.00' + str(i + 1)].select_set(True)

    bpy.ops.object.delete()


def render_room(furniture_const, furniture, scene):
    last_furniture = np.array([scene.wall_thickness, scene.wall_thickness])

    more_furniture = random_furniture(scene, furniture_const, furniture)
    print(more_furniture)
    last_furniture += place_model('chandeliers', scene, last_furniture)
    print("check dimensions:")
    print(last_furniture)
    last_furniture += place_model(furniture_const[0], scene, last_furniture, scale=2)
    print("check dimensions:")
    print(last_furniture)
    last_furniture += place_model(furniture_const[1], scene, last_furniture)
    print("check dimensions:")
    print(last_furniture)
    last_furniture += place_model(furniture_const[2], scene, last_furniture)
    print("check dimensions:")
    print(last_furniture)

    for i in range(len(more_furniture)):
        last_furniture += place_model(furniture[more_furniture[i]], scene, last_furniture)
        print("check dimensions:")
        print(last_furniture)

    loop = len(furniture_const) + len(more_furniture)

# def render_bedroom(scene):
#     furniture_const = ['beds', 'dressers', 'armchairs']
#     furniture = ['armchairs', 'desks', 'beds', 'couches',
#                  'pianos', 'dressers', 'standing_lamps',
#                  'bookshelfs', 'speakers']


# def render_bathroom(scene):
#     furniture_const = ['bathtubs', 'washers', 'standing_lamps']
#     furniture = ['bathtubs', 'washers', 'standing_lamps', 'armchairs', 'bins',
#                  'cabinets']


# def render_kitchen(scene):
#     furniture_const = ['dishwashers', 'desks', 'stoves']
#     furniture = ['armchairs', 'desks', 'dishwashers', 'bins',
#                  'standing_lamps', 'cabinets', 'bookshelfs', 'stoves']


# def render_livingRoom(scene):
#     furniture_const = ['couches', 'desks', 'armchairs']
#     furniture = ['armchairs', 'desks', '', 'couches',
#                  'pianos', 'dressers', 'standing_lamps',
#                  'bookshelfs', 'speakers']


def render_scenes():
    scene = create_walls()
    render_room(['couches', 'desks', 'armchairs'],
                ['armchairs', 'desks', 'couches',
                 'pianos', 'dressers', 'standing_lamps',
                 'bookshelfs', 'speakers'],
                scene)
    # save_image_render(scene)
    change_camera_place(scene, 2)

def change_camera_place(scene, number):
    #na 8m chyba najdalej siega kinect
    #losuje wartosc 0 lub 1 zeby zdecydowac na ktora sciane patrzy
    x_or_y = random.randrange(0, 2)
    # print(x_or_y)

    #jak 0 to patrzy na y
    # if x_or_y == 0:
    #     # scene.camera_location = (scene.size_x, scene.size_y / 2, 1)
    #     scene.camera_rotation = (scene.PI / 2, 0, scene.PI / 2) #scene.PI / 2
    bpy.ops.object.select_all(action='DESELECT')
    scene.camera_rotation = (0, 0, 0)
    bpy.data.objects['Camera'].select_set(True)
    bpy.ops.object.delete()
    #trzeba bedzie dodac od nowa kamere ale w innym miejscu

    # zrobimy tablice ze stalymi polozeniami kamery
    # najmniejsza dlugosc sciany to 3m czyli dla wszystkich pokoi mozna zrobic
    # podstawowe zdjecia na 3m, czyli dla tych najmniejszych pokoi bedzie
    # mniej zdjec a dla najwiekszych najwiecej
    # chyba dosc logicznie
    # startowe:
    # location = (3, scene.size_y / 2, 1)
    # orientation = (scene.PI / 2, 0, scene.PI / 2)

    location_smallest = [(3, scene.size_y / 2, 1), (3, scene.size_y / 2, 3), (3, scene.size_y / 2, 3),
                         (3, scene.size_y / 2, 3)]
    orientation_smallest = [(scene.PI / 2, 0, scene.PI / 2), (scene.PI / 4, 0, scene.PI / 2), (scene.PI / 6, 0, scene.PI / 2),
                            (scene.PI / 4, 0, scene.PI / 2)]

    location = (3, scene.size_y / 2, 3)
    orientation = (scene.PI / 4, 0, scene.PI / 2) # ostatniego nie zmieniac chyba ze chcesz zeby obraz byl krzywo
    bpy.ops.object.camera_add(location=list(location), rotation=list(orientation))
    bpy.context.selected_objects[0].name = "Camera"



def get_depth():
    """Obtains depth map from Blender render.
    :return: The depth map of the rendered camera view as a numpy array of size (H,W).
    """
    z = bpy.data.images['Viewer Node']
    # print(z.pixels)
    w, h = z.size
    dmap = np.array(z.pixels[:], dtype=np.float32) # convert to numpy array
    dmap = np.reshape(dmap, (h, w, 4))[:,:,0]
    dmap = np.rot90(dmap, k=2)
    dmap = np.fliplr(dmap)
    return dmap


def save_image_render(scene):
    bpy.ops.export_scene.obj(filepath="/home/justyna/All/magisterka/pusty.obj")

    # change_camera_place(scene, 2)
    bpy.context.scene.camera = bpy.data.objects['Camera']
    bpy.context.view_layer.objects.active = bpy.data.objects['Sun']

    #moje

    bpy.context.scene.use_nodes = True
    tree = bpy.context.scene.node_tree
    links = tree.links

    # clear default nodes
    for n in tree.nodes:
        tree.nodes.remove(n)

    scene = bpy.context.scene

    # settings = scene.render.image_settings
    # settings.color_depth = '16'
    # settings.file_format = 'PNG'

    scene.view_layers["ViewLayer"].use_pass_z = True
    scene.use_nodes = True

    nodes = scene.node_tree.nodes
    rl = tree.nodes.new('CompositorNodeRLayers')
    norm = tree.nodes.new('CompositorNodeNormalize')
    compositor = tree.nodes.new('CompositorNodeComposite')
    view = tree.nodes.new('CompositorNodeViewer')

    links.new(rl.outputs[0], compositor.inputs[0])
    # links.new(rl.outputs[2], norm.inputs[0])
    # links.new(norm.outputs[0], view.inputs[0])

    links.new(rl.outputs[2], view.inputs[0])

    # # create a file output node and set the path
    # fileOutput = tree.nodes.new(type="CompositorNodeOutputFile")
    # fileOutput.base_path = "/home/justyna/All/magisterka/"
    # fileOutput.file_slots[0].path = 'depth_sprawdzmy.png'
    # links.new(norm.outputs[0], fileOutput.inputs[0])

    bpy.context.scene.render.filepath = "/home/justyna/All/magisterka/rgb.png"
    bpy.ops.render.render(False, animation=False, write_still=True)

    dmap = get_depth()
    print(dmap)
    for pixel in range(len(dmap)):
        # print("sprawdzmy")
        # print(len(dmap[pixel]))
        for pix in range(len(dmap[pixel])):
            if dmap[pixel][pix] >= 7:
                dmap[pixel][pix] = 100000000
            else:
                dmap[pixel][pix] = dmap[pixel][pix]*1000
    print("koniec")

    print(dmap)
    dmap_w = np.array(dmap, dtype=np.uint16)

    cv2.imwrite("sprawdzmy_pokoje2.png", dmap_w)


def auto_render():
    pass

if __name__ == '__main__':
    changeGPU()
    render_scenes()

    # bpy.ops.export_scene.obj(filepath="/home/justyna/All/magisterka/pusty.obj")
    #
    # # TODO: tutaj jest sprawdzane jak to bedzie z losowaniem sciezki
    #
    # place_model('armchairs', scene, [1/2, 1/2])
    #
    # # TODO: tutaj jest sprawdzane jak to jest z zyrandolem
    #
    # place_model('chandeliers', scene, None)
    #
    # # TODO: dodajemy biurko
    #
    # place_model('desks', scene, [1/4, 1/4], scale=2)
    #
    # place_model('bookshelfs', scene, [0, 5/8], scale=2.5)
    #
    # place_model('beds', scene, [5/8, 0], scale=3)
    #
    # bpy.ops.export_scene.obj(filepath="/home/justyna/All/magisterka/plik.obj")



    print('build succeeded')


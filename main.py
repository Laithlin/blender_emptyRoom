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

last_f = np.array([0, 0])
vertical_fur = False

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


def place_model(model, scene, scale=1.0):
    dir = '../mgr_przydatne/' + model
    filename = random.choice(os.listdir(dir))
    path = os.path.join(dir, filename, 'model.obj')
    # print(path)

    file_loc = path
    # use_split_objects musi byc na False bo inaczej importuje
    # sie nie jako pokedynczy obiekt i jest problem z przesuwaniem
    imported_object = bpy.ops.import_scene.obj(filepath=file_loc, use_split_objects=False)
    obj_object = bpy.context.selected_objects[0]
    bpy.context.selected_objects[0].name = "model"
    # print("dimensions:")
    # print(obj_object.dimensions)

    obj_object.scale[0] *= scale
    obj_object.scale[1] *= scale
    obj_object.scale[2] *= scale

    # print(obj_object.dimensions[1])
    if(model == 'chandeliers'):
        move_chandeliers(obj_object, scene)
        # return np.array([0, 0])
    else:
        move_object(obj_object, scene, scale=scale)
        # return np.array([obj_object.dimensions[0]*scale, obj_object.dimensions[2]*scale])


def move_object(obj_object, scene, scale):
    # (x,y,z) x to czerowna, y do gory, z to zielona
    # czerwona na plus, zielona na minus i wtedy jest w pokoju
    # vec = mathutils.Vector(((obj_object.dimensions[0] / 2 * obj_place[0]) * scale + l_fur[0] + scene.size_x * place[0] + scene.wall_thickness,
    #                         (obj_object.dimensions[1] / 2) * scale + 0.02,
    #                         -((obj_object.dimensions[2] / 2 * obj_place[1]) * scale + scene.size_y * place[1] + scene.wall_thickness)))

    #zrobic klase zeby nie uzywac tego globalnie
    global last_f
    global vertical_fur

    rand_x = random.uniform(0, 2)
    rand_y = random.uniform(0, 2)

    # print("ostatni:")
    # print(last_f)
    # print("orientacja: ")
    # print(obj_object.rotation_euler)
    if scene.size_y >= (last_f[1] + obj_object.dimensions[2]*scale + scene.wall_thickness*2):
        # print("mniejsze")
        # print(last_f)
        vec = mathutils.Vector(((obj_object.dimensions[0] / 2) * scale + scene.wall_thickness + rand_y,
                                (obj_object.dimensions[1] / 2) * scale + 0.02,
                                -((obj_object.dimensions[2] / 2) * scale + last_f[1])))
        last_f[1] += obj_object.dimensions[2] * scale
    else:
        last_f[1] -= obj_object.dimensions[2] * scale
        vertical_fur = True
    # print("ostatni po dodaniu:")
    # print(last_f)

    if vertical_fur is True:
        obj_object.rotation_euler[2] = -scene.PI / 2
        # print("wieksze")
        vec = mathutils.Vector(((obj_object.dimensions[0] / 2) * scale + scene.wall_thickness + last_f[0],
                                (obj_object.dimensions[1] / 2) * scale + 0.02,
                                -((obj_object.dimensions[2] / 2) * scale + scene.wall_thickness + last_f[1] + rand_x)))
        last_f[0] += obj_object.dimensions[2] * scale

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
        # print('small')
        return 10
    elif area > 15 and area <= 45:
        # print('medium')
        return 20
    elif area > 45 and area <= 80:
        # print('large')
        return 30
    elif area > 80 and area <= 100:
        # print('xl')
        return 40
    else:
        print('somethng went wrong')
        return None


def random_furniture(scene, furniture_const, furniture):
    furniture_number = number_of_furniture(scene)
    # print("furmiture number " + str(furniture_number))
    furniture_add = furniture_number - len(furniture_const)
    fur_add = []

    for i in range(furniture_add):
        fur_add.append(random.randrange(0, len(furniture)))

    return fur_add


def delete_furniture(loop):
    bpy.ops.object.select_all(action='DESELECT')
    # bpy.data.objects['model'].select_set(True)  # Blender 2.8x
    # bpy.context.selected_objects[0].name = "delete_me"
    # bpy.data.objects.remove(bpy.context.scene.objects['delete_me'], do_unlink=True)
    bpy.data.objects.remove(bpy.data.objects['model'], do_unlink=True)

    for i in range(loop):
        if i < 9:
            # bpy.data.objects['model.00' + str(i + 1)].select_set(True)
            # bpy.context.selected_objects[0].name = "delete_me"
            # bpy.data.objects.remove(bpy.context.scene.objects['delete_me'], do_unlink=True)
            bpy.data.objects.remove(bpy.data.objects['model.00' + str(i + 1)], do_unlink=True)
        elif i < 99:
            # bpy.data.objects['model.0' + str(i + 1)].select_set(True)
            # bpy.context.selected_objects[0].name = "delete_me"
            # bpy.data.objects.remove(bpy.context.scene.objects['delete_me'], do_unlink=True)
            bpy.data.objects.remove(bpy.data.objects['model.0' + str(i + 1)], do_unlink=True)
        else:
            # bpy.data.objects['model.' + str(i + 1)].select_set(True)
            # bpy.context.selected_objects[0].name = "delete_me"
            # bpy.data.objects.remove(bpy.context.scene.objects['delete_me'], do_unlink=True)
            bpy.data.objects.remove(bpy.data.objects['model.' + str(i + 1)], do_unlink=True)

    print("koniec usuwania")
    # bpy.ops.object.delete()


def render_room(furniture_const, furniture, scene):
    # last_furniture = np.array([scene.wall_thickness, scene.wall_thickness])
    global last_f
    global vertical_fur
    vertical_fur = False
    last_f = np.array([scene.wall_thickness,scene.wall_thickness])
    # print("przed wywolaniem")
    # print(last_f)

    more_furniture = random_furniture(scene, furniture_const, furniture)
    # print(more_furniture)
    place_model('chandeliers', scene)
    # print("check dimensions:")
    # print(last_furniture)
    place_model(furniture_const[0], scene, scale=2)
    # print("check dimensions:")
    # print(last_furniture)
    place_model(furniture_const[1], scene)
    # print("check dimensions:")
    # print(last_furniture)
    place_model(furniture_const[2], scene)
    # print("check dimensions:")
    # print(last_furniture)

    for i in range(len(more_furniture)):
        # print("numer:")
        # print(i)
        place_model(furniture[more_furniture[i]], scene)
        # print("check dimensions:")
        # print(last_furniture)

    loop = len(furniture_const) + len(more_furniture)

    return loop


def render_bedroom(scene, i, j):
    bpy.ops.export_scene.obj(
        filepath="/home/justyna/All/magisterka/images_models/models/bedroom_" + str(i) + "_" + str(j) + ".obj")
    furniture_const = ['beds', 'dressers', 'armchairs']
    furniture = ['armchairs', 'desks', 'beds', 'couches',
                 'pianos', 'dressers', 'standing_lamps',
                 'bookshelfs', 'speakers']
    loop = render_room(furniture_const, furniture,
                scene)

    name = "bedroom"

    auto_save(scene, i, j, loop, name)


def render_bathroom(scene, i, j):
    bpy.ops.export_scene.obj(
        filepath="/home/justyna/All/magisterka/images_models/models/bethroom_" + str(i) + "_" + str(j) + ".obj")
    furniture_const = ['bathtubs', 'washers', 'standing_lamps']
    furniture = ['bathtubs', 'washers', 'standing_lamps', 'armchairs', 'bins',
                 'cabinets']
    loop = render_room(furniture_const, furniture,
                scene)

    name = "bathroom"

    auto_save(scene, i, j, loop, name)


def render_kitchen(scene, i, j):
    bpy.ops.export_scene.obj(
        filepath="/home/justyna/All/magisterka/images_models/models/kitchen_" + str(i) + "_" + str(j) + ".obj")
    furniture_const = ['dishwashers', 'desks', 'stoves']
    furniture = ['armchairs', 'desks', 'dishwashers', 'bins',
                 'standing_lamps', 'cabinets', 'bookshelfs', 'stoves']
    loop = render_room(furniture_const, furniture,
                scene)

    name = "kitchen"

    auto_save(scene, i, j, loop, name)


def render_livingRoom(scene, i, j):
    bpy.ops.export_scene.obj(filepath="/home/justyna/All/magisterka/images_models/models/living_room_" + str(i) + "_" + str(j) + ".obj")
    furniture_const = ['couches', 'desks', 'armchairs']
    furniture = ['armchairs', 'desks', 'couches',
                 'pianos', 'dressers', 'standing_lamps',
                 'bookshelfs', 'speakers']
    loop = render_room(furniture_const, furniture,
                scene)
    name = "living_room"

    auto_save(scene, i, j, loop, name)


def auto_save(scene, i, j, loop, name):

    for empty in range(2):
        for k in range(3):
            for l in range(4):
                for n in range(6):
                    change_camera_place(scene, [k, l, n], i, j, empty, name)
        if empty == 0:
            delete_furniture(loop)


def render_scenes():
    scene = create_walls()
    render_room(['couches', 'desks', 'armchairs'],
                ['armchairs', 'desks', 'couches',
                 'pianos', 'dressers', 'standing_lamps',
                 'bookshelfs', 'speakers'],
                scene)
    # bpy.data.objects.remove(bpy.context.scene.objects["model.001"], do_unlink=True)

    # save_image_render(scene)
    # change_camera_place(scene, 2)

    # auto_save(scene, 0, 0, 11)


def change_camera_place(scene, number, i, j, empty, name):
    #na 8m chyba najdalej siega kinect
    #losuje wartosc 0 lub 1 zeby zdecydowac na ktora sciane patrzy
    # x_or_y = random.randrange(0, 2)
    # print(x_or_y)

    #jak 0 to patrzy na y
    # if x_or_y == 0:
    #     # scene.camera_location = (scene.size_x, scene.size_y / 2, 1)
    #     scene.camera_rotation = (scene.PI / 2, 0, scene.PI / 2) #scene.PI / 2
    l_val = check_walla(scene)

    k_values = [[scene.PI / 2, 0, 0], [scene.PI / 2, 0, scene.PI / 2], [scene.PI / 2, 0, scene.PI]]
    l_values = [l_val[0], l_val[1], l_val[1]]
    m_values = [0, -scene.PI/4, -2*scene.PI / 6, -scene.PI / 6, 0, 0]
    n_values = [0, scene.PI / 6, -scene.PI / 6, -scene.PI/4, scene.PI/4, 2*scene.PI/3]

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
    #
    # location_smallest = [(3, scene.size_y / 2, 1), (3, scene.size_y / 2, 3), (3, scene.size_y / 2, 3),
    #                      (3, scene.size_y / 2, 3)]
    # orientation_smallest =
    # [(scene.PI / 2, 0, scene.PI / 2), (scene.PI / 4, 0, scene.PI / 2), (scene.PI / 6, 0, scene.PI / 2),
    #                         (scene.PI / 4, 0, scene.PI / 2)]

    # location = (3, scene.size_y / 2, 3)
    # orientation = (scene.PI / 2, 0, scene.PI / 6) # ostatniego nie zmieniac chyba ze chcesz zeby obraz byl krzywo

    location = l_values[number[0]][number[1]]
    orientation = (k_values[number[0]][0] + m_values[number[2]], k_values[number[0]][1],  k_values[number[0]][2] +
                   n_values[number[2]])

    # -scene.PI / 2 w orientacji w z to patrzy na sciane z drzwiami
    bpy.ops.object.camera_add(location=list(location), rotation=list(orientation))
    bpy.context.selected_objects[0].name = "Camera"

    save_image_render(scene, i, j, number, empty, name)


def check_walla(scene):
    l_walls_front = []
    l_walls_right_left = []

    if scene.size_y <= 4:
        l_walls_front = [(2, scene.size_y/6, 1.5), (3, scene.size_y/6, 1.5), (2, 2*scene.size_y/6, 1.5), (3, 2*scene.size_y/6, 1.5),
                         (2, scene.size_y/2, 1.5), (3, scene.size_y/2, 1.5), (2, 4*scene.size_y/6, 1.5), (3, 4*scene.size_y/6, 1.5),
                         (2, 5*scene.size_y/6, 1.5), (3, 5*scene.size_y/6, 1.5),
                         (2, scene.size_y / 6, 2.5), (3, scene.size_y / 6, 2.5), (2, 2 * scene.size_y / 6, 2.5),
                         (3, 2 * scene.size_y / 6, 2.5),
                         (2, scene.size_y / 2, 2.5), (3, scene.size_y / 2, 2.5), (2, 4 * scene.size_y / 6, 2.5),
                         (3, 4 * scene.size_y / 6, 2.5),
                         (2, 5 * scene.size_y / 6, 2.5), (3, 5 * scene.size_y / 6, 2.5)]

    elif scene.size_y <= 6:
        l_walls_front = [(2, scene.size_y / 6, 1.5), (4, scene.size_y / 6, 1.5), (2, 2 * scene.size_y / 6, 1.5),
                         (4, 2 * scene.size_y / 6, 1.5),
                         (2, scene.size_y / 2, 1.5), (4, scene.size_y / 2, 1.5), (2, 4 * scene.size_y / 6, 1.5),
                         (4, 4 * scene.size_y / 6, 1.5),
                         (2, 5 * scene.size_y / 6, 1.5), (4, 5 * scene.size_y / 6, 1.5),
                         (4, scene.size_y / 6, 2.5), (3, scene.size_y / 6, 2.5), (2, 2 * scene.size_y / 6, 2.5),
                         (3, 2 * scene.size_y / 6, 2.5),
                         (4, scene.size_y / 2, 2.5), (3, scene.size_y / 2, 2.5), (2, 4 * scene.size_y / 6, 2.5),
                         (3, 4 * scene.size_y / 6, 2.5),
                         (2, 5 * scene.size_y / 6, 2.5), (4, 5 * scene.size_y / 6, 2.5)]

    elif scene.size_y < 8:
        l_walls_front = [(2, scene.size_y / 6, 1.5), (4, scene.size_y / 6, 1.5), (6, 2 * scene.size_y / 6, 1.5),
                         (4, 2 * scene.size_y / 6, 1.5),
                         (5, scene.size_y / 2, 1.5), (4, scene.size_y / 2, 1.5), (6, 4 * scene.size_y / 6, 1.5),
                         (4, 4 * scene.size_y / 6, 1.5),
                         (2, 5 * scene.size_y / 6, 1.5), (4, 5 * scene.size_y / 6, 1.5),
                         (4, scene.size_y / 6, 2.5), (5, scene.size_y / 6, 2.5), (2, 2 * scene.size_y / 6, 2.5),
                         (6, 2 * scene.size_y / 6, 2.5),
                         (4, scene.size_y / 2, 2.5), (6, scene.size_y / 2, 2.5), (6, 4 * scene.size_y / 6, 2.5),
                         (5, 4 * scene.size_y / 6, 2.5),
                         (2, 5 * scene.size_y / 6, 2.5), (5, 5 * scene.size_y / 6, 2.5)]

    else:
        l_walls_front = [(2, scene.size_y / 6, 1.5), (4, scene.size_y / 6, 1.5), (7, 2 * scene.size_y / 6, 1.5),
                         (4, 2 * scene.size_y / 6, 1.5),
                         (2, scene.size_y / 2, 1.5), (4, scene.size_y / 2, 1.5), (6, 4 * scene.size_y / 6, 1.5),
                         (4, 4 * scene.size_y / 6, 1.5),
                         (6, 5 * scene.size_y / 6, 1.5), (4, 5 * scene.size_y / 6, 1.5),
                         (4, scene.size_y / 6, 2.5), (3, scene.size_y / 6, 2.5), (7, 2 * scene.size_y / 6, 2.5),
                         (5, 2 * scene.size_y / 6, 2.5),
                         (6, scene.size_y / 2, 2.5), (3, scene.size_y / 2, 2.5), (2, 4 * scene.size_y / 6, 2.5),
                         (3, 4 * scene.size_y / 6, 2.5),
                         (6, 5 * scene.size_y / 6, 2.5), (4, 5 * scene.size_y / 6, 2.5)]

    if scene.size_x <= 4:
        l_walls_right_left = [(scene.size_y / 6, 2, 1.5), (scene.size_y / 6, 3, 1.5), (2 * scene.size_y / 6, 2, 1.5),
                         (2 * scene.size_y / 6, 3, 1.5),
                         (scene.size_y / 2, 2, 1.5), (scene.size_y / 2, 3, 1.5), (4 * scene.size_y / 6, 2, 1.5),
                         (4 * scene.size_y / 6, 3, 1.5),
                         (5 * scene.size_y / 6, 2, 1.5), (5 * scene.size_y / 6, 3, 1.5),
                         (scene.size_y / 6, 2, 2.5), (scene.size_y / 6, 3, 2.5), (2 * scene.size_y / 6, 2, 2.5),
                         (2 * scene.size_y / 6, 3, 2.5),
                         (scene.size_y / 2, 2, 2.5), (scene.size_y / 2, 3, 2.5), (4 * scene.size_y / 6, 2, 2.5),
                         (4 * scene.size_y / 6, 3, 2.5),
                         (5 * scene.size_y / 6, 2, 2.5), (5 * scene.size_y / 6, 3, 2.5)]

    elif scene.size_x <= 6:
        l_walls_right_left = [(scene.size_y / 6, 2, 1.5), (scene.size_y / 6, 4, 1.5), (2 * scene.size_y / 6, 2, 1.5),
                         (2 * scene.size_y / 6, 4, 1.5),
                         (scene.size_y / 2, 2, 1.5), (scene.size_y / 2, 4, 1.5), (4 * scene.size_y / 6, 2, 1.5),
                         (4 * scene.size_y / 6, 4, 1.5),
                         (5 * scene.size_y / 6, 2, 1.5), (5 * scene.size_y / 6, 4, 1.5),
                         (scene.size_y / 6, 4, 2.5), (scene.size_y / 6, 3, 2.5), (2 * scene.size_y / 6, 2, 2.5),
                         (2 * scene.size_y / 6, 3, 2.5),
                         (scene.size_y / 2, 4, 2.5), (scene.size_y / 2, 3, 2.5), (4 * scene.size_y / 6, 2, 2.5),
                         (4 * scene.size_y / 6, 3, 2.5),
                         (5 * scene.size_y / 6, 2, 2.5), (5 * scene.size_y / 6, 4, 2.5)]

    elif scene.size_x < 8:
        l_walls_right_left = [(scene.size_y / 6, 2, 1.5), (scene.size_y / 6, 4, 1.5), (2 * scene.size_y / 6, 6, 1.5),
                         (2 * scene.size_y / 6, 4, 1.5),
                         (scene.size_y / 2, 5, 1.5), (scene.size_y / 2, 4, 1.5), (4 * scene.size_y / 6, 6, 1.5),
                         (4 * scene.size_y / 6, 4, 1.5),
                         (5 * scene.size_y / 6, 2, 1.5), (5 * scene.size_y / 6, 4, 1.5),
                         (scene.size_y / 6, 4, 2.5), (scene.size_y / 6, 5, 2.5), (2 * scene.size_y / 6, 2, 2.5),
                         (2 * scene.size_y / 6, 6, 2.5),
                         (scene.size_y / 2, 4, 2.5), (scene.size_y / 2, 6, 2.5), (4 * scene.size_y / 6, 6, 2.5),
                         (4 * scene.size_y / 6, 5, 2.5),
                         (5 * scene.size_y / 6, 2, 2.5), (5 * scene.size_y / 6, 5, 2.5)]

    else:
        l_walls_right_left = [(scene.size_y / 6, 2, 1.5), (scene.size_y / 6, 4, 1.5), (2 * scene.size_y / 6, 7, 1.5),
                         (2 * scene.size_y / 6, 4, 1.5),
                         (scene.size_y / 2, 2, 1.5), (scene.size_y / 2, 4, 1.5), (4 * scene.size_y / 6, 6, 1.5),
                         (4 * scene.size_y / 6, 4, 1.5),
                         (5 * scene.size_y / 6, 6, 1.5), (5 * scene.size_y / 6, 4, 1.5),
                         (scene.size_y / 6, 4, 2.5), (scene.size_y / 6, 3, 2.5), (2 * scene.size_y / 6, 7, 2.5),
                         (2 * scene.size_y / 6, 5, 2.5),
                         (scene.size_y / 2, 6, 2.5), (scene.size_y / 2, 3, 2.5), (4 * scene.size_y / 6, 2, 2.5),
                         (4 * scene.size_y / 6, 3, 2.5),
                         (5 * scene.size_y / 6, 6, 2.5), (5 * scene.size_y / 6, 4, 2.5)]

    return [l_walls_front, l_walls_right_left]


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


def save_image_render(scene, i, j, number, empty, name):
    # bpy.ops.export_scene.obj(filepath="/home/justyna/All/magisterka/pusty.obj")

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

    if empty == 0:
        bpy.context.scene.render.filepath = "/home/justyna/All/magisterka/images_models/images/with_furniture/rgb/rgb_" \
                                            + name + "_" + str(i) + "_" + str(j) + "_" + str(number[0]) + "_" + str(number[1]) + \
                                            "_" + str(number[2]) + ".png"
    else:
        bpy.context.scene.render.filepath = "/home/justyna/All/magisterka/images_models/images/empty/rgb/rgb_" \
                                            + name + "_" + str(i) + "_" + str(j) + "_" + str(number[0]) + "_" + str(number[1]) + \
                                            "_" + str(number[2]) + ".png"

    bpy.ops.render.render(False, animation=False, write_still=True)

    dmap = get_depth()
    # print(dmap)
    for pixel in range(len(dmap)):
        # print("sprawdzmy")
        # print(len(dmap[pixel]))
        for pix in range(len(dmap[pixel])):
            if dmap[pixel][pix] > 7:
                dmap[pixel][pix] = 100000000
            else:
                dmap[pixel][pix] = dmap[pixel][pix]*1000
    # print("koniec")

    # print(dmap)
    dmap_w = np.array(dmap, dtype=np.uint16)

    if empty == 0:
        cv2.imwrite(
            "/home/justyna/All/magisterka/images_models/images/with_furniture/depth/depth_" + name + "_" +
            str(i) + "_" + str(j)
            + "_" + str(number[0]) + "_" + str(number[1]) + "_" + str(number[2])
            + ".png", dmap_w)
    else:
        cv2.imwrite(
            "/home/justyna/All/magisterka/images_models/images/empty/depth/depth_" + name + "_" +
            str(i) + "_" + str(j)
            + "_" + str(number[0]) + "_" + str(number[1]) + "_" + str(number[2])
            + ".png", dmap_w)



def auto_render():
    for i in range(100):
        scene = create_walls()
        for j in range(50):
            render_bedroom(scene, i, j)
            render_kitchen(scene, i, j)
            render_bathroom(scene, i, j)
            # render_livingRoom(scene, i, j)
        clean_scene()


def test_delete():
    scene = create_walls()
    render_room(['couches', 'desks', 'armchairs'],
                ['armchairs', 'desks', 'couches',
                 'pianos', 'dressers', 'standing_lamps',
                 'bookshelfs', 'speakers'],
                scene)

    delete_furniture(11)
    render_room(['couches', 'desks', 'armchairs'],
                ['armchairs', 'desks', 'couches',
                 'pianos', 'dressers', 'standing_lamps',
                 'bookshelfs', 'speakers'],
                scene)

    delete_furniture(11)
    # render_room(['couches', 'desks', 'armchairs'],
    #             ['armchairs', 'desks', 'couches',
    #              'pianos', 'dressers', 'standing_lamps',
    #              'bookshelfs', 'speakers'],
    #             scene)
    # delete_furniture(11)


if __name__ == '__main__':
    changeGPU()
    # render_scenes()

    auto_render()
    # test_delete()

    # render_scenes()

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


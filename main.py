import sys
import os
import bpy
import mathutils
import random
import numpy as np
import cv2

sys.path.append(os.path.dirname(os.path.realpath(__file__)))
# print(os.path.dirname(os.path.realpath(__file__)))
from scripts.blender_func import RoomScene
from scripts.renderer import Renderer
from scripts.modeler import Modeler


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


def place_model(model, scene, place, obj_place=[1, 1], scale=1.0):
    dir = '../ShapeNetCore.v1(1)/ShapeNetCore.v1/mgr_przydatne/' + model
    filename = random.choice(os.listdir(dir))
    path = os.path.join(dir, filename, 'model.obj')
    # print(path)

    file_loc = path
    # use_split_objects musi byc na False bo inaczej importuje
    # sie nie jako pokedynczy obiekt i jest problem z przesuwaniem
    imported_object = bpy.ops.import_scene.obj(filepath=file_loc, use_split_objects=False)
    obj_object = bpy.context.selected_objects[0]
    # print(obj_object.dimensions)

    obj_object.scale[0] *= scale
    obj_object.scale[1] *= scale
    obj_object.scale[2] *= scale

    # print(obj_object.dimensions[1])
    if(model == 'chandeliers'):
        move_chandeliers(obj_object, scene)
    else:
        move_object(obj_object, scene, place, obj_place=obj_place, scale=scale)


def move_object(obj_object, scene, place, obj_place, scale):
    # (x,y,z) x to czerowna, y do gory, z to zielona
    # czerwona na plus, zielona na minus i wtedy jest w pokoju
    vec = mathutils.Vector(((obj_object.dimensions[0] / 2 * obj_place[0]) * scale + scene.size_x * place[0] + scene.wall_thickness,
                            (obj_object.dimensions[1] / 2) * scale + 0.02,
                            -((obj_object.dimensions[2] / 2 * obj_place[1]) * scale + scene.size_y * place[1] + scene.wall_thickness)))
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

    more_furniture = random_furniture(scene, furniture_const, furniture)
    print(more_furniture)
    place_model('chandeliers', scene, None)
    place_model(furniture_const[0], scene, [0, 0], scale=2)
    place_model(furniture_const[1], scene, [0, 4 / 6])
    place_model(furniture_const[2], scene, [1 / 3, 1], obj_place=[1, -2])

    for i in range(len(more_furniture)):
        place_model(furniture[more_furniture[i]], scene,
                    [(1 / 2 - i) / (i + 1) + i / len(more_furniture), i / len(more_furniture)])

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
    save_image_render(scene)


def get_depth():
    """Obtains depth map from Blender render.
    :return: The depth map of the rendered camera view as a numpy array of size (H,W).
    """
    z = bpy.data.images['Viewer Node']
    w, h = z.size
    dmap = np.array(z.pixels[:], dtype=np.float32) # convert to numpy array
    dmap = np.reshape(dmap, (h, w, 4))[:,:,0]
    dmap = np.rot90(dmap, k=2)
    dmap = np.fliplr(dmap)
    return dmap


def dmap2norm(dmap):
    """Computes surface normals from a depth map.
    :param dmap: A grayscale depth map image as a numpy array of size (H,W).
    :return: The corresponding surface normals map as numpy array of size (H,W,3).
    """
    zx = cv2.Sobel(dmap, cv2.CV_64F, 1, 0, ksize=5)
    zy = cv2.Sobel(dmap, cv2.CV_64F, 0, 1, ksize=5)

    # convert to unit vectors
    normal = np.dstack((-zx, -zy, np.ones_like(dmap)))
    n = np.linalg.norm(normal, axis=2)
    normal[:, :, 0] /= n
    normal[:, :, 1] /= n
    normal[:, :, 2] /= n

    # offset and rescale values to be in 0-1
    normal += 1
    normal /= 2
    return normal[:, :, ::-1].astype(np.float32)


def save_image_render(scene):
    bpy.ops.export_scene.obj(filepath="/home/justyna/All/magisterka/pusty.obj")

    bpy.context.scene.render.filepath = "/home/justyna/All/magisterka/depth.png"
    bpy.ops.render.render(False, animation=False, write_still=True)
    dmap = get_depth()
    nmap = dmap2norm(dmap)
    np.savez_compressed("d.npz", dmap=dmap, nmap=nmap)

    ####################################3
    # # Set save path
    # sce = bpy.context.scene.name
    # bpy.data.scenes[sce].render.filepath = "/home/justyna/All/magisterka/depth.png"
    #
    # # Go into camera-view (optional)
    # for area in bpy.context.screen.areas:
    #     if area.type == 'VIEW_3D':
    #         area.spaces[0].region_3d.view_perspective = 'Camera'
    #         break
    #
    # # Render image through viewport
    # bpy.ops.render.opengl(write_still=True)

    ################################
    # scene.render.image_settings.file_format = 'PNG'
    # image = bpy.data.images["Viewer Node"]

    # image = bpy.data.images.new("view", alpha=True, width=16, height=16)
    # # print(image)
    # # image.use_alpha = True
    # # image.alpha_mode = 'STRAIGHT'
    # image.filepath = "/home/justyna/All/magisterka/depth.png"
    # image.file_format = 'PNG'
    # # image.save_render("/home/justyna/All/magisterka/depth2.png", scene=scene)
    # image.save()
    # select = bpy.ops.object.select_all(action='SELECT')
    # scene.objects.link(select)
    # scene.render.image_settings.file_format = 'PNG'
    # scene.render.filepath = "/home/justyna/All/magisterka/depth.png"
    # bpy.ops.render.render(write_still=1)

    # depth = np.asarray(bpy.data.images["Viewer Node"].pixels)
    # depth = np.reshape(depth, (512, 128, 4))
    # depth = depth[:, :, 0]
    # depth = np.flipud(depth)
    # depth = reverse_mapping(depth)

    # np.save("/home/justyna/All/magisterka/depth.npy", depth)

    # wersja nie wiem ktora
    ###########################################################33
    # image = bpy.data.images.new("depth", width=1024, height=1024, alpha=True, float_buffer=True)
    #
    # # solid white image
    # pixels = [1.0] * (1000 * 1000 * 16)
    #
    # # set pixels
    # image.pixels = pixels
    # print(image.channels)
    #
    # # save image
    # # settings = bpy.context.scene.split_map_settings
    # image.filepath = "/home/justyna/All/magisterka/depth.png"
    # # image.filepath_raw = settings.test_save_path
    # # image.alpha_mode = 'STRAIGHT'
    # image.file_format = 'PNG'
    # # image.generated_color = (0.2, 0.5, 0.4, 0.0)
    # image.generated_type = 'BLANK'
    # image.update()
    # # image.save_render("/home/justyna/All/magisterka/depth2.png")
    # image.save()


if __name__ == '__main__':
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


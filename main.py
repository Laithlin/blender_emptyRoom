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
    d["use"] = 1 # Using all devices, include GPU and CPU
    print(d["name"], d["use"])

bpy.context.scene.cycles.samples = 100

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
    dir = '../mgr_przydatne/' + model
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

    bpy.context.scene.camera = bpy.data.objects['Camera']

    #moje

    bpy.context.scene.use_nodes = True
    tree = bpy.context.scene.node_tree
    links = tree.links

    # clear default nodes
    for n in tree.nodes:
        tree.nodes.remove(n)

    scene = bpy.context.scene
    scene.view_layers["ViewLayer"].use_pass_z = True
    scene.use_nodes = True

    nodes = scene.node_tree.nodes
    rl = tree.nodes.new('CompositorNodeRLayers')
    norm = tree.nodes.new('CompositorNodeNormalize')
    compositor = tree.nodes.new('CompositorNodeComposite')
    view = tree.nodes.new('CompositorNodeViewer')

    links.new(rl.outputs[0], compositor.inputs[0])
    links.new(rl.outputs[2], norm.inputs[0])
    links.new(norm.outputs[0], view.inputs[0])

    # # create a file output node and set the path
    # fileOutput = tree.nodes.new(type="CompositorNodeOutputFile")
    # fileOutput.base_path = "/home/justyna/All/magisterka/"
    # fileOutput.file_slots[0].path = 'depth_sprawdzmy.png'
    # links.new(norm.outputs[0], fileOutput.inputs[0])

    # bpy.context.scene.render.filepath = "/home/justyna/All/magisterka/rgb.png"
    bpy.ops.render.render(False, animation=False, write_still=True)

    dmap = get_depth()
    dmap = dmap * 255
    # # print(dmap)
    #
    cv2.imwrite("sprawdzmy_pokoje.png", dmap)

    #####################################
    # teoretycznie dziala ale wypluwa jakis dziwny obraz
    # bpy.context.scene.render.filepath = "/home/justyna/All/magisterka/depth.png"
    # bpy.ops.render.render(False, animation=False, write_still=True)
    # dmap = get_depth()
    # nmap = dmap2norm(dmap)
    # np.savez_compressed("d.npz", dmap=dmap, nmap=nmap)
    #
    # images = np.load("d.npz")
    # # images.shape
    # plt.ion()
    # plt.figure()
    # plt.imshow(images)

    # nmap = nmap * 255
    # nmap = nmap.astype(np.uint8)
    #
    # im = Image.fromarray(nmap)
    # im.save("/home/justyna/All/magisterka/your_file.png")

    ####################################
    # DZIALAAAA
    # # Set save path
    # sce = bpy.context.scene.name
    # bpy.data.scenes[sce].render.filepath = "/home/justyna/All/magisterka/depth.png"
    #
    # # Go into camera-view (optional)
    # for area in bpy.context.screen.areas:
    #     if area.type == 'VIEW_3D':
    #         area.spaces[0].region_3d.view_perspective = 'CAMERA'
    #         break
    #
    # # Render image through viewport
    # bpy.ops.render.opengl(write_still=True)

    ######################################

    #TODO: tez dziala

    # scene = bpy.context.scene
    # scene.render.image_settings.color_depth = '16'
    # scene.display_settings.display_device = 'sRGB'
    # scene.view_settings.view_transform = 'Raw'
    # scene.sequencer_colorspace_settings.name = 'Raw'
    # scene.use_nodes = True
    # for node in scene.node_tree.nodes:
    #     scene.node_tree.nodes.remove(node)
    # renderNode = scene.node_tree.nodes.new('CompositorNodeRLayers')
    #
    # depthOutputNode = scene.node_tree.nodes.new('CompositorNodeOutputFile')
    # depthOutputNode.format.file_format = 'PNG'
    # depthOutputNode.format.color_depth = '16'
    # depthOutputNode.format.color_mode = 'BW'
    # depthOutputNode.base_path = '/home/justyna/All/magisterka/'
    # depthOutputNode.file_slots[0].path = 'depth.png'
    #
    # scene.node_tree.links.new(renderNode.outputs[2], depthOutputNode.inputs[0])
    #
    # bpy.ops.render.render(write_still=True)

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

    ###################################

    # scene = bpy.context.scene
    #
    # # 解像度を設定
    # # bpy.context.scene.render.resolution_x = scene.resolution_x
    # # bpy.context.scene.render.resolution_y = scene.resolution_y
    # # bpy.context.scene.render.resolution_percentage = scene.resolution_percentage
    #
    # # node を切り替えて、作成したnodeにレンダリング結果を出力
    # bpy.context.scene.use_nodes = True
    # tree = bpy.context.scene.node_tree
    # links = tree.links
    # # default node をクリア
    # for n in tree.nodes:
    #     tree.nodes.remove(n)
    # # input render layer node 作成
    # rl = tree.nodes.new('CompositorNodeRLayers')
    # rl.location = 180, 280
    # # output node 作成
    # v = tree.nodes.new('CompositorNodeViewer')
    # v.location = 750, 210
    # v.use_alpha = False
    #
    # links.new(rl.outputs[2], v.inputs[0])
    #
    # for o in scene.objects:
    #     if o.type == 'CAMERA':
    #         # turning FOV
    #         # o.data.angle = 1.026 * o.data.angle
    #
    #         # set active camera
    #         bpy.context.scene.camera = o
    #
    #         # render
    #         bpy.ops.render.render()
    #         # get rendering result image
    #         pixels = np.array(bpy.data.images['Viewer Node'].pixels)
    #
    #         # 現実とBlender内の長さの比率を導出
    #         real_far_distance = scene.real_far_distance  # メートル
    #         real_near_distance = scene.real_near_distance  # メートル
    #         blender = scene.length_blender_exsample
    #         real = scene.length_real_exsample
    #         blender_real_ratio = blender / real
    #
    #         blender_far_distance = blender_real_ratio * real_far_distance
    #         blender_near_distance = blender_real_ratio * real_near_distance
    #         distance = blender_far_distance - blender_near_distance
    #         # print('blender_real_ratio ', blender_real_ratio)
    #         # print('blender_far_distance ',blender_far_distance)
    #         # print('blender_near_distance ',blender_near_distance)
    #
    #         # デプス(カメラからの距離情報)を色データとして画素に保存
    #         for i in range(np.shape(pixels)[0]):
    #             if pixels[i] > blender_far_distance:
    #                 pixels[i] = 1.0
    #             elif pixels[i] < blender_near_distance:
    #                 pixels[i] = 0.0
    #             else:
    #                 pixels[i] = (pixels[i] - blender_near_distance) / distance
    #                 if i % 4 == 0:
    #                     print('pixels[i] ', pixels[i])
    #
    #         # gamma 補正を除去
    #         pixels[0::4] = np.power(pixels[0::4], 2.27195)
    #         pixels[1::4] = np.power(pixels[1::4], 2.27195)
    #         pixels[2::4] = np.power(pixels[2::4], 2.27195)
    #
    #         # alpha = 1.0
    #         pixels[3::4] = 1.0
    #         bpy.data.images['Viewer Node'].pixels = pixels
    #         bpy.data.images['Viewer Node'].save_render(filepath='/home/justyna/All/magisterka/depth2.png')

    #########################################

    # # Set up rendering of depth map:
    # bpy.context.scene.use_nodes = True
    # tree = bpy.context.scene.node_tree
    # links = tree.links
    #
    # # clear default nodes
    # for n in tree.nodes:
    #     tree.nodes.remove(n)
    #
    # # create input render layer node
    # rl = tree.nodes.new('CompositorNodeRLayers')
    #
    # map = tree.nodes.new(type="CompositorNodeMapValue")
    # # Size is chosen kind of arbitrarily, try out until you're satisfied with resulting depth map.
    # map.size = [30]
    # map.use_min = True
    # map.min = [0]
    # map.use_max = True
    # map.max = [255]
    # links.new(rl.outputs[2], map.inputs[0])
    #
    # invert = tree.nodes.new(type="CompositorNodeInvert")
    # invert.invert_alpha = False
    # invert.invert_rgb = False
    # links.new(map.outputs[0], invert.inputs[1])
    #
    # # The viewer can come in handy for inspecting the results in the GUI
    # depthViewer = tree.nodes.new(type="CompositorNodeViewer")
    # links.new(invert.outputs[0], depthViewer.inputs[0])
    # # Use alpha from input.
    # links.new(rl.outputs[1], depthViewer.inputs[1])
    #
    # # create a file output node and set the path
    # fileOutput = tree.nodes.new(type="CompositorNodeOutputFile")
    # fileOutput.format.color_depth = '16'
    # fileOutput.base_path = "/home/justyna/All/magisterka/"
    # fileOutput.file_slots[0].path = 'depth2.png'
    # links.new(invert.outputs[0], fileOutput.inputs[0])
    #
    # bpy.ops.render.render(write_still=True)


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


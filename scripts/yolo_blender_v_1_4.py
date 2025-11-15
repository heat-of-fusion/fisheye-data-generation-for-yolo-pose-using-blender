import bpy

import os
import numpy as np
import pickle as pkl

import random
import math
from math import radians
from mathutils import Vector, Euler

def print(data):
    for window in bpy.context.window_manager.windows:
        screen = window.screen
        for area in screen.areas:
            if area.type == 'CONSOLE':
                override = {'window': window, 'screen': screen, 'area': area}

                with bpy.context.temp_override(area=area):
                    bpy.ops.console.scrollback_append(text=str(data), type='OUTPUT')

def render(file_name, resX=640, resY=640):
    bpy.context.scene.render.filepath = file_name

    bpy.context.scene.render.resolution_x = resX
    bpy.context.scene.render.resolution_y = resY

    bpy.ops.render.render(write_still=True)

class BaseSpawner():
    def __init__(self, base_obj, config,):
        self.base_obj = base_obj

        self.init_base_obj()

        self.config = config

        self.objs = [base_obj,]

        return

    def init_base_obj(self):
        self.base_obj.hide_set(False)
        self.base_obj.hide_render = False

        self.base_obj.location.x = 0.0
        self.base_obj.location.y = 0.0
        self.base_obj.location.z = 0.0

        self.base_obj.scale.x = 1.0
        self.base_obj.scale.y = 1.0
        self.base_obj.scale.z = 1.0

        self.base_obj.rotation_euler.x = radians(0)
        self.base_obj.rotation_euler.y = radians(0)
        self.base_obj.rotation_euler.z = radians(0)

        return

    def spawn_objs(self, num_objs):
        if num_objs == 0:
            self.objs[0].hide_set(True)
            self.objs[0].hide_render = True

            for child in self.objs[0].children:
                if child.type == 'MESH':
                    child.hide_set(True)
                    child.hide_render = True

            return

        for i in range(num_objs - 1):
            new_obj = self.base_obj.copy()
            new_obj.data = self.base_obj.data.copy()

            for child in self.base_obj.children:
                if child.type == 'MESH':
                    mesh_copy = child.copy()
                    mesh_copy.data = child.data.copy()

                    for modifier in mesh_copy.modifiers:
                        if modifier.type == 'ARMATURE':
                            modifier.object = new_obj

                    for idx, shape in enumerate(mesh_copy.data.shape_keys.key_blocks):
                        shape.value = random.uniform(0.0, 1.0)

                    bpy.context.collection.objects.link(mesh_copy)

                    mesh_copy.parent = new_obj

            self.objs.append(new_obj)

            bpy.context.collection.objects.link(new_obj)

        for i in range(len(self.objs)):
            self.objs[i].location.x = random.uniform(*self.config['rangeLocX'])
            self.objs[i].location.y = random.uniform(*self.config['rangeLocY'])
            self.objs[i].location.z = random.uniform(*self.config['rangeLocZ'])

            scale_factor = np.random.uniform(*self.config['rangeScale'])
            self.objs[i].scale.x = scale_factor
            self.objs[i].scale.y = scale_factor
            self.objs[i].scale.z = scale_factor

            self.objs[i].rotation_euler.x = radians(random.uniform(*self.config['rangeRotX']))
            self.objs[i].rotation_euler.y = radians(random.uniform(*self.config['rangeRotY']))
            self.objs[i].rotation_euler.z = radians(random.uniform(*self.config['rangeRotZ']))

        return

    def despawn_objs(self):
        for obj in self.objs[1:]:
            for child in obj.children:
                if child.type == 'MESH':
                    bpy.data.objects.remove(child, do_unlink = True)

            bpy.data.objects.remove(obj, do_unlink = True)

        self.objs = [self.base_obj]

        self.init_base_obj()

        return

class RiggedObjectSpawner(BaseSpawner):
    def __init__(self, base_obj, config, pose_dir):
        super().__init__(base_obj, config)

        self.pose_dir = pose_dir
        self.pose_type_list = os.listdir(self.pose_dir)

        self.num_objs = None

        self.pose_types = list()

        return

    def init_base_obj(self):
        super().init_base_obj()

        for child in self.base_obj.children:
            if child.type == 'MESH':
                child.hide_set(False)
                child.hide_render = False

        for bone in self.base_obj.pose.bones:
            bone.rotation_mode = 'QUATERNION'

            bone.rotation_quaternion.w = 1.0
            bone.rotation_quaternion.x = 0.0
            bone.rotation_quaternion.y = 0.0
            bone.rotation_quaternion.z = 0.0

        return

    def stick_to_ground(self, trg = None, alpha_margin = 0.0):

        for idx, obj in enumerate([self.base_obj] + self.objs):
            if trg:
                space = (obj.matrix_world @ obj.pose.bones[trg].tail).z
            else:
                space = np.inf
                for bone in obj.pose.bones:

                    _z = min(
                        (obj.matrix_world @ bone.tail).z,
                        (obj.matrix_world @ bone.head).z
                    )

                    if space > _z:
                        space = _z

            print(f'{obj}: {space}')

            obj.location.z -= (space - alpha_margin)

        return

    def spawn_objs(self, num_objs):

        self.num_objs = num_objs

        if num_objs == 0:
            self.objs[0].hide_set(True)
            self.objs[0].hide_render = True

            for child in self.objs[0].children:
                if child.type == 'MESH':
                    child.hide_set(True)
                    child.hide_render = True

            return

        for i in range(num_objs - 1):
            new_obj = self.base_obj.copy()
            new_obj.data = self.base_obj.data.copy()

            for child in self.base_obj.children:
                if child.type == 'MESH':
                    mesh_copy = child.copy()
                    mesh_copy.data = child.data.copy()

                    for modifier in mesh_copy.modifiers:
                        if modifier.type == 'ARMATURE':
                            modifier.object = new_obj

                    if mesh_copy.data.shape_keys:
                        for shape in mesh_copy.data.shape_keys.key_blocks:
                            shape.value = random.uniform(0.0, 1.0)

                    bpy.context.collection.objects.link(mesh_copy)

                    mesh_copy.parent = new_obj

            self.objs.append(new_obj)

            bpy.context.collection.objects.link(new_obj)

        for i in range(len(self.objs)):
            self.objs[i].location.x = random.uniform(*self.config['rangeLocX'])
            self.objs[i].location.y = random.uniform(*self.config['rangeLocY'])
            self.objs[i].location.z = random.uniform(*self.config['rangeLocZ'])

            scale_factor = np.random.uniform(*self.config['rangeScale'])
            self.objs[i].scale.x = scale_factor
            self.objs[i].scale.y = scale_factor
            self.objs[i].scale.z = scale_factor

            self.objs[i].rotation_euler.x = radians(random.uniform(*self.config['rangeRotX']))
            self.objs[i].rotation_euler.y = radians(random.uniform(*self.config['rangeRotY']))
            self.objs[i].rotation_euler.z = radians(random.uniform(*self.config['rangeRotZ']))

            pose_type = self.pose_type_list[np.random.randint(0, len(self.pose_type_list))]
            _dir = self.pose_dir + f'{pose_type}/'

            pose_file_list = os.listdir(_dir)
            _dir = _dir + pose_file_list[np.random.randint(0, len(pose_file_list))]

            pose_file = pkl.load(open(_dir, 'rb'))

            for bone in self.objs[i].pose.bones:
                if bone.name in pose_file.keys():
                    bone.rotation_mode = 'QUATERNION'

                    quat = pose_file[bone.name]
                    bone.rotation_quaternion.w = quat['w']
                    bone.rotation_quaternion.x = quat['x']
                    bone.rotation_quaternion.y = quat['y']
                    bone.rotation_quaternion.z = quat['z']

        return

    def despawn_objs(self):
        super().despawn_objs()

        self.pose_types = list()

        return

class KeypointRiggedObjectSpawner(RiggedObjectSpawner):
    def __init__(self, base_obj, config, pose_dir):
        super().__init__(base_obj, config, pose_dir)

        self.kpt_mapping = [
            'mixamorig:HeadTop_End',
            'mixamorig:Head',
            'mixamorig:Neck',
            'mixamorig:LeftArm',
            'mixamorig:RightArm',
            'mixamorig:LeftForeArm',
            'mixamorig:LeftHandMiddle1',
            'mixamorig:RightForeArm',
            'mixamorig:RightHandMiddle1',
            'mixamorig:LeftUpLeg',
            'mixamorig:RightUpLeg',
            'mixamorig:LeftLeg',
            'mixamorig:LeftFoot',
            'mixamorig:RightLeg',
            'mixamorig:RightFoot',
        ]

        return

    def dir_to_fisheye(self, dir, fov):
        dir_xy = Vector((dir.x, dir.y))
        len_xy = dir_xy.length

        theta = math.atan2(len_xy, -dir.z)

        if theta < 0:
            return None

        r = theta / math.radians(fov)

        uv_centered = Vector((0, 0))
        if len_xy > 0:
            uv_centered = r * (dir_xy / len_xy)

        final_u = 0.5 - uv_centered.x
        final_v = 0.5 + uv_centered.y

        return Vector((final_u, final_v))

    def get_obj_keypoints(self, target_obj, camera, fov = 180):

        keypoints = list()

        for bone_name in self.kpt_mapping:
            bone = target_obj.pose.bones[bone_name]

            target_world_coord = target_obj.matrix_world @ bone.head

            camera_matrix_world = camera.matrix_world

            direction_world = target_world_coord - camera_matrix_world.translation

            camera_world_to_local_rotation = camera_matrix_world.to_3x3().inverted()

            direction_camera_local = camera_world_to_local_rotation @ direction_world
            direction_camera_local.normalize()

            fisheye_uv = self.dir_to_fisheye(direction_camera_local, fov)

            keypoint = np.array([0.0, 0.0])
            keypoint[0] = (1 - fisheye_uv.y)
            keypoint[1] = (1 - fisheye_uv.x)

            keypoints.append(keypoint)

        return np.array(keypoints)

    def get_scene_keypoints(self, camera, fov = 180):
        if self.num_objs == 0:
            return list()

        scene_keypoints = list()

        for obj in self.objs:
            scene_keypoints.append(self.get_obj_keypoints(obj, camera, fov))

        return scene_keypoints

class RandomObjectSpawner(BaseSpawner):
    def __init__(self, base_obj, config):

        super().__init__(base_obj, config)

        # print(self.base_obj.type)
        # assert self.base_obj.type == 'EMPTY', 'Base object must be empty object with mesh children.'

        return

    def init_base_obj(self):
        self.base_obj.hide_set(False)
        self.base_obj.hide_render = False

        for child in self.base_obj.children:
            if child.type == 'MESH':
                child.hide_set(True)
                child.hide_render = True

        self.base_obj.location.x = 0.0
        self.base_obj.location.y = 0.0
        self.base_obj.location.z = 0.0

        self.base_obj.scale.x = 1.0
        self.base_obj.scale.y = 1.0
        self.base_obj.scale.z = 1.0

        self.base_obj.rotation_euler.x = radians(0)
        self.base_obj.rotation_euler.y = radians(0)
        self.base_obj.rotation_euler.z = radians(0)

        return

    def spawn_objs(self, num_objs):
        if num_objs == 0:
            for child in self.objs[0].children:
                if child.type == 'MESH':
                    child.hide_set(True)
                    child.hide_render = True

            return

        for i in range(num_objs - 1):
            new_obj = self.base_obj.copy()
            new_obj.data = self.base_obj.data.copy()

            for child in self.base_obj.children:
                if child.type == 'MESH':
                    mesh_copy = child.copy()
                    mesh_copy.data = child.data.copy()

                    for modifier in mesh_copy.modifiers:
                        if modifier.type == 'ARMATURE':
                            modifier.object = new_obj

                    if mesh_copy.data.shape_keys:
                        for shape in mesh_copy.data.shape_keys.key_blocks:
                            shape.value = random.uniform(0.0, 1.0)

                    bpy.context.collection.objects.link(mesh_copy)

                    mesh_copy.parent = new_obj

            self.objs.append(new_obj)

            bpy.context.collection.objects.link(new_obj)

        for i in range(len(self.objs)):
            self.objs[i].location.x = random.uniform(*self.config['rangeLocX'])
            self.objs[i].location.y = random.uniform(*self.config['rangeLocY'])
            self.objs[i].location.z = random.uniform(*self.config['rangeLocZ'])

            scale_factor = np.random.uniform(*self.config['rangeScale'])
            self.objs[i].scale.x = scale_factor
            self.objs[i].scale.y = scale_factor
            self.objs[i].scale.z = scale_factor

            self.objs[i].rotation_euler.x = radians(random.uniform(*self.config['rangeRotX']))
            self.objs[i].rotation_euler.y = radians(random.uniform(*self.config['rangeRotY']))
            self.objs[i].rotation_euler.z = radians(random.uniform(*self.config['rangeRotZ']))

            active_idx = np.random.randint(0, len(self.objs[i].children))

            self.objs[i].children[active_idx].hide_set(False)
            self.objs[i].children[active_idx].hide_render = False

        return

class StickingKeypointRiggedObjectSpawner(KeypointRiggedObjectSpawner):
    def __init__(self, base_obj, config, pose_dir, p = 0.5):
        super().__init__(base_obj, config, pose_dir)

        self.p = p

        return

    def spawn_objs(self, target_spawner):

        target_objs = target_spawner.objs

        init_flag = True

        for idx, target_obj in enumerate(target_objs):

            if self.p > np.random.random():
                continue

            if init_flag:
                self.objs[0].location.x = target_obj.location.x
                self.objs[0].location.y = target_obj.location.y
                self.objs[0].location.z = target_obj.location.z

                init_flag = False

                continue

            new_obj = self.base_obj.copy()
            new_obj.data = self.base_obj.data.copy()

            for child in self.base_obj.children:
                if child.type == 'MESH':
                    mesh_copy = child.copy()
                    mesh_copy.data = child.data.copy()

                    for modifier in mesh_copy.modifiers:
                        if modifier.type == 'ARMATURE':
                            modifier.object = new_obj

                    if mesh_copy.data.shape_keys:
                        for shape in mesh_copy.data.shape_keys.key_blocks:
                            shape.value = random.uniform(0.0, 1.0)

                    bpy.context.collection.objects.link(mesh_copy)

                    mesh_copy.parent = new_obj

            new_obj.location.x = target_obj.location.x
            new_obj.location.y = target_obj.location.y
            new_obj.location.z = target_obj.location.z

            self.objs.append(new_obj)

            bpy.context.collection.objects.link(new_obj)

        self.num_objs = len(self.objs) - 1

        if self.num_objs == 0:
            self.objs[0].hide_set(True)
            self.objs[0].hide_render = True

            for child in self.objs[0].children:
                if child.type == 'MESH':
                    child.hide_set(True)
                    child.hide_render = True

            return

        for i in range(len(self.objs)):
            scale_factor = np.random.uniform(*self.config['rangeScale'])
            self.objs[i].scale.x = scale_factor
            self.objs[i].scale.y = scale_factor
            self.objs[i].scale.z = scale_factor

            self.objs[i].rotation_euler.x = radians(random.uniform(*self.config['rangeRotX']))
            self.objs[i].rotation_euler.y = radians(random.uniform(*self.config['rangeRotY']))
            self.objs[i].rotation_euler.z = radians(random.uniform(*self.config['rangeRotZ']))

            pose_type = self.pose_type_list[np.random.randint(0, len(self.pose_type_list))]
            _dir = self.pose_dir + f'{pose_type}/'

            pose_file_list = os.listdir(_dir)
            _dir = _dir + pose_file_list[np.random.randint(0, len(pose_file_list))]

            pose_file = pkl.load(open(_dir, 'rb'))

            for bone in self.objs[i].pose.bones:
                if bone.name in pose_file.keys():
                    bone.rotation_mode = 'QUATERNION'

                    quat = pose_file[bone.name]
                    bone.rotation_quaternion.w = quat['w']
                    bone.rotation_quaternion.x = quat['x']
                    bone.rotation_quaternion.y = quat['y']
                    bone.rotation_quaternion.z = quat['z']

        return



if __name__ == '__main__':
    out_dir = 'C:/Users/batma/Desktop/VIDA/data_generation/blender-base/demo/fisheye-data-generation-for-yolo-pose-using-blender/out/'

    pose_dir = f'C:/Users/batma/Desktop/VIDA/data_generation/blender-base/demo/fisheye-data-generation-for-yolo-pose-using-blender/animations/pose/'

    monkey_config = {
        # Location Range
        'rangeLocX': (-2.5, 2.5),
        'rangeLocY': (-3.0, 3.0),
        'rangeLocZ': (0.0, 0.0),

        # Scale Range
        'rangeScale': (0.7, 1.2),

        # Rotation Range
        'rangeRotX': (0.0, 0.0),
        'rangeRotY': (0.0, 0.0),
        'rangeRotZ': (0.0, 360.0),

        # Number Range
        'rangeNum': (0, 7),
    }

    patient_config = {
        # Location Range
        'rangeLocX': (-2.5, 2.5),
        'rangeLocY': (-3.0, 3.0),
        'rangeLocZ': (0.0, 0.0),

        # Scale Range
        'rangeScale': (0.7, 1.2),

        # Rotation Range
        'rangeRotX': (0.0, 0.0),
        'rangeRotY': (0.0, 0.0),
        'rangeRotZ': (0.0, 360.0),

        # Number Range
        'rangeNum': (0, 7),
    }

    walkers_config = {
        # Location Range
        'rangeLocX': (-2.5, 2.5),
        'rangeLocY': (-3.0, 3.0),
        'rangeLocZ': (0.0, 0.0),

        # Scale Range
        'rangeScale': (0.7, 1.2),

        # Rotation Range
        'rangeRotX': (0.0, 0.0),
        'rangeRotY': (0.0, 0.0),
        'rangeRotZ': (0.0, 360.0),

        # Number Range
        'rangeNum': (0, 4),
    }

    scene = bpy.context.scene
    camera = scene.camera

    # Define Objects
    monkey_obj = bpy.data.objects.get('base_monkey')

    patient_obj = bpy.data.objects.get('base_patient')

    walkers_obj = bpy.data.objects.get('base_walkers')

    # Define Object Spawners
    monkey_spawner = BaseSpawner(monkey_obj, monkey_config)

    patient_spawner = KeypointRiggedObjectSpawner(patient_obj, patient_config, pose_dir)

    walkers_spawner = RandomObjectSpawner(walkers_obj, walkers_config)

    for i in range(10):
        camera.location.z = np.random.uniform(2.5, 3.0)
        camera.rotation_euler.z = np.random.uniform(0, 360)

        # Spawn Objects
        monkey_spawner.spawn_objs(np.random.randint(*monkey_config['rangeNum']))
        patient_spawner.spawn_objs(np.random.randint(*patient_config['rangeNum']))
        walkers_spawner.spawn_objs(np.random.randint(*walkers_config['rangeNum']))

        patient_spawner.stick_to_ground(alpha_margin = 0.)

        render(out_dir + f'test{i}.png')

        patient_keypoints = patient_spawner.get_scene_keypoints(camera, 180)

        keypoints = (
            patient_keypoints
        )

        pkl.dump(keypoints, open(out_dir + f'test{i}.pkl', 'wb'))

        monkey_spawner.despawn_objs()
        patient_spawner.despawn_objs()
        walkers_spawner.despawn_objs()

    camera.rotation_euler.z = 0
    camera.location.z = 2.65
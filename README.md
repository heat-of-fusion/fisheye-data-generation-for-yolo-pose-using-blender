
# Blender-based Synthetic Data Generator for Fisheye Pose Estimation

A fully modular pipeline for generating **synthetic human pose datasets** using **Blender**, tailored for **fisheye camera** applications.  
This system programmatically spawns, randomizes, poses, and renders 3D rigged characters and exports their **2D fisheye-projected keypoints** for training pose-estimation models (e.g., YOLO-Pose).

---

## ✨ Features

### 🎥 Fisheye Camera Model
- Implements an **equidistant fisheye projection**.
- Converts world-space keypoints → 2D UV coordinates (normalized 0–1).

### 🧱 Modular Spawner System
Spawner classes automate the entire pipeline:
- Object spawning/despawning
- Location/scale/rotation randomization
- Pose loading & application
- Keypoint extraction

Spawner types:
- `BaseSpawner`
- `RiggedObjectSpawner`
- `KeypointRiggedObjectSpawner` (main spawner)
- `RandomObjectSpawner` (random prop selection)
- `StickingKeypointRiggedObjectSpawner` (attach props to characters)

### 🦴 Rig & Pose Support
- Supports any armature-based character.
- Loads `.pkl` pose files from categorized folders.

### 🔑 2D Keypoint Export
- Output saved as `.pkl`
- Python list of NumPy arrays: each array = a person’s `(N, 2)` keypoints  
- Coordinates normalized to **(y, x) in [0, 1]**

### 🌎 Diverse Randomization
Configure:
- Count per scene
- Spatial ranges
- Scale ranges
- Rotation ranges
- Pose categories
- Probabilistic multi-object interactions

---

## 📂 Example Output

Each iteration produces:

test0.png      # Rendered fisheye image
test0.pkl      # List of persons’ 2D keypoints

````

**Keypoint file structure:**

```python
[
    np.array([[y, x], ..., [y, x]]),  # person 1 (15x2)
    np.array([...]),                  # person 2
    ...
]
````

If no characters spawned → list is empty.

---

## 🛠️ Setup & Installation

### 1. Install Blender

Requires **Blender 3.0+**
Download: [https://www.blender.org/download/](https://www.blender.org/download/)

### 2. Install Python Dependencies (inside Blender Python)

Locate Blender's Python:

* **Windows**
  `C:\Program Files\Blender Foundation\Blender 3.x\3.x\python\bin\python.exe`

* **macOS**
  `/Applications/Blender.app/Contents/Resources/3.x/python/bin/python3.x`

* **Linux**
  `~/blender-3.x/3.x/python/bin/python3.x`

Install NumPy:

```bash
"<path-to-blender-python>" -m pip install numpy
```

---

## 📦 Project Structure Requirements

Your `.blend` file must contain:

* `base_monkey` (static mesh)
* `base_patient` (rigged human)
* `base_walkers` (Empty with multiple mesh children)
* A Camera object (fisheye parameters handled in script)

A directory of `.pkl` pose files is required for animation.

---

## 🚀 How to Run

1. Open your Blender `.blend`.
2. Go to **Scripting** workspace.
3. Load the Python generator script.
4. Update paths:

```python
if __name__ == "__main__":
    out_dir = 'C:/your/output/path/'
    pose_dir = 'C:/your/pose/folder/'
```

5. Press **Run Script** (▶).
6. Blender will generate images & annotations in your `out_dir`.

---

## 🧬 Spawner System Overview

### `BaseSpawner`

* Generic object spawner
* Random location/scale/rotation
* Handles activation/deactivation lifecycle

### `RiggedObjectSpawner`

* Extends `BaseSpawner`
* Applies `.pkl` pose files to an armature
* Ensures characters sit on ground plane

### `KeypointRiggedObjectSpawner`

* Extends `RiggedObjectSpawner`
* Computes world positions of rig bones
* Projects keypoints using fisheye equation
* Contains editable `kpt_mapping`

### `RandomObjectSpawner`

* For an Empty containing multiple meshes
* Randomly selects which child mesh to display

### `StickingKeypointRiggedObjectSpawner`

* Spawns objects at locations of another spawner’s objects
* Useful for props like walking aids

---

## 🔧 Customization

### Add New Objects

In Blender:

1. Add an object or rig.
2. Name it `base_myobject`.

In Python:

```python
obj = bpy.data.objects.get('base_myobject')
my_config = {'rangeLocX': (-5, 5), ...}
spawner = BaseSpawner(obj, my_config)
```

### Add New Pose Files

Directory format:

```
pose/
 ├── standing/
 │    ├── pose1.pkl
 │    └── pose2.pkl
 └── sitting/
      ├── pose3.pkl
```

Pose file structure:

```python
{
    'mixamorig:Hips': {'w': ..., 'x': ..., 'y': ..., 'z': ...},
    ...
}
```

### Customize Keypoints

Edit this list inside `KeypointRiggedObjectSpawner`:

```python
self.kpt_mapping = [
    'mixamorig:HeadTop_End',
    'mixamorig:Head',
    'mixamorig:Neck',
    ...
]
```

---

## 📜 Citation

```bibtex
@software{fisheye_data_generator_2025,
  author = {heat-of-fusion},
  title = {Blender-based Synthetic Data Generator for Fisheye Pose Estimation},
  year = {2025},
  publisher = {GitHub},
  journal = {GitHub repository},
  howpublished = {\url{https://github.com/heat-of-fusion/your-repo-name}}
}
```

---

## 📄 License

Licensed under the **MIT License**.

```

---

필요하면 **코드 자동 인덴트**, **이미지 예시 삽입**, **Badge 적용(GitHub Actions, License badge 등)** 버전으로도 재작성해줄게.
```

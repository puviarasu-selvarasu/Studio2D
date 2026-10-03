import bpy
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
OUTPUT = ROOT / "output"
OUTPUT.mkdir(parents=True, exist_ok=True)

# Reset Blender completely.
bpy.ops.wm.read_factory_settings(use_empty=True)

scene = bpy.context.scene

# Basic render configuration.
scene.render.engine = "BLENDER_WORKBENCH"
scene.render.resolution_x = 640
scene.render.resolution_y = 360
scene.render.resolution_percentage = 100

# Transparent background is not required for this test.
scene.render.film_transparent = False

# Create camera.
camera_data = bpy.data.cameras.new("Studio2D_Camera")
camera = bpy.data.objects.new("Studio2D_Camera", camera_data)
bpy.context.collection.objects.link(camera)

camera.location = (0.0, 0.0, 10.0)
camera.rotation_euler = (0.0, 0.0, 0.0)
camera_data.type = "ORTHO"
camera_data.ortho_scale = 6.0

scene.camera = camera

# Create a simple plane as our first visible 2D-like element.
bpy.ops.mesh.primitive_plane_add(
    size=2.0,
    location=(0.0, 0.0, 0.0),
)

plane = bpy.context.active_object
plane.name = "Studio2D_Test_Plane"

# Rotate the plane so it faces the camera.
plane.rotation_euler = (0.0, 0.0, 0.0)

# Save project.
blend_path = OUTPUT / "phase1_test.blend"
bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))

# Render one frame.
render_path = OUTPUT / "phase1_test.png"
scene.render.filepath = str(render_path)

bpy.ops.render.render(write_still=True)

print("STUDIO2D_BLENDER_TEST_OK")
print(f"BLEND={blend_path}")
print(f"RENDER={render_path}")

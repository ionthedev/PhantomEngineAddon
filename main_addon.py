bl_info = {
    "name": "Phantom Engine Addon",
    "author": "Brandon Friend",
    "version": (1, 0, 0),
    "blender": (4, 2, 0),
    "description": "A utility for creating maps for games using the Phantom Engine",
    "category": "Object",
}

import bpy
import json

# Define the SceneDataExporter class
class SceneDataExporter(bpy.types.Operator):
    """Export Scene Data to PMD with Parent-Child Hierarchy"""
    bl_idname = "export_scene_data.to_pmd"
    bl_label = "Export Scene Data to PMD"
    bl_options = {'REGISTER', 'UNDO'}

    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def collect_custom_properties(self, obj):
        """Collects custom properties from a Blender object."""
        properties = {}
        for key in obj.keys():
            if key not in ('_RNA_UI', 'cycles'):
                properties[key] = obj[key]
        return properties

    def collect_light_data(self, light):
        """Collects relevant data from a Blender light object."""
        data = {
            'type': light.type,
            'energy': light.energy,
            'color': list(light.color),
            'specular_factor': light.specular_factor,
            'shadow_soft_size': light.shadow_soft_size,
        }

        if light.type == 'SPOT':
            data.update({
                'spot_size': light.spot_size,
                'spot_blend': light.spot_blend,
            })

        return data

    def gather_object_info(self, obj):
        """Recursively gathers data from an object, including hierarchy and custom properties."""
        obj_info = {
            'name': obj.name,
            'location': list(obj.location),
            'rotation': list(obj.rotation_euler),
            'scale': list(obj.scale),
            'custom_properties': self.collect_custom_properties(obj),
            'parent': obj.parent.name if obj.parent else None,
            'children': [],
        }

        if obj.type == 'LIGHT':
            obj_info['light_data'] = self.collect_light_data(obj.data)

        for child in obj.children:
            obj_info['children'].append(self.gather_object_info(child))

        return obj_info

    def execute(self, context):
        """Executes the export operation."""
        # Select all objects in the scene
        bpy.ops.object.select_all(action='SELECT')

        # Start collecting data from the root objects (those without parents)
        scene_info = []
        for obj in context.selected_objects:
            if obj.parent is None:
                scene_info.append(self.gather_object_info(obj))

        # Ensure the file has a .PMD extension
        if not self.filepath.lower().endswith(".pmd"):
            self.filepath += ".pmd"

        # Write the collected data to a file
        with open(self.filepath, 'w') as file:
            json.dump(scene_info, file, indent=4)

        self.report({'INFO'}, "Scene data successfully exported to PMD format.")
        return {'FINISHED'}

    def invoke(self, context, event):
        """Invokes the file selector dialog."""
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

# Define the CustomPropertiesPanel and SetCustomProperties classes
class CustomPropertiesPanel(bpy.types.Panel):
    """Creates a Panel in the 3D Viewport to set custom properties."""
    bl_label = "Set Custom Properties"
    bl_idname = "VIEW3D_PT_custom_properties"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Tool"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        layout.prop(scene, "custom_id")
        layout.prop(scene, "custom_collision_type")
        layout.prop(scene, "custom_object_type")
        layout.prop(scene, "custom_rigidbody")
        layout.operator("object.set_custom_properties", text="Set Data")

class SetCustomProperties(bpy.types.Operator):
    """Sets custom properties for selected objects"""
    bl_idname = "object.set_custom_properties"
    bl_label = "Set Custom Properties"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene

        for obj in context.selected_objects:
            obj["ID"] = scene.custom_id
            obj["CollisionType"] = scene.custom_collision_type
            obj["ObjectType"] = scene.custom_object_type
            obj["Rigidbody"] = scene.custom_rigidbody

        self.report({'INFO'}, "Custom properties set for selected objects.")
        return {'FINISHED'}

def menu_func_export(self, context):
    """Adds the export option to the file menu."""
    self.layout.operator(SceneDataExporter.bl_idname, text="Scene Data to PMD")

def register():
    bpy.utils.register_class(SceneDataExporter)
    bpy.utils.register_class(CustomPropertiesPanel)
    bpy.utils.register_class(SetCustomProperties)
    
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)

    bpy.types.Scene.custom_id = bpy.props.StringProperty(name="ID")
    bpy.types.Scene.custom_collision_type = bpy.props.EnumProperty(
        name="CollisionType",
        items=[
            ('CONCAVE', "Concave", ""),
            ('CONVEX', "Convex", ""),
            ('NONE', "None", "")
        ],
        default='NONE'
    )
    bpy.types.Scene.custom_object_type = bpy.props.EnumProperty(
        name="ObjectType",
        items=[
            ('WORLD', "World", ""),
            ('SPAWNER', "Spawner", ""),
            ('BUTTON', "Button", ""),
            ('DOOR', "Door", ""),
            ('LEVER', "Lever", ""),
            ('ITEM', "Item", "")
        ],
        default='WORLD'
    )
    bpy.types.Scene.custom_rigidbody = bpy.props.BoolProperty(name="Rigidbody")

def unregister():
    bpy.utils.unregister_class(SceneDataExporter)
    bpy.utils.unregister_class(CustomPropertiesPanel)
    bpy.utils.unregister_class(SetCustomProperties)
    
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)
    
    del bpy.types.Scene.custom_id
    del bpy.types.Scene.custom_collision_type
    del bpy.types.Scene.custom_object_type
    del bpy.types.Scene.custom_rigidbody

if __name__ == "__main__":
    register()


import bpy
import json

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


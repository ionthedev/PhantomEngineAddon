import bpy

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

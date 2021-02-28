bl_info = {
    "name": "Fortnite Utils",
    "author": "Half",
    "version": (0, 1, 0),
    "blender": (2, 90, 0),
    "location": "View3D > Sidebar > FortniteUtils",
    "description": "Blender Addon for FortniteUtils",
    "category": "FortniteUtils",
}

import bpy
import json
import os

class FortniteUtilsPanel(bpy.types.Panel):
    bl_label = "Fortnite Utils"
    bl_idname = 'FORTNITEUTILS_PT_Main'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'FortniteUtils'

    def draw(self, context):
        layout = self.layout
        
        row = layout.row()
        row.label(text="Armature:", icon='OUTLINER_OB_ARMATURE')

        row = layout.row()
        row.prop(context.scene, 'ikArm')
        row = layout.row()
        row.prop(context.scene, 'ikLeg')
        
        row = layout.row()
        row.operator('fortniteutils.autoik', icon='CON_KINEMATIC')
        row = layout.row()
        row.operator('fortniteutils.duplicate', icon='BONE_DATA')
        row = layout.row()
        row.operator('fortniteutils.eyes', icon='OUTLINER_DATA_ARMATURE')
        
        layout.row()
        
        row = layout.row()
        row.label(text="Mesh:", icon='OUTLINER_OB_MESH')
        row = layout.row()
        row.operator('fortniteutils.quads', icon='MESH_DATA')
        row = layout.row()
        row.operator('fortniteutils.upres', icon='MODIFIER_DATA')
        
        layout.row()
        
        row = layout.row()
        row.label(text="Other:", icon='MODIFIER')
        row = layout.row()
        row.operator('fortniteutils.quit', icon='CANCEL')
        
class FortniteUtilsMain():
    
    def createNewBone(object, new_bone_name, parent_name, parent_connected, head, tail, roll):
        bpy.ops.armature.select_all(action='DESELECT')

        bpy.ops.armature.bone_primitive_add(name=new_bone_name)

        new_edit_bone = object.data.edit_bones[new_bone_name]
        new_edit_bone.use_connect = parent_connected
        new_edit_bone.parent = object.data.edit_bones[parent_name]    
        new_edit_bone.use_inherit_rotation = True
        new_edit_bone.use_local_location = True
        new_edit_bone.use_inherit_scale = False

        new_edit_bone.head = head
        new_edit_bone.tail = tail
        new_edit_bone.roll = roll
        
    def createIKBone(obj, bone_name, pole):
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        pose_bones = {pb.name: pb for pb in bpy.data.objects[obj.name].pose.bones}
        FortniteUtilsMain.createNewBone(obj, "ik_" + bone_name, bone_name, False, pose_bones[bone_name].head, pose_bones[bone_name].tail, obj.data.edit_bones[bone_name].roll)
        obj.data.edit_bones["ik_" + bone_name].parent = obj.data.edit_bones["root"]
        bpy.ops.object.posemode_toggle()
        obj.data.bones[bone_name].select = True
        con = obj.pose.bones[bone_name].constraints.new(type="IK")
        con.target = obj
        con.subtarget = "ik_" + bone_name
        con.pole_target = obj
        con.pole_subtarget = pole
        con.pole_angle = 180
        con.chain_count = 3
        con.use_rotation = True
        
    def createPoleBone(obj, targetBone, finalBone, poleMovement):
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        pose_bones = {pb.name: pb for pb in bpy.data.objects[obj.name].pose.bones}
        FortniteUtilsMain.createNewBone(obj, finalBone, targetBone, False, pose_bones[targetBone].head, pose_bones[targetBone].tail, obj.data.edit_bones[targetBone].roll)
        obj.data.edit_bones[finalBone].parent = obj.data.edit_bones["root"]
        obj.data.edit_bones[finalBone].head.y += poleMovement
        obj.data.edit_bones[finalBone].tail.y += poleMovement

class FortniteUtilsAutoIK(bpy.types.Operator):
    bl_idname = "fortniteutils.autoik"
    bl_label = "Auto IK"
    bl_description = "Automatically adds Inverse Kinematics to the selected Fortnite Armature"
        
    def execute(self, context):
        obj = bpy.context.view_layer.objects.active
        
        if obj.type != 'ARMATURE':
            raise Exception("Selected object must be an armature!")
            
        for bone in obj.pose.bones:
            if "pole" in bone.name:
                raise Exception("Armature is already IK rigged!")
        
        if context.scene.ikLeg == True:
            FortniteUtilsMain.createPoleBone(obj, "calf_r", "ik_pole_foot_r", -.35)
            FortniteUtilsMain.createIKBone(obj, "foot_r", "ik_pole_foot_r")
            FortniteUtilsMain.createPoleBone(obj, "calf_l", "ik_pole_foot_l", -.35)
            FortniteUtilsMain.createIKBone(obj, "foot_l", "ik_pole_foot_l")
        if context.scene.ikArm == True:
            FortniteUtilsMain.createPoleBone(obj, "lowerarm_r", "ik_pole_hand_r", .35)
            FortniteUtilsMain.createIKBone(obj, "hand_r", "ik_pole_hand_r")
            FortniteUtilsMain.createPoleBone(obj, "lowerarm_l", "ik_pole_hand_l", .35)
            FortniteUtilsMain.createIKBone(obj, "hand_l", "ik_pole_hand_l")
            
        self.report({'INFO'}, "Added Inverse Kinematics!")

        return {'FINISHED'}
    
class FortniteUtilsDuplicate(bpy.types.Operator):
    bl_idname = "fortniteutils.duplicate"
    bl_label = "Remove Duplicate Bones"
    bl_description = "Removes .00X bones from armatures"
        
    def execute(self, context):
        obj = bpy.context.view_layer.objects.active
        
        if obj.type != 'ARMATURE':
            raise Exception("Selected object must be an armature!")
        
        bpy.ops.object.editmode_toggle()
        bpy.ops.armature.select_all(action='DESELECT')
        bpy.ops.object.select_pattern(pattern="*.001")
        bpy.ops.object.select_pattern(pattern="*.002")
        bpy.ops.object.select_pattern(pattern="*.003")
        bpy.ops.object.select_pattern(pattern="*.004")
        bpy.ops.object.select_pattern(pattern="*.005")
        bpy.ops.object.select_pattern(pattern="*.006")
        bpy.ops.object.select_pattern(pattern="*.007")
        bpy.ops.object.select_pattern(pattern="*.008")
        bpy.ops.object.select_pattern(pattern="*.009")
        bpy.ops.armature.delete()
        bpy.ops.object.editmode_toggle()
        
        self.report({'INFO'}, "Removed duplicate bones!")
        
        return {'FINISHED'}
    
class FortniteUtilsEyes(bpy.types.Operator):
    bl_idname = "fortniteutils.eyes"
    bl_label = "FaceAttach Fixes"
    bl_description = "Parents eyelids to faceAttach and parents faceAttach to head"
        
    def execute(self, context):
        obj = bpy.context.view_layer.objects.active
        
        if obj.type != 'ARMATURE':
            raise Exception("Selected object must be an armature!")
        
        bpy.ops.object.editmode_toggle()
        obj.data.edit_bones["L_eye_lid_upper_mid"].parent = obj.data.edit_bones["faceAttach"]
        obj.data.edit_bones["R_eye_lid_upper_mid"].parent = obj.data.edit_bones["faceAttach"]
        obj.data.edit_bones["L_eye_lid_lower_mid"].parent = obj.data.edit_bones["faceAttach"]
        obj.data.edit_bones["R_eye_lid_lower_mid"].parent = obj.data.edit_bones["faceAttach"]
        obj.data.edit_bones["faceAttach"].parent = obj.data.edit_bones["head"]
        bpy.ops.object.editmode_toggle()
        
        self.report({'INFO'}, "Finished fixing facial bones!")

        return {'FINISHED'}
    
class FortniteUtilsQuads(bpy.types.Operator):
    bl_idname = "fortniteutils.quads"
    bl_label = "Convert to Quads"
    bl_description = "Converts the selected meshes' polygons to quads"
        
    def execute(self, context):
        obj = bpy.context.view_layer.objects.active
        
        if obj.type != 'MESH':
            raise Exception("Selected object(s) must be a mesh!")
        
        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.tris_convert_to_quads(uvs=True)
        bpy.ops.object.editmode_toggle()
        
        self.report({'INFO'}, "Successfully converted to Quads!")

        return {'FINISHED'}
    
class FortniteUtilsUpres(bpy.types.Operator):
    bl_idname = "fortniteutils.upres"
    bl_label = 'Up-Resolution Mesh'
    bl_description = 'Up-Res\'s the selected meshes with modifiers'
        
    def execute(self, context):
        obj = bpy.context.view_layer.objects.active
        
        if obj.type != 'MESH':
            raise Exception("Selected object(s) must be a mesh!")
        
        for mod in obj.modifiers:
            if mod.type == 'ARMATURE':
                obj.modifiers[mod.name].use_deform_preserve_volume = True
                
        csmooth = obj.modifiers.new(type='CORRECTIVE_SMOOTH', name="Corrective Smooth")
        csmooth.use_pin_boundary = True
        
        sub = obj.modifiers.new(type='SUBSURF', name="Subdivison Surface")
        sub.show_viewport = False
        
        bev = obj.modifiers.new(type='BEVEL', name="Bevel")
        bev.offset_type = 'DEPTH'
        bev.width = 0.0006
        bev.segments = 3
        bev.angle_limit = 0.698132
        bev.show_viewport = False
        
        self.report({'INFO'}, "Bevel and Subdivison Surface are hidden from viewport by default. Up-Resolution has been added.")
        
        return {'FINISHED'}
    
class FortniteUtilsQuit(bpy.types.Operator):
    bl_idname = "fortniteutils.quit"
    bl_label = "Rage Quit"
    bl_description = "Quits blender without saving"
        
    def execute(self, context):
        bpy.ops.wm.quit_blender()
        return {'FINISHED'}
    
class FortniteUtilsSettings(bpy.types.PropertyGroup):
    scene = bpy.types.Scene

    scene.ikArm = bpy.props.BoolProperty(name="IK Arms", default=True)
    scene.ikLeg = bpy.props.BoolProperty(name="IK Legs", default=True)

classes = [FortniteUtilsPanel, FortniteUtilsAutoIK, FortniteUtilsDuplicate, FortniteUtilsEyes, FortniteUtilsQuads, FortniteUtilsUpres, FortniteUtilsQuit]

def register():
    
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
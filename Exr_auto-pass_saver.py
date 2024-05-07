bl_info = {
    "name": "Exr Auto Pass Saver - BL41",
    "description": "Link all render passes to a new EXR-MultiLayer save node",
    "blender": (4, 1, 0),
    "category": "Compositing",
    "author": "3d-io",
    "version": (2, 0),
    "location": "Compositor Tab > Sidebar > Exr Auto Pass Saver",
    "warning": "BSD",
    "wiki_url": "https://github.com/3d-io/",
    "support": "COMMUNITY",
}

import bpy
import subprocess
import os

bpy.types.Scene.exr_auto_pass_saver_clear_all = bpy.props.BoolProperty(
    name="Clear all nodes",
    description="Remove all nodes from the Compositor and add only RenderLayer <-> Saver Node",
    default=False
)

bpy.types.Scene.exr_auto_pass_saver_open_dir = bpy.props.BoolProperty(
    name="Open destination folder",
    description="A folder where the Exr Image is going to be saved",
    default=False
)

class ExrAutoPassSaver(bpy.types.Operator):
    bl_idname = "node.exr_pass_saver"
    bl_label = "Exr Auto Saver"
    bl_options = {'REGISTER', 'UNDO'}

    def cleannodes(self, context):
        try:
            nodesField = context.scene.node_tree
            nodesField.nodes.clear()
        except Exception as e:
            self.report({'ERROR'}, "Failed to clear nodes: " + str(e))

    def openfolder(self, context):
        try:
            path = context.scene.render.filepath
            if os.name == 'nt':
                subprocess.call(f'explorer "{os.path.realpath(path)}"', shell=True)
            else:
                subprocess.call(['xdg-open', os.path.dirname(path)])
        except Exception as e:
            self.report({'ERROR'}, "Failed to open folder: " + str(e))

    def create_nodes(self, context):
        node_tree = context.scene.node_tree
        layersNode = node_tree.nodes.new('CompositorNodeRLayers')
        layersNode.location = (0, 400)

        outputNode = node_tree.nodes.new("CompositorNodeOutputFile")
        outputNode.label = 'EXR-MultiLayer'
        outputNode.base_path = self.get_output_path_str(context)
        outputNode.location = (400, 450)
        outputNode.width = 300
        outputNode.use_custom_color = True
        outputNode.color = (0.686, 0.204, 0.176)
        context.scene.render.image_settings.file_format = 'OPEN_EXR_MULTILAYER'

        for output in layersNode.outputs:
            if output.enabled:
                outputNode.file_slots.new(output.identifier)
                node_tree.links.new(output, outputNode.inputs[-1])

    def get_output_path_str(self, context):
        defaultPath = context.scene.render.filepath
        dirname = os.path.dirname(defaultPath)
        if not dirname.endswith(('/', '\\')):
            dirname += "/"
        if not dirname:
            dirname = os.path.expanduser('~') + "/"
        return os.path.join(dirname, "output.exr")

    def execute(self, context):
        if not context.scene.use_nodes:
            self.report({'WARNING'}, "Node tree not in use. Skipping.")
            return {'CANCELLED'}

        if context.scene.exr_auto_pass_saver_clear_all:
            self.cleannodes(context)

        if context.scene.exr_auto_pass_saver_open_dir:
            self.openfolder(context)

        self.create_nodes(context)

        return {'FINISHED'}


class ExrAutoPassSaverPanel(bpy.types.Panel):
    bl_label = "Exr Auto Pass Saver"
    bl_category = "Exr Auto Pass Saver"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"

    def draw(self, context):
        layout = self.layout
        layout.label(text="Link all nodes:")
        layout.operator(ExrAutoPassSaver.bl_idname, icon='TRACKING_FORWARDS')
        layout.prop(context.scene, "exr_auto_pass_saver_clear_all")
        layout.prop(context.scene, "exr_auto_pass_saver_open_dir")


classes = (ExrAutoPassSaverPanel, ExrAutoPassSaver)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()

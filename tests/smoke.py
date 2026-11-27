"""Run with Blender 5.2; by default tests source add-ons and an optional LoopTools extension."""
import math
from pathlib import Path
import sys

import bmesh
import bpy


SOURCE_NAMES = ("EZDeleteChildBone", "EZLoop", "EZLoopTools", "EZQuadRemeshes", "EZRemeshes")
EXTENSION_IDS = ("ez_delete_child_bone", "ez_loop", "ez_loop_tools",
                 "ez_quad_remeshes", "ez_remeshes")
OPTIONS = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []


def fresh():
    if bpy.context.object and bpy.context.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)


def activate(obj):
    bpy.context.collection.objects.link(obj)
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    return obj


def mesh_object(verts, faces):
    mesh = bpy.data.meshes.new("Test mesh")
    mesh.from_pydata(verts, [], faces)
    return activate(bpy.data.objects.new("Test mesh", mesh))


def bones_test():
    fresh()
    arm = bpy.data.armatures.new("Test rig")
    activate(bpy.data.objects.new("Test rig", arm))
    bpy.ops.object.mode_set(mode='EDIT')
    bones = arm.edit_bones
    for i, (name, parent) in enumerate((("Root", None), ("Bridge", "Root"),
                                       ("Selected child", "Bridge"), ("Leaf", "Selected child"),
                                       ("Other", None))):
        bone = bones.new(name)
        bone.head, bone.tail = (0, i, 0), (0, i + 1, 0)
        if parent:
            bone.parent = bones[parent]
            bone.use_connect = True
    bpy.ops.armature.select_all(action='DESELECT')
    bones["Root"].select = bones["Selected child"].select = True
    bones.active = bones["Root"]
    child_head = bones["Selected child"].head.copy()
    assert bpy.ops.ezdeletecb.delete_child_bones() == {'FINISHED'}
    assert set(bones.keys()) == {"Root", "Selected child", "Other"}
    assert bones["Selected child"].parent == bones["Root"]
    assert bones["Selected child"].head == child_head
    assert bpy.ops.ezdeletecb.delete_child_bones() == {'CANCELLED'}


def bone_protection_test():
    fresh()
    arm = bpy.data.armatures.new("Protected rig")
    activate(bpy.data.objects.new("Protected rig", arm))
    bpy.ops.object.mode_set(mode='EDIT')
    bones = arm.edit_bones
    hidden_collection = arm.collections.new("Hidden")
    hidden_collection.is_visible = False
    inherited_hidden = arm.collections.new("Nested", parent=hidden_collection)
    visible_collection = arm.collections.new("Visible")
    tree = (("Root", None), ("Visible child", "Root"), ("Hidden bone", "Visible child"),
            ("Unselectable", "Visible child"), ("Hidden collection", "Root"),
            ("Visible and hidden collections", "Root"), ("Beyond hidden bone", "Hidden bone"))
    for i, (name, parent) in enumerate(tree):
        bone = bones.new(name)
        bone.head, bone.tail = (0, i, 0), (0, i + 1, 0)
        if parent:
            bone.parent = bones[parent]
            bone.use_connect = True
    bones["Hidden bone"].hide = True
    bones["Unselectable"].hide_select = True
    inherited_hidden.assign(bones["Hidden collection"])
    hidden_collection.assign(bones["Visible and hidden collections"])
    visible_collection.assign(bones["Visible and hidden collections"])
    bpy.ops.armature.select_all(action='DESELECT')
    bones["Root"].select = True
    bones.active = bones["Root"]
    heads = {name: bones[name].head.copy() for name in ("Hidden bone", "Unselectable")}
    assert bpy.ops.ezdeletecb.delete_child_bones() == {'FINISHED'}
    assert set(bones.keys()) == {"Root", "Hidden bone", "Unselectable", "Hidden collection"}
    for name, head in heads.items():
        assert bones[name].parent == bones["Root"]
        assert bones[name].head == head
    assert bones["Hidden bone"].hide and bones["Unselectable"].hide_select
    assert bpy.ops.ezdeletecb.delete_child_bones() == {'CANCELLED'}


def ngon_test():
    ngon = [(math.cos(i * math.tau / 8), math.sin(i * math.tau / 8), 0) for i in range(8)]
    concave = [(0, 0, 0), (4, 0, 0), (4, 4, 0), (3, 4, 0),
               (3, 1, 0), (1, 1, 0), (1, 4, 0), (0, 4, 0)]
    edge_signatures = []
    for op in (bpy.ops.mesh.ez_remeshes_operator_far, bpy.ops.mesh.ez_remeshes_operator_close):
        fresh()
        obj = mesh_object(ngon, [tuple(range(8))])
        obj.data.uv_layers.new(name="Test UV")
        assert op() == {'FINISHED'}
        assert obj.mode == 'OBJECT'
        assert len(obj.data.vertices) == 8
        assert all(3 <= len(f.vertices) <= 4 for f in obj.data.polygons)
        assert obj.data.uv_layers.get("Test UV")
        assert abs(sum(f.area for f in obj.data.polygons) - 2 * math.sqrt(2)) < 1e-5
        edge_signatures.append({tuple(sorted(e.vertices)) for e in obj.data.edges})
        assert op() == {'CANCELLED'}
    assert edge_signatures[0] != edge_signatures[1]

    fresh()
    obj = mesh_object(concave + [(x + 6, y, z) for x, y, z in concave],
                      [tuple(range(8)), tuple(range(8, 16))])
    bpy.context.tool_settings.mesh_select_mode = (False, False, True)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='DESELECT')
    bm = bmesh.from_edit_mesh(obj.data)
    bm.faces.ensure_lookup_table()
    bm.faces[0].select_set(True)
    expected_area = bm.faces[0].calc_area()
    assert bpy.ops.mesh.ez_remeshes_operator_far() == {'FINISHED'}
    assert bpy.context.mode == 'EDIT_MESH'
    assert sum(len(f.verts) > 4 for f in bm.faces) == 1
    reduced = [f for f in bm.faces if len(f.verts) <= 4]
    assert abs(sum(f.calc_area() for f in reduced) - expected_area) < 1e-5
    assert all(f.select for f in reduced)


def quad_test():
    fresh()
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3)
    obj = bpy.context.object
    smooth = obj.modifiers.new("Smooth", 'SMOOTH')
    smooth.factor = 0.123
    props = bpy.context.scene.ez_quadremeshes_props
    props.target_faces = 160
    props.smooth_iterations = 2
    assert bpy.ops.ezquadremeshes.remesh() == {'FINISHED'}
    assert all(len(f.vertices) == 4 for f in obj.data.polygons) and len(obj.data.polygons) > 0
    assert len(obj.modifiers) == 1 and abs(obj.modifiers["Smooth"].factor - 0.123) < 1e-6
    bpy.ops.object.mode_set(mode='EDIT')
    assert not bpy.ops.ezquadremeshes.remesh.poll()
    bpy.ops.object.mode_set(mode='OBJECT')
    obj.shape_key_add(name="Basis")
    assert bpy.ops.ezquadremeshes.remesh() == {'CANCELLED'}

    fresh()
    # Three triangles attached to the same edge: QuadriFlow must not smooth a failed input.
    points = [(0, 0, 0), (2, 0, 0), (1, 1, 0), (1, -1, 0), (1, 0, 1)]
    obj = mesh_object(points, [(0, 1, 2), (1, 0, 3), (0, 1, 4)])
    assert bpy.ops.ezquadremeshes.remesh() == {'CANCELLED'}
    assert [tuple(v.co) for v in obj.data.vertices] == points


def crease_test():
    import importlib

    pkg = next((key for key in bpy.context.preferences.addons.keys()
                if key.startswith("bl_ext.") and key.endswith(".ez_quad_remeshes")),
               "EZQuadRemeshes")
    smooth_mesh = importlib.import_module(pkg + ".ez_quadremeshes_operation").smooth_mesh
    original = [(0, 0, 0), (2, 0, 0), (2, 2, 0), (0, 2, 0), (0, 0, 2), (2, 0, 2)]
    for protect in (True, False):
        fresh()
        obj = mesh_object(original, [(0, 1, 2, 3), (1, 0, 4, 5)])
        assert not any(e.use_edge_sharp for e in obj.data.edges)
        assert abs(obj.data.polygons[0].normal.dot(obj.data.polygons[1].normal)) < 1e-6
        smooth_mesh(obj.data, 2, preserve_boundary=False, preserve_sharp=protect)
        assert all((tuple(obj.data.vertices[i].co) == original[i]) == protect for i in (0, 1))
        assert tuple(obj.data.vertices[2].co) != original[2]  # Smoothing really ran.


def edit_grid(mirror=False):
    fresh()
    size = 5
    verts = [(x + 1.0, y * (0.72 if y == 1 else 1.0),
              0.35 if (x + y) % 3 == 0 else 0.0) for y in range(size) for x in range(size)]
    faces = [(p, p + 1, p + 1 + size, p + size)
             for y in range(size - 1) for x in range(size - 1) for p in [y * size + x]]
    obj = mesh_object(verts, faces)
    if mirror:
        obj.modifiers.new("Mirror", 'MIRROR')
    bpy.context.tool_settings.mesh_select_mode = (False, False, True)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='DESELECT')
    bm = bmesh.from_edit_mesh(obj.data)
    bm.faces.ensure_lookup_table()
    for i in (0, 1, 2, 4, 5, 6, 8, 9, 10):
        bm.faces[i].select_set(True)
    bm.faces.active = bm.faces[5]
    bm.select_history.add(bm.faces[5])
    bmesh.update_edit_mesh(obj.data)
    return obj.data


def selection(mesh):
    bm = bmesh.from_edit_mesh(mesh)
    return tuple(tuple(item.select for item in seq) for seq in (bm.verts, bm.edges, bm.faces))


def loop_test():
    try:
        bpy.ops.mesh.looptools_flatten.get_rna_type()
        has_looptools = True
    except (KeyError, RuntimeError):
        has_looptools = False
    if "--require-looptools" in OPTIONS:
        assert has_looptools, "LoopTools must be installed and enabled for this run"
    mesh = edit_grid()
    original = selection(mesh)
    if not has_looptools:
        assert bpy.ops.mesh.ezlooptools_operation() == {'CANCELLED'}
        for op in (bpy.ops.ezloop.flatten, bpy.ops.ezloop.relax, bpy.ops.ezloop.space):
            assert op() == {'CANCELLED'}
        assert selection(mesh) == original
        print("SKIP: run with LoopTools enabled and --require-looptools to test geometry changes")
        return

    scene = bpy.context.scene
    for opt, scope, mirror in (('FLATTEN', 'HORIZONTAL', False), ('RELAX', 'HORIZONTAL', True),
                               ('SPACE', 'BOUNDARY', False)):
        mesh = edit_grid(mirror)
        original = selection(mesh)
        before = [v.co.copy() for v in bmesh.from_edit_mesh(mesh).verts]
        scene.ezlooptools_operation = opt
        scene.ezlooptools_direction = scope
        assert bpy.ops.mesh.ezlooptools_operation() == {'FINISHED'}
        bm = bmesh.from_edit_mesh(mesh)
        assert tuple(bpy.context.tool_settings.mesh_select_mode) == (False, False, True)
        assert selection(mesh) == original
        assert bm.faces.active.index == 5
        assert [item.index for item in bm.select_history] == [5]
        assert any((v.co - old).length > 1e-5 for v, old in zip(bm.verts, before))
        assert all((v.co - old).length < 1e-5 for v, old, sel in
                   zip(bm.verts, before, original[0]) if not sel)

    for op in (bpy.ops.ezloop.flatten, bpy.ops.ezloop.relax, bpy.ops.ezloop.space):
        edit_grid()
        assert op() == {'FINISHED'}


def main():
    if "--installed" in OPTIONS:
        enabled = set(bpy.context.preferences.addons.keys())
        for name in EXTENSION_IDS:
            assert any(key.startswith("bl_ext.") and key.endswith("." + name) for key in enabled), name
        modules = []
    else:
        import importlib

        sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "addons"))
        modules = [importlib.import_module(name) for name in SOURCE_NAMES]
        for module in modules:
            module.register()
    for test in (bones_test, bone_protection_test, ngon_test, quad_test, crease_test, loop_test):
        test()
        print(f"PASS {test.__name__}")
    fresh()
    for module in reversed(modules):
        module.unregister()
    print(f"All smoke tests passed on Blender {bpy.app.version_string}")


if __name__ == "__main__":
    main()

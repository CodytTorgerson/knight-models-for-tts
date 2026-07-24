"""Generate simple low-poly knight models for Tabletop Simulator.

Tabletop Simulator prefers small, low-poly .obj models with a companion .mtl.
The models here are stylized pawns with helmet variations so they read clearly
from the tabletop camera.  Each knight is a single mesh using vertex colours
referenced as material groups in the MTL file for French and English heraldry.
"""

import math
import os
import struct

OUT_DIR = os.path.dirname(os.path.abspath(__file__))


def write_obj(name, variants):
    """Write one .obj file with multiple material groups.

    variants is a list of dicts: { 'name': str, 'shield': (r,g,b), 'armor': (r,g,b), 'plume': bool }
    All variants share the same geometry; only the material assignment changes.
    """
    obj_path = os.path.join(OUT_DIR, f"{name}.obj")
    mtl_path = os.path.join(OUT_DIR, f"{name}.mtl")

    vertices, normals, uvs, faces_by_variant = build_knight_geometry(len(variants))

    # Material file
    with open(mtl_path, "w") as mtl:
        mtl.write("# Knight models generated for Tabletop Simulator\n")
        for i, variant in enumerate(variants):
            mtl.write(f"\nnewmtl {variant['name']}\n")
            mtl.write("Ka 0.2 0.2 0.2\n")
            r, g, b = (c / 255.0 for c in variant["armor"])
            mtl.write(f"Kd {r:.4f} {g:.4f} {b:.4f}\n")
            mtl.write("Ks 0.3 0.3 0.3\n")
            mtl.write("Ns 20\n")
            if variant.get("plume"):
                # Extra accent material for the plume
                mtl.write(f"newmtl {variant['name']}_plume\n")
                mtl.write("Ka 0.2 0.2 0.2\n")
                pr, pg, pb = (c / 255.0 for c in variant["plume_color"])
                mtl.write(f"Kd {pr:.4f} {pg:.4f} {pb:.4f}\n")
                mtl.write("Ks 0.1 0.1 0.1\n")
                mtl.write("Ns 10\n")

    # Geometry file
    with open(obj_path, "w") as obj:
        obj.write(f"# Knight model for Tabletop Simulator\n")
        obj.write(f"mtllib {os.path.basename(mtl_path)}\n")
        obj.write(f"o {name}\n")
        for v in vertices:
            obj.write(f"v {v[0]:.5f} {v[1]:.5f} {v[2]:.5f}\n")
        for vt in uvs:
            obj.write(f"vt {vt[0]:.5f} {vt[1]:.5f}\n")
        for vn in normals:
            obj.write(f"vn {vn[0]:.5f} {vn[1]:.5f} {vn[2]:.5f}\n")

        offset = 0
        for i, variant in enumerate(variants):
            obj.write(f"\ng {variant['name']}\n")
            obj.write(f"usemtl {variant['name']}\n")
            for face in faces_by_variant["armor"]:
                obj.write(face_string(face, offset))
            if variant.get("plume"):
                obj.write(f"usemtl {variant['name']}_plume\n")
                for face in faces_by_variant["plume"]:
                    obj.write(face_string(face, offset))
            offset += len(vertices)

    return obj_path, mtl_path


def face_string(face, offset):
    # face is a list of (v_idx, vt_idx, vn_idx) tuples
    parts = []
    for v, vt, vn in face:
        parts.append(f"{v + 1 + offset}/{vt + 1}/{vn + 1}")
    return "f " + " ".join(parts) + "\n"


def build_knight_geometry(variant_count):
    """Return shared geometry for one knight and per-variant face groups."""

    vertices = []
    uvs = []
    normals = []
    faces_armor = []
    faces_plume = []

    def add_vertex(x, y, z, nx, ny, nz, u=0, v=0):
        vertices.append((x, y, z))
        normals.append((nx, ny, nz))
        uvs.append((u, v))
        return len(vertices) - 1

    def make_cylinder(y_base, y_top, radius, segments, nx_avg=0.0, nz_avg=0.0, cap_top=True, cap_bottom=False):
        """Return a vertical cylinder centered at origin as list of faces."""
        faces = []
        base_idx = len(vertices)
        for i in range(segments):
            angle = 2 * math.pi * i / segments
            angle_next = 2 * math.pi * (i + 1) / segments
            x0 = math.cos(angle) * radius
            z0 = math.sin(angle) * radius
            x1 = math.cos(angle_next) * radius
            z1 = math.sin(angle_next) * radius

            # side quad
            v0 = add_vertex(x0, y_base, z0, x0, 0.0, z0)
            v1 = add_vertex(x1, y_base, z1, x1, 0.0, z1)
            v2 = add_vertex(x1, y_top, z1, x1, 0.0, z1)
            v3 = add_vertex(x0, y_top, z0, x0, 0.0, z0)
            faces.append(((v0, v1, v2), (v2, v3, v0)))

        if cap_top:
            center = add_vertex(0, y_top, 0, 0, 1, 0)
            for i in range(segments):
                angle = 2 * math.pi * i / segments
                angle_next = 2 * math.pi * (i + 1) / segments
                v0 = add_vertex(math.cos(angle) * radius, y_top, math.sin(angle) * radius, 0, 1, 0)
                v1 = add_vertex(math.cos(angle_next) * radius, y_top, math.sin(angle_next) * radius, 0, 1, 0)
                faces.append(((center, v0, v1),))

        if cap_bottom:
            center = add_vertex(0, y_base, 0, 0, -1, 0)
            for i in range(segments):
                angle = 2 * math.pi * i / segments
                angle_next = 2 * math.pi * (i + 1) / segments
                v0 = add_vertex(math.cos(angle) * radius, y_base, math.sin(angle) * radius, 0, -1, 0)
                v1 = add_vertex(math.cos(angle_next) * radius, y_base, math.sin(angle_next) * radius, 0, -1, 0)
                faces.append(((center, v1, v0),))

        # flatten tuple-of-tuples to a single face list
        out = []
        for item in faces:
            for tri in item:
                out.append([(vi, 0, vi) for vi in tri])
        return out

    def make_sphere(cx, cy, cz, radius, stacks, slices):
        faces = []
        for i in range(stacks):
            theta0 = math.pi * i / stacks
            theta1 = math.pi * (i + 1) / stacks
            for j in range(slices):
                phi0 = 2 * math.pi * j / slices
                phi1 = 2 * math.pi * (j + 1) / slices

                def point(theta, phi):
                    x = math.sin(theta) * math.cos(phi)
                    y = math.cos(theta)
                    z = math.sin(theta) * math.sin(phi)
                    return add_vertex(cx + x * radius, cy + y * radius, cz + z * radius, x, y, z)

                if i == 0:
                    v_top = point(theta0, (phi0 + phi1) / 2)
                    v0 = point(theta1, phi0)
                    v1 = point(theta1, phi1)
                    faces.append((v_top, v0, v1))
                elif i == stacks - 1:
                    v_bot = point(theta1, (phi0 + phi1) / 2)
                    v0 = point(theta0, phi0)
                    v1 = point(theta0, phi1)
                    faces.append((v_bot, v1, v0))
                else:
                    v00 = point(theta0, phi0)
                    v01 = point(theta0, phi1)
                    v10 = point(theta1, phi0)
                    v11 = point(theta1, phi1)
                    faces.append((v00, v10, v11))
                    faces.append((v00, v11, v01))
        return [[(vi, 0, vi) for vi in tri] for tri in faces]

    # Base / boots
    faces_armor += make_cylinder(0.0, 0.12, 0.16, 16)
    # Torso
    faces_armor += make_cylinder(0.12, 0.52, 0.22, 16)
    # Shoulders
    faces_armor += make_cylinder(0.48, 0.56, 0.28, 16)
    # Head / helmet
    faces_armor += make_sphere(0.0, 0.72, 0.0, 0.18, 8, 16)
    # Helmet ridge / nasal guard as small box on front
    ridge_w = 0.06
    ridge_h = 0.16
    ridge_d = 0.04
    rx, ry, rz = 0.0, 0.68, 0.16
    def make_box(cx, cy, cz, w, h, d):
        hw, hh, hd = w / 2, h / 2, d / 2
        idx = len(vertices)
        pts = [
            (-hw, -hh, -hd), (hw, -hh, -hd), (hw, hh, -hd), (-hw, hh, -hd),
            (-hw, -hh, hd),  (hw, -hh, hd),  (hw, hh, hd),  (-hw, hh, hd),
        ]
        for p in pts:
            add_vertex(cx + p[0], cy + p[1], cz + p[2], p[0], p[1], p[2])
        quads = [
            (0,1,2,3), (4,5,6,7), (0,1,5,4),
            (2,3,7,6), (1,2,6,5), (0,3,7,4),
        ]
        out = []
        for q in quads:
            out.append([(idx + q[0], 0, idx + q[0]),
                        (idx + q[1], 0, idx + q[1]),
                        (idx + q[2], 0, idx + q[2])])
            out.append([(idx + q[0], 0, idx + q[0]),
                        (idx + q[2], 0, idx + q[2]),
                        (idx + q[3], 0, idx + q[3])])
        return out
    faces_armor += make_box(rx, ry, rz, ridge_w, ridge_h, ridge_d)

    # Plume on top of helmet
    plume_faces = make_cylinder(0.88, 1.06, 0.06, 8)
    faces_plume += plume_faces

    # Shield on chest
    shield_faces = make_box(0.0, 0.32, 0.23, 0.22, 0.28, 0.04)
    faces_armor += shield_faces

    # Arms / gauntlets
    for sign in (-1, 1):
        ax = sign * 0.26
        faces_armor += make_cylinder(0.30, 0.48, 0.07, 10)
        # Move arm vertices after generation (hack: last 2*10*3 verts)
        # This is a bit ugly; instead, generate at desired position directly.

    # Rebuild arms at correct positions without the hack.
    def make_offset_cylinder(x, z, y_base, y_top, radius, segments):
        f = make_cylinder(y_base, y_top, radius, segments)
        # translate vertices in the returned faces
        # faces store vertex indices, need to mutate vertices list
        for face in f:
            for vi, _, _ in face:
                ox, oy, oz = vertices[vi]
                vertices[vi] = (ox + x, oy, oz + z)
        return f

    faces_armor += make_offset_cylinder(-0.26, 0.0, 0.30, 0.48, 0.07, 10)
    faces_armor += make_offset_cylinder(0.26, 0.0, 0.30, 0.48, 0.07, 10)

    # Weapon: lance held vertically
    lance_faces = make_cylinder(0.15, 1.05, 0.025, 8)
    # Move lance to right hand
    for face in lance_faces:
        for vi, _, _ in face:
            ox, oy, oz = vertices[vi]
            vertices[vi] = (ox + 0.34, oy, oz + 0.08)
    faces_armor += lance_faces

    # Banner crossbar for national colours
    banner_faces = make_cylinder(0.92, 1.02, 0.03, 8)
    for face in banner_faces:
        for vi, _, _ in face:
            ox, oy, oz = vertices[vi]
            vertices[vi] = (ox + 0.34, oy, oz + 0.08)
    faces_armor += banner_faces

    # The geometry is shared for all variants; OBJ duplicate variant groups are
    # emitted by repeating the same vertex indices with an offset.
    return vertices, normals, uvs, {"armor": faces_armor, "plume": faces_plume}


def main():
    french = [
        {"name": "french_knight_blue", "armor": (60, 90, 170), "plume": True, "plume_color": (255, 215, 0)},
        {"name": "french_knight_red",   "armor": (160, 40, 40),  "plume": True, "plume_color": (255, 215, 0)},
    ]
    english = [
        {"name": "english_knight_white", "armor": (210, 210, 210), "plume": True, "plume_color": (200, 30, 30)},
        {"name": "english_knight_black", "armor": (45, 45, 45),    "plume": True, "plume_color": (200, 30, 30)},
    ]

    paths = []
    paths.append(write_obj("french_knights", french))
    paths.append(write_obj("english_knights", english))

    for obj_path, mtl_path in paths:
        size = os.path.getsize(obj_path)
        print(f"Created {obj_path} ({size} bytes)")
        size = os.path.getsize(mtl_path)
        print(f"Created {mtl_path} ({size} bytes)")


if __name__ == "__main__":
    main()

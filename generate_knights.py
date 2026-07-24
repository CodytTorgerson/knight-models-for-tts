"""Generate simple, clean knight models for Tabletop Simulator.

Each knight is a single low-poly mesh with a small solid-colour PNG texture.
TTS requires a .obj file and a .png diffuse image for Custom Model import.
"""

import math
import os

from PIL import Image

OUT_DIR = os.path.dirname(os.path.abspath(__file__))


def build_knight_geometry():
    """Return a compact, board-game-style knight mesh."""

    vertices = []
    uvs = []
    normals = []
    faces = []

    def add_vertex(x, y, z, nx, ny, nz, u=0.5, v=0.5):
        vertices.append((x, y, z))
        normals.append((nx, ny, nz))
        uvs.append((u, v))
        return len(vertices) - 1

    def make_cylinder(y_base, y_top, radius, segments, u_base=0.0, v_scale=1.0):
        faces_out = []
        for i in range(segments):
            a0 = 2 * math.pi * i / segments
            a1 = 2 * math.pi * (i + 1) / segments
            x0 = math.cos(a0) * radius
            z0 = math.sin(a0) * radius
            x1 = math.cos(a1) * radius
            z1 = math.sin(a1) * radius

            u0 = i / segments
            u1 = (i + 1) / segments
            v0 = y_base
            v1 = y_top

            v0_idx = add_vertex(x0, y_base, z0, x0, 0.0, z0, u0, v0)
            v1_idx = add_vertex(x1, y_base, z1, x1, 0.0, z1, u1, v0)
            v2_idx = add_vertex(x1, y_top, z1, x1, 0.0, z1, u1, v1)
            v3_idx = add_vertex(x0, y_top, z0, x0, 0.0, z0, u0, v1)
            faces_out.append([(v0_idx, u0, v0), (v1_idx, u1, v0), (v2_idx, u1, v1)])
            faces_out.append([(v0_idx, u0, v0), (v2_idx, u1, v1), (v3_idx, u0, v1)])
        return faces_out

    def make_sphere(cx, cy, cz, radius, stacks, slices):
        faces_out = []
        for i in range(stacks):
            theta0 = math.pi * i / stacks
            theta1 = math.pi * (i + 1) / stacks
            for j in range(slices):
                phi0 = 2 * math.pi * j / slices
                phi1 = 2 * math.pi * (j + 1) / slices

                def point(theta, phi, u, v):
                    x = math.sin(theta) * math.cos(phi)
                    y = math.cos(theta)
                    z = math.sin(theta) * math.sin(phi)
                    return add_vertex(cx + x * radius, cy + y * radius, cz + z * radius, x, y, z, u, v)

                u0 = j / slices
                u1 = (j + 1) / slices
                v0 = i / stacks
                v1 = (i + 1) / stacks

                if i == 0:
                    v_top = point(theta0, (phi0 + phi1) / 2, (u0 + u1) / 2, v0)
                    v0 = point(theta1, phi0, u0, v1)
                    v1 = point(theta1, phi1, u1, v1)
                    faces_out.append([(v_top, (u0 + u1) / 2, v0), (v0, u0, v1), (v1, u1, v1)])
                elif i == stacks - 1:
                    v_bot = point(theta1, (phi0 + phi1) / 2, (u0 + u1) / 2, v1)
                    v0 = point(theta0, phi0, u0, v0)
                    v1 = point(theta0, phi1, u1, v0)
                    faces_out.append([(v_bot, (u0 + u1) / 2, v1), (v1, u1, v0), (v0, u0, v0)])
                else:
                    v00 = point(theta0, phi0, u0, v0)
                    v01 = point(theta0, phi1, u1, v0)
                    v10 = point(theta1, phi0, u0, v1)
                    v11 = point(theta1, phi1, u1, v1)
                    faces_out.append([(v00, u0, v0), (v10, u0, v1), (v11, u1, v1)])
                    faces_out.append([(v00, u0, v0), (v11, u1, v1), (v01, u1, v0)])
        return faces_out

    def make_box(cx, cy, cz, w, h, d):
        hw, hh, hd = w / 2, h / 2, d / 2
        idx = len(vertices)
        pts = [
            (-hw, -hh, -hd), (hw, -hh, -hd), (hw, hh, -hd), (-hw, hh, -hd),
            (-hw, -hh, hd),  (hw, -hh, hd),  (hw, hh, hd),  (-hw, hh, hd),
        ]
        box_normals = [
            (0, 0, -1), (0, 0, -1), (0, 0, -1), (0, 0, -1),
            (0, 0, 1),  (0, 0, 1),  (0, 0, 1),  (0, 0, 1),
        ]
        for p, n in zip(pts, box_normals):
            add_vertex(cx + p[0], cy + p[1], cz + p[2], n[0], n[1], n[2], 0.5, 0.5)
        quads = [
            (0, 1, 2, 3), (4, 5, 6, 7), (0, 1, 5, 4),
            (2, 3, 7, 6), (1, 2, 6, 5), (0, 3, 7, 4),
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

    def make_offset_cylinder(x, z, y_base, y_top, radius, segments):
        f = make_cylinder(y_base, y_top, radius, segments)
        for face in f:
            for vi, _, _ in face:
                ox, oy, oz = vertices[vi]
                vertices[vi] = (ox + x, oy, oz + z)
        return f

    # Board-game knight: short, wide, stable pawn-like shape
    # Wide base
    faces += make_cylinder(0.00, 0.10, 0.22, 20)
    faces += make_cylinder(0.10, 0.24, 0.20, 18)
    # Torso tapering in
    faces += make_cylinder(0.24, 0.36, 0.16, 16)
    faces += make_cylinder(0.36, 0.46, 0.12, 14)
    # Helmet dome
    faces += make_sphere(0.0, 0.54, 0.0, 0.13, 8, 16)
    # Visor slit / nasal guard
    faces += make_box(0.0, 0.52, 0.12, 0.03, 0.05, 0.02)
    # Plume crest: a vertical fin on top of helmet
    plume = make_cylinder(0.62, 0.70, 0.025, 6)
    for face in plume:
        for vi, _, _ in face:
            ox, oy, oz = vertices[vi]
            vertices[vi] = (ox, oy, oz + 0.06)
    faces += plume
    # Shield embossed on chest
    faces += make_box(0.0, 0.24, 0.13, 0.10, 0.14, 0.025)

    return vertices, normals, uvs, faces


def make_texture(name, armor_rgb, plume_rgb, size=64):
    """Create a small PNG texture: top half plume colour, bottom half armour."""
    img = Image.new("RGB", (size, size), armor_rgb)
    px = img.load()
    for y in range(size // 2, size):
        for x in range(size):
            px[x, y] = plume_rgb
    tex_path = os.path.join(OUT_DIR, f"{name}.png")
    img.save(tex_path, "PNG")
    return tex_path


def write_obj(name, vertices, normals, uvs, faces):
    """Write a single-material .obj referencing a .png texture."""
    obj_path = os.path.join(OUT_DIR, f"{name}.obj")
    mtl_path = os.path.join(OUT_DIR, f"{name}.mtl")

    with open(mtl_path, "w") as mtl:
        mtl.write("# Generated MTL for Tabletop Simulator\n")
        mtl.write(f"newmtl {name}\n")
        mtl.write("Ka 0.5 0.5 0.5\n")
        mtl.write("Kd 1.0 1.0 1.0\n")
        mtl.write("Ks 0.2 0.2 0.2\n")
        mtl.write("Ns 20\n")
        mtl.write(f"map_Kd {name}.png\n")

    with open(obj_path, "w") as obj:
        obj.write(f"# Knight model for Tabletop Simulator: {name}\n")
        obj.write(f"mtllib {os.path.basename(mtl_path)}\n")
        obj.write(f"o {name}\n")
        obj.write(f"usemtl {name}\n")
        for v in vertices:
            obj.write(f"v {v[0]:.5f} {v[1]:.5f} {v[2]:.5f}\n")
        for vt in uvs:
            obj.write(f"vt {vt[0]:.5f} {vt[1]:.5f}\n")
        for vn in normals:
            obj.write(f"vn {vn[0]:.5f} {vn[1]:.5f} {vn[2]:.5f}\n")
        for face in faces:
            parts = []
            for v_idx, u, v in face:
                parts.append(f"{v_idx + 1}/{len(parts) + 1}/{v_idx + 1}")
            obj.write("f " + " ".join(parts) + "\n")

    return obj_path, mtl_path


def main():
    variants = [
        ("french_blue_knight",  (60, 90, 170),  (255, 215, 0)),
        ("french_red_knight",   (160, 40, 40),  (255, 215, 0)),
        ("english_white_knight", (210, 210, 210), (200, 30, 30)),
        ("english_black_knight", (45, 45, 45),    (200, 30, 30)),
    ]

    vertices, normals, uvs, faces = build_knight_geometry()

    for name, armor_rgb, plume_rgb in variants:
        tex_path = make_texture(name, armor_rgb, plume_rgb)
        obj_path, mtl_path = write_obj(name, vertices, normals, uvs, faces)
        print(f"Created {obj_path}")
        print(f"Created {mtl_path}")
        print(f"Created {tex_path}")


if __name__ == "__main__":
    main()

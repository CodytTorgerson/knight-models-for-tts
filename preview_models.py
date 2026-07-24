"""Render a simple preview image of all knight OBJ models.

This is a tiny software renderer using matplotlib so we can validate the
models without installing Blender.
"""

import math
import os

import matplotlib.pyplot as plt
import numpy as np

OUT_DIR = os.path.dirname(os.path.abspath(__file__))


def load_obj(path):
    vertices = []
    faces = []
    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if line.startswith("v "):
                parts = line.split()
                vertices.append([float(parts[1]), float(parts[2]), float(parts[3])])
            elif line.startswith("f "):
                parts = line.split()
                idx = [int(p.split("/")[0]) - 1 for p in parts[1:]]
                faces.append(idx)
    return np.array(vertices, dtype=float), faces


def transform(vertices, angle_y, angle_x, scale=1.0):
    ry = math.radians(angle_y)
    rx = math.radians(angle_x)

    cy, sy = math.cos(ry), math.sin(ry)
    rot_y = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])

    cx, sx = math.cos(rx), math.sin(rx)
    rot_x = np.array([[1, 0, 0], [0, cx, -sx], [0, sx, cx]])

    v = vertices.copy()
    v = v @ rot_y.T
    v = v @ rot_x.T
    v *= scale
    return v


def render_axis(ax, vertices, faces, title, view_label, base_color):
    # Painter's algorithm: sort faces by average depth (z), draw back-to-front
    face_data = []
    for face in faces:
        pts = vertices[face]
        if len(pts) < 3:
            continue
        normal = np.cross(pts[1] - pts[0], pts[2] - pts[0])
        norm_len = np.linalg.norm(normal)
        if norm_len == 0:
            continue
        normal /= norm_len
        # Skip back-facing triangles
        if normal[2] < 0:
            continue
        avg_z = np.mean(pts[:, 2])
        face_data.append((avg_z, pts, normal))

    # Draw farthest faces first
    face_data.sort(key=lambda x: x[0], reverse=True)

    light = np.array([-0.3, -0.7, -1.0])
    light /= np.linalg.norm(light)

    for _, pts, normal in face_data:
        shade = max(0.2, np.dot(normal, light) * 0.6 + 0.4)
        r = min(1.0, base_color[0] * shade)
        g = min(1.0, base_color[1] * shade)
        b = min(1.0, base_color[2] * shade)
        xs = pts[:, 0]
        ys = pts[:, 1]
        ax.fill(xs, ys, color=(r, g, b), edgecolor="none")

    ax.set_aspect("equal")
    ax.set_title(title, fontsize=11)
    ax.set_xlabel(view_label, fontsize=9)
    ax.set_xlim(-0.5, 0.5)
    ax.set_ylim(-0.05, 1.05)
    ax.invert_yaxis()
    ax.axis("off")


def main():
    models = [
        ("french_blue_knight.obj", "French Blue", (0.24, 0.35, 0.67)),
        ("french_red_knight.obj", "French Red", (0.63, 0.16, 0.16)),
        ("english_white_knight.obj", "English White", (0.82, 0.82, 0.82)),
        ("english_black_knight.obj", "English Black", (0.18, 0.18, 0.18)),
    ]

    fig, axes = plt.subplots(len(models), 2, figsize=(8, 12))
    fig.suptitle("Knight Model Previews", fontsize=14, y=0.98)

    for row, (filename, title, base_color) in enumerate(models):
        path = os.path.join(OUT_DIR, filename)
        vertices, faces = load_obj(path)

        front = transform(vertices, angle_y=0, angle_x=0, scale=1.0)
        side = transform(vertices, angle_y=90, angle_x=0, scale=1.0)

        render_axis(axes[row, 0], front, faces, title, "Front view", base_color)
        render_axis(axes[row, 1], side, faces, title, "Side view", base_color)

    plt.tight_layout(rect=[0, 0, 1, 0.97])
    preview_path = os.path.join(OUT_DIR, "preview.png")
    plt.savefig(preview_path, dpi=150)
    print(f"Saved preview to {preview_path}")


if __name__ == "__main__":
    main()

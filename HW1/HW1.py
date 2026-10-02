import sys

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import LineCollection


def make_cube():
    """Return the cube's vertices V (8x3), edges E (12x2), and vertex labels."""
    V = np.array(
        [
            [-1, -1, -1],  # A
            [1, -1, -1],   # B
            [1, 1, -1],    # C
            [-1, 1, -1],   # D
            [-1, -1, 1],   # E
            [1, -1, 1],    # F
            [1, 1, 1],     # G
            [-1, 1, 1],    # H
        ],
        dtype=float,
    )
    E = np.array(
        [
            [0, 1], [1, 2], [2, 3], [3, 0],  # back face (z = -1)
            [4, 5], [5, 6], [6, 7], [7, 4],  # front face (z = +1)
            [0, 4], [1, 5], [2, 6], [3, 7],  # connectors
        ],
        dtype=int,
    )
    labels = list("ABCDEFGH")
    return V, E, labels


def world_to_camera(V, camera_pos):
    """Translate world-space points into camera space: p = P - c."""
    return V - np.asarray(camera_pos, dtype=float)


def project_vertices(V, camera_pos, f=1.0, near=1e-3):
    """Pinhole-project world points V (Nx3) to image-plane coordinates U (Nx2).

    u = -f * x / z,  v = -f * y / z,  where z < 0 in front of the camera.
    Depth is clamped to at most -near so we never divide by ~0 or flip
    points that sit on or behind the camera plane.
    """
    p = world_to_camera(V, camera_pos)
    z = np.minimum(p[:, 2], -near)
    return -f * p[:, :2] / z[:, None]


def plot_projection(U, E, labels, camera_pos, out="projected_cube.png"):
    """Draw the projected wireframe with labeled vertices and save it to `out`."""
    fig, ax = plt.subplots(figsize=(7, 7))

    ax.add_collection(LineCollection(U[E], colors="teal", linewidths=1.5))
    ax.scatter(U[:, 0], U[:, 1], c="crimson", zorder=3)
    for name, (u, v) in zip(labels, U):
        ax.annotate(
            f"{name} ({u:.2f}, {v:.2f})",
            (u, v),
            xytext=(4, 4),
            textcoords="offset points",
            fontweight="bold",
            fontsize=8,
        )

    ax.set_aspect("equal")
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.set_xlabel("u (Image Plane X)")
    ax.set_ylabel("v (Image Plane Y)")
    ax.set_title(f"Pinhole Perspective Projection of 3D Cube\ncamera = {tuple(camera_pos)}")
    ax.autoscale()
    ax.margins(0.1)

    fig.savefig(out, dpi=150, bbox_inches="tight")
    return fig, ax


# --- Optional (not graded): OpenGL/glfw live view ----------------------------

def draw_wireframe_gl(U, E):
    """Draw the projected edges as GL_LINES (assumes glOrtho already set up)."""
    from OpenGL.GL import GL_LINES, glBegin, glEnd, glVertex2f

    glBegin(GL_LINES)
    for u, v in U[E].reshape(-1, 2):
        glVertex2f(u, v)
    glEnd()


def run_gl(V, E, camera_pos, f=1.0, orbit=True):
    """Open a glfw window and render the wireframe, optionally orbiting the camera."""
    import glfw
    from OpenGL.GL import (
        GL_COLOR_BUFFER_BIT, GL_MODELVIEW, GL_PROJECTION,
        glClear, glClearColor, glColor3f, glLineWidth,
        glLoadIdentity, glMatrixMode, glOrtho,
    )

    if not glfw.init():
        raise RuntimeError("glfw failed to initialize")
    window = glfw.create_window(700, 700, "Cube Projection (GL_LINES)", None, None)
    if not window:
        glfw.terminate()
        raise RuntimeError("glfw failed to create a window")
    glfw.make_context_current(window)

    c0 = np.asarray(camera_pos, dtype=float)
    radius = np.hypot(c0[0], c0[2])
    angle0 = np.arctan2(c0[0], c0[2])

    glClearColor(1, 1, 1, 1)
    glLineWidth(2)
    while not glfw.window_should_close(window):
        if orbit:
            a = angle0 + 0.5 * glfw.get_time()
            c = np.array([radius * np.sin(a), c0[1], radius * np.cos(a)])
        else:
            c = c0
        U = project_vertices(V, c, f=f)

        # Fit the view to the projected points, keeping a square aspect.
        center = (U.min(axis=0) + U.max(axis=0)) / 2
        half = (U.max(axis=0) - U.min(axis=0)).max() / 2 * 1.2 + 1e-6
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(center[0] - half, center[0] + half, center[1] - half, center[1] + half, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        glClear(GL_COLOR_BUFFER_BIT)
        glColor3f(0.0, 0.5, 0.5)
        draw_wireframe_gl(U, E)

        glfw.swap_buffers(window)
        glfw.poll_events()

    glfw.terminate()


def main():
    V, E, labels = make_cube()

    camera_pos = (0, 1, 6)
    U = project_vertices(V, camera_pos)
    for name, (u, v) in zip(labels, U):
        print(f"{name}: ({u:+.3f}, {v:+.3f})")
    plot_projection(U, E, labels, camera_pos)

    if "--gl" in sys.argv:
        run_gl(V, E, camera_pos)


if __name__ == "__main__":
    main()

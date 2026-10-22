#This is the starter code for HW2_A. We need to perform the "TODO" parts of this code. 

import ctypes

import glfw
import numpy as np
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader


# ---------------------------------------------------------
# 1. Initialize GLFW
# ---------------------------------------------------------

if not glfw.init():
    raise Exception("GLFW could not be initialized")


# Request OpenGL 3.3 Core Profile
glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

# Needed on macOS
glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, GL_TRUE)


# ---------------------------------------------------------
# TODO 1:
# Create an 800 x 600 window.
# Change "Your Name" to your actual name.
# ---------------------------------------------------------

window = glfw.create_window(
    800,
    600,
    "HW2: Intro to Shaders - Noah Crouch",
    None,
    None
)

if not window:
    glfw.terminate()
    raise Exception("GLFW window could not be created")

glfw.make_context_current(window)


# ---------------------------------------------------------
# 2. GLSL Vertex Shader
# ---------------------------------------------------------

vertex_shader = """
#version 330 core

layout (location = 0) in vec3 aPos;
layout (location = 1) in vec3 aColor;

out vec3 vColor;

void main()
{
    gl_Position = vec4(aPos, 1.0);
    vColor = aColor;
}
"""


# ---------------------------------------------------------
# 3. GLSL Fragment Shader
# ---------------------------------------------------------

fragment_shader = """
#version 330 core

in vec3 vColor;

out vec4 FragColor;

void main()
{
    FragColor = vec4(vColor, 1.0);
}
"""


# ---------------------------------------------------------
# 4. Compile and link shaders
# ---------------------------------------------------------

# validate=False: on macOS Core Profile, glValidateProgram fails
# because no VAO is bound yet at this point.
shader_program = compileProgram(
    compileShader(vertex_shader, GL_VERTEX_SHADER),
    compileShader(fragment_shader, GL_FRAGMENT_SHADER),
    validate=False
)


# ---------------------------------------------------------
# 5. Vertex Data
#
# Each vertex contains:
#
#       x, y, z, r, g, b
#
# TODO 2:
# Define three vertices:
#
#   Bottom-left  -> Red
#   Bottom-right -> Green
#   Top-center   -> Blue
#
# Choose coordinates that place the triangle clearly
# inside the window.
# ---------------------------------------------------------

vertices = np.array([

    # Position                 # Color
    # x      y      z          r      g      b

    -0.6,  -0.5,   0.0,       1.0,   0.0,   0.0,   # Bottom-left  -> Red
     0.6,  -0.5,   0.0,       0.0,   1.0,   0.0,   # Bottom-right -> Green
     0.0,   0.6,   0.0,       0.0,   0.0,   1.0,   # Top-center   -> Blue

], dtype=np.float32)


# ---------------------------------------------------------
# 6. Create VAO and VBO
# ---------------------------------------------------------

VAO = glGenVertexArrays(1)
VBO = glGenBuffers(1)

glBindVertexArray(VAO)

glBindBuffer(GL_ARRAY_BUFFER, VBO)


# ---------------------------------------------------------
# TODO 3:
# Upload the vertex array to the GPU using glBufferData.
#
# Hint:
# The buffer target is GL_ARRAY_BUFFER.
# The data should not normally change after being uploaded.
# ---------------------------------------------------------

glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)


# ---------------------------------------------------------
# 7. Configure Vertex Attributes
#
# Each vertex contains 6 floats:
#
#     3 position floats
#     3 color floats
#
# A float occupies 4 bytes.
# ---------------------------------------------------------

stride = 6 * 4


# ---------------------------------------------------------
# TODO 4:
# Configure attribute location 0 for POSITION.
#
# Position contains:
#     3 floats
#     starts at byte offset 0
# ---------------------------------------------------------

glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(0))
glEnableVertexAttribArray(0)


# ---------------------------------------------------------
# TODO 5:
# Configure attribute location 1 for COLOR.
#
# Color contains:
#     3 floats
#     starts after the 3 position floats
# ---------------------------------------------------------

glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(3 * 4))
glEnableVertexAttribArray(1)


# Unbind
glBindBuffer(GL_ARRAY_BUFFER, 0)
glBindVertexArray(0)


# ---------------------------------------------------------
# 8. Render Loop
# ---------------------------------------------------------

while not glfw.window_should_close(window):

    glfw.poll_events()

    # -----------------------------------------------------
    # TODO 6:
    # Choose ONE background color:
    #
    # Dark:
    # glClearColor(0.1, 0.1, 0.1, 1.0)
    #
    # OR
    #
    # Light:
    # glClearColor(0.8, 0.8, 0.8, 1.0)
    # -----------------------------------------------------

    glClearColor(0.1, 0.1, 0.1, 1.0)

    glClear(GL_COLOR_BUFFER_BIT)

    # Activate shader program
    glUseProgram(shader_program)

    # Bind VAO
    glBindVertexArray(VAO)

    # Draw the triangle
    glDrawArrays(GL_TRIANGLES, 0, 3)

    # Swap front and back buffers
    glfw.swap_buffers(window)


# ---------------------------------------------------------
# 9. Cleanup
# ---------------------------------------------------------

glDeleteVertexArrays(1, [VAO])
glDeleteBuffers(1, [VBO])
glDeleteProgram(shader_program)

glfw.terminate()
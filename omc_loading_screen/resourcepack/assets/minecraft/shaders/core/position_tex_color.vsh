#version 150

uniform sampler2D Sampler0;

in vec3 Position;
in vec2 UV0;
in vec4 Color;

uniform mat4 ModelViewMat;
uniform mat4 ProjMat;

out vec2 texCoord0;
out vec4 vertexColor;

void main() {
    gl_Position = ProjMat * ModelViewMat * vec4(Position, 1.0);

    texCoord0 = UV0;
    vertexColor = Color;
    if(texelFetch(Sampler0, ivec2(267, 146), 0) == vec4(1)) { // Mojang logo check
        gl_Position = vec4(2.0, 2.0, 2.0, 1.0); // Move the vertex out of view
    }
}

#version 150

in vec3 Position;
in vec4 Color;

uniform mat4 ModelViewMat;
uniform mat4 ProjMat;

out vec4 vertexColor;
out vec3 pos;

void main() {
    gl_Position = ProjMat * ModelViewMat * vec4(Position, 1.0);

    vertexColor = Color;
    if (Color.rgb == vec3(239/255.0, 50/255.0, 61/255.0) && (gl_Position.x == -1.0 || gl_Position.x >= 0.9999) && (gl_Position.y <= -0.9999 || gl_Position.y == 1.0)) {
        // Background color
        vertexColor.rgb = vec3(43/255.0, 42/255.0, 63/255.0);
    } else if (
        Color.rgb == vec3(1.0) && 
        (gl_Position.x <= 0.7 && gl_Position.x >= -0.7) &&
        (gl_Position.y <= -0.5 && gl_Position.y >= -0.75)
    ) { // Checks to ensure we are only changing the color of the loading bar.
        // It is not a perfect check, but it mostly works detecting if it's not something else.
        // Loading bar
        vertexColor.rgb = vec3(243/255.0, 111/255.0, 155/255.0);
    }
    pos = Position;
}

#version 150

/*
 Code inspired by https://non0reo.github.io/ImgToShader/
*/

#define WIDTH 960
#define HEIGHT 540

in vec4 vertexColor;
in vec3 pos;

uniform vec4 ColorModulator;
uniform mat4 ProjMat;
uniform vec2 ScreenSize;

out vec4 fragColor;

#moj_import <loading_screen_utils.glsl>
#moj_import <image/logo_openmc_right.glsl>
#moj_import <image/logo_openmc_left.glsl>

ivec2 imageSize = ivec2(WIDTH, HEIGHT);

void main() {
    
    vec4 color = vertexColor;
    if (color.a == 0.0) {
        discard;
    }
    if (color.rgb == vec3(43/255.0, 42/255.0, 63/255.0)) {
        // Background
        vec2 RealSSize = getScreenSize(ProjMat, ScreenSize);
        vec2 pixelUnit = RealSSize / imageSize;
        ivec2 RealPixelPos = getPixelPos(pixelUnit, pos.xy);
        vec3 newColorRight = pColorRight(RealPixelPos, imageSize);
        if (newColorRight != vec3(-1)) {
            fragColor = vec4(newColorRight/255.0, color.a) * ColorModulator;
            return;
        }
        vec3 newColorLeft = pColorLeft(RealPixelPos - ivec2(1, 0), imageSize);
        if (newColorLeft != vec3(-1)) {
            fragColor = vec4(newColorLeft/255.0, color.a) * ColorModulator;
            return;
        }
    }
    fragColor = color * ColorModulator;
}

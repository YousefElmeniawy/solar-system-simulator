#version 330 core
layout(location=0) in vec3 aPosition;
uniform mat4 uModel; uniform mat4 uView; uniform mat4 uProjection;
out vec3 vWorldPos; out vec3 vNormal;
void main(){
    vec4 world = uModel * vec4(aPosition,1.0);
    vWorldPos = world.xyz;
    // Inverse-transpose normal matrix preserves normals under non-uniform scaling.
    vNormal = mat3(transpose(inverse(uModel))) * aPosition;
    gl_Position = uProjection * uView * world;
}

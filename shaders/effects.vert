#version 330 core
layout(location=0) in vec3 aPosition;
layout(location=1) in vec3 aColor;
layout(location=2) in float aSize;
uniform mat4 uView; uniform mat4 uProjection; uniform mat4 uModel;
out vec3 vColor; out float vAlpha;
void main(){
    vec4 world=uModel*vec4(aPosition,1.0); vec4 viewPos=uView*world;
    gl_Position=uProjection*viewPos; gl_PointSize=clamp(aSize*180.0/max(1.0,-viewPos.z),1.0,6.0);
    vColor=aColor; vAlpha=1.0;
}

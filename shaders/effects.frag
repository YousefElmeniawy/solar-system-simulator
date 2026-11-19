#version 330 core
in vec3 vColor; in float vAlpha; uniform int uRoundPoint; uniform float uGlobalAlpha; out vec4 FragColor;
void main(){
    float a=uGlobalAlpha*vAlpha;
    if(uRoundPoint==1){ vec2 d=gl_PointCoord-vec2(0.5); float r=length(d); if(r>0.5) discard; a*=smoothstep(0.5,0.08,r); }
    FragColor=vec4(vColor,a);
}

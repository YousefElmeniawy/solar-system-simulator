#version 330 core
in vec3 vWorldPos; in vec3 vNormal;
uniform vec3 uColor; uniform vec3 uCameraPos; uniform vec3 uLightPos;
uniform int uEmissive; uniform int uLighting;
out vec4 FragColor;
void main(){
    if(uEmissive==1){ FragColor=vec4(uColor,1.0); return; }
    if(uLighting==0){ FragColor=vec4(uColor,1.0); return; }
    vec3 N=normalize(vNormal); vec3 L=normalize(uLightPos-vWorldPos); vec3 V=normalize(uCameraPos-vWorldPos);
    // Ambient + Lambert diffuse + Blinn-Phong specular.
    float diff=max(dot(N,L),0.0); vec3 H=normalize(L+V);
    float spec=pow(max(dot(N,H),0.0),32.0)*0.22;
    float attenuation=1.0/(1.0+0.006*dot(uLightPos-vWorldPos,uLightPos-vWorldPos));
    vec3 lit=uColor*(0.25+attenuation*diff*0.92)+vec3(spec*attenuation);
    FragColor=vec4(lit,1.0);
}

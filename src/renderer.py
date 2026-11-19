"""OpenGL 3.3 renderer: static mesh/VBO pipeline, Phong materials and effects."""
from __future__ import annotations
from pathlib import Path
import ctypes, math
import numpy as np
import pygame
from OpenGL.GL import *
from .mesh import uv_sphere, ring_mesh, orbit_line
from .math3d import identity, translation, rotation_y, rotation_z
from .planet_data import PLANETS

ROOT=Path(__file__).resolve().parent.parent

def _shader(path): return (ROOT/'shaders'/path).read_text(encoding='utf-8')
def _program(vs,fs):
    program=glCreateProgram(); shaders=[]
    for typ,src in ((GL_VERTEX_SHADER,vs),(GL_FRAGMENT_SHADER,fs)):
        sh=glCreateShader(typ); glShaderSource(sh,src); glCompileShader(sh)
        if not glGetShaderiv(sh,GL_COMPILE_STATUS):
            log=glGetShaderInfoLog(sh).decode('utf8','replace'); raise RuntimeError(f'Shader compile failed: {log}')
        glAttachShader(program,sh); shaders.append(sh)
    glLinkProgram(program)
    if not glGetProgramiv(program,GL_LINK_STATUS): raise RuntimeError('Shader link failed: '+glGetProgramInfoLog(program).decode('utf8','replace'))
    for sh in shaders: glDeleteShader(sh)
    return program

def _uniform(program,name): return glGetUniformLocation(program,name)
def _mat(program,name,value):
    glUniformMatrix4fv(_uniform(program,name),1,GL_TRUE,np.asarray(value,dtype=np.float32))
def _make_vao(data, usage=GL_STATIC_DRAW):
    data=np.ascontiguousarray(data,dtype=np.float32)
    vao=glGenVertexArrays(1); buf=glGenBuffers(1); glBindVertexArray(vao); glBindBuffer(GL_ARRAY_BUFFER,buf)
    glBufferData(GL_ARRAY_BUFFER,data.nbytes,data,usage); glEnableVertexAttribArray(0); glVertexAttribPointer(0,3,GL_FLOAT,GL_FALSE,0,None)
    glBindVertexArray(0); return vao,buf,len(data)

class Renderer:
    def __init__(self,width,height):
        self.width,self.height=width,height
        self.planet_program=_program(_shader('planet.vert'),_shader('planet.frag'))
        self.effect_program=_program(_shader('effects.vert'),_shader('effects.frag'))
        self.sphere_vao,self.sphere_vbo,self.sphere_count=_make_vao(uv_sphere())
        self.ring_vao,self.ring_vbo,self.ring_count=_make_vao(ring_mesh())
        self.orbits={p.key:_make_vao(orbit_line(p.orbit_radius))[0:3] for p in PLANETS}
        self.star_vao,self.star_vbo,self.star_count=self._create_stars(1500)
        self.particle_vao=glGenVertexArrays(1); self.particle_vbo=glGenBuffers(1); self.particle_count=0
        glBindVertexArray(self.particle_vao); glBindBuffer(GL_ARRAY_BUFFER,self.particle_vbo)
        stride=7*4
        for idx,size,offset in ((0,3,0),(1,3,12),(2,1,24)):
            glEnableVertexAttribArray(idx); glVertexAttribPointer(idx,size,GL_FLOAT,GL_FALSE,stride,ctypes.c_void_p(offset))
        glBindVertexArray(0)
        self.line_vao,self.line_vbo,_=_make_vao(np.zeros((2,3),dtype=np.float32),GL_DYNAMIC_DRAW)
        self.hud_program=self._make_hud_program(); self.hud_vao,self.hud_vbo=self._make_hud_quad()
        self.hud_texture=glGenTextures(1); glBindTexture(GL_TEXTURE_2D,self.hud_texture)
        glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER,GL_LINEAR); glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,GL_LINEAR)
        self.ui_surface=pygame.Surface((width,height),pygame.SRCALPHA,32)
        glEnable(GL_DEPTH_TEST); glDepthFunc(GL_LEQUAL); glEnable(GL_CULL_FACE); glCullFace(GL_BACK); glFrontFace(GL_CCW)
        glEnable(GL_PROGRAM_POINT_SIZE); glClearColor(.008,.012,.028,1.0)

    def _create_stars(self,count):
        rng=np.random.default_rng(42); d=rng.normal(size=(count,3)); d/=np.linalg.norm(d,axis=1,keepdims=True)
        r=rng.uniform(52,112,(count,1)); pos=d*r
        cols=rng.choice(np.array([[.63,.75,1.0],[1.0,.83,.65],[.82,.90,1.0],[1,1,1]],dtype=np.float32),size=count)
        size=rng.uniform(0.8,1.9,(count,1)).astype(np.float32)
        data=np.ascontiguousarray(np.concatenate((pos.astype(np.float32),cols,size),axis=1))
        vao=glGenVertexArrays(1); vbo=glGenBuffers(1); glBindVertexArray(vao); glBindBuffer(GL_ARRAY_BUFFER,vbo); glBufferData(GL_ARRAY_BUFFER,data.nbytes,data,GL_STATIC_DRAW)
        stride=7*4
        for idx,n,offset in ((0,3,0),(1,3,12),(2,1,24)):
            glEnableVertexAttribArray(idx); glVertexAttribPointer(idx,n,GL_FLOAT,GL_FALSE,stride,ctypes.c_void_p(offset))
        glBindVertexArray(0); return vao,vbo,count

    def _make_hud_program(self):
        vs='''#version 330 core\nlayout(location=0) in vec2 p; layout(location=1) in vec2 t; out vec2 uv; void main(){uv=t;gl_Position=vec4(p,0,1);}'''
        fs='''#version 330 core\nin vec2 uv; uniform sampler2D image; out vec4 color; void main(){color=texture(image,uv);}'''
        return _program(vs,fs)
    def _make_hud_quad(self):
        data=np.array([[-1,-1,0,0],[1,-1,1,0],[1,1,1,1],[-1,-1,0,0],[1,1,1,1],[-1,1,0,1]],dtype=np.float32)
        vao=glGenVertexArrays(1); vbo=glGenBuffers(1); glBindVertexArray(vao); glBindBuffer(GL_ARRAY_BUFFER,vbo); glBufferData(GL_ARRAY_BUFFER,data.nbytes,data,GL_STATIC_DRAW)
        glEnableVertexAttribArray(0); glVertexAttribPointer(0,2,GL_FLOAT,GL_FALSE,16,None); glEnableVertexAttribArray(1); glVertexAttribPointer(1,2,GL_FLOAT,GL_FALSE,16,ctypes.c_void_p(8)); glBindVertexArray(0)
        return vao,vbo

    def resize(self,w,h):
        self.width=max(1,w); self.height=max(1,h); glViewport(0,0,self.width,self.height)
        self.ui_surface=pygame.Surface((self.width,self.height),pygame.SRCALPHA,32)
    def _draw_lines(self,vertices,view,projection,color,width=1.0,mode=GL_LINES):
        a=np.ascontiguousarray(vertices,dtype=np.float32); glUseProgram(self.effect_program)
        _mat(self.effect_program,'uModel',identity()); _mat(self.effect_program,'uView',view); _mat(self.effect_program,'uProjection',projection)
        glUniform1i(_uniform(self.effect_program,'uRoundPoint'),0); glUniform1f(_uniform(self.effect_program,'uGlobalAlpha'),color[3] if len(color)>3 else 1.0)
        # Effect shader consumes a per-vertex color; supply a temporary interleaved buffer for lines.
        data=np.empty((len(a),7),dtype=np.float32); data[:,:3]=a; data[:,3:6]=color[:3]; data[:,6]=1.0
        vao=glGenVertexArrays(1); vbo=glGenBuffers(1); glBindVertexArray(vao); glBindBuffer(GL_ARRAY_BUFFER,vbo); glBufferData(GL_ARRAY_BUFFER,data.nbytes,data,GL_STREAM_DRAW)
        stride=28
        for idx,n,off in ((0,3,0),(1,3,12),(2,1,24)):
            glEnableVertexAttribArray(idx); glVertexAttribPointer(idx,n,GL_FLOAT,GL_FALSE,stride,ctypes.c_void_p(off))
        glLineWidth(width); glDrawArrays(mode,0,len(a)); glDeleteBuffers(1,[vbo]); glDeleteVertexArrays(1,[vao]); glBindVertexArray(0)

    def _draw_points(self,vao,count,view,projection,model=identity(),alpha=1.0):
        glUseProgram(self.effect_program); _mat(self.effect_program,'uModel',model); _mat(self.effect_program,'uView',view); _mat(self.effect_program,'uProjection',projection)
        glUniform1i(_uniform(self.effect_program,'uRoundPoint'),1); glUniform1f(_uniform(self.effect_program,'uGlobalAlpha'),alpha)
        glBindVertexArray(vao); glDrawArrays(GL_POINTS,0,count); glBindVertexArray(0)

    def render(self,bodies,view,projection,camera_pos,stars,orbits,labels,particles_enabled,particle_system,lighting=True):
        glViewport(0,0,self.width,self.height); glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
        if stars:
            glDepthMask(GL_FALSE); self._draw_points(self.star_vao,self.star_count,view,projection); glDepthMask(GL_TRUE)
        if orbits:
            glEnable(GL_BLEND); glBlendFunc(GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA)
            for key,(vao,vbo,count) in self.orbits.items():
                glUseProgram(self.effect_program); _mat(self.effect_program,'uModel',identity()); _mat(self.effect_program,'uView',view); _mat(self.effect_program,'uProjection',projection)
                glUniform1i(_uniform(self.effect_program,'uRoundPoint'),0); glUniform1f(_uniform(self.effect_program,'uGlobalAlpha'),.52)
                glVertexAttrib3f(1,.30,.48,.72)
                glBindVertexArray(vao); glLineWidth(1.0); glDrawArrays(GL_LINE_STRIP,0,count); glBindVertexArray(0)
            glDisable(GL_BLEND)
        # Opaque bodies use the material shader; Saturn's annular child uses a dedicated mesh.
        glUseProgram(self.planet_program); _mat(self.planet_program,'uView',view); _mat(self.planet_program,'uProjection',projection)
        glUniform3f(_uniform(self.planet_program,'uLightPos'),0,0,0); glUniform3f(_uniform(self.planet_program,'uCameraPos'),*map(float,camera_pos)); glUniform1i(_uniform(self.planet_program,'uLighting'),int(lighting))
        for body in bodies:
            if body.key=='saturn_rings':
                glDisable(GL_CULL_FACE); _mat(self.planet_program,'uModel',body.model); glUniform3f(_uniform(self.planet_program,'uColor'),*body.color); glUniform1i(_uniform(self.planet_program,'uEmissive'),1)
                glBindVertexArray(self.ring_vao); glDrawArrays(GL_TRIANGLES,0,self.ring_count); glEnable(GL_CULL_FACE); continue
            _mat(self.planet_program,'uModel',body.model); col=body.color
            if body.selected: col=tuple(min(1.0,c*1.25+.12) for c in col)
            glUniform3f(_uniform(self.planet_program,'uColor'),*col); glUniform1i(_uniform(self.planet_program,'uEmissive'),int(body.emissive))
            glBindVertexArray(self.sphere_vao); glDrawArrays(GL_TRIANGLES,0,self.sphere_count)
        glBindVertexArray(0)
        if particles_enabled and particle_system:
            positions,colors,alpha,sizes=particle_system.drawable()
            packed=np.concatenate((positions,colors*alpha[:,None],sizes[:,None]),axis=1).astype(np.float32)
            glBindBuffer(GL_ARRAY_BUFFER,self.particle_vbo); glBufferData(GL_ARRAY_BUFFER,packed.nbytes,packed,GL_STREAM_DRAW)
            # Particle points fade in by their alpha through per-particle color intensity.
            self._draw_points(self.particle_vao,len(packed),view,projection)
        return self._project_bodies(bodies,view,projection) if labels else {}

    def _project_bodies(self,bodies,view,projection):
        out={}; vp=projection@view
        for b in bodies:
            if b.key in ('saturn_rings',): continue
            q=vp@np.array([*b.world_position,1.0]);
            if q[3]<=0: continue
            ndc=q[:3]/q[3]; sx=int((ndc[0]*.5+.5)*self.width); sy=int((1-(ndc[1]*.5+.5))*self.height)
            if -30<sx<self.width+30 and -30<sy<self.height+30: out[b.key]=(sx,sy)
        return out

    def draw_hud(self,surface):
        raw=pygame.image.tostring(surface,'RGBA',True); glBindTexture(GL_TEXTURE_2D,self.hud_texture)
        glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA,self.width,self.height,0,GL_RGBA,GL_UNSIGNED_BYTE,raw)
        glDisable(GL_DEPTH_TEST); glEnable(GL_BLEND); glBlendFunc(GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA)
        glUseProgram(self.hud_program); glUniform1i(_uniform(self.hud_program,'image'),0); glActiveTexture(GL_TEXTURE0); glBindTexture(GL_TEXTURE_2D,self.hud_texture)
        glBindVertexArray(self.hud_vao); glDrawArrays(GL_TRIANGLES,0,6); glBindVertexArray(0)
        glDisable(GL_BLEND); glEnable(GL_DEPTH_TEST)

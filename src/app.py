"""Main application loop, input routing and interaction state."""
from __future__ import annotations
import math, sys, time
import pygame
from OpenGL.GL import *
from .animation import SimulationClock
from .camera import OrbitCamera
from .particles import SolarWind
from .planet_data import PLANETS, BY_KEY
from .renderer import Renderer
from .scene import SolarScene
from .ui import HUD

WIDTH,HEIGHT=1440,900

def run():
    pygame.init(); pygame.display.set_caption('Interactive 3D Solar System Simulator | IT311')
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION,3)
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION,3)
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_PROFILE_MASK,pygame.GL_CONTEXT_PROFILE_CORE)
    pygame.display.gl_set_attribute(pygame.GL_DOUBLEBUFFER,1); pygame.display.gl_set_attribute(pygame.GL_DEPTH_SIZE,24)
    try:
        screen=pygame.display.set_mode((WIDTH,HEIGHT),pygame.OPENGL|pygame.DOUBLEBUF|pygame.RESIZABLE)
    except pygame.error as e:
        pygame.quit(); raise SystemExit('Could not create an OpenGL 3.3 window. Install a current graphics driver and ensure OpenGL 3.3 Core is available.\n'+str(e))
    try: renderer=Renderer(WIDTH,HEIGHT)
    except Exception as e:
        pygame.quit(); raise SystemExit(f'OpenGL renderer initialization failed: {e}')
    clock=pygame.time.Clock(); sim=SimulationClock(); camera=OrbitCamera(); scene=SolarScene(); wind=SolarWind(); hud=HUD()
    selected='earth'; flags={'orbits':True,'stars':True,'labels':True,'particles':False}; lighting=True
    dragging=False; last_mouse=(0,0); running=True; last_positions={}; fps=60.0

    def focus_selected():
        body=next((b for b in scene.bodies(sim.days,selected) if b.key==selected),None)
        if body: camera.focus(body.world_position,max(4.0,body.radius*7.5))

    def select_body(key):
        nonlocal selected
        selected=key

    while running:
        dt=min(clock.tick(120)/1000.0,.1); fps=clock.get_fps() or fps
        sim.update(dt); wind.update(dt,sim.speed if not sim.paused else 0.0)
        bodies=scene.bodies(sim.days,selected)
        view=camera.view_matrix(); projection=camera.projection_matrix(renderer.width,renderer.height)
        label_positions=renderer.render(bodies,view,projection,camera.eye,flags['stars'],flags['orbits'],flags['labels'],flags['particles'],wind,lighting)
        # The HUD draws on a same-sized transparent surface, then the renderer composites it.
        if renderer.ui_surface.get_size()!=(renderer.width,renderer.height): renderer.ui_surface=pygame.Surface((renderer.width,renderer.height),pygame.SRCALPHA,32)
        hud.draw(renderer.ui_surface,selected,sim,sim.paused,'Orthographic' if camera.orthographic_mode else 'Perspective',flags,fps,
                 f'eye=({camera.eye[0]:.1f},{camera.eye[1]:.1f},{camera.eye[2]:.1f})',label_positions)
        renderer.draw_hud(renderer.ui_surface); pygame.display.flip()

        for event in pygame.event.get():
            if event.type==pygame.QUIT: running=False
            elif event.type==pygame.VIDEORESIZE:
                screen=pygame.display.set_mode(event.size,pygame.OPENGL|pygame.DOUBLEBUF|pygame.RESIZABLE); renderer.resize(*event.size)
            elif event.type==pygame.MOUSEBUTTONDOWN:
                if event.button==1:
                    # Nearest projected body under pointer acts as an accessible mouse picker.
                    hits=[]
                    for key,(px,py) in label_positions.items():
                        d=math.hypot(event.pos[0]-px,event.pos[1]-py)
                        if d<34: hits.append((d,key))
                    if hits: select_body(min(hits)[1])
                    else: dragging=True; last_mouse=event.pos
                elif event.button==4: camera.zoom(1)
                elif event.button==5: camera.zoom(-1)
            elif event.type==pygame.MOUSEBUTTONUP and event.button==1: dragging=False
            elif event.type==pygame.MOUSEMOTION and dragging:
                dx=event.pos[0]-last_mouse[0]; dy=event.pos[1]-last_mouse[1]; camera.orbit(dx,dy); last_mouse=event.pos
            elif event.type==pygame.MOUSEWHEEL: camera.zoom(event.y)
            elif event.type==pygame.KEYDOWN:
                k=event.key
                if k==pygame.K_ESCAPE: running=False
                elif k==pygame.K_SPACE: sim.toggle_pause()
                elif k in (pygame.K_PLUS,pygame.K_EQUALS,pygame.K_KP_PLUS): sim.change_speed(1)
                elif k in (pygame.K_MINUS,pygame.K_KP_MINUS): sim.change_speed(-1)
                elif k==pygame.K_0: sim.reset()
                elif pygame.K_1<=k<=pygame.K_8: select_body(PLANETS[k-pygame.K_1].key)
                elif k==pygame.K_RIGHT:
                    idx=next((i for i,p in enumerate(PLANETS) if p.key==selected),-1); select_body(PLANETS[(idx+1)%len(PLANETS)].key)
                elif k==pygame.K_LEFT:
                    idx=next((i for i,p in enumerate(PLANETS) if p.key==selected),0); select_body(PLANETS[(idx-1)%len(PLANETS)].key)
                elif k==pygame.K_f: focus_selected()
                elif k==pygame.K_b: camera.focus((0,0,0),38.0)
                elif k==pygame.K_r: camera.reset()
                elif k==pygame.K_v: camera.orthographic_mode=not camera.orthographic_mode
                elif k==pygame.K_o: flags['orbits']=not flags['orbits']
                elif k==pygame.K_s: flags['stars']=not flags['stars']
                elif k==pygame.K_n: flags['labels']=not flags['labels']
                elif k==pygame.K_p: flags['particles']=not flags['particles']
                elif k==pygame.K_g: lighting=not lighting
                elif k==pygame.K_SLASH or k==pygame.K_QUESTION: hud.help_visible=not hud.help_visible
    pygame.quit()
    return 0

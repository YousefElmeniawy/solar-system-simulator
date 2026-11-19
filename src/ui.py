"""Compact Pygame HUD composited over the OpenGL scene; no side control panel."""
from __future__ import annotations
import pygame
from .planet_data import BY_KEY

BG=(9,15,30,230); LINE=(48,69,100,220); TEXT=(232,240,252); MUTED=(151,170,199); CYAN=(83,204,226)

class HUD:
    def __init__(self):
        self.small=pygame.font.Font(None,18)
        self.title=pygame.font.Font(None,31)
        self.help_visible=False

    def _text(self,surface,text,pos,font=None,color=TEXT):
        surface.blit((font or self.small).render(str(text),True,color),pos)

    def _panel(self,surface,rect,color=BG,radius=12):
        pygame.draw.rect(surface,color,rect,border_radius=radius)
        pygame.draw.rect(surface,LINE,rect,1,border_radius=radius)

    def draw(self,surface,selected_key,clock,paused,projection,flags,fps,camera_text,label_positions=None):
        w,h=surface.get_size()
        surface.fill((0,0,0,0))
        # Compact title and simulation status only; Mission Control has been removed.
        self._panel(surface,pygame.Rect(20,18,min(520,w-40),66))
        self._text(surface,'SOLAR SYSTEM  /  IT311',(38,28),self.title)
        self._text(surface,'Interactive 3D simulator  •  Visual scale, not to scale',(40,55),self.small,MUTED)
        eye=camera_text.replace('eye=','eye ') if camera_text else ''
        status=f"DAY {clock.days:,.1f}   {'PAUSED' if paused else 'RUNNING'}   {clock.speed:g}x ({clock.days_per_second*clock.speed:g} d/s)   {projection}   FPS {fps:.0f}   {eye}"
        self._panel(surface,pygame.Rect(20,92,min(850,w-40),37),radius=10)
        self._text(surface,status,(34,101),self.small,CYAN)
        # Body labels remain available independently of the removed side panel.
        if flags.get('labels',True):
            for key,(x,y) in (label_positions or {}).items():
                if key in ('moon','sun'):
                    continue
                name=BY_KEY[key].name if key in BY_KEY else key.title()
                self._text(surface,name,(x+7,y-18),self.small,(220,235,255))
        self._panel(surface,pygame.Rect(20,h-72,min(650,w-40),52),radius=10)
        self._text(surface,'SPACE pause  |  - / + speed  |  drag orbit  |  wheel zoom  |  V projection  |  ? help',(34,h-61),self.small,TEXT)
        if self.help_visible:
            rect=pygame.Rect(max(20,w//2-260),max(100,h//2-180),520,360)
            self._panel(surface,rect,(10,17,32,248),16)
            self._text(surface,'KEYBOARD & MOUSE',(rect.x+24,rect.y+22),self.title,CYAN)
            lines=[
                '1–8 select planet     Left / Right previous / next',
                'F focus selection     B return to full-system view',
                'SPACE pause / resume     - / + change simulation speed',
                '0 reset simulation day     R reset camera',
                'V switch perspective / orthographic projection',
                'O orbits     S stars     N labels     P solar-wind particles',
                'G toggle lighting',
                'Drag mouse orbit camera     Scroll to zoom',
                '? show / hide help     ESC quit',
            ]
            y=rect.y+68
            for line in lines:
                self._text(surface,line,(rect.x+24,y),self.small,TEXT)
                y+=27

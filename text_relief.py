"""Readable raised lettering for all Kivy Labels and Buttons."""
from kivy.clock import Clock
from kivy.core.text import Label as CoreLabel
from kivy.graphics import Color, Rectangle
from kivy.metrics import dp, sp
from kivy.uix.button import Button

def enlarge(value):
    return sp(float(value[:-2]))*1.10 if isinstance(value,str) and value.endswith('sp') else float(value)*1.10

def relief(widget):
    if getattr(widget,'_relief',None): return widget
    widget._relief=TextRelief(widget)
    return widget

class TextRelief:
    def __init__(self,widget):
        self.widget=widget
        self.target_size=widget.font_size
        self.fitting=False
        self.update=Clock.create_trigger(self.refresh,0)
        with widget.canvas.after:
            Color(.10,.08,.27,.92)
            self.depth2=Rectangle(size=(0,0))
            Color(.22,.13,.42,.94)
            self.depth=Rectangle(size=(0,0))
            Color(1,.82,.31,.98)
            self.edge=Rectangle(size=(0,0))
            Color(1,1,.96,.92)
            self.bevel=Rectangle(size=(0,0))
            Color(1,1,1,1)
            self.face=Rectangle(size=(0,0))
        widget.bind(texture=self.update,size=self.update,text=self.update,
                    text_size=self.update,font_name=self.update,bold=self.update,
                    font_size=self.font_changed,pos=self.position,color=self.update)
        self.update()
    def font_changed(self,widget,value):
        if not self.fitting: self.target_size=value
        self.update()
    def fit(self):
        w=self.widget
        if w.width<=dp(10) or w.height<=dp(10) or not w.text: return
        width=max(dp(1),(w.text_size[0] or w.width)-dp(8))
        height=max(dp(1),min(w.height,w.text_size[1] or w.height)-dp(7))
        size=self.target_size
        minimum=min(size,max(sp(10),size*.60))
        for _ in range(90):
            probe=CoreLabel(text=w.text,font_name=w.font_name,font_size=size,
                bold=w.bold,italic=w.italic,
                text_size=(None if isinstance(w,Button) else width,None),
                line_height=w.line_height)
            probe.refresh()
            if (probe.texture.height<=height and
                (not isinstance(w,Button) or probe.texture.width<=width)) or size<=minimum: break
            size=max(minimum,size-sp(.5))
        if abs(w.font_size-size)>.01:
            self.fitting=True;w.font_size=size;self.fitting=False
    def refresh(self,*_):
        w=self.widget
        if w.texture is None or not w.text:
            for rect in (self.depth2,self.depth,self.edge,self.bevel,self.face): rect.size=(0,0)
            return
        self.fit()
        mask=CoreLabel(text=w.text,font_name=w.font_name,font_size=w.font_size,
            bold=w.bold,italic=w.italic,text_size=w.text_size,
            halign=w.halign,valign=w.valign,padding=w.padding,
            line_height=w.line_height,color=(1,1,1,1))
        mask.refresh()
        for rect in (self.depth2,self.depth,self.edge,self.bevel):
            rect.texture=mask.texture;rect.size=mask.texture.size
        self.face.texture=w.texture;self.face.size=w.texture.size
        self.position()
    def position(self,*_):
        w=self.widget
        for rect,dx,dy in ((self.depth2,dp(1.8),-dp(3.0)),
                           (self.depth,dp(1.1),-dp(2.0)),
                           (self.edge,dp(-.9),dp(-.9)),
                           (self.bevel,dp(-.8),dp(1.0)),
                           (self.face,0,0)):
            rect.pos=(int(w.center_x-rect.size[0]/2)+dx,
                      int(w.center_y-rect.size[1]/2)+dy)

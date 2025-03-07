from manim import *

class demo(Scene):
   def construct(self):
        a= np.random.randint(0, 255, size=(3, 4)) 
        img = ImageMobject(np.uint8(a)) 
        img.height = 6 
        img.set_resampling_algorithm(RESAMPLING_ALGORITHMS['cubic']) 
        
        self.play()


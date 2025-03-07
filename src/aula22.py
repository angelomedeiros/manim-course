from manim import *

class demo(Scene):
    def construct(self):
        circle = Circle(radius=0.5, stroke_width=10, color=RED, fill_opacity=0.3)
        rect = SurroundingRectangle(circle)

        self.play(Write(circle), Write(rect))


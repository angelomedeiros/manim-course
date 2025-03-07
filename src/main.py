from manim import *

class DefaultTemplate(Scene):
    def construct(self):
        circle = Circle()  # create a circle
        circle.set_fill(BLUE, opacity=0.7)  # set color and transparency

        square = Square(fill_opacity=0.7, color=GREEN, fill_color=YELLOW)  # create a square
        square.set_fill(RED, opacity=0.8)
        square.flip(LEFT)  # flip horizontally
        square.rotate(-3 * TAU / 8)  # rotate a certain amount

        self.play(Create(square))  # animate the creation of the square
        self.play(Transform(square, circle))  # interpolate the square into the circle
        self.play(FadeOut(square))  # fade out animation

        rect = RoundedRectangle(fill_opacity=0.2, color=RED)        
        self.play(DrawBorderThenFill(rect))


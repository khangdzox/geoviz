from manim import *


class TestScene(MovingCameraScene):
    def construct(self):
        text = Text("this is a test").to_edge(UP)
        self.play(Write(text))

        self.wait(1)

        circle = Circle(radius=5, color=RED).move_to((0, 5, 0))
        new_circle = Circle(radius=5, color=BLUE).move_to((0, 5, 0))

        self.play(self.camera.auto_zoom([text, circle], margin=3))

        self.play(
            AnimationGroup(
                [
                    Create(circle),
                    Write(Text("I have a circle").next_to(circle, DOWN, 0.5)),
                ]
            )
        )

        self.play(Create(new_circle))

        self.remove(circle)
        self.add(circle)

        self.play(circle.animate.set_color(YELLOW))
        self.play(circle.animate.set_color(RED))

        self.wait(5)

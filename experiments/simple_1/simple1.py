import numpy as np
from manim import *


class SupplementaryAngles(Scene):
    def construct(self):
        # Base line split into two rays
        left_ray = Line(ORIGIN, LEFT * 4)
        right_ray = Line(ORIGIN, RIGHT * 4)

        # Center point
        O = Dot(ORIGIN)
        label_O = MathTex("O").next_to(O, DOWN)

        # Slanted ray at 47 degrees from the right ray
        angle_deg = 47
        angle_rad = angle_deg * DEGREES
        slanted_ray = Line(
            ORIGIN, 3 * (np.cos(angle_rad) * RIGHT + np.sin(angle_rad) * UP)
        )

        # Angles
        angle_47 = Angle(right_ray, slanted_ray, radius=1)
        angle_x = Angle(slanted_ray, left_ray, radius=1.2)

        # Labels
        label_47 = MathTex("47^\\circ").move_to(
            angle_47.point_from_proportion(0.5) + 0.2 * UP
        )

        label_x = MathTex("x").move_to(angle_x.point_from_proportion(0.5) + 0.2 * UP)

        # Equation (no answer)
        equation = MathTex("x + 47^\\circ = 180^\\circ").to_edge(UP)

        # Animations
        self.play(Create(left_ray), Create(right_ray))
        self.play(FadeIn(O), Write(label_O))
        self.play(Create(slanted_ray))
        self.play(Create(angle_47), Write(label_47))
        self.play(Create(angle_x), Write(label_x))
        self.play(Write(equation))

        self.wait(2)

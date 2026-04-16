from manim import *


class TriangleAngleProblem(Scene):
    def construct(self):
        # Title
        title = Text("Geometry Problem Visualization", font_size=36)
        self.play(Write(title))
        self.wait(1)
        self.play(title.animate.to_edge(UP))

        # Define triangle points
        A = LEFT * 3 + DOWN * 1
        B = RIGHT * 3 + DOWN * 1
        C = LEFT * 3 + UP * 3

        # Create triangle
        triangle = Polygon(A, B, C)
        self.play(Create(triangle))

        # Label points
        label_A = Text("A").next_to(A, DOWN)
        label_B = Text("B").next_to(B, DOWN)
        label_C = Text("C").next_to(C, UP)
        self.play(Write(label_A), Write(label_B), Write(label_C))

        # Mark right angle at A
        right_angle = RightAngle(Line(A, B), Line(A, C), length=0.4)
        self.play(Create(right_angle))

        # Show angle at B = 30°
        angle_B = Angle(Line(B, A), Line(B, C), radius=0.7, other_angle=True)
        angle_B_label = Text(r"30^\circ").next_to(angle_B, RIGHT)
        self.play(Create(angle_B), Write(angle_B_label))

        # Midpoint I of BC
        I = (B + C) / 2
        point_I = Dot(I)
        label_I = Text("I").next_to(I, RIGHT)

        self.play(FadeIn(point_I), Write(label_I))

        # Draw line AI
        line_AI = Line(A, I)
        self.play(Create(line_AI))

        # Highlight angle AIB (unknown)
        angle_AIB = Angle(Line(I, A), Line(I, B), radius=0.8)
        angle_AIB_label = Text("?").next_to(angle_AIB, UP)

        self.play(Create(angle_AIB), Write(angle_AIB_label))

        # Problem statement
        question = Text("Find ∠AIB", font_size=32)
        question.to_edge(DOWN)

        self.play(Write(question))
        self.wait(2)

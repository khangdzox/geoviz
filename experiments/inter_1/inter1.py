from manim import *


class RightTriangleAltitude(Scene):
    def construct(self):
        # Define points
        A = LEFT * 3
        B = RIGHT * 3
        C = A + UP * 2.5  # will adjust to make right angle visually

        # Adjust C so triangle is right-angled at C
        # Construct using vectors: AC ⟂ BC
        A = np.array([-3, 0, 0])
        C = np.array([-1, 2.4, 0])
        B = np.array([3, 0, 0])

        # Lines
        AC = Line(A, C)
        BC = Line(B, C)
        AB = Line(A, B)

        # Foot of perpendicular from C to AB
        H = AB.get_projection(C)

        CH = Line(C, H)

        # Points
        dot_A = Dot(A)
        dot_B = Dot(B)
        dot_C = Dot(C)
        dot_H = Dot(H)

        # Labels
        label_A = MathTex("A").next_to(dot_A, DOWN)
        label_B = MathTex("B").next_to(dot_B, DOWN)
        label_C = MathTex("C").next_to(dot_C, UP)
        label_H = MathTex("H").next_to(dot_H, DOWN)

        # Side labels (given only)
        label_AC = MathTex("5").next_to(AC, LEFT)
        label_BC = MathTex("12").next_to(BC, RIGHT)

        # Right angle marker at C
        right_angle = RightAngle(Line(C, A), Line(C, B), length=0.3)

        # Animation
        self.play(Create(dot_A), Create(dot_B))
        self.play(Create(AB))
        self.play(Create(dot_C))
        self.play(Create(AC), Create(BC))
        self.play(Create(right_angle))

        self.play(Write(label_A), Write(label_B), Write(label_C))
        self.play(Write(label_AC), Write(label_BC))

        self.play(Create(dot_H))
        self.play(Create(CH))
        self.play(Write(label_H))

        self.wait()

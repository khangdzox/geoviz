from manim import *


class TangentSecantDiagram(Scene):
    def construct(self):
        # Circle
        circle = Circle(radius=2).shift(LEFT * 1.5)
        center = circle.get_center()

        # External point P
        P = Dot(RIGHT * 4)
        P_label = MathTex("P").next_to(P, RIGHT)

        # Tangent point T (approximate)
        T = Dot(circle.point_at_angle(PI / 4))
        T_label = MathTex("T").next_to(T, UP)

        # Tangent line PT
        tangent_line = Line(P.get_center(), T.get_center())

        # Secant points A and B
        # Define a line from P through the circle
        secant_dir = LEFT + DOWN * 0.3
        secant_line_full = Line(P.get_center(), P.get_center() + secant_dir * 6)

        # Approximate intersection points A and B
        A = Dot(circle.point_at_angle(-PI / 6))
        B = Dot(circle.point_at_angle(-2 * PI / 3))

        A_label = MathTex("A").next_to(A, DOWN)
        B_label = MathTex("B").next_to(B, LEFT)

        # Secant segments
        secant_line = Line(P.get_center(), B.get_center())

        # Length labels
        PT_label = MathTex("8").next_to(tangent_line, UP)
        PA_label = MathTex("4").next_to(Line(P.get_center(), A.get_center()), DOWN)

        # Animations
        self.play(Create(circle))
        self.play(FadeIn(P), Write(P_label))

        self.play(Create(tangent_line), FadeIn(T), Write(T_label))
        self.play(Write(PT_label))

        self.play(Create(secant_line))
        self.play(FadeIn(A), Write(A_label))
        self.play(FadeIn(B), Write(B_label))
        self.play(Write(PA_label))

        self.wait()

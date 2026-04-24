import numpy as np
from manim import *

# =========================
# Helper Functions
# =========================


def midpoint(A, B):
    return (A + B) / 2


def circumcenter(A, B, C):
    ax, ay = A[:2]
    bx, by = B[:2]
    cx, cy = C[:2]

    d = 2 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))

    ux = (
        (ax**2 + ay**2) * (by - cy)
        + (bx**2 + by**2) * (cy - ay)
        + (cx**2 + cy**2) * (ay - by)
    ) / d

    uy = (
        (ax**2 + ay**2) * (cx - bx)
        + (bx**2 + by**2) * (ax - cx)
        + (cx**2 + cy**2) * (bx - ax)
    ) / d

    return np.array([ux, uy, 0])


# =========================
# Scene
# =========================


class GeometryScene(MovingCameraScene):
    def construct(self):

        # =========================
        # Step 1: Triangle ABC
        # =========================
        step_text = Text("Construct triangle ABC").to_edge(UP)
        self.add(step_text)

        b = 6
        a = 7
        theta = np.deg2rad(50)

        A = np.array([0, 0, 0])
        B = np.array([b, 0, 0])
        C = np.array([a * np.cos(theta), a * np.sin(theta), 0])

        dot_A = Dot(A, color=WHITE)
        label_A = MathTex("A").next_to(dot_A, DOWN)

        dot_B = Dot(B, color=WHITE)
        label_B = MathTex("B").next_to(dot_B, DOWN)

        dot_C = Dot(C, color=WHITE)
        label_C = MathTex("C").next_to(dot_C, UP)

        AB = Line(A, B, color=GRAY)
        BC = Line(B, C, color=GRAY)
        CA = Line(C, A, color=GRAY)

        self.play(
            FadeIn(dot_A),
            Write(label_A),
            FadeIn(dot_B),
            Write(label_B),
            FadeIn(dot_C),
            Write(label_C),
            Create(AB),
            Create(BC),
            Create(CA),
            run_time=2,
        )

        self.play(FadeOut(step_text))

        # update frame after step 1
        self.play(self.camera.frame.animate.move_to((A + B + C) / 3).scale(1.6))

        # =========================
        # Step 2: Circumcircle (O)
        # =========================
        step_text2 = Text("Construct circumcircle (O)").to_edge(UP)
        self.play(FadeIn(step_text2))

        O = circumcenter(A, B, C)

        dot_O = Dot(O, color=YELLOW)
        label_O = MathTex("O").next_to(dot_O, RIGHT)

        OA = np.linalg.norm(O - A)
        circle_O = Circle(radius=OA, color=BLUE).move_to(O)

        self.play(FadeIn(dot_O), Write(label_O))
        self.play(Create(circle_O), run_time=1.5)

        self.play(FadeOut(step_text2))

        # update frame after step 2
        self.play(self.camera.frame.animate.move_to((A + B + C + O) / 4).scale(1.8))

        self.wait(1)

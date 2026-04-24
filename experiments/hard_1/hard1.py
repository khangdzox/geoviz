import numpy as np
from manim import *

# ---------- Helpers ----------


def extend_line(p1, p2, scale=10):
    d = p2 - p1
    d = d / np.linalg.norm(d)
    return Line(p1 - d * scale, p2 + d * scale)


def circle_circle_intersection(c1, r1, c2, r2):
    d = np.linalg.norm(c2 - c1)
    a = (r1**2 - r2**2 + d**2) / (2 * d)
    h = np.sqrt(max(r1**2 - a**2, 0))
    p = c1 + a * (c2 - c1) / d
    perp = np.array([-(c2 - c1)[1], (c2 - c1)[0], 0]) / d
    return p + h * perp, p - h * perp


def line_circle_intersection(p1, p2, c, r):
    d = p2 - p1
    f = p1 - c
    a = np.dot(d, d)
    b = 2 * np.dot(f, d)
    c_ = np.dot(f, f) - r * r
    disc = max(b * b - 4 * a * c_, 0)

    t1 = (-b + np.sqrt(disc)) / (2 * a)
    t2 = (-b - np.sqrt(disc)) / (2 * a)

    return p1 + t1 * d, p1 + t2 * d


class GeometryScene(MovingCameraScene):
    def construct(self):
        # ---------- Base geometry ----------
        A = np.array([-4, 0, 0])
        B = np.array([-2, 0, 0])
        C = np.array([1, 0, 0])
        D = np.array([4, 0, 0])

        c1 = (A + C) / 2
        r1 = np.linalg.norm(A - C) / 2

        c2 = (B + D) / 2
        r2 = np.linalg.norm(B - D) / 2

        Xp, Yp = circle_circle_intersection(c1, r1, c2, r2)
        Zp = line_intersection((Xp, Yp), (B, C))

        Pp = Xp * 0.3 + Yp * 0.7

        i1, i2 = line_circle_intersection(C, Pp, c1, r1)
        Mp = i1 if np.linalg.norm(i1 - C) > 1e-6 else i2

        i1, i2 = line_circle_intersection(B, Pp, c2, r2)
        Np = i1 if np.linalg.norm(i1 - B) > 1e-6 else i2

        # ---------- Objects ----------
        base = extend_line(A, D)
        XY = extend_line(Xp, Yp)
        CP = extend_line(C, Pp)
        BP = extend_line(B, Pp)
        AM = extend_line(A, Mp)
        DN = extend_line(D, Np)

        circ1 = Circle(r1).move_to(c1)
        circ2 = Circle(r2).move_to(c2)

        pts = [A, B, C, D, Xp, Yp, Zp, Pp, Mp, Np]
        names = ["A", "B", "C", "D", "X", "Y", "Z", "P", "M", "N"]

        dots = VGroup(*[Dot(p) for p in pts])
        labels = VGroup(
            *[
                MathTex(n).scale(0.7).next_to(p, DOWN if i < 4 else RIGHT)
                for i, (p, n) in enumerate(zip(pts, names))
            ]
        )

        # ---------- CAMERA FIT (correct) ----------
        geom_group = VGroup(base, XY, CP, BP, AM, DN, circ1, circ2, dots)

        self.camera.frame.move_to(geom_group.get_center())
        self.camera.frame.set(width=geom_group.width * 1.25)

        # ---------- Animation ----------

        # Base
        self.play(Create(base))
        self.play(FadeIn(dots[:4]), Write(labels[:4]))
        self.wait(0.6)

        # Circles (strong highlight)
        self.play(Create(circ1), Create(circ2))
        self.play(
            circ1.animate.set_stroke(YELLOW, 5), circ2.animate.set_stroke(YELLOW, 5)
        )
        self.wait(0.6)
        self.play(
            circ1.animate.set_stroke(WHITE, 2), circ2.animate.set_stroke(WHITE, 2)
        )

        # X,Y and XY
        self.play(FadeIn(dots[4:6]), Write(labels[4:6]))
        self.play(Create(XY))
        self.play(XY.animate.set_stroke(BLUE, 5))
        self.wait(0.6)
        self.play(XY.animate.set_stroke(WHITE, 2))

        # Z
        self.play(FadeIn(dots[6]), Write(labels[6]))
        self.wait(0.5)

        # P
        self.play(FadeIn(dots[7]), Write(labels[7]))
        self.wait(0.5)

        # CP, M (highlight)
        self.play(Create(CP))
        self.play(FadeIn(dots[8]), Write(labels[8]))
        self.play(dots[8].animate.set_color(YELLOW))
        self.wait(0.4)
        self.play(dots[8].animate.set_color(WHITE))

        # BP, N (highlight)
        self.play(Create(BP))
        self.play(FadeIn(dots[9]), Write(labels[9]))
        self.play(dots[9].animate.set_color(YELLOW))
        self.wait(0.4)
        self.play(dots[9].animate.set_color(WHITE))

        # Final lines AM, DN (strong highlight)
        self.play(Create(AM), Create(DN))
        self.play(AM.animate.set_stroke(RED, 5), DN.animate.set_stroke(RED, 5))
        self.wait(0.6)
        self.play(AM.animate.set_stroke(WHITE, 2), DN.animate.set_stroke(WHITE, 2))

        self.wait(2)

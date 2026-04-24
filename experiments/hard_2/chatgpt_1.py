import numpy as np
from manim import *


# ---------------- geometry ----------------
def circumcenter(A, B, C):
    mid_AB = (A + B) / 2
    mid_BC = (B + C) / 2

    dAB = B - A
    dBC = C - B

    pAB = np.array([-dAB[1], dAB[0], 0])
    pBC = np.array([-dBC[1], dBC[0], 0])

    t = np.linalg.solve(np.column_stack((pAB[:2], -pBC[:2])), (mid_BC - mid_AB)[:2])[0]

    return mid_AB + t * pAB


def foot(P, A, B):
    AP = P - A
    AB = B - A
    t = np.dot(AP, AB) / np.dot(AB, AB)
    return A + t * AB


def line_intersection(A, B, C, D):
    AB = B - A
    CD = D - C

    t = np.linalg.solve(np.column_stack((AB[:2], -CD[:2])), (C - A)[:2])[0]

    return A + t * AB


def midpoint(A, B):
    return (A + B) / 2


def orthocenter(A, B, C):
    D = foot(A, B, C)
    E = foot(B, A, C)
    return line_intersection(A, D, B, E)


# ---------------- FIXED: real circle-line intersection ----------------
def circle_line_intersection(A, B, O, R):
    d = B - A
    d = d / np.linalg.norm(d)
    f = A - O

    a = np.dot(d, d)
    b = 2 * np.dot(f, d)
    c = np.dot(f, f) - R**2

    t = np.roots([a, b, c])

    P1 = A + t[0] * d
    P2 = A + t[1] * d

    return P1 if np.linalg.norm(P1 - A) > np.linalg.norm(P2 - A) else P2


# controlled segment
def seg(P, Q):
    return Line(P, Q)


# camera
def fit(scene, objs):
    g = VGroup(*objs)
    scene.play(
        scene.camera.frame.animate.move_to(g.get_center()).set(
            width=max(g.width * 1.4, 6), height=max(g.height * 1.4, 4)
        ),
        run_time=0.6,
    )


def replace(scene, old, msg):
    new = Text(msg).to_edge(UP)
    scene.play(FadeOut(old), FadeIn(new))
    return new


# ---------------- scene ----------------
class GeometryScene(MovingCameraScene):
    def construct(self):

        current = []

        def add(m):
            current.append(m)
            return m

        # ---------------- points ----------------
        A = np.array([-3, 2, 0])
        B = np.array([-4, -2, 0])
        C = np.array([3, -1, 0])

        O = circumcenter(A, B, C)
        R = np.linalg.norm(A - O)

        D = foot(A, B, C)

        # FIXED E (no singular system anymore)
        E = circle_line_intersection(A, D, O, R)

        K = foot(E, A, B)
        S = line_intersection(A, O, B, C)
        I = midpoint(A, B)
        H = orthocenter(A, B, C)

        # ---------------- text ----------------
        text = Text("").to_edge(UP)
        self.add(text)

        # ---------------- Step 1 ----------------
        text = replace(self, text, "Tam giác ABC")

        A_d = add(Dot(A))
        B_d = add(Dot(B))
        C_d = add(Dot(C))
        A_l = add(Text("A").next_to(A_d, UP))
        B_l = add(Text("B").next_to(B_d, LEFT))
        C_l = add(Text("C").next_to(C_d, RIGHT))

        tri = add(Polygon(A, B, C, color=BLUE))

        self.play(Create(VGroup(A_d, B_d, C_d, A_l, B_l, C_l, tri)))
        fit(self, current)

        # ---------------- Step 2 ----------------
        text = replace(self, text, "Đường tròn ngoại tiếp (O)")

        circle = Circle(radius=R, color=GREEN).move_to(O)
        O_d = add(Dot(O))
        O_l = add(Text("O").next_to(O_d, UP))

        self.play(Create(circle), Create(O_d), Write(O_l))
        fit(self, current)

        # ---------------- Step 3 ----------------
        text = replace(self, text, "Đường cao AD")

        BC = add(seg(B, C).set_color(GRAY))
        AD = add(seg(A, D).set_color(GRAY))

        D_d = add(Dot(D))
        D_l = add(Text("D").next_to(D_d, DOWN))

        self.play(Create(BC), Create(AD), Create(D_d), Write(D_l))
        fit(self, current)

        # ---------------- Step 4 ----------------
        text = replace(self, text, "AD cắt (O) tại E")

        AE = add(seg(A, E).set_color(GRAY))
        E_d = add(Dot(E, color=YELLOW))
        E_l = add(Text("E").next_to(E_d, UP))

        self.play(Create(AE), Create(E_d), Write(E_l))
        fit(self, current)

        # ---------------- Step 5 (EARLY EK) ----------------
        text = replace(self, text, "EK ⟂ AB tại K")

        AB = add(seg(A, B).set_color(GRAY))
        AK = add(seg(A, K).set_color(GRAY))
        KB = add(seg(K, B).set_color(GRAY))

        K_d = add(Dot(K, color=YELLOW))
        K_l = add(Text("K").next_to(K_d, DOWN))

        self.play(Create(AB), Create(AK), Create(KB), Create(K_d), Write(K_l))
        fit(self, current)

        # ---------------- Question A ----------------
        text = replace(self, text, "Chứng minh E, D, B, K cùng thuộc một đường tròn")

        temp_circle = Circle.from_three_points(E, D, B).set_color(PURPLE)
        self.play(Create(temp_circle))
        self.play(Indicate(VGroup(E_d, D_d, B_d, K_d)))
        self.play(FadeOut(temp_circle))
        self.wait(1)

        # ---------------- Step 6 ----------------
        text = replace(self, text, "AO cắt BC tại S")

        AO = add(seg(A, O).set_color(GRAY))
        S_d = add(Dot(S, color=ORANGE))
        S_l = add(Text("S").next_to(S_d, RIGHT))

        self.play(Create(AO), Create(S_d), Write(S_l))
        fit(self, current)

        # ---------------- Question B ----------------
        text = replace(self, text, "Chứng minh EA là phân giác ∠CEK và AB·AC = AE·AS")

        CE = add(seg(C, E).set_color(GRAY))
        EK = add(seg(E, K).set_color(GRAY))

        self.play(Create(CE), Create(EK))
        self.play(Indicate(VGroup(CE, EK, E_d)))

        # highlight all involved for product relation
        self.play(Indicate(VGroup(A_d, B_d, C_d, E_d, S_d)))
        self.wait(2)

        # ---------------- Step 7 ----------------
        text = replace(self, text, "H trực tâm, I trung điểm AB")

        I_d = add(Dot(I, color=PURPLE))
        I_l = add(Text("I").next_to(I_d, UP))

        H_d = add(Dot(H, color=RED))
        H_l = add(Text("H").next_to(H_d, DOWN))

        self.play(Create(I_d), Write(I_l))
        self.play(Create(H_d), Write(H_l))
        fit(self, current)

        # ---------------- Question C ----------------
        text = replace(self, text, "Chứng minh SI ⟂ HK")

        SI = add(seg(S, I).set_color(GRAY))
        HK = add(seg(H, K).set_color(GRAY))

        right = RightAngle(SI, HK, length=0.25)

        self.play(Create(SI), Create(HK), Create(right))
        self.play(Indicate(VGroup(SI, HK)))
        self.wait(3)

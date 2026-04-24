import numpy as np
from manim import *

# ================= HELPERS =================


def midpoint(A, B):
    return (A + B) / 2


def line_intersection(A, B, C, D):
    AB = B - A
    CD = D - C
    t = np.linalg.solve(np.column_stack((AB[:2], -CD[:2])), (C - A)[:2])[0]
    return A + t * AB


def foot_of_perpendicular(P, A, B):
    AB = B - A
    t = np.dot(P - A, AB) / np.dot(AB, AB)
    return A + t * AB


def circumcenter(A, B, C):
    ax, ay = A[:2]
    bx, by = B[:2]
    cx, cy = C[:2]
    D = 2 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
    ux = (
        (ax**2 + ay**2) * (by - cy)
        + (bx**2 + by**2) * (cy - ay)
        + (cx**2 + cy**2) * (ay - by)
    ) / D
    uy = (
        (ax**2 + ay**2) * (cx - bx)
        + (bx**2 + by**2) * (ax - cx)
        + (cx**2 + cy**2) * (bx - ax)
    ) / D
    return np.array([ux, uy, 0])


def circle_line_intersect(center, radius, P, Q):
    d = Q - P
    f = P - center
    a = np.dot(d, d)
    b = 2 * np.dot(f, d)
    c = np.dot(f, f) - radius**2
    disc = b**2 - 4 * a * c
    if disc < 0:
        return []
    res = []
    for s in [-1, 1]:
        t = (-b + s * np.sqrt(disc)) / (2 * a)
        res.append(P + t * d)
    return res


def orthocenter(A, B, C):
    foot_B = foot_of_perpendicular(B, A, C)
    foot_C = foot_of_perpendicular(C, A, B)
    return line_intersection(B, foot_B, C, foot_C)


# ================= COORDINATES =================

A = np.array([0, 0, 0])
B = np.array([4, 0, 0])
C = np.array([1.5, 3, 0])

O = circumcenter(A, B, C)
D = foot_of_perpendicular(A, B, C)
r = np.linalg.norm(A - O)

E_candidates = circle_line_intersect(O, r, A, D)
E = E_candidates[0] if np.linalg.norm(E_candidates[0] - A) > 1e-6 else E_candidates[1]

K = foot_of_perpendicular(E, A, B)
S = line_intersection(A, O, B, C)
H = orthocenter(A, B, C)
I = midpoint(A, B)

# ================= SCENE =================


class GeometryScene(MovingCameraScene):
    def setup(self):
        self.__all_objects = []
        self.__step_text = None

    def draw_point(self, label, coords, direction=UP):
        dot = Dot(coords, color=WHITE)
        tex = MathTex(label).next_to(dot, direction, buff=0.15)
        self.__all_objects += [dot, tex]
        self.__fit_camera()
        self.play(FadeIn(dot), FadeIn(tex), run_time=0.2)
        return dot, tex

    def draw_segment(self, P, Q, color=GRAY):
        line = Line(P, Q, color=color)
        self.__all_objects.append(line)
        self.__fit_camera()
        self.play(Create(line), run_time=0.5)
        return line

    def draw_circle(self, center, radius, color=TEAL):
        circ = Circle(radius=radius, color=color).move_to(center)
        self.__all_objects.append(circ)
        self.__fit_camera()
        self.play(Create(circ), run_time=0.5)
        return circ

    def __fit_camera(self, margin=1):
        group = VGroup(*self.__all_objects)
        if self.__step_text:
            group.add(self.__step_text)
        self.camera.auto_zoom(group, margin=margin)

    def highlight(self, *objects, color=YELLOW, duration=0.5):
        original_colors = [obj.get_color() for obj in objects]
        self.play(*[obj.animate.set_color(color) for obj in objects])
        self.wait(duration)
        self.play(
            *[obj.animate.set_color(c) for obj, c in zip(objects, original_colors)]
        )

    def set_step_text(self, string):
        if self.__step_text:
            self.remove(self.__step_text)
        self.__step_text = Text(string).scale(0.5)
        self.__fit_camera()
        self.play(Write(self.__step_text))

    def construct(self):

        self.setup()

        # --- Step 1 ---
        self.set_step_text("Cho tam giác ABC có ba góc nhọn (AB < AC)")
        dot_A, _ = self.draw_point("A", A)
        dot_B, _ = self.draw_point("B", B)
        dot_C, _ = self.draw_point("C", C)
        seg_AB = self.draw_segment(A, B, BLUE)
        seg_BC = self.draw_segment(B, C, BLUE)
        seg_CA = self.draw_segment(C, A, BLUE)
        self.highlight(seg_AB, seg_BC, seg_CA)

        # --- Step 2 ---
        self.set_step_text("nội tiếp đường tròn (O)")
        dot_O, _ = self.draw_point("O", O)
        circle_O = self.draw_circle(O, np.linalg.norm(A - O))
        self.highlight(circle_O)

        # --- Step 3 ---
        self.set_step_text("Đường cao AD của tam giác ABC")
        dot_D, _ = self.draw_point("D", D)
        seg_AD = self.draw_segment(A, D)
        self.highlight(seg_AD)

        # --- Step 4 ---
        self.set_step_text("cắt đường tròn (O) tại điểm E")
        dot_E, _ = self.draw_point("E", E)
        self.highlight(dot_E)

        # --- Step 5 ---
        self.set_step_text(
            "Gọi K là chân đường vuông góc kẻ từ điểm E đến đường thẳng AB"
        )
        dot_K, _ = self.draw_point("K", K)
        seg_EK = self.draw_segment(E, K)
        self.highlight(seg_EK)

        # --- Step 6 ---
        self.set_step_text("Chứng minh bốn điểm E, D, B, K cùng thuộc một đường tròn")
        seg_DB = self.draw_segment(D, B)
        seg_BK = self.draw_segment(B, K)
        seg_KE = self.draw_segment(K, E)
        seg_ED = self.draw_segment(E, D)
        self.highlight(seg_DB, seg_BK, seg_KE, seg_ED, color=RED, duration=1.5)

        # --- Step 7 ---
        self.set_step_text("Đường thẳng AO cắt đường thẳng BC tại điểm S")
        dot_S, _ = self.draw_point("S", S)
        self.highlight(dot_S)

        # --- Step 8 ---
        self.set_step_text("Chứng minh EA là tia phân giác của góc CEK")
        seg_EA = self.draw_segment(E, A)
        seg_EC = self.draw_segment(E, C)
        self.highlight(seg_EC, seg_EK, color=RED, duration=1)
        self.highlight(seg_EA, color=RED, duration=1)

        # --- Step 9 ---
        self.set_step_text("AB.AC = AE.AS")
        seg_AC = self.draw_segment(A, C, BLUE)
        seg_AE = self.draw_segment(A, E)
        seg_AS = self.draw_segment(A, S)
        self.highlight(seg_AB, seg_AC, color=RED, duration=1)
        self.highlight(seg_AE, seg_AS, color=RED, duration=1)

        # --- Step 10 ---
        self.set_step_text("Gọi H là trực tâm của tam giác ABC")
        dot_H, _ = self.draw_point("H", H)
        self.highlight(dot_H)

        # --- Step 11 ---
        self.set_step_text("I là trung điểm của đoạn thẳng AB")
        dot_I, _ = self.draw_point("I", I)
        self.highlight(dot_I)

        # --- Step 12 ---
        self.set_step_text("Chứng minh đường thẳng SI vuông góc với đường thẳng HK")
        seg_SI = self.draw_segment(S, I)
        seg_HK = self.draw_segment(H, K)
        self.highlight(seg_SI, seg_HK, color=RED, duration=1.5)

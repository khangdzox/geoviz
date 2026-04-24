import numpy as np
from manim import *

# ── Coordinate solver functions ──────────────────────────────────────────────


def midpoint(A, B):
    return (A + B) / 2


def line_intersection(A, B, C, D):
    """Intersection of line AB and line CD."""
    AB = B - A
    CD = D - C
    t = np.linalg.solve(np.column_stack((AB[:2], -CD[:2])), (C - A)[:2])[0]
    return A + t * AB


def foot_of_perpendicular(P, A, B):
    """Foot of perpendicular from point P to line AB."""
    AB = B - A
    t = np.dot(P - A, AB) / np.dot(AB, AB)
    return A + t * AB


def circumcenter(A, B, C):
    ax, ay = A[:2]
    bx, by = B[:2]
    cx, cy = C[:2]
    Dv = 2 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
    ux = (
        (ax**2 + ay**2) * (by - cy)
        + (bx**2 + by**2) * (cy - ay)
        + (cx**2 + cy**2) * (ay - by)
    ) / Dv
    uy = (
        (ax**2 + ay**2) * (cx - bx)
        + (bx**2 + by**2) * (ax - cx)
        + (cx**2 + cy**2) * (bx - ax)
    ) / Dv
    return np.array([ux, uy, 0])


def circle_line_intersect(center, radius, P, Q):
    """Returns list of intersection points of circle with line PQ."""
    d = Q - P
    f = P - center
    a = np.dot(d, d)
    b = 2 * np.dot(f, d)
    c_val = np.dot(f, f) - radius**2
    disc = b**2 - 4 * a * c_val
    if disc < 0:
        return []
    results = []
    for sign in [-1, 1]:
        t = (-b + sign * np.sqrt(disc)) / (2 * a)
        results.append(P + t * d)
    return results


def extend_segment_to_point(A, B, E):
    """Returns new segment endpoints so the drawn segment visually reaches E."""
    AB = B - A
    denom = np.dot(AB, AB)
    if denom < 1e-12:
        return A, B
    t = np.dot(E - A, AB) / denom
    if t < 0:
        return E, B
    elif t > 1:
        return A, E
    else:
        return A, B


def orthocenter(A, B, C):
    """Returns orthocenter of triangle ABC."""
    foot_B = foot_of_perpendicular(B, A, C)
    foot_C = foot_of_perpendicular(C, A, B)
    return line_intersection(B, foot_B, C, foot_C)


# ── Coordinate computations ──────────────────────────────────────────────────

A = np.array([0.0, 0.0, 0.0])
B = np.array([4.0, 0.0, 0.0])
C = np.array([5.0 * np.cos(np.deg2rad(50)), 5.0 * np.sin(np.deg2rad(50)), 0.0])

O = circumcenter(A, B, C)
radius = float(np.linalg.norm(O - A))

# D = foot of altitude from A to BC
D = foot_of_perpendicular(A, B, C)

# E = second intersection of line AD with circle (O), E ≠ A
pts = circle_line_intersect(O, radius, A, D)
E = None
for pt in pts:
    if np.linalg.norm(pt - A) > 0.01:
        E = pt
        break

# K = foot of perpendicular from E to line AB
K = foot_of_perpendicular(E, A, B)

# Check if K lies on segment AB
K_t = float(np.dot(K - A, B - A) / np.dot(B - A, B - A))
K_on_AB = 0.0 <= K_t <= 1.0

# S = intersection of line AO with line BC
S = line_intersection(A, O, B, C)

# H = orthocenter of triangle ABC
H = orthocenter(A, B, C)

# I = midpoint of AB
I = midpoint(A, B)

# Circumcircle through D, E, B, K
O_DEBK = circumcenter(D, E, B)
r_DEBK = float(np.linalg.norm(O_DEBK - D))

# Intersection of lines SI and HK (for right-angle annotation in part c)
X_SIHK = line_intersection(S, I, H, K)


# ── Scene ────────────────────────────────────────────────────────────────────


class GeometryScene(MovingCameraScene):
    def setup(self):
        super().setup()
        self._all_objects = []
        self._step_text = None

    # ── private helpers ──────────────────────────────────────────────────────

    def _position_step_text(self):
        """Reposition _step_text above bounding box of _all_objects."""
        if self._step_text is None:
            return
        objs = [o for o in self._all_objects if o is not None]
        if objs:
            bb = Group(*objs)
            self._step_text.next_to(bb, UP, buff=0.4)
        else:
            self._step_text.to_edge(UP)

    def _fit_camera(self, margin=1.0):
        """Reposition step text then zoom camera to fit all objects."""
        self._position_step_text()
        objs = [o for o in self._all_objects if o is not None]
        if self._step_text is not None:
            objs = objs + [self._step_text]
        if not objs:
            return
        self.play(
            self.camera.auto_zoom(objs, margin=margin, animate=True),
            run_time=0.4,
        )

    def _remove_obj(self, obj):
        self.remove(obj)
        if obj in self._all_objects:
            self._all_objects.remove(obj)

    def _add_segment_silent(self, P, Q, color=GRAY):
        """Add a segment without animation (used when splitting an existing segment)."""
        seg = Line(P, Q, color=color, stroke_width=2)
        self._all_objects.append(seg)
        self.add(seg)
        return seg

    # ── public drawing interface ─────────────────────────────────────────────

    def draw_point(self, label, coords, direction=UP):
        """Draw a single labeled point with FadeIn animation."""
        dot = Dot(point=coords, color=WHITE, radius=0.06)
        lbl = MathTex(label, color=WHITE, font_size=28).next_to(
            dot, direction, buff=0.1
        )
        self._all_objects.extend([dot, lbl])
        self._fit_camera()
        self.play(FadeIn(dot), FadeIn(lbl), run_time=0.4)
        return dot, lbl

    def draw_points(self, *specs):
        """
        Draw multiple labeled points simultaneously.
        Each spec is a tuple: (label_str, coords, direction).
        Calls _fit_camera once, then plays all FadeIn together.
        Returns a dict: {label_str: (dot, lbl)}.
        """
        dots_and_labels = []
        for label, coords, direction in specs:
            dot = Dot(point=coords, color=WHITE, radius=0.06)
            lbl = MathTex(label, color=WHITE, font_size=28).next_to(
                dot, direction, buff=0.1
            )
            self._all_objects.extend([dot, lbl])
            dots_and_labels.append((label, dot, lbl))
        self._fit_camera()
        self.play(
            *[FadeIn(dot) for _, dot, _ in dots_and_labels],
            *[FadeIn(lbl) for _, _, lbl in dots_and_labels],
            run_time=0.6,
        )
        return {label: (dot, lbl) for label, dot, lbl in dots_and_labels}

    def draw_segment(self, P, Q, color=GRAY):
        """Draw a single segment with Create animation."""
        seg = Line(P, Q, color=color, stroke_width=2)
        self._all_objects.append(seg)
        self._fit_camera()
        self.play(Create(seg), run_time=1.0)
        return seg

    def draw_segments(self, *specs):
        """
        Draw multiple segments simultaneously.
        Each spec is a tuple: (P, Q, color).
        Calls _fit_camera once, then plays all Create together.
        Returns a list of Line objects in the same order as specs.
        """
        segs = []
        for P, Q, color in specs:
            seg = Line(P, Q, color=color, stroke_width=2)
            self._all_objects.append(seg)
            segs.append(seg)
        self._fit_camera()
        self.play(*[Create(s) for s in segs], run_time=1.0)
        return segs

    def draw_circle(self, center, radius_val, color=TEAL):
        """Draw a circle with Create animation."""
        circ = Circle(radius=radius_val, color=color, stroke_width=2).move_to(center)
        self._all_objects.append(circ)
        self._fit_camera()
        self.play(Create(circ), run_time=1.0)
        return circ

    def highlight(self, *objects, color=YELLOW, duration=0.5):
        original_colors = []
        for obj in objects:
            if hasattr(obj, "get_color"):
                original_colors.append(obj.get_color())
            else:
                original_colors.append(WHITE)
        # Bring highlighted objects to front
        for obj in objects:
            self.remove(obj)
            self.add(obj)
        self.play(*[obj.animate.set_color(color) for obj in objects], run_time=0.3)
        self.wait(duration)
        self.play(
            *[
                obj.animate.set_color(original_colors[i])
                for i, obj in enumerate(objects)
            ],
            run_time=0.3,
        )

    def set_step_text(self, string):
        if self._step_text is not None:
            self.play(FadeOut(self._step_text), run_time=0.3)
            self.remove(self._step_text)
            self._step_text = None
        txt = Text(string, font_size=22, color=YELLOW)
        self._step_text = txt
        self._position_step_text()
        self._fit_camera()
        self.play(Write(txt), run_time=0.8)

    def draw_right_angle(self, vertex, dir1, dir2, size=0.18):
        """
        Draw a right-angle square marker at vertex.
        dir1, dir2: vectors of the two perpendicular directions meeting at vertex.
        """
        d1 = np.array(dir1, dtype=float)
        d2 = np.array(dir2, dtype=float)
        d1 = d1 / np.linalg.norm(d1)
        d2 = d2 / np.linalg.norm(d2)
        p1 = vertex + size * d1
        p2 = vertex + size * d2
        p3 = vertex + size * d1 + size * d2
        marker = VGroup(
            Line(p1, p3, color=WHITE, stroke_width=1.5),
            Line(p2, p3, color=WHITE, stroke_width=1.5),
        )
        self._all_objects.append(marker)
        self.play(Create(marker), run_time=0.4)
        return marker

    def draw_equal_angles(
        self, vertex, ray1_pt, ray2_pt, ray3_pt, ray4_pt, radius=0.3, color=ORANGE
    ):
        """
        Draw two equal-angle arc markers at vertex:
          arc1: from direction of ray1_pt to direction of ray2_pt
          arc2: from direction of ray3_pt to direction of ray4_pt
        """

        def make_arc(v, p_start, p_end, r):
            d1 = (p_start - v)[:2]
            d2 = (p_end - v)[:2]
            a1 = float(np.arctan2(d1[1], d1[0]))
            a2 = float(np.arctan2(d2[1], d2[0]))
            diff = float((a2 - a1 + np.pi) % (2 * np.pi) - np.pi)
            arc = Arc(
                radius=r,
                start_angle=a1,
                angle=diff,
                color=color,
                stroke_width=2,
            ).shift(v)
            return arc

        arc1 = make_arc(vertex, ray1_pt, ray2_pt, radius)
        arc2 = make_arc(vertex, ray3_pt, ray4_pt, radius + 0.12)
        grp = VGroup(arc1, arc2)
        self._all_objects.append(grp)
        self.play(Create(grp), run_time=0.6)
        return grp

    def draw_tick_marks(self, P, Q, n=1, size=0.12, color=WHITE):
        """
        Draw n tick marks perpendicular to segment PQ at its midpoint,
        indicating equal length.
        """
        mid = (P + Q) / 2
        direction = Q - P
        length = np.linalg.norm(direction)
        if length < 1e-9:
            return VGroup()
        unit = direction / length
        perp = np.array([-unit[1], unit[0], 0.0])
        spacing = size * 0.6
        ticks = VGroup()
        offsets = np.linspace(-(n - 1) / 2, (n - 1) / 2, n) * spacing
        for off in offsets:
            center = mid + off * unit
            p_start = center - (size / 2) * perp
            p_end = center + (size / 2) * perp
            ticks.add(Line(p_start, p_end, color=color, stroke_width=2))
        self._all_objects.append(ticks)
        self.play(Create(ticks), run_time=0.4)
        return ticks

    # ── main animation ───────────────────────────────────────────────────────

    def construct(self):

        # ── Triangle ABC: all points then all sides then highlight ────────────
        self.set_step_text("Tam giác ABC nội tiếp đường tròn (O)")

        pts = self.draw_points(
            ("A", A, DOWN + LEFT),
            ("B", B, DOWN),
            ("C", C, UP + LEFT),
        )
        dot_A, label_A = pts["A"]
        dot_B, label_B = pts["B"]
        dot_C, label_C = pts["C"]

        seg_AB, seg_AC, seg_BC = self.draw_segments(
            (A, B, BLUE),
            (A, C, BLUE),
            (B, C, BLUE),
        )
        self.highlight(seg_AB, seg_AC, seg_BC, color=YELLOW, duration=0.4)

        # ── Circumcircle ─────────────────────────────────────────────────────
        self.set_step_text("Đường tròn ngoại tiếp (O)")
        dot_O, label_O = self.draw_point("O", O, RIGHT)
        circle_O = self.draw_circle(O, radius, color=TEAL)
        self.highlight(circle_O, color=YELLOW, duration=0.4)

        # ── Altitude foot D — split BC silently ──────────────────────────────
        self.set_step_text("Đường cao AD cắt đường tròn (O) tại E")
        self._remove_obj(seg_BC)
        seg_BD = self._add_segment_silent(B, D, color=BLUE)
        seg_DC = self._add_segment_silent(D, C, color=BLUE)

        dot_D, label_D = self.draw_point("D", D, DOWN)
        self.highlight(dot_D, color=YELLOW, duration=0.4)

        # Segment AD + right-angle mark AD⊥BC
        seg_AD = self.draw_segment(A, D, color=GRAY)
        self.highlight(seg_AD, color=YELLOW, duration=0.4)

        d_AD_dir = A - D
        d_AD_dir = d_AD_dir / np.linalg.norm(d_AD_dir)
        d_DB_dir = B - D
        d_DB_dir = d_DB_dir / np.linalg.norm(d_DB_dir)
        ra_AD_BC = self.draw_right_angle(D, d_AD_dir, d_DB_dir, size=0.18)

        # Point E — draw AE on top of AD (no removal, no flash)
        # seg_AD remains; seg_AE is longer and covers it completely (same color).
        seg_AE = self.draw_segment(A, E, color=GRAY)
        dot_E, label_E = self.draw_point("E", E, RIGHT)
        self.highlight(dot_E, color=YELLOW, duration=0.4)

        # ── Point K and segment EK + right-angle mark EK⊥AB ─────────────────
        self.set_step_text("K là chân đường vuông góc từ E đến AB")

        seg_EK = self.draw_segment(E, K, color=GRAY)

        if K_on_AB:
            self._remove_obj(seg_AB)
            seg_AK = self._add_segment_silent(A, K, color=BLUE)
            seg_KB = self._add_segment_silent(K, B, color=BLUE)
        else:
            seg_BK = self.draw_segment(B, K, color=GRAY)

        dot_K, label_K = self.draw_point("K", K, RIGHT)
        self.highlight(dot_K, seg_EK, color=YELLOW, duration=0.4)

        d_KE_dir = E - K
        d_KE_dir = d_KE_dir / np.linalg.norm(d_KE_dir)
        d_KA_dir = A - K
        d_KA_dir = d_KA_dir / np.linalg.norm(d_KA_dir)
        ra_EK_AB = self.draw_right_angle(K, d_KE_dir, d_KA_dir, size=0.18)

        # ── Question a) — temporary circumcircle through D, E, B, K ─────────
        self.set_step_text("a) E, D, B, K cùng thuộc một đường tròn?")

        circ_DEBK = Circle(radius=r_DEBK, color=GREEN, stroke_width=2).move_to(O_DEBK)
        self.add(circ_DEBK)
        self.play(Create(circ_DEBK), run_time=1.0)

        self.highlight(dot_E, dot_D, dot_B, dot_K, color=RED, duration=1.5)

        self.play(FadeOut(circ_DEBK), run_time=0.5)
        self.remove(circ_DEBK)

        # ── Point S ──────────────────────────────────────────────────────────
        self.set_step_text("b) AO cắt BC tại S")
        seg_AS = self.draw_segment(A, S, color=GRAY)
        dot_S, label_S = self.draw_point("S", S, DOWN)
        self.highlight(dot_S, color=YELLOW, duration=0.4)

        # ── Question b) part 1 — EA bisects angle CEK ────────────────────────
        self.set_step_text("b) EA là tia phân giác góc CEK?")
        seg_EC = self.draw_segment(E, C, color=GRAY)
        eq_ang = self.draw_equal_angles(E, C, A, A, K, radius=0.35, color=ORANGE)
        self.highlight(seg_EC, seg_AE, seg_EK, color=RED, duration=1.5)
        self.play(FadeOut(eq_ang), run_time=0.4)
        self._remove_obj(eq_ang)

        # ── Question b) part 2 — AB·AC = AE·AS ──────────────────────────────
        self.set_step_text("b) AB · AC = AE · AS?")
        self.highlight(seg_AB, seg_AC, color=RED, duration=1.5)
        self.wait(0.3)
        self.highlight(seg_AE, seg_AS, color=RED, duration=1.5)

        # ── Point H ──────────────────────────────────────────────────────────
        self.set_step_text("c) H là trực tâm tam giác ABC")
        dot_H, label_H = self.draw_point("H", H, RIGHT)
        self.highlight(dot_H, color=YELLOW, duration=0.4)

        # ── Point I + tick marks on AI and IB ────────────────────────────────
        self.set_step_text("I là trung điểm AB")
        dot_I, label_I = self.draw_point("I", I, DOWN)
        self.highlight(dot_I, color=YELLOW, duration=0.4)

        ticks_AI = self.draw_tick_marks(A, I, n=1, size=0.14, color=WHITE)
        ticks_IB = self.draw_tick_marks(I, B, n=1, size=0.14, color=WHITE)
        self.highlight(ticks_AI, ticks_IB, color=YELLOW, duration=0.4)

        # ── Question c) SI ⊥ HK ──────────────────────────────────────────────
        self.set_step_text("c) SI ⊥ HK?")

        si_p1, si_p2 = extend_segment_to_point(S, I, X_SIHK)
        hk_p1, hk_p2 = extend_segment_to_point(H, K, X_SIHK)

        seg_IS = self.draw_segment(si_p1, si_p2, color=GRAY)
        seg_HK = self.draw_segment(hk_p1, hk_p2, color=GRAY)

        d_SI_dir = (I - S) / np.linalg.norm(I - S)
        d_HK_dir = (K - H) / np.linalg.norm(K - H)
        ra_SI_HK = self.draw_right_angle(X_SIHK, d_SI_dir, d_HK_dir, size=0.18)

        self.highlight(seg_IS, seg_HK, color=RED, duration=1.5)

        self.wait(1)

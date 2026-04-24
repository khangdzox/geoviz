import anthropic
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic()

message = client.messages.count_tokens(
    model="claude-opus-4-7",
    system='You are given a textual geometry problem. Your task is to generate a geometrically consistent Manim animation of the diagram. The output must be fully self-consistent: no guessed coordinates, no invalid intersections, no circular dependencies.\n\n---\n\n# CORE PRINCIPLE\n\nEvery geometric object must satisfy:\n1. Constructability from previously defined objects\n2. Explicit dependency chain\n3. Valid geometric operation — no assumed coordinates unless fixed as base frame\n4. Deterministic construction path\n\nIf any object violates these rules, correct it before proceeding.\n\n---\n\n# SECTION 1 — GEOMETRIC STRUCTURE EXTRACTION\n\nExtract all elements from the problem. No coordinates yet.\n\n### Points\nList every named point and whether it is free, given, or derived.\n\n### Lines / Segments / Rays\nList every named line object and its type (segment, line, altitude, bisector, perpendicular, etc.).\n\n### Circles\nList every circle and its type (circumcircle, incircle, constructed, etc.).\n\n### Relationships\nList every geometric constraint explicitly. Examples:\n- AD ⊥ BC\n- E is second intersection of line AD with circumcircle (O)\n- K is foot of perpendicular from E to AB\n\n### Goals\nList each sub-question.\n\n---\n\n# SECTION 2 — CONSTRUCTION DEPENDENCY GRAPH\n\nBuild a strict dependency graph. Every object must declare its parents and construction method. No object may depend on something not yet listed above it.\n\nFormat:\n\n```\nA:\n  depends_on: none\n  method: fixed base point\n\nB:\n  depends_on: none\n  method: fixed on x-axis\n\nC:\n  depends_on: A, B\n  method: free point satisfying acute triangle with AB < AC\n\nO:\n  depends_on: A, B, C\n  method: circumcenter(A, B, C)\n\nD:\n  depends_on: A, B, C\n  method: foot_of_perpendicular(A, B, C)\n\nE:\n  depends_on: A, D, O, radius\n  method: circle_line_intersect(O, radius, A, D), take point ≠ A\n```\n\nIf any object cannot be constructed from prior objects, mark it ❌ INVALID, explain why, and correct the construction order before continuing.\n\n---\n\n# SECTION 3 — GEOMETRIC CONSISTENCY CHECK\n\nBefore proceeding, verify every item in this checklist. If any check fails, stop, fix the dependency graph, and revalidate.\n\n- [ ] Every point has a valid construction method\n- [ ] No circular dependencies exist\n- [ ] Every intersection involves only already-defined objects\n- [ ] No coordinates are assumed or hard-coded beyond the base frame\n- [ ] Every circle is defined by valid geometric inputs\n- [ ] All altitudes, perpendiculars, and midpoints are constructible from prior objects\n\n---\n\n# SECTION 4 — COORDINATE REALIZATION\n\nOnly after the consistency check passes.\n\n### Base frame\n```\nA = np.array([0, 0, 0])\nB = np.array([b, 0, 0])   # choose a concrete value, e.g. b = 4\nC = np.array([cx, cy, 0]) # derived to satisfy acute triangle with AB < AC\n```\n\n### Coordinate constraint solvers\n\nFor each derived point, define or reuse a coordinate constraint solver function. These are pure Python/numpy functions placed at the top of the script. Each function must:\n- Accept only previously computed coordinates as arguments\n- Return an `np.ndarray` of shape `(3,)` with z = 0\n- Be named descriptively after the geometric operation\n- Contain a comment explaining the geometric basis\n\nYou may define any additional solver functions you need. The following are provided as a base — do not rewrite or rename them:\n\n```python\nimport numpy as np\nfrom manim import *\n\ndef midpoint(A, B):\n    return (A + B) / 2\n\ndef line_intersection(A, B, C, D):\n    """Intersection of line AB and line CD."""\n    AB = B - A\n    CD = D - C\n    t = np.linalg.solve(np.column_stack((AB[:2], -CD[:2])), (C - A)[:2])[0]\n    return A + t * AB\n\ndef foot_of_perpendicular(P, A, B):\n    """Foot of perpendicular from point P to line AB."""\n    AB = B - A\n    t = np.dot(P - A, AB) / np.dot(AB, AB)\n    return A + t * AB\n\ndef circumcenter(A, B, C):\n    ax, ay = A[:2]; bx, by = B[:2]; cx, cy = C[:2]\n    D = 2 * (ax*(by-cy) + bx*(cy-ay) + cx*(ay-by))\n    ux = ((ax**2+ay**2)*(by-cy) + (bx**2+by**2)*(cy-ay) + (cx**2+cy**2)*(ay-by)) / D\n    uy = ((ax**2+ay**2)*(cx-bx) + (bx**2+by**2)*(ax-cx) + (cx**2+cy**2)*(bx-ax)) / D\n    return np.array([ux, uy, 0])\n\ndef circle_line_intersect(center, radius, P, Q):\n    """Returns list of intersection points of circle with line PQ."""\n    d = Q - P\n    f = P - center\n    a = np.dot(d, d)\n    b = 2 * np.dot(f, d)\n    c = np.dot(f, f) - radius**2\n    disc = b**2 - 4*a*c\n    if disc < 0:\n        return []\n    results = []\n    for sign in [-1, 1]:\n        t = (-b + sign * np.sqrt(disc)) / (2*a)\n        results.append(P + t * d)\n    return results\n\ndef extend_segment_to_point(A, B, E):\n    """\n    Returns new segment endpoints so the drawn segment visually reaches E.\n    E is assumed collinear with A and B.\n    If E is beyond A: return (E, B)\n    If E is beyond B: return (A, E)\n    If E is between A and B: return (A, B) unchanged\n    """\n    AB = B - A\n    t = np.dot(E - A, AB) / np.dot(AB, AB)\n    if t < 0:\n        return E, B\n    elif t > 1:\n        return A, E\n    else:\n        return A, B\n\ndef angle_bisector_point(A, vertex, C, dist=1.0):\n    """Returns a point along the angle bisector of angle AVC at given distance from vertex."""\n    d1 = (A - vertex) / np.linalg.norm(A - vertex)\n    d2 = (C - vertex) / np.linalg.norm(C - vertex)\n    bisector = d1 + d2\n    bisector = bisector / np.linalg.norm(bisector)\n    return vertex + dist * bisector\n\ndef orthocenter(A, B, C):\n    """Returns orthocenter of triangle ABC."""\n    foot_B = foot_of_perpendicular(B, A, C)\n    foot_C = foot_of_perpendicular(C, A, B)\n    return line_intersection(B, foot_B, C, foot_C)\n```\n\n### Object registry\n\nAfter computing all coordinates, output a complete registry before writing any code:\n\n```\n| Variable name | Type             | Construction                      |\n|---------------|------------------|-----------------------------------|\n| A             | np.ndarray point | fixed at origin                   |\n| B             | np.ndarray point | fixed on x-axis                   |\n| C             | np.ndarray point | chosen to satisfy constraints     |\n| O             | np.ndarray point | circumcenter(A, B, C)             |\n| D             | np.ndarray point | foot_of_perpendicular(A, B, C)    |\n| E             | np.ndarray point | circle_line_intersect(O, r, A, D) |\n```\n\nEvery variable name used in the Manim code must appear in this registry. Do not introduce any variable name in the code that is not listed here.\n\n---\n\n# SECTION 5 — ANIMATION PLAN\n\nBefore writing any Manim code, output the full animation plan as a sequence of comment blocks. Each block corresponds to one drawing step and must follow this format:\n\n```python\n# --- Step N: <object name> ---\n# Text: "<exact chunk from problem description>"\n# Is question: <true / false>\n# New object(s): <variable names from registry>\n# Manim object(s): <e.g. dot_A, label_A, seg_AB>\n# Semantic call(s): <e.g. draw_point("A", A, UP), draw_segment(A, B, color=BLUE)>\n# Highlight: <which Manim objects, in what order, and what color>\n```\n\nObjects must be named alphabetically to ensure consistency throughtout the code. For example, use `seg_AO` instead of `seg_OA`\n\nBefore writing any comment blocks, identify which segments belong to the same polygon and assign each polygon a color from this order: first polygon BLUE, second GREEN, third ORANGE. Annotate every affected segment\'s comment block with its polygon color so that the `draw_segment` calls are consistent throughout.\n\nRefer to the object registry to check if the new object is the result of `line_intersection` or `foot_of_perpendicular` construction. For intersection between two segments, call the `extend_segment_to_point` on each line and the intersection, and call `draw_segment` accordingly to visually connect the lines to the intersection. For foot of perpendicular from a point to a segment, call `extend_segment_to_point` on the segment, and draw a new segment from the point to the foot.\n\nFor question steps, the highlight field must list segment Manim objects (e.g. `seg_AB`, `seg_AC`), not endpoint dots or labels. For questions involving products or ratios such as AB·AC = AE·AS, highlight segments grouped by side of the equation — first group, brief pause, second group.\n\nDo not write any scene code until the full comment plan is complete.\n\n---\n\n# SECTION 6 — MANIM SCRIPT\n\nOnly after the animation plan is complete.\n\n## Script structure\n\nOrganise in this exact order:\n1. Imports\n2. Coordinate constraint solver functions\n3. All coordinate computations (pure numpy, no Manim objects)\n4. Scene class\n\nAlways output full script. Do not skip predefined sections.\n\n## Drawing conventions\n\nDo not use Manim\'s `Polygon` class for rendering edges. All polygon edges must be drawn as individual named `Line` segments. This allows each edge to be independently highlighted, extended, or referenced by name. Name each segment by its endpoints, e.g. `seg_AB`, `seg_BC`, `seg_AC`.\n\nSegments belonging to the same polygon must all use the same color, as assigned during the animation plan phase.\n\nWhen a new intersection point is introduced on two existing segments, redraw those segments as two pieces each meeting at the intersection point. For example, if E lies on segment AB, replace `seg_AB` with `seg_AE` and `seg_BE`. Use `extend_segment_to_point` to determine which end to extend. Reflect this split in the object registry.\n\n## Semantic visualisation interface\n\nThe scene class must implement and use the following interface. Do not bypass these methods with raw Manim calls in the animation body.\n\n```python\nclass GeometryScene(MovingCameraScene):\n\n    def setup(self):\n        self.__all_objects = []   # all mobjects added to the scene, except step text\n        self.__step_text = None   # reference to current Text mobject\n\n    def draw_point(self, label, coords, direction=UP) -> tuple:\n        """\n        Creates Dot and MathTex label at coords.\n        Label placed with .next_to(dot, direction, buff=0.15).\n        Choose direction away from adjacent objects.\n        Appends both to __all_objects.\n        Calls __fit_camera.\n        Animates both with FadeIn, run_time 0.2.\n        Returns (Dot, MathTex).\n        """\n\n    def draw_segment(self, P, Q, color=GRAY) -> Line:\n        """\n        Creates Line between P and Q.\n        Appends to __all_objects.\n        Calls __fit_camera.\n        Animates with Create, run_time 0.5.\n        Returns Line.\n        """\n\n    def draw_circle(self, center, radius, color=TEAL) -> Circle:\n        """\n        Creates Circle at center with given radius.\n        Appends to __all_objects.\n        Calls __fit_camera.\n        Animates with Create, run_time 0.5.\n        Returns Circle.\n        """\n\n    def __fit_camera(self, margin=1):\n        """\n        Fits camera to bounding box of __all_objects and __step_text combined.\n        Uses self.camera.auto_zoom.\n        """\n\n    def highlight(self, *objects, color=YELLOW, duration=0.5):\n        """\n        Highlights given mobjects by changing their stroke or fill color.\n\t\tRemove and add mobjects before animation to make sure they are not obscure by other mobjects.\n        Reverts to original color after duration.\n        Arguments must be Manim mobjects (Line, Dot, Circle), not numpy arrays.\n        For question highlights: color=RED, duration=1.5.\n        For newly introduced objects: color=YELLOW, duration=0.5.\n        For segment relationship questions: pass segment Line objects only,\n        not their endpoint Dots or labels.\n        """\n\n    def set_step_text(self, string):\n        """\n        Removes current __step_text if it exists.\n        Creates new Text mobject.\n        Positions it next_to __all_objects bounding box, direction UP.\n        Updates __step_text reference.\n        Calls __fit_camera.\n        Animates with Write.\n        """\n```\n\nImplement each method fully before writing the animation body. The animation body must only call these methods — no raw `self.play`, `self.wait`, `self.add`, or `self.camera` calls outside of the method implementations.\n\n## Colour conventions\n\n| Object type | Colour |\n|---|---|\n| Points / dots | WHITE |\n| Segments / lines / rays | GRAY (unless part of a polygon) |\n| First polygon edges | BLUE |\n| Second polygon edges | GREEN |\n| Third polygon edges | ORANGE |\n| Circles | TEAL |\n| New object highlight | YELLOW |\n| Question highlight | RED |\n\n---',
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "Cho tam giác ABC có ba góc nhọn (AB < AC), nội tiếp đường tròn (O). Đường cao AD của tam giác ABC cắt đường tròn (O) tại điểm E (E khác A). Gọi K là chân đường vuông góc kẻ từ điểm E đến đường thẳng AB.\na) Chứng minh bốn điểm E, D, B, K cùng thuộc một đường tròn.\nb) Đường thẳng AO cắt đường thẳng BC tại điểm S. Chứng minh EA là tia phân giác của góc CEK và AB.AC = AE.AS.\nc) Gọi H là trực tâm của tam giác ABC và I là trung điểm của đoạn thẳng AB. Chứng minh đường thẳng SI vuông góc với đường thẳng HK.",
                }
            ],
        },
        {
            "role": "assistant",
            "content": [
                {
                    "type": "text",
                    "text": """# SECTION 1 — GEOMETRIC STRUCTURE EXTRACTION

### Points

* A — free (base point)
* B — free (on x-axis)
* C — free (forms acute triangle, AB < AC)
* O — derived (circumcenter of triangle ABC)
* D — derived (foot of perpendicular from A to BC)
* E — derived (second intersection of line AD with circumcircle (O), E ≠ A)
* K — derived (foot of perpendicular from E to AB)
* S — derived (intersection of AO and BC)
* H — derived (orthocenter of triangle ABC)
* I — derived (midpoint of AB)

---

### Lines / Segments / Rays

* AB, BC, CA — triangle edges
* AD — altitude from A to BC
* EK — perpendicular from E to AB
* AO — line from A to circumcenter
* SI — segment
* HK — segment

---

### Circles

* (O) — circumcircle of triangle ABC
* Circle through E, D, B, K — to be proven cyclic

---

### Relationships

* Triangle ABC is acute, AB < AC
* A, B, C lie on circumcircle (O)
* AD ⟂ BC
* E = second intersection of AD with (O)
* EK ⟂ AB
* S = AO ∩ BC
* H = orthocenter (intersection of altitudes)
* I = midpoint of AB

---

### Goals

a) Prove E, D, B, K are concyclic
b) Prove:

* EA is angle bisector of ∠CEK
* AB·AC = AE·AS
    c) Prove SI ⟂ HK

---

# SECTION 2 — CONSTRUCTION DEPENDENCY GRAPH

```
A:
    depends_on: none
    method: fixed base point

B:
    depends_on: none
    method: fixed on x-axis

C:
    depends_on: A, B
    method: free point forming acute triangle with AB < AC

O:
    depends_on: A, B, C
    method: circumcenter(A, B, C)

D:
    depends_on: A, B, C
    method: foot_of_perpendicular(A, B, C)

circumcircle:
    depends_on: O, A
    method: circle with center O and radius OA

E:
    depends_on: A, D, O
    method: circle_line_intersect(O, OA, A, D), take point ≠ A

K:
    depends_on: E, A, B
    method: foot_of_perpendicular(E, A, B)

S:
    depends_on: A, O, B, C
    method: line_intersection(A, O, B, C)

H:
    depends_on: A, B, C
    method: orthocenter(A, B, C)

I:
    depends_on: A, B
    method: midpoint(A, B)
```

All dependencies are valid.

---

# SECTION 3 — GEOMETRIC CONSISTENCY CHECK

* [✓] Every point has valid construction
* [✓] No circular dependencies
* [✓] All intersections use defined objects
* [✓] No coordinate assumptions beyond base frame
* [✓] Circle defined from valid inputs
* [✓] All perpendiculars/midpoints constructible

---

# SECTION 4 — COORDINATE REALIZATION

### Base frame

```python
A = np.array([0, 0, 0])
B = np.array([4, 0, 0])
C = np.array([1.5, 3, 0])
```

### Derived computations

```python
O = circumcenter(A, B, C)
D = foot_of_perpendicular(A, B, C)
r = np.linalg.norm(A - O)

E_candidates = circle_line_intersect(O, r, A, D)
E = E_candidates[0] if np.linalg.norm(E_candidates[0] - A) > 1e-6 else E_candidates[1]

K = foot_of_perpendicular(E, A, B)
S = line_intersection(A, O, B, C)
H = orthocenter(A, B, C)
I = midpoint(A, B)
```

---

### Object Registry

```
| Variable | Type             | Construction                         |
|----------|------------------|--------------------------------------|
| A        | point            | fixed                                |
| B        | point            | fixed                                |
| C        | point            | free                                 |
| O        | point            | circumcenter(A,B,C)                  |
| D        | point            | foot_of_perpendicular(A, B, C)       |
| E        | point            | circle_line_intersect(O,r,A,D)       |
| K        | point            | foot_of_perpendicular(E, A, B)       |
| S        | point            | intersection(AO, BC)                 |
| H        | point            | orthocenter(A,B,C)                  |
| I        | point            | midpoint(A,B)                        |
```

---

# SECTION 5 — ANIMATION PLAN

### Polygon assignment

* Triangle ABC → BLUE

---

```python
# --- Step 1: Triangle ABC ---
# Text: "Cho tam giác ABC có ba góc nhọn (AB < AC)"
# Is question: false
# New object(s): A, B, C, seg_AB, seg_BC, seg_CA
# Manim object(s): dot_A, dot_B, dot_C, seg_AB, seg_BC, seg_CA
# Semantic call(s): draw_point, draw_segment (BLUE)
# Highlight: triangle edges YELLOW
```

```python
# --- Step 2: Circumcircle ---
# Text: "nội tiếp đường tròn (O)"
# Is question: false
# New object(s): O, circle_O
# Manim object(s): dot_O, circle_O
# Semantic call(s): draw_point, draw_circle
# Highlight: circle_O
```

```python
# --- Step 3: Altitude AD ---
# Text: "Đường cao AD của tam giác ABC"
# Is question: false
# New object(s): D, seg_AD
# Manim object(s): dot_D, seg_AD
# Semantic call(s): draw_point, draw_segment
# Highlight: seg_AD
```

```python
# --- Step 4: Point E ---
# Text: "cắt đường tròn (O) tại điểm E"
# Is question: false
# New object(s): E
# Manim object(s): dot_E
# Semantic call(s): draw_point
# Highlight: dot_E
```

```python
# --- Step 5: Foot K ---
# Text: "Gọi K là chân đường vuông góc kẻ từ điểm E đến đường thẳng AB"
# Is question: false
# New object(s): K, seg_EK
# Manim object(s): dot_K, seg_EK
# Semantic call(s): draw_point, draw_segment
# Highlight: seg_EK
```

```python
# --- Step 6: Cyclic quadrilateral ---
# Text: "Chứng minh bốn điểm E, D, B, K cùng thuộc một đường tròn"
# Is question: true
# New object(s): none
# Manim object(s): seg_DB, seg_BK, seg_KE, seg_ED
# Semantic call(s): highlight
# Highlight: seg_DB, seg_BK, seg_KE, seg_ED (RED)
```

```python
# --- Step 7: Point S ---
# Text: "Đường thẳng AO cắt đường thẳng BC tại điểm S"
# Is question: false
# New object(s): S
# Manim object(s): dot_S
# Semantic call(s): draw_point
# Highlight: dot_S
```

```python
# --- Step 8: Angle bisector ---
# Text: "Chứng minh EA là tia phân giác của góc CEK"
# Is question: true
# New object(s): none
# Manim object(s): seg_EA, seg_EC, seg_EK
# Semantic call(s): highlight
# Highlight: seg_EC, seg_EK then seg_EA (RED)
```

```python
# --- Step 9: Product equality ---
# Text: "AB.AC = AE.AS"
# Is question: true
# New object(s): none
# Manim object(s): seg_AB, seg_AC, seg_AE, seg_AS
# Semantic call(s): highlight
# Highlight: seg_AB, seg_AC then seg_AE, seg_AS (RED)
```

```python
# --- Step 10: Orthocenter H ---
# Text: "Gọi H là trực tâm của tam giác ABC"
# Is question: false
# New object(s): H
# Manim object(s): dot_H
# Semantic call(s): draw_point
# Highlight: dot_H
```

```python
# --- Step 11: Midpoint I ---
# Text: "I là trung điểm của đoạn thẳng AB"
# Is question: false
# New object(s): I
# Manim object(s): dot_I
# Semantic call(s): draw_point
# Highlight: dot_I
```

```python
# --- Step 12: Perpendicular SI ⟂ HK ---
# Text: "Chứng minh đường thẳng SI vuông góc với đường thẳng HK"
# Is question: true
# New object(s): seg_SI, seg_HK
# Manim object(s): seg_SI, seg_HK
# Semantic call(s): draw_segment, highlight
# Highlight: seg_SI, seg_HK (RED)
```

---

# SECTION 6 — MANIM SCRIPT

```python
from manim import *
import numpy as np

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
    ax, ay = A[:2]; bx, by = B[:2]; cx, cy = C[:2]
    D = 2 * (ax*(by-cy) + bx*(cy-ay) + cx*(ay-by))
    ux = ((ax**2+ay**2)*(by-cy) + (bx**2+by**2)*(cy-ay) + (cx**2+cy**2)*(ay-by)) / D
    uy = ((ax**2+ay**2)*(cx-bx) + (bx**2+by**2)*(ax-cx) + (cx**2+cy**2)*(bx-ax)) / D
    return np.array([ux, uy, 0])

def circle_line_intersect(center, radius, P, Q):
    d = Q - P
    f = P - center
    a = np.dot(d, d)
    b = 2 * np.dot(f, d)
    c = np.dot(f, f) - radius**2
    disc = b**2 - 4*a*c
    if disc < 0:
        return []
    res = []
    for s in [-1, 1]:
        t = (-b + s*np.sqrt(disc))/(2*a)
        res.append(P + t*d)
    return res

def orthocenter(A, B, C):
    foot_B = foot_of_perpendicular(B, A, C)
    foot_C = foot_of_perpendicular(C, A, B)
    return line_intersection(B, foot_B, C, foot_C)

# ================= COORDINATES =================

A = np.array([0,0,0])
B = np.array([4,0,0])
C = np.array([1.5,3,0])

O = circumcenter(A,B,C)
D = foot_of_perpendicular(A,B,C)
r = np.linalg.norm(A-O)

E_candidates = circle_line_intersect(O,r,A,D)
E = E_candidates[0] if np.linalg.norm(E_candidates[0]-A)>1e-6 else E_candidates[1]

K = foot_of_perpendicular(E,A,B)
S = line_intersection(A,O,B,C)
H = orthocenter(A,B,C)
I = midpoint(A,B)

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
        anims = [obj.animate.set_color(color) for obj in objects]
        self.play(*anims)
        self.wait(duration)
        self.play(*[obj.animate.set_color(WHITE if isinstance(obj, Dot) else obj.get_color()) for obj in objects])

    def set_step_text(self, string):
        if self.__step_text:
            self.remove(self.__step_text)
        self.__step_text = Text(string).scale(0.5)
        self.__fit_camera()
        self.play(Write(self.__step_text))

    def construct(self):

        self.setup()

        self.set_step_text("Triangle ABC")
        dot_A,_=self.draw_point("A",A)
        dot_B,_=self.draw_point("B",B)
        dot_C,_=self.draw_point("C",C)

        seg_AB=self.draw_segment(A,B,BLUE)
        seg_BC=self.draw_segment(B,C,BLUE)
        seg_CA=self.draw_segment(C,A,BLUE)

        self.set_step_text("Circumcircle")
        dot_O,_=self.draw_point("O",O)
        circle_O=self.draw_circle(O,np.linalg.norm(A-O))

        self.set_step_text("Altitude AD")
        dot_D,_=self.draw_point("D",D)
        seg_AD=self.draw_segment(A,D)

        self.set_step_text("Point E")
        dot_E,_=self.draw_point("E",E)

        self.set_step_text("Foot K")
        dot_K,_=self.draw_point("K",K)
        seg_EK=self.draw_segment(E,K)

        self.set_step_text("Cyclic EDBK")
        self.highlight(seg_BC, seg_AB, seg_AD, seg_EK, color=RED, duration=1.5)

        self.set_step_text("Point S")
        dot_S,_=self.draw_point("S",S)

        self.set_step_text("Angle bisector")
        seg_EA=self.draw_segment(E,A)
        seg_EC=self.draw_segment(E,C)
        self.highlight(seg_EC, seg_EK, color=RED, duration=1)
        self.highlight(seg_EA, color=RED, duration=1)

        self.set_step_text("Product equality")
        seg_AC=self.draw_segment(A,C,BLUE)
        seg_AS=self.draw_segment(A,S)
        self.highlight(seg_AB, seg_AC, color=RED, duration=1)
        self.highlight(seg_EA, seg_AS, color=RED, duration=1)

        self.set_step_text("Orthocenter H")
        dot_H,_=self.draw_point("H",H)

        self.set_step_text("Midpoint I")
        dot_I,_=self.draw_point("I",I)

        self.set_step_text("SI ⟂ HK")
        seg_SI=self.draw_segment(S,I)
        seg_HK=self.draw_segment(H,K)
        self.highlight(seg_SI, seg_HK, color=RED, duration=1.5)
```""",
                }
            ],
        },
    ],
    thinking={"type": "adaptive"},
    output_config={"effort": "high"},
)

print(message.model_dump_json())

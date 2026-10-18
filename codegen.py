"""Generate a Manim CE scene script from a topic + animation type.

Usage:
    python codegen.py "<topic>" <anim_type> <duration_seconds> <orientation> > scene.py

anim_type: stick_figure | whiteboard | kinetic_typography | motion_graphics |
           puppet | infographic | background_loop | vertical_shorts
orientation: landscape | vertical
"""
import sys


def esc(s: str) -> str:
    return s.replace("\\", "\\\\").replace('"', '\\"')


TOPIC = esc(sys.argv[1]) if len(sys.argv) > 1 else "Hello World"
DURATION = sys.argv[2] if len(sys.argv) > 2 else "8"
ANIM_TYPE = sys.argv[3] if len(sys.argv) > 3 else "motion_graphics"
ORIENTATION = sys.argv[4] if len(sys.argv) > 4 else "landscape"

# Orientation block injected into Scene init so Manim renders the right canvas.
ORIENT_BLOCK = ""
if ORIENTATION == "vertical":
    ORIENT_BLOCK = '''
    def __init__(self, **kwargs):
        kwargs["pixel_height"] = 1920
        kwargs["pixel_width"] = 1080
        kwargs["frame_rate"] = 30
        super().__init__(**kwargs)
'''


STICK_FIGURE = f'''from manim import *

class GeneratedScene(Scene):
{ORIENT_BLOCK}
    def construct(self):
        title = Text("{TOPIC}", font_size=36)
        title.to_edge(UP, buff=0.5)

        body = Line(UP * 0.8, DOWN * 0.8, color=WHITE)
        head = Circle(radius=0.3, color=WHITE).move_to(UP * 1.1)
        eyes = VGroup(
            Dot(radius=0.05).move_to(LEFT * 0.1 + UP * 1.2),
            Dot(radius=0.05).move_to(RIGHT * 0.1 + UP * 1.2)
        )
        arms = Line(LEFT * 0.6, RIGHT * 0.6, color=WHITE).move_to(UP * 0.4)
        legs = VGroup(
            Line(DOWN * 0.8, DOWN * 0.8 + RIGHT * 0.5, color=WHITE),
            Line(DOWN * 0.8, DOWN * 0.8 + LEFT * 0.5, color=WHITE)
        )
        figure = VGroup(body, head, eyes, arms, legs)

        self.play(Write(title))
        self.play(Create(figure))
        self.play(figure.animate.shift(RIGHT * 3), run_time=2)
        self.play(figure.animate.shift(LEFT * 3), run_time=2)
        self.wait({DURATION})
'''

WHITEBOARD = f'''from manim import *

class GeneratedScene(Scene):
{ORIENT_BLOCK}
    def construct(self):
        title = Text("{TOPIC}", font_size=40)
        title.to_edge(UP, buff=0.5)

        box = RoundedRectangle(corner_radius=0.2, width=4.5, height=2.2, color=BLUE)
        box.move_to(DOWN * 0.3)
        label = Text("Main Idea", font_size=24).move_to(box.get_center())
        arrow = Arrow(LEFT * 3, LEFT * 1.2, color=YELLOW).move_to(UP * 0.5)

        self.play(Write(title))
        self.wait(0.5)
        self.play(Create(box))
        self.play(Write(label))
        self.play(Create(arrow))
        self.wait({DURATION})
'''

KINETIC_TYPOGRAPHY = f'''from manim import *

class GeneratedScene(Scene):
{ORIENT_BLOCK}
    def construct(self):
        words = "{TOPIC}".split()
        mobjs = []
        for i, w in enumerate(words):
            t = Text(w, font_size=34)
            t.move_to(LEFT * 3.5 + RIGHT * i * 1.4 + UP * (0.4 * (i % 2)))
            mobjs.append(t)

        for t in mobjs:
            self.play(FadeIn(t, shift=UP * 0.5), run_time=0.45)
        self.wait({DURATION})
'''

MOTION_GRAPHICS = f'''from manim import *

class GeneratedScene(Scene):
{ORIENT_BLOCK}
    def construct(self):
        title = Text("{TOPIC}", font_size=34)
        title.to_edge(UP, buff=0.5)

        shapes = VGroup(
            Square(side_length=1, color=RED),
            Circle(radius=0.5, color=GREEN),
            Triangle(color=BLUE),
            RegularPolygon(n=6, color=ORANGE)
        )
        shapes.arrange(RIGHT, buff=0.9)
        shapes.move_to(DOWN * 0.2)

        self.play(Write(title))
        self.play(Create(shapes))
        self.play(
            shapes[0].animate.scale(1.6).set_color(YELLOW),
            shapes[1].animate.shift(UP * 1.5),
            shapes[2].animate.rotate(PI),
            shapes[3].animate.set_fill(PURPLE, opacity=0.6),
            run_time=2
        )
        self.wait({DURATION})
'''

PUPPET = f'''from manim import *

class GeneratedScene(Scene):
{ORIENT_BLOCK}
    def construct(self):
        title = Text("{TOPIC}", font_size=34)
        title.to_edge(UP, buff=0.5)

        # Simple cutout puppet: head + body + limbs
        head = Ellipse(width=0.9, height=1.1, color=ORANGE).set_fill(ORANGE, opacity=1)
        body = RoundedRectangle(width=0.9, height=1.4, color=BLUE).set_fill(BLUE, opacity=0.9).next_to(head, DOWN, buff=0.1)
        l_arm = Line(LEFT * 0.5, LEFT * 1.2, color=ORANGE, stroke_width=6).next_to(body.get_top(), LEFT, buff=0.1)
        r_arm = Line(RIGHT * 0.5, RIGHT * 1.2, color=ORANGE, stroke_width=6).next_to(body.get_top(), RIGHT, buff=0.1)
        l_leg = Line(DOWN * 0.2, DOWN * 1.0 + LEFT * 0.4, color=ORANGE, stroke_width=6).next_to(body.get_bottom(), LEFT, buff=0.1)
        r_leg = Line(DOWN * 0.2, DOWN * 1.0 + RIGHT * 0.4, color=ORANGE, stroke_width=6).next_to(body.get_bottom(), RIGHT, buff=0.1)

        puppet = VGroup(head, body, l_arm, r_arm, l_leg, r_leg)
        puppet.move_to(ORIGIN)

        self.play(Write(title))
        self.play(Create(puppet))
        self.play(puppet.animate.shift(RIGHT * 2), run_time=1.5)
        self.play(puppet.animate.shift(LEFT * 4), run_time=1.5)
        self.play(puppet.animate.shift(RIGHT * 2), run_time=1.5)
        self.wait({DURATION})
'''

INFOGRAPHIC = f'''from manim import *

class GeneratedScene(Scene):
{ORIENT_BLOCK}
    def construct(self):
        title = Text("{TOPIC}", font_size=34)
        title.to_edge(UP, buff=0.5)

        values = [3, 5, 2, 7, 4]
        bars = VGroup()
        labels = VGroup()
        colors = [RED, ORANGE, YELLOW, GREEN, BLUE]
        for i, v in enumerate(values):
            bar = Rectangle(width=0.7, height=v * 0.8, color=colors[i]).set_fill(colors[i], opacity=0.9)
            bar.move_to(LEFT * 1.8 + RIGHT * i * 0.9 + DOWN * 1.6 + UP * (v * 0.4))
            txt = Text(str(v), font_size=20).next_to(bar, UP, buff=0.15)
            bars.add(bar)
            labels.add(txt)

        self.play(Write(title))
        self.play(Create(bars), Write(labels), run_time=2)
        self.wait({DURATION})
'''

BACKGROUND_LOOP = f'''from manim import *

class GeneratedScene(Scene):
{ORIENT_BLOCK}
    def construct(self):
        title = Text("{TOPIC}", font_size=30)
        title.to_edge(UP, buff=0.4)

        rings = VGroup()
        for i in range(6):
            r = Circle(radius=0.6 + i * 0.35, color=interpolate_color(BLUE, PURPLE, i / 6))
            r.set_stroke(width=2, opacity=0.8)
            rings.add(r)
        rings.move_to(DOWN * 0.4)

        self.play(Write(title))
        self.play(Create(rings))
        self.play(
            rings.animate.rotate(PI * 2),
            run_time=3,
            rate_func=linear
        )
        self.wait({DURATION})
'''

VERTICAL_SHORTS = f'''from manim import *

class GeneratedScene(Scene):
{ORIENT_BLOCK}
    def construct(self):
        title = Text("{TOPIC}", font_size=36)
        title.move_to(UP * 1.5)

        body = Line(UP * 0.8, DOWN * 0.8, color=WHITE)
        head = Circle(radius=0.3, color=WHITE).move_to(UP * 1.1)
        arms = Line(LEFT * 0.6, RIGHT * 0.6, color=WHITE).move_to(UP * 0.4)
        legs = VGroup(
            Line(DOWN * 0.8, DOWN * 0.8 + RIGHT * 0.5, color=WHITE),
            Line(DOWN * 0.8, DOWN * 0.8 + LEFT * 0.5, color=WHITE)
        )
        figure = VGroup(body, head, arms, legs)

        self.play(Write(title))
        self.play(Create(figure))
        self.play(figure.animate.shift(RIGHT * 2), run_time=1.5)
        self.play(figure.animate.shift(LEFT * 4), run_time=1.5)
        self.play(figure.animate.shift(RIGHT * 2), run_time=1.5)
        self.wait({DURATION})
'''

TEMPLATES = {
    "stick_figure": STICK_FIGURE,
    "whiteboard": WHITEBOARD,
    "kinetic_typography": KINETIC_TYPOGRAPHY,
    "motion_graphics": MOTION_GRAPHICS,
    "puppet": PUPPET,
    "infographic": INFOGRAPHIC,
    "background_loop": BACKGROUND_LOOP,
    "vertical_shorts": VERTICAL_SHORTS,
}

if __name__ == "__main__":
    print(TEMPLATES.get(ANIM_TYPE, MOTION_GRAPHICS))

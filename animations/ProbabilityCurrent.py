from manim import *
import numpy as np
from scipy.fft import fft, ifft, fftfreq

class ProbabilityCurrent(Scene):
    def __init__(self, whattime_scene2=8, whattime_scene3=20, **kwargs):
        super().__init__(**kwargs)
        self.whattime_scene2 = whattime_scene2
        self.whattime_scene3 = whattime_scene3

        # Физические константы
        self.hbar = 1.0
        self.m = 1.0
        self.X_MIN, self.X_MAX = -15.0, 15.0
        self.SAMPLES = 2048 # Для FFT лучше степени двойки

        # Атрибуты для симуляции
        self.x_vals = np.linspace(self.X_MIN, self.X_MAX, self.SAMPLES)
        self.psi_t = None
        self.potential_v = None
        self.k_vals = fftfreq(self.SAMPLES, d=self.x_vals[1] - self.x_vals[0]) * 2 * np.pi

    def intro(self, title_text):
        title = Text(title_text).to_edge(UP)
        self.play(Write(title))
        self.wait(1)
        return title

    def outro(self):
        thanks = Text("Спасибо за внимание!").scale(1.2)
        self.play(Write(thanks))
        self.wait(2)
        self.play(FadeOut(thanks))

    # ===================== ФИЗИЧЕСКИЕ МЕТОДЫ =====================
    def _psi_initial(self, x, sigma=0.5, k0=5.0, x0=-5.0):
        return (2 * np.pi * sigma**2)**(-0.25) * np.exp(-((x - x0)**2) / (4 * sigma**2)) * np.exp(1j * k0 * x)

    def _potential_step(self, x, U0=3.0):
        return np.piecewise(x, [x < 0, x >= 0], [0, U0])

    def _evolve_split_step(self, dt):
        self.psi_t *= np.exp(-1j * self.potential_v * dt / (2 * self.hbar))
        self.psi_t = fft(self.psi_t)
        self.psi_t *= np.exp(-1j * self.hbar * self.k_vals**2 * dt / (2 * self.m))
        self.psi_t = ifft(self.psi_t)
        self.psi_t *= np.exp(-1j * self.potential_v * dt / (2 * self.hbar))

    def _get_psi_data_numerical(self):
        return np.abs(self.psi_t)**2

    # ===================== ГРАФИЧЕСКИЕ УТИЛИТЫ ===================
    def _make_axes(self, y_range=[-0.5, 1.5, 0.5]):
        ax = Axes(
            x_range=[self.X_MIN, self.X_MAX, 2], y_range=y_range,
            x_length=12, y_length=6, tips=False,
            axis_config={"include_numbers": True}
        )
        labels = VGroup(
            MathTex("x").scale(0.8).next_to(ax.x_axis, RIGHT, buff=0.2),
            MathTex(r"|\psi|^2, V(x)").scale(0.8).next_to(ax.y_axis, UP, buff=0.2),
        )
        return ax, labels

    # ===================== КОНСТРУКТОРЫ СЦЕН =====================
    def construct_scene1_derivation(self):
        title = self.intro("Вывод уравнения непрерывности")
        
        schrodinger_eq = MathTex(r"i\hbar \frac{\partial \psi}{\partial t} = -\frac{\hbar^2}{2m}\frac{\partial^2 \psi}{\partial x^2} + V\psi", font_size=38).shift(UP * 2)
        schrodinger_conj_eq = MathTex(r"-i\hbar \frac{\partial \psi^*}{\partial t} = -\frac{\hbar^2}{2m}\frac{\partial^2 \psi^*}{\partial x^2} + V\psi^*", font_size=38).next_to(schrodinger_eq, DOWN, buff=0.5)
        
        prob_density = MathTex(r"P = |\psi|^2 = \psi^*\psi", font_size=42).move_to(schrodinger_eq.get_center() + DOWN * 2.5)
        self.play( Write(prob_density))
        self.wait(2)

        time_derivative = MathTex(r"\frac{\partial P}{\partial t} = \frac{\partial \psi^*}{\partial t}\psi + \psi^*\frac{\partial \psi}{\partial t}", font_size=42).move_to(prob_density.get_center())
        self.play(ReplacementTransform(prob_density, time_derivative))
        self.wait(2)

        self.play(Write(schrodinger_eq), Write(schrodinger_conj_eq))
        self.wait(2)

        after_substitution = MathTex(r"\frac{\partial P}{\partial t} = \frac{i\hbar}{2m}(\psi\frac{\partial^2 \psi^*}{\partial x^2} - \psi^*\frac{\partial^2 \psi}{\partial x^2})", font_size=42).move_to(time_derivative.get_center())
        self.play(FadeOut(schrodinger_eq), FadeOut(schrodinger_conj_eq), ReplacementTransform(time_derivative, after_substitution))
        self.wait(3)

        continuity_eq_form = MathTex(r"\frac{\partial P}{\partial t} = -\frac{\partial}{\partial x}\left[ \frac{i\hbar}{2m}(\psi^*\frac{\partial \psi}{\partial x} - \psi\frac{\partial \psi^*}{\partial x}) \right]", font_size=38)
        self.play(ReplacementTransform(after_substitution, continuity_eq_form))
        self.wait(3)

        continuity_final = MathTex(r"\frac{\partial P}{\partial t} + \frac{\partial j}{\partial x} = 0", font_size=48).move_to(UP * 0.5)
        prob_current_formula = MathTex(r"j(x,t) = \frac{-i\hbar}{m} (\psi^*\frac{\partial \psi}{\partial x}-\psi\frac{\partial \psi^*}{\partial x})", font_size=48).next_to(continuity_final, DOWN, buff=0.8)
        self.play(ReplacementTransform(continuity_eq_form, continuity_final), Write(prob_current_formula))
        
        frame = SurroundingRectangle(prob_current_formula, color=YELLOW)
        self.play(Create(frame))
        self.wait(4)

        self.play(FadeOut(VGroup(title, continuity_final, prob_current_formula, frame)))

    def construct_scene2_wavepacket(self):
        title = self.intro("Свободный волновой пакет")
        
        psi_formula = MathTex(r"\psi(x,0) \sim e^{-\frac{(x-x_0)^2}{4\sigma^2}} e^{ik_0x}", font_size=42)
        psi_formula.to_corner(UR).shift(DOWN * 1.5)
        self.play(Write(psi_formula))
        self.play(FadeOut(title))

        ax, labels = self._make_axes()
        self.play(Create(ax), FadeIn(labels))

        self.potential_v = self._potential_step(self.x_vals, U0=0)
        self.psi_t = self._psi_initial(self.x_vals, k0=5, sigma=1.0, x0=-7.0)

        density_graph = always_redraw(
            lambda: ax.plot(lambda x: np.interp(x, self.x_vals, self._get_psi_data_numerical()), color=BLUE, use_smoothing=False).set_stroke(width=4)
        )
        self.add(density_graph)

        dt = 0.02
        num_steps = int(self.whattime_scene2 / dt)
        for _ in range(num_steps):
            self._evolve_split_step(dt)
            self.wait(1/self.camera.frame_rate)

        self.wait(2)
        self.play(FadeOut(VGroup(psi_formula, ax, labels, density_graph)))

    def construct_scene3_scattering(self):
        U0 = 10.0
        title = self.intro(f"Рассеяние на ступеньке, E < U0 (U0={U0})")
        self.play(FadeOut(title))

        ax, labels = self._make_axes(y_range=[-0.5, U0 + 1, 2])
        self.play(Create(ax), FadeIn(labels))

        self.potential_v = self._potential_step(self.x_vals, U0=U0)
        self.psi_t = self._psi_initial(self.x_vals, k0=5, sigma=1.0)
        
        potential_graph = ax.plot(lambda x: self._potential_step(x, U0=U0), color=RED, use_smoothing=False)
        potential_label = MathTex("V(x)", color=RED).next_to(potential_graph, UR, buff=-0.8)
        self.play(Create(potential_graph), Write(potential_label))

        density_graph = always_redraw(
            lambda: ax.plot(lambda x: np.interp(x, self.x_vals, self._get_psi_data_numerical()), color=BLUE, use_smoothing=False).set_stroke(width=4)
        )
        self.add(density_graph)

        dt = 0.01
        num_steps = int(self.whattime_scene3 / dt)
        for _ in range(num_steps):
            self._evolve_split_step(dt)
            self.wait(1/self.camera.frame_rate)

        self.wait(2)
        self.play(FadeOut(VGroup(ax, labels, potential_graph, potential_label, density_graph)))

    # ===================== ГЛАВНЫЙ КОНСТРУКТОР =====================
    def construct(self):
        self.construct_scene1_derivation()
        # self.construct_scene2_wavepacket()
        # self.construct_scene3_scattering()
        self.outro()

if __name__ == "__main__":
    scene = ProbabilityCurrent()
    scene.render()
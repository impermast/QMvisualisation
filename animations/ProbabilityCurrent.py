from manim import *
import numpy as np
from scipy.fft import fft, ifft, fftfreq

class ProbabilityCurrent(Scene):
    DESCRIPTION = "Описание анимации 'Поток вероятности': Эта анимация объясняет концепцию потока вероятности в квантовой механике. Она включает вывод уравнения непрерывности, демонстрацию свободного волнового пакета и рассеяние волнового пакета на потенциальном барьере, визуализируя плотность вероятности и ток вероятности."

    @classmethod
    def get_info(cls):
        return {
            "name": cls.__name__,
            "description": cls.DESCRIPTION
        }
    def __init__(self, whattime = 50, num_steps = 200, **kwargs):
        super().__init__(**kwargs)
        self.whattime_scene1 = (3/10) * whattime
        self.whattime_scene2 = (3/10) * whattime
        self.whattime_scene3 = (4/10) * whattime

        # Физические константы
        self.hbar = 1.0
        self.m = 2.0
        self.num_steps = num_steps
        self.X_MIN, self.X_MAX = -10.0, 10.0
        self.SAMPLES = 2**15 # Для FFT лучше степени двойки

        # Атрибуты для симуляции
        self.psi_t = None
        self.potential_v = None
        self.x_vals = np.linspace(self.X_MIN, self.X_MAX, self.SAMPLES)
        self.k_vals = fftfreq(self.SAMPLES, d=self.x_vals[1] - self.x_vals[0]) * 2 * np.pi
        print(self.k_vals)

    def intro(self, title_text, dt = 1):
        title = Text(title_text).to_edge(UP)
        self.play(Write(title), run_time=1*dt)
        return title

    def outro(self, dt = 1):
        thanks = Text("Спасибо за внимание!").scale(1.2)
        self.play(Write(thanks), run_time=1*dt)
        self.wait(0.5*dt)
        self.play(FadeOut(thanks), run_time=0.5*dt)

    # ===================== ФИЗИЧЕСКИЕ МЕТОДЫ =====================
    def _psi_initial(self, x, sigma=0.1, k0=2.0, x0=-11.0):
        return (2 * np.pi * sigma**2)**(-0.25) * np.exp(-((x - x0)**2) / (4 * sigma**2)) * np.exp(1j * k0 * x)

    def _create_trapezoid_potential(self, x, U0, x_start, ramp_length):
        x_end_ramp = x_start + ramp_length
        conds = [
            x < x_start,
            (x >= x_start) & (x < x_end_ramp),
            x >= x_end_ramp
        ]
        funcs = [
            0,
            lambda x_in: U0 * (x_in - x_start) / ramp_length,
            U0
        ]
        return np.piecewise(x, conds, funcs)

    def _evolve_split_step(self, dt):
        self.psi_t *= np.exp(-1j * self.potential_v * dt / (2 * self.hbar))
        self.psi_t = fft(self.psi_t)
        self.psi_t *= np.exp(-1j * self.hbar * self.k_vals**2 * dt / (2 * self.m))
        self.psi_t = ifft(self.psi_t)
        self.psi_t *= np.exp(-1j * self.potential_v * dt / (2 * self.hbar))

    def _get_psi_data_numerical(self):
        return np.abs(self.psi_t)**2

    def _get_j_data_numerical(self):
        psi_k = fft(self.psi_t)

        # Фильтруем высокие частоты, чтобы сгладить производную
        k_cutoff = 20.0
        psi_k[np.abs(self.k_vals) > k_cutoff] = 0

        d_psi_dx_k = 1j * self.k_vals * psi_k
        d_psi_dx = ifft(d_psi_dx_k)
        
        j = (self.hbar / (2 * self.m * 1j)) * (np.conj(self.psi_t) * d_psi_dx - self.psi_t * np.conj(d_psi_dx))
        return np.real(j)

    def _get_psi_reflected_data(self):
        psi_r = self.psi_t.copy()
        psi_r[self.x_vals >= 0] = 0
        return np.abs(psi_r)**2

    def _get_psi_transmitted_data(self):
        psi_t = self.psi_t.copy()
        psi_t[self.x_vals < 0] = 0
        return np.abs(psi_t)**2

    # ===================== ГРАФИЧЕСКИЕ УТИЛИТЫ ===================
    def _make_axes(self, y_range=[-0.5, 1.2, 0.5]):
        ax = Axes(
            x_range=[self.X_MIN, self.X_MAX, 2], y_range=y_range,
            x_length=12, y_length=6, tips=False,
            axis_config={"include_numbers": True}
        )
        labels = VGroup(
            MathTex("x").scale(0.8).next_to(ax.x_axis, RIGHT, buff=0.2),
            MathTex(r"|\psi|^2, j").scale(0.8).next_to(ax.y_axis, UP, buff=0.2),
        )
        return ax, labels

    # ===================== КОНСТРУКТОРЫ СЦЕН =====================
    def construct_scene1_derivation(self):
        dt = self.whattime_scene1 / 24
        title = self.intro("Вывод уравнения непрерывности")

        # Schrodinger equations
        schrodinger_eq = MathTex(r"i\hbar \frac{\partial \psi}{\partial t} = -\frac{\hbar^2}{2m}\frac{\partial^2 \psi}{\partial x^2} + V\psi", font_size=38).shift(UP * 1.5)
        schrodinger_conj_eq = MathTex(r"-i\hbar \frac{\partial \psi^*}{\partial t} = -\frac{\hbar^2}{2m}\frac{\partial^2 \psi^*}{\partial x^2} + V\psi^*", font_size=38).next_to(schrodinger_eq, DOWN, buff=1)
        
        self.play(Write(schrodinger_eq), run_time=1*dt)
        self.play(Write(schrodinger_conj_eq), run_time=0.5*dt)
        self.wait(0.5*dt)

        # Multiply by psi* and psi
        eq1_mod = MathTex(r"\psi^* i\hbar \frac{\partial \psi}{\partial t} = -\psi^* \frac{\hbar^2}{2m}\frac{\partial^2 \psi}{\partial x^2} + \psi^* V\psi", font_size=38).move_to(schrodinger_eq)
        eq2_mod = MathTex(r"-\psi i\hbar \frac{\partial \psi^*}{\partial t} = -\psi \frac{\hbar^2}{2m}\frac{\partial^2 \psi^*}{\partial x^2} + \psi V\psi^*", font_size=38).move_to(schrodinger_conj_eq)

        self.play(
            Transform(schrodinger_eq, eq1_mod),
            Transform(schrodinger_conj_eq, eq2_mod), 
            run_time=1*dt
        )
        self.wait(2*dt)

        # Subtract equations
        subtracted_eq = MathTex(
            r"i\hbar \psi^*\frac{\partial \psi}{\partial t} + i\hbar\psi\frac{\partial \psi^*}{\partial t} = -\frac{\hbar^2}{2m}\psi^*\frac{\partial^2 \psi}{\partial x^2} +\frac{\hbar^2}{2m}\psi\frac{\partial^2 \psi^*}{\partial x^2}",
            font_size=38
        ).center()

        eq_group = VGroup(schrodinger_eq, schrodinger_conj_eq)
        self.play(Transform(eq_group, subtracted_eq), run_time=1*dt)
        self.wait(2*dt)

        # Simplify LHS to show time derivative
        continuity_eq_step1 = MathTex(
            r"i\hbar \frac{\partial (\psi^*\psi)}{\partial t} = -\frac{\hbar^2}{2m}(\psi^*\frac{\partial^2 \psi}{\partial x^2} - \psi\frac{\partial^2 \psi^*}{\partial x^2})",
            font_size=38
        ).move_to(subtracted_eq)
        self.play(Transform(eq_group, continuity_eq_step1), run_time=1*dt)
        self.wait(2*dt)

        # Simplify RHS to show spatial derivative
        continuity_eq_step2 = MathTex(
            r"i\hbar \frac{\partial (\psi^*\psi)}{\partial t} = -\frac{\hbar^2}{2m}\frac{\partial}{\partial x}(\psi^*\frac{\partial \psi}{\partial x} - \psi\frac{\partial \psi^*}{\partial x})",
            font_size=38
        ).move_to(continuity_eq_step1)
        self.play(Transform(eq_group, continuity_eq_step2), run_time=1*dt)
        self.wait(2*dt)

        # Rearrange to continuity form
        rearranged_eq = MathTex(
            r"\frac{\partial (\psi^*\psi)}{\partial t} + \frac{\partial}{\partial x} \left( \frac{\hbar}{2mi}(\psi^*\frac{\partial \psi}{\partial x} - \psi\frac{\partial \psi^*}{\partial x}) \right) = 0",
            font_size=36 # smaller to fit
        ).move_to(eq_group)
        self.play(Transform(eq_group, rearranged_eq), run_time=1*dt)
        self.wait(2*dt)

        # Define rho and j
        defs_group = VGroup(
            MathTex(r"\rho = \psi^*\psi", font_size=48),
            MathTex(r"j = \frac{\hbar}{2mi}(\psi^*\frac{\partial \psi}{\partial x} - \psi\frac{\partial \psi^*}{\partial x})", font_size=40)
        ).arrange(DOWN, buff=0.5).to_corner(DL)
        
        self.play(Write(defs_group), run_time=1*dt)
        self.wait(2*dt)

        # Final continuity equation
        final_eq = MathTex(r"\frac{\partial \rho}{\partial t} + \frac{\partial j}{\partial x} = 0", font_size=48).move_to(eq_group)
        self.play(
            Transform(eq_group, final_eq),
            Circumscribe(defs_group[0]),
            Circumscribe(defs_group[1]), 
            run_time=1*dt
        )
        self.wait(2*dt)
        self.play(FadeOut(title), FadeOut(eq_group), FadeOut(defs_group), run_time=1*dt)

    def construct_scene2_wavepacket(self, sim_time_start=0.0, sim_time_end=4.0):
        dt = (1/3 * self.whattime_scene2) / 9
        psi_col = BLUE
        j_col = GREEN

        title = self.intro("Свободный волновой пакет", dt=dt)
        psi_formula = MathTex(r"\psi(x,0) \sim e^{-(x-x_0)^2/4\sigma^2} e^{ik_0x}", font_size=40, color=psi_col)
        psi_formula.to_corner(UL).shift(DOWN * 1.5)
        
        j_formula = MathTex(r"j = \frac{\hbar}{2mi}(\psi^*\frac{\partial \psi}{\partial x} - \psi\frac{\partial \psi^*}{\partial x})", font_size=40, color=j_col)
        j_formula.to_corner(UR).shift(DOWN * 1.5)

        self.play(Write(psi_formula), Write(j_formula), run_time=1*dt)
        self.play(FadeOut(title),run_time=1*dt)

        ax, labels = self._make_axes()
        
        time_tracker = ValueTracker(sim_time_start)
        time_label = VGroup(
            MathTex("t = "),
            DecimalNumber(time_tracker.get_value(), num_decimal_places=2, show_ellipsis=False)
        ).arrange(RIGHT).to_corner(UL)

        time_label[1].add_updater(lambda m: m.set_value(time_tracker.get_value()))

        self.play(Create(ax), FadeIn(labels), Write(time_label), run_time=1*dt)

        self.potential_v = self._create_trapezoid_potential(self.x_vals, U0=0, x_start=0, ramp_length=0)
        self.psi_t = self._psi_initial(self.x_vals, k0=4, sigma=0.6, x0=-6.0)

        density_graph = ax.plot(lambda x: np.interp(x, self.x_vals, self._get_psi_data_numerical()), color=psi_col, use_smoothing=False).set_stroke(width=4)
        j_graph = ax.plot(lambda x: np.interp(x, self.x_vals, self._get_j_data_numerical()), color=j_col, use_smoothing=False).set_stroke(width=4)
        graphs = VGroup(density_graph, j_graph)

        # --- Исправленный updater ---
        sim_time_prev = ValueTracker(time_tracker.get_value())

        def evolve_updater(mobs, dt):
            sim_dt = time_tracker.get_value() - sim_time_prev.get_value()
            if sim_dt == 0: return

            self._evolve_split_step(sim_dt)
            sim_time_prev.set_value(time_tracker.get_value())

            new_density_graph = ax.plot(lambda x: np.interp(x, self.x_vals, self._get_psi_data_numerical()), color=psi_col, use_smoothing=False).set_stroke(width=4)
            new_j_graph = ax.plot(lambda x: np.interp(x, self.x_vals, self._get_j_data_numerical()), color=j_col, use_smoothing=False).set_stroke(width=4)
            mobs[0].become(new_density_graph)
            mobs[1].become(new_j_graph)
        # --------------------------

        graphs.add_updater(evolve_updater)
        self.add(graphs)
        
        animation_duration = 2/3 * self.whattime_scene2
        self.play(time_tracker.animate.set_value(sim_time_end), run_time=animation_duration, rate_func=linear)
        
        graphs.remove_updater(evolve_updater)

        self.wait(2*dt)
        self.play(FadeOut(VGroup(psi_formula, j_formula, ax, labels, graphs, time_label)), run_time=1*dt)

    def construct_scene3_scattering(self, sim_time_start=0.0, sim_time_end=8.0):

        dt = 1/3 * self.whattime_scene3 / 8

        k0=4
        E0 = (k0*k0)/(2 * self.m)
        U0 = 0.97* E0
        title = self.intro(f"Рассеяние на потенциале, E > U0", dt=dt)
        
        r_col = RED
        t_col = BLUE
        j_col = GREEN
        pot_col = ORANGE

        j_formula = MathTex(r"j = \frac{\hbar}{2mi}(\psi^*\frac{\partial \psi}{\partial x} - \psi\frac{\partial \psi^*}{\partial x})", font_size=40, color=j_col)
        j_formula.to_corner(UR).shift(DOWN * 1)

        self.play(FadeOut(title), Write(j_formula), run_time=1*dt)

        ax, labels = self._make_axes(y_range=[-0.5, 1.8, 2])

        time_tracker = ValueTracker(sim_time_start)
        time_label = VGroup(
            MathTex("t = "),
            DecimalNumber(time_tracker.get_value(), num_decimal_places=2, show_ellipsis=False)
        ).arrange(RIGHT).to_corner(UL)

        time_label[1].add_updater(lambda m: m.set_value(time_tracker.get_value()))

        self.play(Create(ax), FadeIn(labels), Write(time_label), run_time=2*dt)

        self.potential_v = self._create_trapezoid_potential(self.x_vals, U0=U0, x_start=0, ramp_length=0)
        self.psi_t = self._psi_initial(self.x_vals, k0=k0, sigma=0.6, x0 = -5.0)
        
        potential_graph = ax.plot(lambda x: self._create_trapezoid_potential(x, U0=U0*4/(k0*k0), x_start=-0.0, ramp_length=0), color=pot_col, use_smoothing=False)
        potential_label = MathTex("V(x)", color=pot_col).next_to(potential_graph, RIGHT, buff=-0.8)
        self.play(Create(potential_graph), Write(potential_label), run_time=1*dt)

        # Create the graphs
        reflected_graph = ax.plot(lambda x: np.interp(x, self.x_vals, self._get_psi_reflected_data()), color=r_col, use_smoothing=True).set_stroke(width=4)
        transmitted_graph = ax.plot(lambda x: np.interp(x, self.x_vals, self._get_psi_transmitted_data()), color=t_col, use_smoothing=True).set_stroke(width=4)
        j_graph = ax.plot(lambda x: np.interp(x, self.x_vals, self._get_j_data_numerical()), color=j_col, use_smoothing=True).set_stroke(width=3)
        graphs = VGroup(reflected_graph, transmitted_graph, j_graph)

        # --- Исправленный updater ---
        sim_time_prev = ValueTracker(time_tracker.get_value())

        def evolve_updater(mobs, dt):
            sim_dt = time_tracker.get_value() - sim_time_prev.get_value()
            if sim_dt == 0: return

            self._evolve_split_step(sim_dt)
            sim_time_prev.set_value(time_tracker.get_value())

            new_reflected_graph = ax.plot(lambda x: np.interp(x, self.x_vals, self._get_psi_reflected_data()), color=r_col, use_smoothing=True).set_stroke(width=4)
            new_transmitted_graph = ax.plot(lambda x: np.interp(x, self.x_vals, self._get_psi_transmitted_data()), color=t_col, use_smoothing=True).set_stroke(width=4)
            new_j_graph = ax.plot(lambda x: np.interp(x, self.x_vals, self._get_j_data_numerical()), color=j_col, use_smoothing=True).set_stroke(width=3)
            mobs[0].become(new_reflected_graph)
            mobs[1].become(new_transmitted_graph)
            mobs[2].become(new_j_graph)
        # --------------------------

        graphs.add_updater(evolve_updater)
        self.add(graphs)
        
        animation_duration = 2/3 * self.whattime_scene3
        self.play(time_tracker.animate.set_value(sim_time_end), run_time=animation_duration, rate_func=linear)
        
        graphs.remove_updater(evolve_updater)

        # Fade out
        self.wait(2*dt)
        self.play(FadeOut(VGroup(ax, labels, potential_graph, potential_label, graphs, j_formula, time_label)), run_time=1*dt)

    # ===================== ГЛАВНЫЙ КОНСТРУКТОР =====================
    def construct(self):
        intro = self.intro("Что такое поток вероятности?")
        self.wait(1)
        self.play(FadeOut(intro),run_time=0.5)

        self.construct_scene1_derivation()
        self.construct_scene2_wavepacket(sim_time_start=0.0, sim_time_end=5)
        self.construct_scene3_scattering(sim_time_start=0.0, sim_time_end=5)
        self.outro()

if __name__ == "__main__":
    scene = ProbabilityCurrent(whattime=50, num_steps=200)
    scene.render()

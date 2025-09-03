from manim import *
import numpy as np

class BoxExpansion(Scene):
    def __init__(self, whattime=25, test_logic=False, **kwargs):
        super().__init__(**kwargs)
        # Параметры
        self.whattime = whattime
        self.test_logic = test_logic
        self.name = self.__class__.__name__

        # Физические константы
        self.hbar = 1.0
        self.m = 1.0
        self.a = 6.0
        self.L0 = self.a / 2
        self.X_MIN, self.X_MAX = 0.0, self.a
        self.SAMPLES = 1500
        self.N_MAX = 12

        # Предварительный расчет коэффициентов для ускорения
        self._coeffs = np.array([self._c_n_numeric(n) for n in range(1, self.N_MAX + 1)])

    def get_default_params(self):
        """Возвращает словарь с дефолтными параметрами класса."""
        return {
            "whattime": self.whattime,
            "test_logic": self.test_logic,
        }

    # ===================== ФИЗИЧЕСКИЕ МЕТОДЫ =====================
    def _phi_n(self, n, x, L=None):
        if L is None: L = self.a
        return np.where((x >= 0) & (x <= L), np.sqrt(2 / L) * np.sin(n * np.pi * x / L), 0.0)

    def _psi_init(self, x):
        return np.where((x >= 0) & (x <= self.L0), np.sqrt(2 / self.L0) * np.sin(np.pi * x / self.L0), 0.0)

    def _E_n(self, n, L=None):
        if L is None: L = self.a
        return (n**2) * (np.pi**2) * (self.hbar**2) / (2 * self.m * (L**2))

    def _c_n_numeric(self, n):
        xx = np.linspace(0, self.a, self.SAMPLES)
        integrand = self._psi_init(xx) * self._phi_n(n, xx, self.a)
        return np.trapz(integrand, xx)

    def _psi_t(self, x, t, N=None):
        if N is None: N = self.N_MAX
        coeffs = self._coeffs[:N]
        phis = np.array([self._phi_n(n, x, self.a) for n in range(1, N + 1)])
        phases = np.exp(-1j * np.array([self._E_n(n, self.a) for n in range(1, N + 1)]) * t / self.hbar)
        psi = np.tensordot(coeffs * phases, phis, axes=(0, 0))
        return psi

    # ===================== ГРАФИЧЕСКИЕ УТИЛИТЫ ===================
    def _make_axes(self):
        ax = Axes(
            x_range=[self.X_MIN, self.X_MAX, self.a / 6], y_range=[-1.3, 1.3, 0.5],
            x_length=10, y_length=5, tips=False,
            axis_config={"include_numbers": False}
        )
        labels = VGroup(
            Tex("$x$").scale(0.8).next_to(ax.x_axis, RIGHT, buff=0.2),
            Tex("$\\psi$").scale(0.8).next_to(ax.y_axis, UP, buff=0.2),
        )
        return ax, labels

    def _box_walls(self, L, ax, color=YELLOW):
        wall_left = DashedLine(ax.c2p(0, -1.3), ax.c2p(0, 1.3), color=color)
        wall_right = DashedLine(ax.c2p(L, -1.3), ax.c2p(L, 1.3), color=color)
        return VGroup(wall_left, wall_right)

    def _plot_func(self, ax, f, color=BLUE, **kwargs):
        xs = np.linspace(self.X_MIN, self.X_MAX, self.SAMPLES)
        ys = f(xs)
        return ax.plot_line_graph(xs, ys, line_color=color, **kwargs).set_stroke(width=3)

    # ===================== ОСНОВНОЙ КОНСТРУКТОР =======================
    def construct(self):
        if self.test_logic:
            ax, labels = self._make_axes()
            walls = self._box_walls(self.a, ax)
            psi0_graph = self._plot_func(ax, self._psi_init, color=BLUE)
            title = Tex("Тестовый рендер: Начальное состояние").scale(0.8).to_edge(UP)
            self.add(ax, labels, walls, psi0_graph, title)
            self.wait(4)
            return

        # Распределение времени по частям анимации
        time_alloc = {'intro': 2, 'setup': 12, 'coeffs': 10, 'evolution': 15, 'outro': 2}
        total_units = sum(time_alloc.values())
        t_unit = self.whattime / total_units

        title = Tex("Частица в ящике: внезапное расширение").to_edge(UP)
        self.play(FadeIn(title), run_time=t_unit * time_alloc['intro']*2/3)
        self.play(FadeOut(title), run_time=t_unit * time_alloc['intro']/3)

        ax, labels = self._make_axes()
        self.play(Create(ax), FadeIn(labels), run_time=t_unit * 2)

        # --- Часть 1: Начальные условия и расширение ---
        walls0 = self._box_walls(self.L0, ax, color=YELLOW)
        self.play(Create(walls0), run_time=t_unit * 2)
        lbl0 = MathTex("L_0=\\frac{a}{2}").scale(0.8).next_to(walls0[1], UP)
        self.play(FadeIn(lbl0), run_time=t_unit)

        psi0_graph = self._plot_func(ax, self._psi_init, color=BLUE)
        self.play(Create(psi0_graph), run_time=t_unit * 2)
        self.play(FadeOut(lbl0), run_time=2*t_unit)

        walls1 = self._box_walls(self.a, ax, color=YELLOW)
        arrow = Arrow(walls0[1].get_right() + RIGHT * 0.2, walls1[1].get_right(), buff=0, color=RED)
        sudden = Tex("внезапно").scale(0.8).next_to(arrow, UP, buff=0.1)
        self.play(GrowArrow(arrow), FadeIn(sudden), run_time=t_unit * 2)
        self.play(Transform(walls0[1], walls1[1]))
        lbl1 = MathTex("L_1=a").scale(0.8).next_to(walls0[1], UP)
        self.play(Transform(lbl0, lbl1), run_time=t_unit)
        self.wait(t_unit * 2)

        # --- Часть 2: Проекция на новый базис и коэффициенты ---
        part2_title = Tex("Проекция на новый базис и $|c_n|^2$").scale(0.8).to_corner(UL)
        self.play(FadeOut(arrow, sudden), FadeIn(part2_title))

        # Показываем базисные функции
        phis = VGroup()
        for n in range(1, 7):
            g = self._plot_func(ax, lambda x, n=n: self._phi_n(n, x, self.a), color=GREY, use_smoothing=False)
            g.set_stroke(width=2, opacity=0.7)
            phis.add(g)
        self.play(FadeOut(psi0_graph), LaggedStart(*[Create(g) for g in phis], lag_ratio=0.12), run_time=t_unit * 3)
        
        # Показываем гистограмму
        probs = np.abs(self._coeffs)**2
        probs = probs / probs.sum()

        bars = VGroup()
        x0, y0 = ax.c2p(0, -1.2)[:2]
        bar_width = (ax.c2p(self.a, 0)[0] - x0) / (self.N_MAX + 2)
        for i, p in enumerate(probs):
            height = 2.0 * p
            bar = Rectangle(width=bar_width * 0.8, height=height, fill_color=GREEN, fill_opacity=0.7, stroke_width=0)
            bar.move_to(np.array([x0 + (i + 1) * bar_width, y0 + height / 2, 0]))
            label = Text(str(i + 1), font_size=20).next_to(bar, DOWN, buff=0.05)
            bars.add(VGroup(bar, label))

        caption = Tex("$|c_n|^2$").scale(0.8).next_to(bars, UP, buff=0.2)
        self.play(FadeIn(self._plot_func(ax, self._psi_init, color=BLUE)), run_time=t_unit)
        self.play(LaggedStart(*[FadeIn(b) for b in bars], lag_ratio=0.05), FadeIn(caption), run_time=t_unit * 4)
        self.wait(t_unit * 2)

        # --- Часть 3: Временная эволюция ---
        self.play(
            FadeOut(VGroup(*self.mobjects).remove(title, ax, labels, walls0)),
            run_time=t_unit
        )
        part3_title = Tex("Временная эволюция $|\\psi(x,t)|^2$").scale(0.8).to_corner(UL)
        self.play(FadeIn(part3_title))

        t_tracker = ValueTracker(0.0)
        
        def density_graph():
            xs = np.linspace(self.X_MIN, self.X_MAX, self.SAMPLES)
            psi_vals = self._psi_t(xs, t_tracker.get_value())
            dens = np.abs(psi_vals)**2
            dens = dens / (dens.max() + 1e-9) # Нормировка для визуализации
            return self._plot_func(ax, lambda x: np.interp(x, xs, dens), color=BLUE, use_smoothing=False)

        graph = always_redraw(density_graph)
        t_label = always_redraw(lambda: Tex(f"t = {t_tracker.get_value():.2f}").scale(0.7).to_edge(DOWN))
        
        self.play(FadeIn(graph), FadeIn(t_label), run_time=t_unit)
        self.play(t_tracker.animate.set_value(25.0), run_time=t_unit * time_alloc['evolution'], rate_func=linear)
        self.wait(t_unit)

        # --- Часть 4: Финальное сравнение ---
        self.play(
            FadeOut(VGroup(*self.mobjects).remove(title)),
            run_time=t_unit
        )
        
        comp_title = Tex("Сравнение: внезапное vs адиабатическое расширение").to_edge(UP)
        self.play(Write(comp_title))

        def make_hist(probs, color):
            g = VGroup()
            for i, p in enumerate(probs, start=1):
                bar = Rectangle(width=0.35, height=3.0 * p, fill_opacity=0.8, fill_color=color, stroke_width=0)
                bar.shift(RIGHT * (i * 0.45))
                label = Text(str(i), font_size=20).next_to(bar, DOWN, buff=0.05)
                g.add(VGroup(bar, label))
            return g

        # Внезапный случай
        left_hist = make_hist(probs, color=GREEN).shift(LEFT * 3.5)
        left_title = Tex("Внезапно").scale(0.8).next_to(left_hist, UP)
        
        # Адиабатический случай (система остается в основном состоянии, n=1 -> n=2)
        probs_adi = np.zeros_like(probs)
        probs_adi[1] = 1.0  # n=2 для ящика шириной 'a' соответствует n=1 для 'a/2'
        right_hist = make_hist(probs_adi, color=BLUE).shift(RIGHT * 3.5)
        right_title = Tex("Адиабатически").scale(0.8).next_to(right_hist, UP)

        self.play(FadeIn(VGroup(left_hist, left_title)), run_time=t_unit * 2)
        self.play(FadeIn(VGroup(right_hist, right_title)), run_time=t_unit * 2)
        self.wait(t_unit * time_alloc['outro'])

if __name__ == "__main__":
    # test_logic=True покажет статичный кадр для быстрой проверки
    scene = BoxExpansion(whattime=60, test_logic=False)
    scene.render()

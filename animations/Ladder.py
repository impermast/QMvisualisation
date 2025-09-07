#ladder.py
from manim import *
import numpy as np
from typing import Tuple

#ladder.py
from manim import *
import numpy as np
from typing import Tuple

class Ladder(ThreeDScene):
    DESCRIPTION = "Описание анимации 'Потенциальная ступенька': Эта анимация демонстрирует поведение квантовой частицы, сталкивающейся с потенциальной ступенькой. Показаны случаи, когда энергия частицы больше и меньше высоты ступеньки, включая прохождение, отражение и затухание."

    @classmethod
    def get_info(cls):
        return {
            "name": cls.__name__,
            "description": cls.DESCRIPTION
        }
    def __init__(self,
                 k=3, q=1, whattime=10,test_logic=False,
                 axmin=-5, axmax=5, Num_of_points = 200,
                 title = Text("Ступенька", font_size=60, color=WHITE).to_edge(UP),
                   **kwargs):
        """k - волновое число до барьера, q - после. whattime - время анимации."""
        super().__init__(**kwargs)
        self.k = k
        self.q = q
        self.E = 1
        self.whattime = whattime
        self.test_logic=test_logic
        self.xmin=axmin
        self.xmax=axmax
        self.Num=Num_of_points
        self.title=title
        self.name = self.__class__.__name__

    def get_default_params(self):
        """Возвращает словарь с дефолтными параметрами класса."""
        return {
            "k": self.k,
            "q": self.q,
            "whattime": self.whattime,
            "test_logic": self.test_logic,
            "xmin": self.xmin,
            "xmax": self.xmax,
            "Num_of_points": self.Num,
            "title": self.title
        }    

    def create_axes(self):
        """Определение осей 3D графика"""
        axes = ThreeDAxes(
            x_range=[self.xmin, self.xmax, 1],
            y_range=[-3, 4, 1],
            z_range=[-3, 4, 1],
            axis_config={"color": BLUE,
            "include_numbers": True},

        )
        labels = axes.get_axis_labels(
            x_label=Tex("x"),    # Ось x
            y_label=Tex(r"$Re(\psi)$"),  # Ось y — действительная часть
            z_label=Tex(r"$Im(\psi)$")   # Ось z — мнимая часть
        )
        self.set_camera_orientation(phi=0 * DEGREES, theta=-90 * DEGREES)
        self.move_camera(zoom=0.9)
        return axes,labels
    
    def solution_text(self, size: int) -> Tuple[VGroup, VGroup]:
        """ Функция для отображения текста, который описывает решение"""
        textL = Tex(
            r"$\psi(x) = e^{ikx} + R e^{-ikx}$",
            font_size=size,
            color=WHITE
        ).to_corner(LEFT)

        if self.E > 0: # E > U_0, прохождение
            textR = Tex(r"$\psi(x) = T e^{iqx}$", font_size=size).to_edge(RIGHT)
        else: # E < U_0, затухание
            textR = Tex(r"$\psi(x) = T e^{-qx}$", font_size=size).to_edge(RIGHT)

        borderL = SurroundingRectangle(textL, color=WHITE, buff=0.1)
        borderR = SurroundingRectangle(textR, color=WHITE, buff=0.1)
        return VGroup(textL, textR), VGroup(borderL, borderR)

    def psi(self, x):
        """Волновая функция для потенциальной ступеньки."""
        k, q = self.k, self.q

        if self.E > 0:  # E > U_0, прохождение
            R = (k - q) / (k + q)
            T = 2 * k / (k + q)
            func1 = lambda x: np.exp(1j * k * x) + R * np.exp(-1j * k * x)
            func2 = lambda x: T * np.exp(1j * q * x)
            conditions = [x < 0, x >= 0]
            return np.piecewise(x+0j, conditions, [func1, func2])
        else:  # E < U_0, затухание
            R = (k - 1j * q) / (k + 1j * q)
            T = 2 * k / (k + 1j * q)
            func3 = lambda x: np.exp(1j * k * x) + R * np.exp(-1j * k * x)
            func4 = lambda x: T * np.exp(-q * x)
            conditions = [x < 0, x >= 0]
            return np.piecewise(x+0j, conditions, [func3, func4])

    def potential(self,x):
        """Potential"""
        conditions = [
            x < 0,  # Первая область
            x >= 0  # Вторая область
        ]
        functions = [
            lambda x: 0, 
            lambda x: 1,
        ]
        return np.piecewise(x, conditions, functions)

    def draw_potential(self, axes):
        """Создание графика потенциала."""
        x_vals = np.linspace(self.xmin, self.xmax, self.Num)
        y_vals = np.real(self.potential(x_vals))
        z_vals = np.zeros(self.Num)

        graph = axes.plot_line_graph(
            x_vals, y_vals, z_vals,
            line_color=GREEN, add_vertex_dots=False,
            stroke_width=8
        )
        return graph

    def draw_psifunc(self, axes, t_value):
        """Создание графика волновой функции в 3D"""
        x_vals = np.linspace(self.xmin, self.xmax, self.Num)
        
        # Корректная временная эволюция psi(x,t) = psi(x) * exp(-i*w*t)
        # где w = E/hbar. Примем 2m=1, hbar=1, тогда E = k^2, w = k^2.
        omega = self.k**2
        psi_t = self.psi(x_vals) * np.exp(-1j * omega * t_value)
        
        y_vals = np.real(psi_t)
        z_vals = np.imag(psi_t)
        
        graph = axes.plot_line_graph(
            x_vals, y_vals, z_vals,
            line_color=RED, 
            add_vertex_dots=True, vertex_dot_radius= 0.01, 
            vertex_dot_style=dict(fill_color=WHITE),
            stroke_width=4
        )
        return graph

    def draw_circle(self, axes, t):
        """Создает круг в точке сшивки с радиусом, равным модулю psi(0, t)."""
        radius = 2*np.abs(self.psi(0, t))**2  # Используйте модуль psi для радиуса
        phi = np.angle(self.psi(0, t))
        circle = Circle(radius=radius, color=YELLOW, fill_opacity=0.1)
        circle.move_to([0, 0, 0])  # Перемещаем круг в начало координат
        circle.rotate(90 * DEGREES, axis=DOWN)

        # Убедитесь, что координаты точки соответствуют правильному расположению
        dot = Dot3D(color=YELLOW_D, radius=0.2).move_to([0, radius * np.cos(phi), radius * np.sin(phi)])
        # label = Text(f'({radius})').next_to(dot, UP)
        return VGroup(circle, dot)

    def run_case(self, case_name: str, axes, labels):
        """Запускает анимацию для одного случая (E > U0 или E < U0)."""
        tmax=self.whattime/2
        case_text = Text(case_name, font_size=48).to_edge(UP)
        solution, border = self.solution_text(30)

        self.play(FadeIn(case_text, shift=UP))
        self.play(FadeOut(case_text), Write(solution), Create(border))
        
        t = ValueTracker(0)
        psi_graph = always_redraw(lambda: self.draw_psifunc(axes, t.get_value()))
        potent = self.draw_potential(axes)

        self.play(FadeOut(solution), FadeOut(border), Create(VGroup(psi_graph, potent)), Create(VGroup(axes, labels)), run_time=0.5)

        self.play(t.animate.set_value(2 * tmax / 5),
                  run_time=2 * tmax / 5, rate_func=linear)
        self.move_camera(phi=75 * DEGREES, theta=-120 * DEGREES)
        self.play(t.animate.set_value(tmax),
                  run_time=3 * tmax / 5, rate_func=linear)
        
        # Очистка сцены для следующего кейса
        self.play(
            FadeOut(VGroup(axes, labels, psi_graph, potent)),
            run_time=0.5
        )
        self.remove(psi_graph) 

    def construct(self):
        potentialTex = Tex(
            r"$U(x) = U_0\,[x>0]$",
            color=GREEN
        )

        self.play(Write(self.title), Write(potentialTex), run_time=1)
        self.wait(1)
        self.play(FadeOut(self.title), FadeOut(potentialTex), run_time=0.5)


        axes, labels = self.create_axes()
        if self.test_logic == True:
            graph = self.draw_psifunc(axes, 0)
            self.add(axes, labels, graph)
            self.wait(4)
        else:
            # --- Случай E > U_0 ---
            self.E = 1
            self.run_case("E > U₀ (Прохождение и отражение)", axes, labels)

            # --- Случай E < U_0 ---
            self.set_camera_orientation(phi=0 * DEGREES, theta=-90 * DEGREES) # Восстанавливаем камеру
            self.E = -1
            self.run_case("E < U₀ (Полное отражение и затухание)", axes, labels)

            self.set_camera_orientation(phi=0 * DEGREES, theta=-90 * DEGREES)
            thank_you_text = Text("Спасибо за внимание!", font_size=40, color=WHITE)
            self.play(Write(thank_you_text), run_time=1)
            self.wait(1)
            self.play(FadeOut(thank_you_text), run_time=0.5)


if __name__ == "__main__":
    # Для E > U₀, k > q. Для E < U₀, q - параметр затухания.
    scene = Ladder(k=2, q=1, whattime=10, test_logic=False)
    scene.render()
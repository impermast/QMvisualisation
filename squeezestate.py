from manim import *
import numpy as np
from scipy.special import hermite

class Sqeeze2D(ThreeDScene):
    def __init__(self,
                 x0=0, p0=10, dx0 = 0.5, dp0 = 1,
                 whattime=0.1,a=5, 
                 test_logic=True,Num_of_points = 10,
                 title = Text("Сжатое (когерентное) состояние.", font_size=50, color=WHITE),
                   **kwargs):
        super().__init__(**kwargs)
        self.x0 = x0
        self.p0 = p0
        self.dx0 = dx0
        self.dp0 = dp0
        self.whattime = whattime
        self.test_logic=test_logic
        self.a=a
        self.Num=Num_of_points
        self.title=title
        self.class_name = self.__class__.__name__
        self.t_value = ValueTracker(0)

    def get_default_params(self):
        """Возвращает словарь с дефолтными параметрами класса."""
        return {
            "x0": self.x0,
            "p0": self.p0,
            "dx0": self.dx0,
            "dp0": self.dp0,
            "a": self.a,
            "whattime": self.whattime,
            "test_logic": self.test_logic,
            "Num_of_points": self.Num,
            "title": self.title
        }    
    def create_axes(self):
        xmin = -self.a
        xmax= self.a
        Num=self.Num        
        """Определение осей 3D графика"""
        axes = Axes(
            x_range=[xmin, xmax, 1],
            y_range=[-1, 1.2, 1],
            axis_config={"color": BLUE,
            "include_numbers": False},

        )
        labels = axes.get_axis_labels(
            x_label=Tex("x"),    # Ось x
            y_label=Tex(r"$Re(\psi)$"),  # Ось y — действительная часть
        )
        return axes,labels

    def create_axes3D(self):
        xmin = -self.a
        xmax= self.a
        Num=self.Num        
        """Определение осей 3D графика"""
        axes = ThreeDAxes(
            x_range=[xmin, xmax, 1],
            y_range=[-0.1, 0.1, 0.1],
            z_range=[-0.1, 0.1, 0.1],
            axis_config={"color": BLUE,
            "include_numbers": True},
        )
        labels = axes.get_axis_labels(
            x_label=Tex("x"),    # Ось x
            y_label=Tex(r"$Re(\psi)$"),  # Ось y — действительная часть
            z_label=Tex(r"$Im(\psi)$")   # Ось z — мнимая часть
        )
        self.set_camera_orientation(phi=85 * DEGREES, theta=-120 * DEGREES)
        return axes,labels
    

    def solution_text(self,size):
        """ Функция для отображения текста, который описывает решение"""
        textX = Tex(r"$\psi_0(x) = e^{\cfrac{i p_0 x}{\hbar}} e^{-\cfrac{(x - x_0)^2}{4 \sigma_x^2}} \left( \cfrac{1}{2 \pi \sigma_x^2} \right)^{1/4}$", font_size=size).to_edge(UL)
        textP = Tex(r"$\psi_0(p) = e^{-\cfrac{i (p - p_0) x_0}{\hbar}} e^{-\cfrac{(p - p_0)^2}{4 \sigma_p^2}} \left( \cfrac{1}{2 \pi \sigma_p^2} \right)^{1/4}$", font_size=size).next_to(textX, RIGHT)
        borderX = SurroundingRectangle(textX, color=WHITE, buff=0.1)
        borderP = SurroundingRectangle(textX, color=WHITE, buff=0.1)
        return VGroup(textX,textP),VGroup(borderX,borderP)
        
    def psi(self,x, p0, x0, sigma_x):
        """Волновая функция осцилятора"""
        exp_momentum = np.exp(1j*p0*x)
        exp_position = np.exp(-((x - x0)**2) / (4 * sigma_x**2))
        norm = (1 / (2 * np.pi * sigma_x**2))**(1/4)
        return norm * exp_momentum * exp_position 

    def psi_p(self,p, p_0, x_0, sigma_p):
        """Волновая функция осцилятора в импульсном представлении"""
        exp_position = np.exp(-1j * (p - p_0) * x_0)
        exp_position = np.exp(-((p - p_0)**2) / (4 * sigma_p**2))
        norm = (1 / (2 * np.pi * sigma_p**2))**(1/4)
        return norm*exp_position*exp_position
    def eigen_func(self,x,p0):
        norm = np.sqrt(2*np.pi)
        exp_momentum = np.exp(1j*p0*x)
        return exp_momentum/norm
    def complex_solution(self, x, p, t):
        E = p**2 / (2 *1)
        psi = self.eigen_func(x, p) *self.psi_p(p, self.p0, self.x0, self.dp0)* np.exp(-1j * E * t)
        return psi


    def animate_single_solution(self, p):
        t1 = self.whattime        
        curve = always_redraw(
            lambda: ParametricFunction(
                lambda x: np.array([x, np.real(self.complex_solution(x, p, self.t_value.get_value())), 
                                    np.imag(self.complex_solution(x, p, self.t_value.get_value()))]),
                t_range=[-self.a, self.a],
                color=RED
            )
        )
        self.play(Create(curve))
        self.play(self.t_value.animate.set_value(5 * t1), run_time=5 * t1, rate_func=linear)
        self.play(FadeOut(curve), run_time=t1)
        

    def animate_multiple_solutions(self, p_vals):
        t1 = self.whattime
        curves = VGroup()
        colors = [RED, ORANGE, YELLOW, GREEN, BLUE, PURPLE]
        for i,p in enumerate(p_vals):
            curve = always_redraw(
                lambda p=p: ParametricFunction(
                    lambda x: np.array([x, np.real(self.complex_solution(x, p, self.t_value.get_value())), 
                                        np.imag(self.complex_solution(x, p, self.t_value.get_value()))]),
                    t_range=[-self.a, self.a],
                    color=colors[i%6]
                )
            )
            curves.add(curve)  # Добавляем кривую в группу
        self.play(Create(curves))
        self.play(self.t_value.animate.set_value(5 * t1), run_time=5 * t1, rate_func=linear)
        self.play(FadeOut(curves), run_time=t1)

    
    def construct(self):
        x_0 = self.x0  
        p_0 = self.p0
        sigma_x = self.dx0
        sigma_p = self.dp0
        t1 = self.whattime

        colors = [RED, ORANGE, YELLOW, GREEN, BLUE, PURPLE]

        #Название
        self.play(Write(self.title),run_time=t1)
        self.wait(t1)
        self.play(FadeOut(self.title),run_time=t1)
        #Вступление с решением
        solution,border = self.solution_text(40)
        self.play(Write(solution),Create(border),run_time=t1)
        self.wait(3*t1)
        self.play(FadeOut(solution),FadeOut(border),run_time=t1)

        #начальная функция
        # axes,labels = self.create_axes()
        # graphX = axes.plot(lambda x: np.real(self.psi(x,p_0,x_0,sigma_x)),
        #           color = RED_A, stroke_width=2)
        # self.play(Create(axes),Create(labels),Create(graphX),run_time = 3*t1)
        # self.wait(5*t1)        

        # #График разложения по с.ф 2D
        # summed_graph = axes.plot(lambda x: 0, color=WHITE)
        # p_vals = np.linspace(p_0-2,p_0+2,5)
        # for i,p in enumerate(p_vals):
        #     momfunc = axes.plot(
        #         lambda x: np.real(np.real(self.psi_p(p, p_0, x_0, sigma_p))* self.eigen_func(x,p)),
        #         color=colors[i%6], stroke_width=4
        #     )
        #     self.play(Create(momfunc),run_time = 1*t1)
        #     new_summed_graph = axes.plot(
        #         lambda x: np.real(sum(np.real(self.psi_p(p_val, p_0, x_0, sigma_p)) * self.eigen_func(x, p_val) for p_val in p_vals[:i+1])),
        #         color=WHITE)
        #     self.play(Transform(summed_graph, new_summed_graph), FadeOut(momfunc),run_time = 2*t1)
        #     self.wait(1*t1)
        # self.play(FadeOut(summed_graph), FadeOut(axes), FadeOut(labels),FadeOut(graphX),run_time = 1*t1)

        #Эволюция сф в 3D
        axes3,labels3 = self.create_axes3D()
        self.play(Create(axes3),Create(labels3),run_time=2*t1)
        p_vals = [p_0,p_0+1,p_0-1]
        self.animate_multiple_solutions(p_vals)
        self.play(FadeOut(axes3), FadeOut(labels3),run_time = 2*t1)
        
        #спасибо за внимание
        self.set_camera_orientation(phi=0 * DEGREES, theta=-90 * DEGREES)
        thank_you_text = Text("Спасибо за внимание!", font_size=40, color=WHITE)
        self.play(Write(thank_you_text),run_time=t1)
        self.wait(1*t1)
        self.play(FadeOut(thank_you_text),run_time=t1)


if __name__ == "__main__":
    scene = Sqeeze2D()
    scene.render()

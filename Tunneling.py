from manim import *
import numpy as np

class Tunneling3D(ThreeDScene):
    def __init__(self,
                 k=3, q=1, whattime=20, a=2,test_logic=False,
                 axmin=-5, axmax=5, Num_of_points = 200,
                 title = Text("Задача 3. Туннельный эффект", font_size=60, color=WHITE),
                   **kwargs):
        """Best params: q<k, k = 1.5-3; q=1"""
        super().__init__(**kwargs)
        self.k = k
        self.q = q
        self.a = a
        self.whattime = whattime
        self.test_logic=test_logic
        self.xmin=axmin
        self.xmax=axmax
        self.Num=Num_of_points
        self.title=title
    
    def create_axes(self):
        xmin = self.xmin
        xmax=self.xmax
        Num=self.Num        
        """Определение осей 3D графика"""
        axes = ThreeDAxes(
            
            x_range=[xmin, xmax, 1],
            y_range=[-10, 10, 2],
            z_range=[-10, 10, 2],
            axis_config={"color": BLUE,
            "include_numbers": True},

        )
        labels = axes.get_axis_labels(
            x_label=Tex("x"),    # Ось x
            y_label=Tex("Re"),  # Ось y — действительная часть
            z_label=Tex("Im")   # Ось z — мнимая часть
        )
        self.set_camera_orientation(phi=0 * DEGREES, theta=-90 * DEGREES)
        return axes,labels
    

    def solution_text(self,size):
        """ Функция для отображения текста, который описывает решение"""
        textL = Tex(
            r"$\psi(x,t) = e^{i(kx - \omega t)} + R e^{i(-kx - \omega t)}$",
            font_size=size,
            color=WHITE
        ).to_corner(UL) 
        textM = Tex(r"$A \cosh(x) + B \sinh(x)$", font_size=size).to_edge(UP)
        textR = Tex(r"$\psi(x,t) = T e^{i(kx - \omega t)}$", font_size=size).to_edge(UR)
        borderL = SurroundingRectangle(textL, color=WHITE, buff=0.1)
        borderM = SurroundingRectangle(textM, color=WHITE, buff=0.1)
        borderR = SurroundingRectangle(textR, color=WHITE, buff=0.1)
        return VGroup(textL,textM,textR),VGroup(borderL,borderM,borderR)



    def psi(self, x, t):
        """Волновая функция"""  
        def A(k, w, a):
            numerator = -2*(np.cosh(a * w)+ (1j*w/k) *np.sinh(a * w))
            denominator = (1-w*w/(k*k))* np.sinh(a * w)
            return numerator / denominator
        def B(k, w, a):
            numerator = 2 * (np.sinh(a*w)-(1j*w/k)*np.cosh(a * w))
            denominator = (1-w*w/(k*k))* np.sinh(a * w)
            return numerator / denominator
        def T(k, w, a):
            return (A(k,w,a)*np.sinh(a * w)+B(k, w, a)* np.cosh(a * w))
        def R(k, w, a):
            return B(k,w,a)-1
        conditions = [
            x < 0,                       # Первая область
            (x >= 0) & (x <= self.a),        # Вторая область
            x > self.a                       # Третья область
        ]
        def func1(x): 
            return 0j+(np.exp(1j * (self.k * x)) + R(self.k,self.q,self.a) * np.exp(1j * (-self.k * x)))       
        def func2(x): 
            return 0j+(A(self.k,self.q,self.a)* np.sinh((self.q * x)) + B(self.k,self.q,self.a)* np.cosh((self.q * x)))
        def func3(x): 
            return 0j+T(self.k,self.q,self.a) * np.exp(1j * (self.k * (x-self.a)))
        return np.piecewise(x+0j, conditions, [func1, func2, func3])

    def potential(self,x):
        """Potential"""
        conditions = [
            x < 0,                       # Первая область
            (x >= 0) & (x <= self.a),        # Вторая область
            x > self.a                       # Третья область
        ]
        functions = [
            lambda x: 0, 
            lambda x: 5,                     
            lambda x: 0                                                 
        ]
        return np.piecewise(x, conditions, functions)
    
    def draw_potential(self, axes):
        """Создание графика волновой функции в 3D"""
        x_vals = np.linspace(self.xmin, self.xmax, self.Num)
        y_vals = np.real(self.potential(x_vals))
        z_vals = np.zeros(self.Num)

        # Построение графика
        graph = axes.plot_line_graph(
            x_vals, y_vals, z_vals,
            line_color=GREEN, add_vertex_dots=False,
            stroke_width=8
        )
        return graph
    
    def draw_psifunc(self, axes, t_value):
        """Создание графика волновой функции в 3D"""
        xmin = self.xmin
        xmax=self.xmax
        Num=self.Num 
        x_vals = np.linspace(xmin, xmax, Num)
        y_vals = np.cos(-t_value)*np.real(self.psi(x_vals, t_value))
        z_vals = np.sin(-t_value)*np.imag(self.psi(x_vals, t_value))
        graph = axes.plot_line_graph(
            x_vals, y_vals, z_vals,
            line_color=RED, 
            add_vertex_dots=True, vertex_dot_radius= 0.05, 
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
    
    def construct(self):
        self.play(Write(self.title))
        self.wait(2)
        self.play(FadeOut(self.title))

        axes,labels = self.create_axes()
        print(f'test logic = {self.test_logic}')
        if self.test_logic == True:
            graph = self.draw_psifunc(axes,0)
            self.add(axes,labels, graph)
            self.wait(4)

        else:
            t = ValueTracker(0)
            t_max = 10
            psi_graph = always_redraw(lambda: self.draw_psifunc(axes, t.get_value()))  
            potent =  self.draw_potential(axes)  
            solution,border = self.solution_text(30)      
            self.add(
                psi_graph,
                potent,
                )
            self.play(Write(solution),Create(border))
            self.wait(1)
            self.play(FadeOut(solution),FadeOut(border))

            self.play(Create(VGroup(axes,labels)))
            self.play(t.animate.set_value(3*t_max /5), 
                run_time=3*self.whattime/5, rate_func=linear)
            self.move_camera(phi=75 * DEGREES, theta=-120 * DEGREES)
            self.wait(0.5)
            self.play(t.animate.set_value(t_max), 
                run_time=2*self.whattime/5, rate_func=linear)  
            self.wait(0.5)
            self.play(FadeOut(VGroup(axes,labels)),FadeOut(psi_graph), FadeOut(axes),FadeOut(potent), run_time=1)

            thank_you_text = Text("Спасибо за внимание!", font_size=40, color=WHITE)
            self.play(Write(thank_you_text))
            self.wait(1)
            self.play(FadeOut(thank_you_text))



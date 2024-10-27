from manim import *
import numpy as np
from scipy.special import hermite

class Oscilator2D(ThreeDScene):
    def __init__(self,
                 n=1, w=1, whattime=1,a=5, 
                 test_logic=True,Num_of_points = 100,
                 title = Text("Задача 15. Одномерный осцилятор.", font_size=50, color=WHITE),
                   **kwargs):
        super().__init__(**kwargs)
        self.n = n
        self.w = w
        self.norm = np.sqrt(2**self.n* np.math.factorial(self.n))/ self.w**(1/4)
        self.whattime = whattime
        self.test_logic=test_logic
        self.a=a
        self.Num=Num_of_points
        self.title=title
    def get_default_params(self):
        """Возвращает словарь с дефолтными параметрами класса."""
        return {
            "n": self.n,
            "w": self.w,
            "a": self.a,
            "whattime": self.whattime,
            "test_logic": self.test_logic,
            "Num_of_points": self.Num,
            "title": self.title
        }    
    def create_axes(self):
        xmin = self.a
        xmax=self.a
        Num=self.Num        
        """Определение осей 3D графика"""
        axes = Axes(
            x_range=[xmin, xmax, 1],
            y_range=[0, 10, 2],
            axis_config={"color": BLUE,
            "include_numbers": False},

        )
        labels = axes.get_axis_labels(
            x_label=Tex("x"),    # Ось x
            y_label=Tex(r"$Re(\psi)$"),  # Ось y — действительная часть
        )
        return axes,labels
    

    def solution_text(self,size):
        """ Функция для отображения текста, который описывает решение"""
        textM = Tex(r"$\psi_n(x) = C_n H_n(\sqrt{\cfrac{m\omega}{\hbar}}x) e^{-\cfrac{\omega x^2}{2\hbar}}$", font_size=size).to_edge(UP)
        borderM = SurroundingRectangle(textM, color=WHITE, buff=0.1)
        return textM,borderM



    def psi(self, x, k):
        """Волновая функция осцилятора"""  
        H_n = hermite(k)(x * np.sqrt(self.w))
        norm = 4*np.sqrt(2**k * np.math.factorial(k))/ self.w**(1/4)
        return H_n * np.exp(-self.w*x**2 / 2)/norm

    def potential(self,x):
        """Potential"""                        
        return self.w**2 *x**2/2
    
    def draw_potential(self):
        """Создание графика волновой функции в 3D"""
        graph = FunctionGraph(
            self.potential, x_range=[-self.a,self.a],
            color=WHITE,
            stroke_width=6
        )
        return graph

    
    def construct(self):
        levels = 6
        shift_down = 3.5
        self.play(Write(self.title),run_time=1)
        self.wait(0.5)
        self.play(FadeOut(self.title),run_time=0.5)

        colors = [RED, ORANGE, YELLOW, GREEN, BLUE, PURPLE]

        solution,border = self.solution_text(40)
        self.play(Write(solution),Create(border),run_time=0.7)
        self.wait(0.5)
        self.play(FadeOut(solution),FadeOut(border),run_time=0.5)

        potent = self.draw_potential().shift(DOWN * (shift_down + 0.5))
        all_objects = [potent]
        self.play(Create(potent))
        for i in range(levels):
            energy_level = Line(start=LEFT*5, end=RIGHT*5, color=colors[i]).shift(UP*i*1.3+ DOWN * shift_down)
            
            energy_text = MathTex(
                rf"E_{i} = {2*i+1}\hbar \omega/2",
                font_size=24
            ).next_to(energy_level, RIGHT)
            self.play(Create(energy_level),Create(energy_text))

            wave_function = FunctionGraph(
                lambda x: self.psi(x,i), x_range=[-self.a, self.a], color=colors[i]
            ).shift(UP*i*1.3+ DOWN * shift_down)
            self.play(Create(wave_function))
            
            all_objects.append(energy_level)
            all_objects.append(wave_function)
            all_objects.append(energy_text)

        self.wait(0.5)
        self.play(*[FadeOut(obj) for obj in all_objects], run_time=0.5)
            
        thank_you_text = Text("Спасибо за внимание!", font_size=40, color=WHITE)
        self.play(Write(thank_you_text),run_time=0.5)
        self.wait(0.5)
        self.play(FadeOut(thank_you_text),run_time=0.5)


if __name__ == "__main__":
    scene = Oscilator2D()
    scene.render()

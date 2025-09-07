from manim import *
import numpy as np

class AngleChecker(ThreeDScene):
    def construct(self):
        axes = ThreeDAxes()
        labels = axes.get_axis_labels(
            x_label=Tex("x",font_size=40),    # Ось x
            y_label=Tex("y",font_size=40),  # Ось y — действительная часть
            z_label=Tex("z",font_size=40)   # Ось z — мнимая часть
        )
        self.set_camera_orientation(phi=105 * DEGREES, theta=-205 * DEGREES)
        self.add(axes,labels)
        self.wait()

class Squeeze(ThreeDScene):
    DESCRIPTION = "Описание анимации 'Сжатое (когерентное) состояние': Эта анимация исследует эволюцию сжатых когерентных состояний в квантовой механике. Она демонстрирует, как волновой пакет может сжиматься в одном измерении за счет расширения в другом, сохраняя при этом минимальную неопределенность."

    @classmethod
    def get_info(cls):
        return {
            "name": cls.__name__,
            "description": cls.DESCRIPTION
        }
    def __init__(self,
                 x0=-7, p0=10, dp0 = 2,
                 whattime=0.1,xaxis=10, 
                 test_logic=True,Num_of_points = 10,
                 title = Text("Сжатое (когерентное) состояние.", font_size=50, color=WHITE),
                   **kwargs):
        super().__init__(**kwargs)
        self.x0 = x0
        self.p0 = p0
        self.dx0 = 0.5/dp0
        self.dp0 = dp0
        self.whattime = whattime
        self.test_logic=test_logic
        self.xaxis=xaxis
        self.Num=Num_of_points
        self.title=title
        self.name = self.__class__.__name__
        self.t_value = ValueTracker(0)

    def get_default_params(self):
        """Возвращает словарь с дефолтными параметрами класса."""
        return {
            "x0": self.x0,
            "p0": self.p0,
            "dx0": self.dx0,
            "dp0": self.dp0,
            "xaxis": self.xaxis,
            "whattime": self.whattime,
            "test_logic": self.test_logic,
            "Num_of_points": self.Num,
            "title": self.title
        }    
    
    def Ending(self,fulltime):
        #спасибо за внимание
        t1=fulltime/3
        self.set_camera_orientation(phi=0 * DEGREES, theta=-90 * DEGREES)
        thank_you_text = Text("Спасибо за внимание!", font_size=40, color=WHITE)
        self.play(Write(thank_you_text),run_time=t1)
        self.wait(1*t1)
        self.play(FadeOut(thank_you_text),run_time=t1)
    def Starting(self,fulltime):
        t1=fulltime/3
        #Название
        self.set_camera_orientation(phi=0 * DEGREES, theta=-90 * DEGREES)
        self.play(Write(self.title),run_time=t1)
        self.wait(t1)
        self.play(FadeOut(self.title),run_time=t1)

    def create_axes2D(self):
        xmin = -self.xaxis
        xmax= self.xaxis
        Num=self.Num        
        """Определение осей 3D графика"""
        axes = Axes(
            x_range=[xmin, xmax, 1],
            y_range=[-1, 1.2, 1],
            tips=False,
            axis_config={"color": BLUE,
            "include_numbers": False},

        )
        labels = axes.get_axis_labels(
            x_label=Tex("x"),    # Ось x
            y_label=Tex(r"$Re(\psi)$"),  # Ось y — действительная часть
        )
        return axes,labels

    def create_axes3D(self):
        xmin = -self.xaxis
        xmax= self.xaxis
        Num=self.Num        
        """Определение осей 3D графика"""
        axes = ThreeDAxes(
            x_range=(xmin, xmax, 1),
            y_range=(-0.6, 0.7, 0.5),
            z_range=(-0.6, 0.7,0.5),
            axis_config={"color": BLUE,
            "include_numbers": False},
        )
        labels = axes.get_axis_labels(
            x_label=Tex("x",font_size=25),    # Ось x
            y_label=Tex(r"$Re(\psi)$",font_size=25),  # Ось y — действительная часть
            z_label=Tex(r"$Im(\psi)$",font_size=25)   # Ось z — мнимая часть
        )
        self.set_camera_orientation(phi=75 * DEGREES, theta=-105 * DEGREES)
        return axes,labels
    

    def solution_text(self,size):
        """ Функция для отображения текста, который описывает решение"""
        textX = Tex(r"$\psi_0(x) = e^{\cfrac{i p_0 x}{\hbar}} e^{-\cfrac{(x - x_0)^2}{4 \sigma_x^2}} \left( \cfrac{1}{2 \pi \sigma_x^2} \right)^{1/4}$", font_size=size).to_edge(UP)
        textP = Tex(r"$\psi_0(p) = e^{-\cfrac{i (p - p_0) x_0}{\hbar}} e^{-\cfrac{(p - p_0)^2}{4 \sigma_p^2}} \left( \cfrac{1}{2 \pi \sigma_p^2} \right)^{1/4}$", font_size=size).next_to(textX, DOWN)
        borderX = SurroundingRectangle(textX, color=WHITE, buff=0.1)
        borderP = SurroundingRectangle(textP, color=WHITE, buff=0.1)
        return VGroup(textX,textP),VGroup(borderX,borderP)
    
    def explanation(self,fulltime, text_size=0.35):
        t1 = fulltime/22

        solution,border = self.solution_text(40)
        self.play(Write(solution),Create(border),run_time=t1)
        self.wait(2*t1)
        self.play(FadeOut(solution),FadeOut(border),run_time=t1)
        
        evolution_operator = MathTex(r"\hat{U}(t) = e^{-i H t/\hbar}", font_size=int(72 * 1.5*text_size))
        evolution_action = MathTex(r"\hat{U}(t)|\psi(0)\rangle = |\psi(t)\rangle", font_size=int(72 * 1.5*text_size))
        text_evolutionoperator = Text("Оператор эволюции системы во времени.", font_size=int(72 * text_size)).next_to(evolution_operator, DOWN)
        eigen_action = MathTex(r"\hat{U}(t) |\psi(0)\rangle = \int |E\rangle e^{-i E t} \langle E|\psi(0)\rangle  dE", font_size=int(72 * 1.5*text_size))
        text_exponent = Text("Действие экспоненты оператора\nна произвольную функцию вычислить сложно.", font_size=int(72 * text_size)).next_to(evolution_action, 2*DOWN)
        text_eigen = Text("Решение — интеграл по эволюционирующим с.ф.", font_size=int(72 * text_size)).next_to(eigen_action, 2*UP)
        decomposition = MathTex(r"|\psi(0)\rangle = \int |E\rangle \langle E|\psi(0)\rangle  dE", font_size=int(72 * 1.5*text_size))
        text_conclusion = Text("Иногда с.ф оператора H легко найти.", font_size=int(72 * text_size)).next_to(eigen_action, 2*DOWN)
        conclusion2 =  MathTex(r"[\hat{H},\,\hat{p}] = 0 \Rightarrow |E\rangle = \sum |p\rangle", font_size=int(72 *1.5* text_size)).next_to(text_conclusion, 1*DOWN)
        final_solution = MathTex(r"\psi(x,t) = \int c(p) e^{-i E_p t} \phi_p(x) dp", font_size=int(72 *1.5* text_size))


        self.play(Write(evolution_operator),Write(text_evolutionoperator),run_time = t1*2)
        self.wait(1)

        self.play(TransformMatchingShapes(evolution_operator,evolution_action),FadeOut(text_evolutionoperator),Write(text_exponent),run_time = t1)
        self.wait(1)

        self.play(TransformMatchingShapes(evolution_action, decomposition),FadeOut(text_exponent),Write(text_eigen),   run_time = t1*3)
        self.wait(1)  
        
        self.play(TransformMatchingShapes(decomposition, eigen_action),run_time = t1*3)
        self.wait(1)
        
        self.play(FadeOut(text_eigen),ReplacementTransform(eigen_action, final_solution),Write(text_conclusion),Write(conclusion2),  run_time = t1*3)
        self.wait(1)
        
        self.play(FadeOut(final_solution),FadeOut(text_conclusion),FadeOut(conclusion2),  run_time = t1)
        
    def psi(self,x, p0, x0, sigma_x):
        """Волновая функция сжатого состояния"""
        exp_momentum = np.exp(1j*p0*x)
        exp_position = np.exp(-((x - x0)**2) / (4 * sigma_x**2))
        norm = (1 / (2 * np.pi * sigma_x**2))**(1/4)
        return norm * exp_momentum * exp_position 

    def psi_p(self,p, p_0, x_0, sigma_p):
        """Волновая функция для сжатого состояния в импульсном представлении"""
        exp_position = np.exp(-1j * (p - p_0) * x_0)
        exp_gauss = np.exp(-((p - p_0)**2) / (4 * sigma_p**2))
        norm = (1 / (2 * np.pi * sigma_p**2))**(1/4)
        return norm*exp_position*exp_gauss
    def eigen_func(self,x,p):
        norm = np.sqrt(2*np.pi)
        exp_momentum = np.exp(1j*p*x)
        return exp_momentum/norm
    def complex_solution(self, x, p, t):
        E = p**2 / (2 *1)
        psi = self.eigen_func(x, p) *self.psi_p(p, self.p0, self.x0, self.dp0)* np.exp(-1j * E * t)
        return psi
    def total_solution(self,x,t):
        p0 = self.p0
        E0= p0*p0/(2*1)
        alpha = 1/(4*self.dp0*self.dp0)+ (1j*t)/(2)

        psi = np.exp(1j*(p0*x-E0*t))*np.exp(-(x-self.x0-p0*t)**2/(4*alpha))
        norm = (8*np.pi*self.dp0*self.dp0*alpha*alpha)**(1/4)
        return psi/norm

    
    def eigenFunc2D(self,fulltime,colors):
        #4t1+12t1+4t1+12t1+2t1+t1+0.5t1+10t1+0.5t1=46t1
        t1 = fulltime/46
        x_0 = self.x0
        p_0=self.p0
        sigma_x=self.dx0
        sigma_p=self.dp0
        p_num = 21
        

        axes,labels = self.create_axes2D()
        graphX = axes.plot(lambda x: np.real(self.psi(x,p_0,x_0,sigma_x)),
                  color = PURPLE_E, stroke_width=3)
        explanation_text = Text("Разложение по с.ф оператора p", font_size=20).shift(3 * UP + 4 * RIGHT)
        
        p_value = ValueTracker(p_0)
        p_value_display = DecimalNumber(p_value.get_value(), num_decimal_places=1, font_size=30).next_to(explanation_text , DOWN)
        p_label = Text("p = ", font_size=26).next_to(p_value_display, LEFT)
        p_value_display.add_updater(lambda mob: mob.set_value(p_value.get_value()))
    
        self.play(Create(axes),FadeIn(labels),Create(graphX),Write(explanation_text), run_time = t1)
        self.wait(2*t1)        

        #График разложения по с.ф 2D
        summed_graph = axes.plot(lambda x: 0, color=WHITE)
        p_vals = np.linspace(p_0-3,p_0+3,p_num)
        dp = p_vals[2]-p_vals[1]

        amplitudes = np.array([2 if p < p_num/3 else 16 if p < 2*p_num/3 else 1 for p in p_vals])
        normalized_times = amplitudes / amplitudes.sum()
        self.play( Write(p_label), Create(p_value_display),run_time = t1)
        
        for i, (p, norm_time) in enumerate(zip(p_vals, normalized_times)):
            self.play(p_value.animate.set_value(p), run_time=0.1 * t1)
            momfunc = axes.plot(
                lambda x: np.real(self.complex_solution(x, p, 0)),
                color=colors[i % 6], stroke_width=5
            )
            self.play(Create(momfunc), run_time=p_num * t1 * norm_time/2) 
            new_summed_graph = axes.plot(
                lambda x: sum(np.real(self.complex_solution(x,p_val,0)*dp) for p_val in p_vals[:i+1]),
                color=WHITE
            )
            self.play(FadeTransform(momfunc,summed_graph),Transform(summed_graph, new_summed_graph), run_time= 4 * t1 * norm_time)
            self.wait(0.5*t1)

        self.play(ReplacementTransform(summed_graph, graphX), run_time=2 * t1)
        self.play(FadeOut(explanation_text), FadeOut(p_label),FadeOut(summed_graph) , FadeOut(p_value_display), run_time=1 * t1)

        explanation_text1 = Text("Эволюцию во времени В.Ф.", font_size=20).shift(3 * DOWN + 4 * RIGHT)
        anitime = ValueTracker(0)
        graphXT = always_redraw(lambda: axes.plot(
                lambda x: np.real(self.total_solution(x, anitime.get_value())),
                color=PURPLE_E,
                stroke_width=6
            ))
        self.play(Create(graphXT),FadeOut(graphX),Write(explanation_text1), run_time=0.5*t1)
        self.play(anitime.animate.set_value(0.2),Unwrite(explanation_text1,reverse=False), run_time=1 * t1, rate_func=linear)
        self.play(anitime.animate.set_value(2), run_time=9 * t1, rate_func=linear)
        self.play(FadeOut(axes), FadeOut(labels),FadeOut(graphXT),run_time = 0.5*t1)

    def TimeSolution3D(self,fulltime,colors):
        t1 = fulltime/46
        p_0=self.p0
        #1+2+1+1+1+1+2  +1+5+1+5+4+10+10+1=46t1
        #Объясняющие тексты
        explanation_text1 = Text("У разных с.ф. разная частота вращения", font_size=int(30))
        explanation_text2 = Text("Эволюция полного решения — это не просто вращение в комплексной плоскости.", font_size=int(20))
        explanation_text3 = Text("Рассмотрим анимацию эволюции с.ф в 3D", font_size=int(20)).shift(DOWN)
        self.play(Write(explanation_text1),run_time=t1)
        self.wait(2*t1)
        self.play(Transform(explanation_text1,explanation_text2),run_time=t1)
        self.play(Write(explanation_text3),run_time=t1)
        self.wait(t1)
        self.play(FadeOut(explanation_text1,shift=DOWN),FadeOut(explanation_text2,shift=DOWN),FadeOut(explanation_text3,shift=DOWN),run_time=t1)


        axes3, labels3 = self.create_axes3D()
        self.play(Create(axes3), Create(labels3), run_time=2 * t1)

        # Одиночный график с.ф.
        curve1 = always_redraw(
            lambda: axes3.plot_parametric_curve(
                lambda x: np.array([x, np.real(self.complex_solution(x, p_0, self.t_value.get_value())), 
                                    np.imag(self.complex_solution(x, p_0, self.t_value.get_value()))]),
                t_range=[-self.xaxis, self.xaxis],
                color=RED
            )
        )
        self.play(Create(curve1), run_time=1 * t1)
        self.play(self.t_value.animate.set_value(2), run_time=5 * t1, rate_func=linear)

        # Несколько графиков с.ф.
        p_vals = np.linspace(p_0 - 3, p_0 + 3, 2)
        curvesN = VGroup(curve1) 
        for i, p in enumerate(p_vals):
            curve = always_redraw(
                lambda p=p, color=colors[i % 6]: axes3.plot_parametric_curve(
                    lambda x: np.array([x,  
                                        np.real(self.complex_solution(x, p, self.t_value.get_value())), 
                                        np.imag(self.complex_solution(x, p, self.t_value.get_value()))]),
                    t_range=np.array([-self.xaxis, self.xaxis]),
                    color=color
                )
            )
            curvesN.add(curve)  # Добавляем кривую в группу
        self.play(Create(curvesN), run_time=t1)
        self.play(self.t_value.animate.set_value(4), run_time=5 * t1, rate_func=linear)

        # Слияние с.ф. и анимация итогового решения
        e = ValueTracker(0)
        total_curve = always_redraw(
            lambda: axes3.plot_parametric_curve(
                lambda x: np.array([x, 
                                    np.real(self.total_solution(x, e.get_value())), 
                                    np.imag(self.total_solution(x, e.get_value()))]),
                t_range=[-self.xaxis, self.xaxis],
                color=WHITE
            )
        )

        self.play(ReplacementTransform(curvesN, total_curve), run_time=4 * t1)
        
        self.play(e.animate.set_value(0.5),run_time=5 * t1)

        # Анимация времени для итогового решения
        self.move_camera(phi=65 * DEGREES, theta=-205 * DEGREES, 
                         frame_center=[0, 0, 0], run_time=15* t1,
                         added_anims=[e.animate(run_time=15 * t1).set_value(2)])

        self.play(FadeOut(total_curve), FadeOut(axes3), FadeOut(labels3), run_time=t1)

  
    
    def construct(self):
        colors = [RED_B, GREEN_B, GOLD_B, BLUE_B, PURPLE_B,YELLOW_B]
        tfactor=self.whattime
        self.Starting(2)
        #Вступление с решением       
        self.explanation(16)

        #разложение по сф в 2д
        self.eigenFunc2D(40*tfactor,colors)

        #Эволюция сф в 3D
        self.TimeSolution3D(20*tfactor,colors)

        self.Ending(2)
        



if __name__ == "__main__":
    scene = Squeeze(whattime=1, test_logic=False)
    scene.render()
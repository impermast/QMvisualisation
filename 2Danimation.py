from manim import *
import numpy as np

class QuantumScattering(Scene):
    def construct(self):
        # Определение осей
        axes = Axes(
            x_range=[-5, 5, 1],
            y_range=[-2, 2, 1],
            axis_config={"color": BLUE},
        )
        labels = axes.get_axis_labels(x_label="x", y_label="Re")

        # Параметры волновой функции
        k = 1  # волновое число до барьера
        q = 0.5  # волновое число после барьера
        A = 1  # амплитуда
        V0 = 1  # высота барьера
        t_max = 10  # длительность анимации
        self.time_tracker = ValueTracker(0)

        # Функция для волновой функции
        def psi(x, t):
            if x < 0:
                return A * (np.exp(1j * (k * x - t)) + np.exp(-1j * (k * x + t)))
            else:
                return A * np.exp(1j * (q * x - t))

        # Обновление графика волновой функции во времени
        def wave_func_graph(t):
            wave = axes.plot(
                lambda x: np.real(psi(x, t)),
                color=YELLOW,
                x_range=[-5, 5],
            )
            return wave

        # Начальное состояние
        wave_graph = always_redraw(lambda: wave_func_graph(self.time_tracker.get_value()))

        # Анимация
        self.add(axes, labels, wave_graph)
        self.play(Create(wave_graph), run_time=t_max, rate_func=linear)

# Запуск анимации
if __name__ == "__main__":
    from manim import *
    config.media_width = "100%"
    scene = QuantumScattering()
    scene.render()
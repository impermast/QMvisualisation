# Архитектура QMvisualisation

## Цель

QMvisualisation — надстройка над Manim для создания сложных учебных визуализаций квантовой механики.

Проект должен облегчать:
- 2D/3D визуализацию комплексных волновых функций;
- временную эволюцию;
- переходы между состояниями;
- визуальное разложение и сложение состояний;
- координатное и импульсное представления;
- переходы между представлениями;
- переиспользуемые LaTeX-объяснения;
- intro/outro и другие презентационные элементы.

Сцены могут сильно отличаться друг от друга, поэтому педагогический сценарий остаётся обычным Python/Manim-кодом.

---

## 1. QuantumState

`QuantumState` описывает квантовое состояние и не зависит от Manim.

Минимальная идея:

```python
class QuantumState:
    name: str
    description: str
    parameters: dict
    latex: dict[str, str]

    def psi(self, x, t=0):
        ...
```

Конкретные состояния могут иметь любые собственные параметры:

```python
state.x0
state.p0
state.sigma
state.n
```

`parameters` нужен как удобное перечисление параметров для визуалов, подписей и будущих интерфейсов.

Возможные специализации:
- `GaussianState`
- `SqueezedState`
- `HarmonicEigenstate`
- `SuperpositionState`
- `SampledState`

Импульсное представление может быть дополнительным методом:

```python
state.psi_p(p, t=0)
```

Если аналитическая форма отсутствует, позже можно добавить численное преобразование.

---

## 2. QuantumSystem

`QuantumSystem` описывает систему / гамильтониан и также не зависит от Manim.

Минимальная идея:

```python
class QuantumSystem:
    name: str
    description: str
    parameters: dict
    latex: dict[str, str]

    def potential(self, x, t=0):
        ...
```

Примеры:
- `FreeParticle`
- `HarmonicOscillator`
- `InfiniteWell`
- `FiniteWell`
- `PotentialBarrier`

`QuantumState` и `QuantumSystem` не наследуются друг от друга и не обязаны хранить ссылки друг на друга.

Если операция требует обе сущности, они передаются явно:

```python
EvolveState(state, system)
```

Это важно для задач со сменой гамильтониана или потенциала.

---

## 3. Единицы

Во внутреннем численном коде:

```text
ħ = c = 1
```

Не таскать фундаментальные константы по формулам без необходимости.

Но формулы, которые показываются студентам, должны быть физически полными:

```python
system.latex["energy"] = r"E=\frac{\hbar^2 k^2}{2m}"
```

---

## 4. LaTeX metadata

`QuantumState` и `QuantumSystem` могут хранить стандартные формулы, связанные с объектом:

```python
latex = {
    "wavefunction": r"\psi(x,t)=...",
    "probability": r"P(x,t)=|\psi(x,t)|^2",
}
```

или:

```python
latex = {
    "potential": r"V(x)=\frac12 m\omega^2x^2",
    "energy": r"E_n=\hbar\omega(n+\frac12)",
}
```

Эти формулы должны переиспользоваться в `FormulaExplanation`, подписях и других визуалах, а не переписываться в каждой сцене.

---

## 5. Visual objects

Visual objects — Manim-объекты, которые отображают физические сущности.

Примеры:

```python
WaveFunction2D(state)
WaveFunction3D(state)
ProbabilityDensity(state)
MomentumView(state)
PotentialView(system)
BasisView(state)
```

Они могут импортировать Manim.

Физические вычисления по возможности должны жить в `QuantumState` / `QuantumSystem`, а не внутри визуального класса.

---

## 6. Semantic animations

Нужны переиспользуемые анимации с физическим смыслом:

```python
EvolveState(...)
MorphState(...)
DecomposeState(...)
ComposeStates(...)
ToMomentumSpace(...)
ToCoordinateSpace(...)
```

Их задача — скрывать повторяющуюся низкоуровневую Manim-механику.

Важно различать:
- физическую временную эволюцию;
- чисто визуальный morph между двумя объектами.

---

## 7. Presentation presets

Отдельно существуют переиспользуемые элементы оформления:

```python
Intro(...)
Outro(...)
FormulaExplanation(...)
DefinitionCard(...)
EquationTransition(...)
```

Они могут брать `name`, `description`, `latex`, `parameters` из state/system, но не являются частью физического ядра.

---

## 8. Scene

`Scene` — верхний уровень.

Она отвечает за то, что и в каком порядке объясняется студенту.

```python
class ExampleScene(ThreeDScene):
    def construct(self):
        state = ...
        system = ...

        wave = WaveFunction3D(state)

        self.play(...)
        self.play(...)
```

Не заменять свободу Manim-сцен универсальным конфигом.

---

## Главный поток

```text
QuantumState + QuantumSystem
            ↓
      Visual objects
            ↓
   Semantic animations
            ↓
          Scene
```

Presentation presets используются параллельно для оформления и объяснений.

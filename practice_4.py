from abc import ABC, abstractmethod
from typing import Callable, Self

import sympy


class IntegralCalcer(ABC):
    __slots__ = ()

    @abstractmethod
    def calc(
        self,
        f: Callable[[float], float],
        a: float,
        b: float
    ) -> float:
        pass

    def _validate_bounds(self, a: float, b: float) -> None:
        if a >= b:
            raise ValueError("Должно выполняться условие a < b")

    def __str__(self) -> str:
        return self.__class__.__name__

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"

    @classmethod
    def from_config(cls, config: dict) -> Self:
        return cls(**config)


class RectangularCalcer(IntegralCalcer):
    __slots__ = ("_n",)

    _n: int

    def __init__(self, n: int) -> None:
        if n <= 0:
            raise ValueError("Количество разбиений n должно быть больше 0")
        self._n = n

    def calc(
        self,
        f: Callable[[float], float],
        a: float,
        b: float
    ) -> float:
        self._validate_bounds(a, b)

        h: float = (b - a) / self._n
        result: float = 0.0

        for i in range(self._n):
            x: float = a + (i + 0.5) * h
            result += f(x)

        return result * h


class SimpsonCalcer(IntegralCalcer):
    __slots__ = ("_n",)

    _n: int

    def __init__(self, n: int) -> None:
        if n <= 0:
            raise ValueError("Количество разбиений n должно быть больше 0")
        if n % 2 != 0:
            raise ValueError("Для метода Симпсона n должно быть чётным")
        self._n = n

    def calc(
        self,
        f: Callable[[float], float],
        a: float,
        b: float
    ) -> float:
        self._validate_bounds(a, b)

        h: float = (b - a) / self._n

        result: float = f(a) + f(b)

        for i in range(1, self._n):
            x: float = a + i * h

            if i % 2 == 0:
                result += 2 * f(x)
            else:
                result += 4 * f(x)

        return result * h / 3


class AnalyticCalcer(IntegralCalcer):
    __slots__ = ("_symbol",)

    _symbol: str

    def __init__(self, symbol: str = "x") -> None:
        self._symbol = symbol

    def calc(
        self,
        f: sympy.Expr | str,
        a: float,
        b: float
    ) -> float:
        self._validate_bounds(a, b)

        if isinstance(f, str):
            expr: sympy.Expr = sympy.sympify(f)
        else:
            expr = f

        x: sympy.Symbol = sympy.Symbol(self._symbol)
        result = sympy.integrate(expr, (x, a, b))

        if result.has(sympy.Integral):
            raise ValueError("SymPy не смог вычислить интеграл аналитически")

        return float(result)


if __name__ == "__main__":
    # Один и тот же интеграл:
    # ∫(x^2) dx от 0 до 1 = 1/3
    def f(x: float) -> float:
        return x ** 2

    a: float = 0.0
    b: float = 1.0

    rectangular: RectangularCalcer = RectangularCalcer(100)
    simpson: SimpsonCalcer = SimpsonCalcer(100)
    analytic: AnalyticCalcer = AnalyticCalcer()

    rectangular_result: float = rectangular.calc(f, a, b)
    simpson_result: float = simpson.calc(f, a, b)
    analytic_result: float = analytic.calc("x**2", a, b)

    print("=== Вычисление интеграла ===")
    print(f"Прямоугольники: {rectangular_result}")
    print(f"Симпсон:        {simpson_result}")
    print(f"Аналитически:   {analytic_result}")

    print("\n=== Погрешность ===")
    print(f"Погрешность прямоугольников: "
          f"{abs(rectangular_result - analytic_result)}")
    print(f"Погрешность Симпсона:        "
          f"{abs(simpson_result - analytic_result)}")

    print("\n=== __str__ и __repr__ ===")
    print(str(rectangular))
    print(repr(simpson))

    print("\n=== Проверка __slots__ ===")
    try:
        rectangular.new_attribute = 10
    except AttributeError as error:
        print("Новый атрибут добавить нельзя:", error)

    print("\n=== from_config ===")
    analytic_from_config: AnalyticCalcer = AnalyticCalcer.from_config(
        {"symbol": "x"}
    )
    print(analytic_from_config)
    print(analytic_from_config.calc("x**2", a, b))

    print("\n=== Проверка ошибок ===")

    try:
        RectangularCalcer(0)
    except ValueError as error:
        print("n = 0:", error)

    try:
        SimpsonCalcer(5)
    except ValueError as error:
        print("Нечётное n:", error)

    try:
        rectangular.calc(f, 2.0, 1.0)
    except ValueError as error:
        print("a >= b:", error)

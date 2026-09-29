import math

class Angle:
    def __init__(self, radians: float):
        self._radians = float(radians)

    @classmethod
    def from_radians(cls, rad: float):
        return cls(rad)

    @classmethod
    def from_degrees(cls, deg: float):
        return cls(math.radians(deg))

    def get_radians(self) -> float:
        return self._radians

    def set_radians(self, rad: float):
        self._radians = float(rad)

    def get_degrees(self) -> float:
        return math.degrees(self._radians)

    def set_degrees(self, deg: float):
        self._radians = math.radians(deg)

    def _normalize(self) -> float:
        # Приведение к диапазону [0, 2*pi) для корректного сравнения периодичности
        two_pi = 2 * math.pi
        return self._radians % two_pi

    def __str__(self) -> str:
        return f"{self._radians:.4f} rad ({self.get_degrees():.2f}°)"

    def __repr__(self) -> str:
        return f"Angle(radians={self._radians})"

    def __float__(self) -> float:
        return self._radians

    def __int__(self) -> int:
        return int(self._radians)

    def __eq__(self, other) -> bool:
        if isinstance(other, (int, float)):
            other = Angle(other)
        if not isinstance(other, Angle):
            return NotImplemented
        return math.isclose(self._normalize(), other._normalize(), abs_tol=1e-9)

    def __lt__(self, other) -> bool:
        if isinstance(other, (int, float)):
            other = Angle(other)
        if not isinstance(other, Angle):
            return NotImplemented
        return self._normalize() < other._normalize()

    def __le__(self, other) -> bool:
        return self.__lt__(other) or self.__eq__(other)

    def __gt__(self, other) -> bool:
        if isinstance(other, (int, float)):
            other = Angle(other)
        if not isinstance(other, Angle):
            return NotImplemented
        return self._normalize() > other._normalize()

    def __ge__(self, other) -> bool:
        return self.__gt__(other) or self.__eq__(other)

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)

    def __add__(self, other):
        if isinstance(other, Angle):
            return Angle(self._radians + other._radians)
        elif isinstance(other, (int, float)):
            return Angle(self._radians + other)
        return NotImplemented

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        if isinstance(other, Angle):
            return Angle(self._radians - other._radians)
        elif isinstance(other, (int, float)):
            return Angle(self._radians - other)
        return NotImplemented

    def __rsub__(self, other):
        if isinstance(other, (int, float)):
            return Angle(other - self._radians)
        return NotImplemented

    def __mul__(self, other):
        if isinstance(other, (int, float)):
            return Angle(self._radians * other)
        return NotImplemented

    def __rmul__(self, other):
        return self.__mul__(other)

    def __truediv__(self, other):
        if isinstance(other, (int, float)):
            return Angle(self._radians / other)
        return NotImplemented


class AngleRange:
    def __init__(self, start, end, include_start: bool = True, include_end: bool = True):
        self.start = self._to_angle(start)
        self.end = self._to_angle(end)
        self.include_start = include_start
        self.include_end = include_end

    @staticmethod
    def _to_angle(val) -> Angle:
        if isinstance(val, Angle):
            return val
        if isinstance(val, (int, float)):
            return Angle(val)
        raise TypeError("Должен быть float, int или Angle")

    def _get_normalized_bounds(self):
        # Возвращает нормализованные границы промежутка на окружности [0, 2pi)
        s = self.start._normalize()
        e = self.end._normalize()
        return s, e

    def get_length(self) -> float:
        s, e = self._get_normalized_bounds()
        if math.isclose(s, e, abs_tol=1e-9):
            if self.include_start and self.include_end:
                return 2 * math.pi  # Весь круг, если точки совпадают и включены
            return 0.0
        if s <= e:
            return e - s
        else:
            return (2 * math.pi - s) + e

    def __abs__(self) -> float:
        return self.get_length()

    def __str__(self) -> str:
        left = "[" if self.include_start else "("
        right = "]" if self.include_end else ")"
        return f"{left}{self.start._radians:.4f} rad, {self.end._radians:.4f} rad{right}"

    def __repr__(self) -> str:
        return f"AngleRange({repr(self.start)}, {repr(self.end)}, include_start={self.include_start}, include_end={self.include_end})"

    def __eq__(self, other) -> bool:
        if not isinstance(other, AngleRange):
            return NotImplemented
        # Эквивалентность: одинаковая длина и одинаковое начало (с учетом периодичности)
        return (self.start == other.start and 
                self.end == other.end and 
                self.include_start == other.include_start and 
                self.include_end == other.include_end)

    def __lt__(self, other) -> bool:
        if not isinstance(other, AngleRange):
            return NotImplemented
        return self.get_length() < other.get_length()

    def __le__(self, other) -> bool:
        if not isinstance(other, AngleRange):
            return NotImplemented
        return self.get_length() <= other.get_length()

    def __gt__(self, other) -> bool:
        if not isinstance(other, AngleRange):
            return NotImplemented
        return self.get_length() > other.get_length()

    def __ge__(self, other) -> bool:
        if not isinstance(other, AngleRange):
            return NotImplemented
        return self.get_length() >= other.get_length()

    def __contains__(self, item) -> bool:
        if isinstance(item, (int, float, Angle)):
            angle = self._to_angle(item)
            val = angle._normalize()
            s, e = self._get_normalized_bounds()

            # Обработка равенства границам
            if math.isclose(val, s, abs_tol=1e-9):
                return self.include_start
            if math.isclose(val, e, abs_tol=1e-9):
                return self.include_end

            if s <= e:
                return s < val < e
            else:  # Промежуток через ноль (например, от 1.5pi до 0.5pi)
                return val > s or val < e

        elif isinstance(item, AngleRange):
            # Проверка, входит ли один промежуток в другой
            if item.get_length() > self.get_length():
                return False
            # Проверяем граничные точки подпромежутка
            if item.start not in self:
                if not (math.isclose(item.start._normalize(), self.start._normalize(), abs_tol=1e-9) and self.include_start >= item.include_start):
                    return False
            if item.end not in self:
                if not (math.isclose(item.end._normalize(), self.end._normalize(), abs_tol=1e-9) and self.include_end >= item.include_end):
                    return False
            return True
        return False

    def __add__(self, other):
        # Операция в общем виде возвращает список промежутков
        if not isinstance(other, AngleRange):
            return NotImplemented
        # Здесь представлена базовая логика объединения пересекающихся промежутков
        # Для демонстрации: если они пересекаются, объединяем, иначе возвращаем оба
        if self.start in other or self.end in other or other.start in self or other.end in self:
            # Упрощенное объединение (по длинам и границам)
            s = self.start if self.start <= other.start else other.start
            e = self.end if self.end >= other.end else other.end
            return [AngleRange(s, e, self.include_start or other.include_start, self.include_end or other.include_end)]
        return [self, other]

    def __sub__(self, other):
        # Вычитание промежутков (разность множеств)
        if not isinstance(other, AngleRange):
            return NotImplemented
        # Базовая демонстрационная реализация вычитания
        if other in self and self != other:
            # Разбиение на два промежутка
            r1 = AngleRange(self.start, other.start, self.include_start, not other.include_start)
            r2 = AngleRange(other.end, self.end, not other.include_end, self.include_end)
            return [r for r in [r1, r2] if r.get_length() > 0]
        elif self == other:
            return []
        return [self]


# Демонстрация работоспособности
if __name__ == "__main__":
    print("=== ДЕМОНСТРАЦИЯ КЛАССА Angle ===")
    a1 = Angle.from_degrees(90)
    a2 = Angle.from_radians(math.pi / 2)
    a3 = Angle.from_radians(2 * math.pi + math.pi / 2) # Периодичность

    print(f"a1 (90 градусов): {a1}")
    print(f"a2 (pi/2 радиан): {repr(a2)}")
    print(f"a3 (2pi + pi/2): {a3}")
    print(f"Сравнение a1 == a3 (с учетом периодичности): {a1 == a3}")
    
    a1.set_degrees(180)
    print(f"Изменили a1 на 180 градусов: {a1.get_radians()} рад")
    
    print(f"Преобразование в float: {float(a2)}")
    print(f"Сложение a2 + math.pi: {a2 + math.pi}")
    print(f"Умножение a2 * 2: {a2 * 2}")

    print("\n=== ДЕМОНСТРАЦИЯ КЛАССА AngleRange ===")
    r1 = AngleRange(0, math.pi, include_start=True, include_end=False)
    r2 = AngleRange(Angle.from_degrees(0), Angle.from_degrees(180), include_start=True, include_end=False)
    
    print(f"Промежуток r1: {r1}")
    print(f"Эквивалентность r1 == r2: {r1 == r2}")
    print(f"Длина промежутка r1 (abs): {abs(r1)}")
    
    test_angle = Angle.from_degrees(45)
    print(f"Входит ли 45 градусов в r1?: {test_angle in r1}")
    
    out_angle = Angle.from_degrees(200)
    print(f"Входит ли 200 градусов в r1?: {out_angle in r1}")
    
    print(f"Операции сложения (объединения) r1 + r1: {r1 + r1}")

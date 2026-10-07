import math


class Angle:
    """Класс для хранения угла. Внутри угол хранится в радианах."""

    def __init__(self, radians: float):
        self._radians = float(radians)

    @classmethod
    def from_radians(cls, radians: float):
        return cls(radians)

    @classmethod
    def from_degrees(cls, degrees: float):
        return cls(math.radians(degrees))

    # Геттеры и сеттеры без @property
    def get_radians(self) -> float:
        return self._radians

    def set_radians(self, radians: float) -> None:
        self._radians = float(radians)

    def get_degrees(self) -> float:
        return math.degrees(self._radians)

    def set_degrees(self, degrees: float) -> None:
        self._radians = math.radians(degrees)

    def _normalize(self) -> float:
        """Представляет угол в диапазоне [0, 2*pi)."""
        return self._radians % (2 * math.pi)

    def __str__(self) -> str:
        return f"{self._radians:.4f} рад ({self.get_degrees():.2f}°)"

    def __repr__(self) -> str:
        return f"Angle({self._radians!r})"

    def __float__(self) -> float:
        return self._radians

    def __int__(self) -> int:
        return int(self._radians)

    def _as_angle(self, other):
        if isinstance(other, Angle):
            return other
        if isinstance(other, (int, float)):
            return Angle(other)
        return NotImplemented

    # Сравнение с учетом периодичности 2*pi
    def __eq__(self, other) -> bool:
        other = self._as_angle(other)
        if other is NotImplemented:
            return NotImplemented
        return math.isclose(
            self._normalize(),
            other._normalize(),
            abs_tol=1e-9
        )

    def __lt__(self, other) -> bool:
        other = self._as_angle(other)
        if other is NotImplemented:
            return NotImplemented
        return self._normalize() < other._normalize() and not math.isclose(
            self._normalize(), other._normalize(), abs_tol=1e-9
        )

    def __le__(self, other) -> bool:
        return self == other or self < other

    def __gt__(self, other) -> bool:
        other = self._as_angle(other)
        if other is NotImplemented:
            return NotImplemented
        return self._normalize() > other._normalize() and not math.isclose(
            self._normalize(), other._normalize(), abs_tol=1e-9
        )

    def __ge__(self, other) -> bool:
        return self == other or self > other

    def __ne__(self, other) -> bool:
        return not self == other

    # Арифметика
    def __add__(self, other):
        if isinstance(other, Angle):
            return Angle(self._radians + other._radians)
        if isinstance(other, (int, float)):
            return Angle(self._radians + other)
        return NotImplemented

    def __radd__(self, other):
        return self + other

    def __sub__(self, other):
        if isinstance(other, Angle):
            return Angle(self._radians - other._radians)
        if isinstance(other, (int, float)):
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
        return self * other

    def __truediv__(self, other):
        if isinstance(other, (int, float)):
            return Angle(self._radians / other)
        return NotImplemented


class AngleRange:
    """
    Промежуток на окружности углов.

    Числа при создании считаются радианами.
    """

    EPS = 1e-9

    def __init__(
        self,
        start,
        end,
        include_start: bool = True,
        include_end: bool = True
    ):
        self.start = self._to_angle(start)
        self.end = self._to_angle(end)
        self.include_start = include_start
        self.include_end = include_end

    @staticmethod
    def _to_angle(value) -> Angle:
        if isinstance(value, Angle):
            return value
        if isinstance(value, (int, float)):
            return Angle(value)
        raise TypeError("Граница должна быть float, int или Angle")

    def _bounds(self):
        return self.start._normalize(), self.end._normalize()

    def get_length(self) -> float:
        start, end = self._bounds()

        if math.isclose(start, end, abs_tol=self.EPS):
            if self.include_start and self.include_end:
                return 2 * math.pi
            return 0.0

        if start < end:
            return end - start

        return 2 * math.pi - start + end

    def __abs__(self) -> float:
        return self.get_length()

    def __str__(self) -> str:
        left = "[" if self.include_start else "("
        right = "]" if self.include_end else ")"
        return (
            f"{left}{self.start.get_radians():.4f}, "
            f"{self.end.get_radians():.4f}{right}"
        )

    def __repr__(self) -> str:
        return (
            f"AngleRange({self.start!r}, {self.end!r}, "
            f"include_start={self.include_start}, "
            f"include_end={self.include_end})"
        )

    # Сравнение промежутков выполняем по их длине.
    def __eq__(self, other) -> bool:
        if not isinstance(other, AngleRange):
            return NotImplemented

        return (
            math.isclose(
                self.get_length(),
                other.get_length(),
                abs_tol=self.EPS
            )
            and self.start == other.start
            and self.end == other.end
            and self.include_start == other.include_start
            and self.include_end == other.include_end
        )

    def __lt__(self, other) -> bool:
        if not isinstance(other, AngleRange):
            return NotImplemented
        return self.get_length() < other.get_length() - self.EPS

    def __le__(self, other) -> bool:
        return self == other or self < other

    def __gt__(self, other) -> bool:
        if not isinstance(other, AngleRange):
            return NotImplemented
        return self.get_length() > other.get_length() + self.EPS

    def __ge__(self, other) -> bool:
        return self == other or self > other

    def __ne__(self, other) -> bool:
        return not self == other

    # Представляем круг как обычный отрезок [0, 2*pi].
    # Это упрощает объединение и вычитание.
    def _parts(self):
        start, end = self._bounds()
        full = 2 * math.pi

        if math.isclose(start, end, abs_tol=self.EPS):
            if self.include_start and self.include_end:
                return [(0.0, full, True, True)]
            return []

        if start < end:
            return [(start, end, self.include_start, self.include_end)]

        return [
            (start, full, self.include_start, True),
            (0.0, end, True, self.include_end)
        ]

    @classmethod
    def _from_parts(cls, parts):
        """Превращает линейные части обратно в список AngleRange."""
        full = 2 * math.pi

        if not parts:
            return []

        # Полный круг
        if len(parts) == 1:
            a, b, ia, ib = parts[0]
            if math.isclose(a, 0, abs_tol=cls.EPS) and \
               math.isclose(b, full, abs_tol=cls.EPS) and ia and ib:
                return [cls(0, 0, True, True)]

        result = []

        # Если есть части около 0 и 2*pi, соединяем их в один
        if len(parts) >= 2:
            first = parts[0]
            last = parts[-1]

            if (
                math.isclose(first[0], 0, abs_tol=cls.EPS)
                and math.isclose(last[1], full, abs_tol=cls.EPS)
            ):
                merged = (
                    last[0],
                    first[1],
                    last[2],
                    first[3]
                )
                middle = parts[1:-1]

                for part in middle:
                    result.append(cls(part[0], part[1], part[2], part[3]))

                result.append(cls(merged[0], merged[1], merged[2], merged[3]))
                return result

        for a, b, ia, ib in parts:
            if b - a > cls.EPS:
                result.append(cls(a, b, ia, ib))

        return result

    @staticmethod
    def _merge_parts(parts):
        if not parts:
            return []

        parts = sorted(parts, key=lambda part: part[0])
        result = [parts[0]]

        for current in parts[1:]:
            a, b, ia, ib = current
            x, y, ix, iy = result[-1]

            overlaps = a < y - AngleRange.EPS
            touches = math.isclose(a, y, abs_tol=AngleRange.EPS)

            if overlaps or (touches and (iy or ia)):
                new_end = max(y, b)

                if b > y + AngleRange.EPS:
                    end_included = ib
                elif math.isclose(b, y, abs_tol=AngleRange.EPS):
                    end_included = iy or ib
                else:
                    end_included = iy

                result[-1] = (x, new_end, ix, end_included)
            else:
                result.append(current)

        return result

    def __contains__(self, item) -> bool:
        if isinstance(item, (int, float, Angle)):
            angle = self._to_angle(item)
            value = angle._normalize()

            for a, b, include_a, include_b in self._parts():
                left_ok = value > a or (
                    include_a and math.isclose(value, a, abs_tol=self.EPS)
                )
                right_ok = value < b or (
                    include_b and math.isclose(value, b, abs_tol=self.EPS)
                )

                if left_ok and right_ok:
                    return True

            return False

        if isinstance(item, AngleRange):
            # Все части item должны целиком лежать в self.
            for a, b, include_a, include_b in item._parts():
                test = AngleRange(a, b, include_a, include_b)

                if test.get_length() == 0:
                    continue

                if not self._contains_part(test):
                    return False

            return True

        return False

    def _contains_part(self, other) -> bool:
        """Проверка, что обычный кусок лежит внутри текущего промежутка."""
        for a, b, include_a, include_b in other._parts():
            found = False

            for x, y, ix, iy in self._parts():
                left_ok = (
                    a > x + self.EPS
                    or (math.isclose(a, x, abs_tol=self.EPS)
                        and (ix or not include_a))
                )
                right_ok = (
                    b < y - self.EPS
                    or (math.isclose(b, y, abs_tol=self.EPS)
                        and (iy or not include_b))
                )

                if left_ok and right_ok:
                    found = True
                    break

            if not found:
                return False

        return True

    def __add__(self, other):
        """Объединение двух промежутков. Результат — список промежутков."""
        if not isinstance(other, AngleRange):
            return NotImplemented

        parts = self._parts() + other._parts()
        parts = self._merge_parts(parts)
        return self._from_parts(parts)

    def __sub__(self, other):
        """Разность промежутков. Результат — список промежутков."""
        if not isinstance(other, AngleRange):
            return NotImplemented

        result = self._parts()

        for oa, ob, oia, oib in other._parts():
            new_result = []

            for a, b, ia, ib in result:
                # Нет пересечения
                if ob < a or math.isclose(ob, a, abs_tol=self.EPS):
                    if math.isclose(ob, a, abs_tol=self.EPS):
                        if not (oib and ia):
                            new_result.append((a, b, ia, ib))
                    else:
                        new_result.append((a, b, ia, ib))
                    continue

                if oa > b or math.isclose(oa, b, abs_tol=self.EPS):
                    if math.isclose(oa, b, abs_tol=self.EPS):
                        if not (oia and ib):
                            new_result.append((a, b, ia, ib))
                    else:
                        new_result.append((a, b, ia, ib))
                    continue

                # Левая часть после вычитания
                if oa > a or math.isclose(oa, a, abs_tol=self.EPS):
                    left_end_included = not oia
                    if oa > a + self.EPS or (ia and left_end_included):
                        new_result.append(
                            (a, oa, ia, left_end_included)
                        )

                # Правая часть после вычитания
                if ob < b or math.isclose(ob, b, abs_tol=self.EPS):
                    right_start_included = not oib
                    if b > ob + self.EPS or (right_start_included and ib):
                        new_result.append(
                            (ob, b, right_start_included, ib)
                        )

            result = new_result

        result = self._merge_parts(result)
        return self._from_parts(result)


def show_ranges(ranges):
    if not ranges:
        return "∅"
    return " + ".join(str(r) for r in ranges)


# ---------------------------------------------------------
# Демонстрация
# ---------------------------------------------------------

if __name__ == "__main__":
    print("=" * 60)
    print("ЛАБОРАТОРНАЯ РАБОТА 1 — УГЛЫ")
    print("=" * 60)

    print("\n1. СОЗДАНИЕ УГЛОВ")
    angle1 = Angle.from_degrees(90)
    angle2 = Angle.from_radians(math.pi / 2)
    angle3 = Angle.from_radians(2 * math.pi + math.pi / 2)

    print("angle1:", angle1)
    print("angle2:", angle2)
    print("angle3:", angle3)

    print("\n2. ПЕРИОДИЧНОСТЬ И СРАВНЕНИЕ")
    print("angle1 == angle2:", angle1 == angle2)
    print("angle1 == angle3:", angle1 == angle3)
    print("30° < 90°:", Angle.from_degrees(30) < angle1)
    print("90° <= 90°:", angle1 <= angle2)
    print("120° > 90°:", Angle.from_degrees(120) > angle1)
    print("120° != 90°:", Angle.from_degrees(120) != angle1)

    print("\n3. ГЕТТЕРЫ И СЕТТЕРЫ")
    print("angle1 в радианах:", angle1.get_radians())
    print("angle1 в градусах:", angle1.get_degrees())

    angle1.set_radians(math.pi)
    print("После set_radians(pi):", angle1)

    angle1.set_degrees(45)
    print("После set_degrees(45):", angle1)

    print("\n4. ПРЕОБРАЗОВАНИЯ И АРИФМЕТИКА")
    print("float(angle2):", float(angle2))
    print("int(angle2):", int(angle2))
    print("45° + 30°:", angle1 + Angle.from_degrees(30))
    print("90° + pi:", angle2 + math.pi)
    print("90° - pi/2:", angle2 - math.pi / 2)
    print("90° * 2:", angle2 * 2)
    print("90° / 2:", angle2 / 2)

    print("\n5. СОЗДАНИЕ ПРОМЕЖУТКОВ")
    r1 = AngleRange(0, math.pi, True, False)
    r2 = AngleRange(
        Angle.from_degrees(0),
        Angle.from_degrees(180),
        True,
        False
    )

    print("r1:", r1)
    print("r2:", r2)
    print("repr(r1):", repr(r1))
    print("r1 == r2:", r1 == r2)
    print("Длина r1:", abs(r1))

    print("\n6. СРАВНЕНИЕ ПРОМЕЖУТКОВ")
    short_range = AngleRange(0, math.pi / 2, True, False)
    long_range = AngleRange(0, math.pi)

    print("short_range:", short_range)
    print("long_range:", long_range)
    print("short_range < long_range:", short_range < long_range)
    print("short_range <= long_range:", short_range <= long_range)
    print("long_range > short_range:", long_range > short_range)
    print("long_range >= short_range:", long_range >= short_range)
    print("short_range != long_range:", short_range != long_range)

    print("\n7. ОПЕРАЦИЯ IN — УГОЛ В ПРОМЕЖУТКЕ")
    test_angle = Angle.from_degrees(45)
    edge_angle = Angle.from_degrees(90)

    print("45° in [0°, 90°):", test_angle in short_range)
    print("90° in [0°, 90°):", edge_angle in short_range)

    print("\n8. ОПЕРАЦИЯ IN — ПРОМЕЖУТОК В ПРОМЕЖУТКЕ")
    small = AngleRange(
        Angle.from_degrees(30),
        Angle.from_degrees(60)
    )
    big = AngleRange(
        Angle.from_degrees(0),
        Angle.from_degrees(90)
    )

    print("small:", small)
    print("big:", big)
    print("small in big:", small in big)
    print("big in small:", big in small)

    print("\n9. СЛОЖЕНИЕ ПРОМЕЖУТКОВ (ОБЪЕДИНЕНИЕ)")
    first = AngleRange(0, math.pi / 2)
    second = AngleRange(math.pi / 4, math.pi)

    print("first:", first)
    print("second:", second)
    print("first + second:", show_ranges(first + second))

    separate = AngleRange(math.pi, 3 * math.pi / 2)
    print("first + separate:", show_ranges(first + separate))

    print("\n10. ВЫЧИТАНИЕ ПРОМЕЖУТКОВ")
    whole = AngleRange(0, math.pi)
    removed = AngleRange(math.pi / 3, 2 * math.pi / 3)

    print("whole:", whole)
    print("removed:", removed)
    print("whole - removed:", show_ranges(whole - removed))

    print("\n11. ПРОМЕЖУТОК ЧЕРЕЗ 0")
    around_zero = AngleRange(
        Angle.from_degrees(300),
        Angle.from_degrees(60)
    )

    print("around_zero:", around_zero)
    print("330° in around_zero:",
          Angle.from_degrees(330) in around_zero)
    print("30° in around_zero:",
          Angle.from_degrees(30) in around_zero)
    print("180° in around_zero:",
          Angle.from_degrees(180) in around_zero)

    print("\n" + "=" * 60)
    print("Демонстрация завершена.")
    print("=" * 60)

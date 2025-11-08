from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, List, Dict, Set
from abc import ABC, abstractmethod


# ============== Moves ==============

class Move(ABC):
    name: str

    @abstractmethod
    def apply(self, s: int) -> int:
        ...


@dataclass(frozen=True)
class AddMove(Move):
    k: int

    def __post_init__(self):
        object.__setattr__(self, "name", f"+{self.k}")

    def apply(self, s: int) -> int:
        return s + self.k


@dataclass(frozen=True)
class SubtractMove(Move):
    k: int

    def __post_init__(self):
        object.__setattr__(self, "name", f"-{self.k}")

    def apply(self, s: int) -> int:
        return s - self.k


@dataclass(frozen=True)
class MultiplyMove(Move):
    factor: int

    def __post_init__(self):
        object.__setattr__(self, "name", f"*{self.factor}")

    def apply(self, s: int) -> int:
        return s * self.factor


@dataclass(frozen=True)
class DivideMove(Move):
    divisor: int
    mode: str = "floor"  # 'floor' | 'ceil' | 'round'

    def __post_init__(self):
        object.__setattr__(self, "name", f"//{self.divisor}({self.mode})")

    def apply(self, s: int) -> int:
        d = self.divisor
        if self.mode == "floor":
            return s // d
        elif self.mode == "ceil":
            # целочисленное округление вверх
            return -(-s // d)
        elif self.mode == "round":
            return int(round(s / d))
        else:
            raise ValueError(f"Unknown divide mode: {self.mode}")


@dataclass(frozen=True)
class FuncMove(Move):
    f: Callable[[int], int]
    label: str = "f(s)"

    def __post_init__(self):
        object.__setattr__(self, "name", self.label)

    def apply(self, s: int) -> int:
        return self.f(s)


# ============== Terminal condition ==============

@dataclass(frozen=True)
class TerminalCondition:
    threshold: int
    comparator: str = "le"  # 'le' (<=) or 'ge' (>=)

    def is_terminal(self, s: int) -> bool:
        if self.comparator == "le":
            return s <= self.threshold
        elif self.comparator == "ge":
            return s >= self.threshold
        else:
            raise ValueError("comparator must be 'le' or 'ge'")


# ============== Game ==============

@dataclass
class Game:
    terminal: TerminalCondition
    moves: List[Move]
    s_min: int
    s_max: int
    monotonic: str = "decreasing"  # or 'increasing'

    def next_states(self, s: int) -> List[int]:
        # Уникальные ходы
        return sorted({m.apply(s) for m in self.moves})


# ============== Analyzer ==============

class Analyzer:
    def __init__(self, game: Game):
        self.g = game

    def classify_up_to_k2(self) -> Dict[int, str]:
        """
        Возвращает словарь: s -> one of {'W1', 'L1', 'W2', 'L2', 'UNRESOLVED'}
        Предполагается монотонность всех ходов в одну сторону.
        """
        g = self.g
        t = g.terminal

        labels: Dict[int, str] = {}
        W: Dict[int, Set[int]] = {1: set(), 2: set()}
        L: Dict[int, Set[int]] = {0: set(), 1: set(), 2: set()}

        # База: терминальные позиции
        if t.comparator == "le":
            # Терминал: s <= T
            L[0] = set(range(g.s_min, min(g.s_max, t.threshold) + 1))
            # Для убывающих ходов идём от T+1 вверх
            state_iter = range(t.threshold + 1, g.s_max + 1)
        else:
            # Терминал: s >= T
            L[0] = set(range(max(g.s_min, t.threshold), g.s_max + 1))
            # Для возрастающих ходов идём сверху вниз
            state_iter = range(min(g.s_max, t.threshold - 1), g.s_min - 1, -1)

        for s in state_iter:
            dests = g.next_states(s)

            # W1: есть ход в терминал
            if any(t.is_terminal(d) for d in dests):
                labels[s] = "W1"
                W[1].add(s)
                continue

            # L1: не W1 и все ходы ведут в W1
            if dests and all(d in W[1] for d in dests):
                labels[s] = "L1"
                L[1].add(s)
                continue

            # W2: есть ход в L1
            if any(d in L[1] for d in dests):
                labels[s] = "W2"
                W[2].add(s)
                continue

            # L2: не W1/В2 и все ходы ведут в W1∪W2
            if dests and all((d in W[1] or d in W[2]) for d in dests):
                labels[s] = "L2"
                L[2].add(s)
                continue

            labels[s] = "UNRESOLVED"

        return labels

    def solve_19_20_21(self) -> dict:
        labels = self.classify_up_to_k2()

        # 19: минимальный S в L1
        s19 = min((s for s, lab in labels.items() if lab == "L1"), default=None)

        # 20: два наименьших S в W2 (по определению уже не W1)
        w2_list = sorted(s for s, lab in labels.items() if lab == "W2")
        s20 = w2_list[:2]

        # 21: минимальный S в L2 (не L1 по явному условию)
        s21 = min((s for s, lab in labels.items() if lab == "L2"), default=None)

        return {"19": s19, "20": s20, "21": s21}


# ============== Пример использования под вашу игру ==============

def build_current_game(s_max: int = 600) -> Game:
    terminal = TerminalCondition(threshold=30, comparator="le")
    moves: List[Move] = [
        SubtractMove(3),
        SubtractMove(5),
        DivideMove(4, mode="floor"),
    ]
    # Игра убывающая (каждый ход уменьшает s), анализируем S ∈ [31..s_max]
    return Game(
        terminal=terminal,
        moves=moves,
        s_min=31,
        s_max=s_max,
        monotonic="decreasing",
    )


if __name__ == "__main__":
    game = build_current_game(s_max=600)
    ans = Analyzer(game).solve_19_20_21()
    print("Задание 19:", ans["19"])
    print("Задание 20:", *ans["20"])
    print("Задание 21:", ans["21"])
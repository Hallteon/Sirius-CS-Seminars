import itertools
from typing import List, Tuple


class AutoSolver:
    def __init__(self, expression: str, bool_table: List[List[bool]],
                 answer_column: List[bool], variables: List[str]) -> None:
        self.bool_table = bool_table
        self.answer_column = answer_column

        self.expression = expression # = '{0} & {1}', будут побитовые операции
        self.variables = variables

        self.var_count = len(variables)

    def _get_solutions(self, result: bool) -> List[Tuple[int, ...]]:
        """Метод для получения всех вариантов комбинаций значений переменных. """

        all_solutions = list(itertools.product([0,1 ], repeat=self.var_count))

        return [solution for solution in all_solutions if eval(self.expression.format(*solution)) == result]

    def _get_var_result(self, index_permutation: Tuple[int, ...]) -> str:
        return ''.join([self.variables[i] for i in index_permutation])

    def _check_permutation(self, solutions: List[Tuple[int, ...]],
                           result_bool: bool) -> bool:
        """Метод для проверки корректности перестановки решений."""

        full_solution_match = []

        table_indexes = [i for i in range(len(self.answer_column)) if result_bool == self.answer_column[i]]
        bool_table_rows = [self.bool_table[i] for i in table_indexes]

        for table_row in bool_table_rows:
            table_row_match = []

            for solution_row in solutions:
                solution_match = True

                for i in range(len(solution_row)):
                    if table_row[i] is not None and table_row[i] != solution_row[i]:
                        solution_match = False

                table_row_match.append(solution_match)

            full_solution_match.append(True in table_row_match)

        return False not in full_solution_match

    def _rearrange_solution(self, solutions: List[Tuple[int, ...]],
                            index_permutation: Tuple[int, ...]) -> List[Tuple[int, ...]]:
        """Метод для перестановки колонок решений по перестановке индексов."""

        return [tuple(row[i] for i in index_permutation) for row in solutions]

    def _get_index_permutations(self) -> List[Tuple[int, ...]]:
        """Метод для получения перестановки индексов колонок."""

        base_indexes = [i for i in range(self.var_count)]

        return list(itertools.permutations(base_indexes))

    def get_answer(self) -> str | None:
        """Метод для получения финального строкового ответа из
        переменных."""

        is_few_answers = (True in self.answer_column) and (False in self.answer_column)

        if is_few_answers:
            true_solutions = self._get_solutions(result=True)
            false_solutions = self._get_solutions(result=False)

            index_permutations = self._get_index_permutations()

            for index_perm in index_permutations:
                true_perm_solutions = self._rearrange_solution(solutions=true_solutions,
                                                               index_permutation=index_perm)
                false_perm_solutions = self._rearrange_solution(solutions=false_solutions,
                                                                index_permutation=index_perm)

                true_perm_solutions_check = self._check_permutation(solutions=true_perm_solutions,
                                                                    result_bool=True)
                false_perm_solutions_check = self._check_permutation(solutions=false_perm_solutions,
                                                                     result_bool=False)

                if true_perm_solutions_check and false_perm_solutions_check:
                    return self._get_var_result(index_permutation=index_perm)

        else:
            solutions = self._get_solutions(result=self.answer_column[0])
            index_permutations = self._get_index_permutations()

            for index_perm in index_permutations:
                perm_solutions = self._rearrange_solution(solutions=solutions, index_permutation=index_perm)
                perm_solutions_check = self._check_permutation(solutions=perm_solutions,
                                                               result_bool=self.answer_column[0])

                if perm_solutions_check:
                    return self._get_var_result(index_permutation=index_perm)


if __name__ == '__main__':
    print(AutoSolver(bool_table=[[True, None, None, False],
                                 [None, False, True, None],
                                 [True, False, False, True]],
                     answer_column=[True, True, True],
                     expression='(not {3} or {2}) and ((not {1} or {0}) == (not {2} or {1}))',
                     variables=['x', 'y', 'z', 'w']).get_answer()) # correct

    print(AutoSolver(bool_table=[[False, None, False, None],
                                 [None, True, None, True],
                                 [None, True, True, None]],
                     answer_column=[True, False, False],
                     expression='({0} and {1} or not {0}) and {3} or {2}',
                     variables=['x', 'y', 'z', 'w']).get_answer()) # correct
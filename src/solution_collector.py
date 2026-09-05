from typing import Callable, Optional

from ortools.sat.python import cp_model


class SolutionCollector(cp_model.CpSolverSolutionCallback):
    """CP-SATソルバーが見つけた解を重複排除しつつ収集し、limit件に達したら探索を止めるコールバック。"""

    def __init__(
        self,
        variables: list,
        limit: int = 100,
        callback: Optional[Callable[[int, list], None]] = None,
    ):
        super().__init__()
        self.variables = variables
        # 収集する解の最大件数
        self.limit = limit
        # 解が1件見つかるたびに呼び出す任意のコールバック(solution_no, indexesを受け取る)
        self.callback = callback
        # これまでに見つかった解(各解はTrueになった変数のインデックスのタプル)
        self.solutions: list[tuple[int, ...]] = []
        # 重複した解を弾くための既出インデックス集合
        self.seen: set[tuple[int, ...]] = set()

    def on_solution_callback(self) -> None:
        """ソルバーが新しい解を見つけるたびに呼ばれる(ortoolsのフレームワークからの呼び出し)。"""
        indexes = tuple(
            i for i, var in enumerate(self.variables)
            if self.Value(var) == 1
        )

        if indexes in self.seen:
            return

        self.seen.add(indexes)
        self.solutions.append(indexes)

        if self.callback is not None:
            self.callback(len(self.solutions), list(indexes))

        if len(self.solutions) >= self.limit:
            self.StopSearch()

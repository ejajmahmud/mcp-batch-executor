"""Topological graph dependency solver and batch tool executor."""
from typing import Dict, List, Any, Callable, Set


class BatchExecutor:
    def __init__(self):
        self._steps: Dict[str, Dict[str, Any]] = {}

    def add_step(self, step_id: str, tool_name: str, arguments: Dict[str, Any], depends_on: List[str] = None) -> None:
        self._steps[step_id] = {
            "tool_name": tool_name,
            "arguments": arguments,
            "depends_on": set(depends_on or [])
        }

    def resolve_stages(self) -> List[List[str]]:
        """Resolves execution stages using topological grouping."""
        in_degree: Dict[str, int] = {k: len(v["depends_on"]) for k, v in self._steps.items()}
        stages: List[List[str]] = []
        visited: Set[str] = set()

        while len(visited) < len(self._steps):
            current_stage = [
                node for node, deg in in_degree.items()
                if deg == 0 and node not in visited
            ]
            if not current_stage:
                raise ValueError("Dependency cycle detected in batch steps.")

            stages.append(current_stage)
            for node in current_stage:
                visited.add(node)
                # Decrement dependents
                for other_node, step in self._steps.items():
                    if node in step["depends_on"]:
                        in_degree[other_node] -= 1

        return stages

    def execute(self, tool_runner: Callable[[str, Dict[str, Any]], Any]) -> Dict[str, Any]:
        stages = self.resolve_stages()
        results: Dict[str, Any] = {}

        for stage in stages:
            for step_id in stage:
                step = self._steps[step_id]
                # Render results of prior steps into arguments if templated
                args = {}
                for k, v in step["arguments"].items():
                    if isinstance(v, str) and v.startswith("$"):
                        ref_id = v[1:]
                        args[k] = results.get(ref_id)
                    else:
                        args[k] = v
                results[step_id] = tool_runner(step["tool_name"], args)

        return results

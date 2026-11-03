"""Unit tests for BatchExecutor."""
import unittest
from mcp_batch_executor.executor import BatchExecutor

class TestBatchExecutor(unittest.TestCase):
    def test_independent_steps_single_stage(self):
        b = BatchExecutor()
        b.add_step("s1", "t1", {})
        b.add_step("s2", "t2", {})
        stages = b.resolve_stages()
        self.assertEqual(len(stages), 1)
        self.assertEqual(set(stages[0]), {"s1", "s2"})

    def test_multi_stage_dependencies(self):
        b = BatchExecutor()
        b.add_step("s1", "t1", {})
        b.add_step("s2", "t2", {}, depends_on=["s1"])
        stages = b.resolve_stages()
        self.assertEqual(stages, [["s1"], ["s2"]])

    def test_cycle_detection(self):
        b = BatchExecutor()
        b.add_step("s1", "t1", {}, depends_on=["s2"])
        b.add_step("s2", "t2", {}, depends_on=["s1"])
        with self.assertRaises(ValueError):
            b.resolve_stages()

    def test_execution_pass_results(self):
        b = BatchExecutor()
        b.add_step("step1", "add", {"val": 5})
        b.add_step("step2", "mul", {"input": "$step1"}, depends_on=["step1"])
        results = b.execute(lambda tool, args: args["val"] * 2 if tool == "add" else args["input"] * 3)
        self.assertEqual(results["step1"], 10)
        self.assertEqual(results["step2"], 30)

if __name__ == "__main__":
    unittest.main()

import unittest
from app.domain.column import Column
from app.domain.dataset import DatasetSpecification
from app.domain.enums import ColumnType, StrategyType
from app.generation.context import GenerationContext
from app.generation.generation_plan import GenerationPlan
from app.generation.orchestrator import GenerationOrchestrator
from app.generation.planners.rule_based_planner import RuleBasedPlanner
from app.generation.providers.faker_provider import FakerProvider
from app.generation.registry import StrategyRegistry
from app.generation.strategies.first_name_strategy import FirstNameStrategy
from app.generation.strategies.last_name_strategy import LastNameStrategy
from app.generation.strategies.name_strategy import NameStrategy
from app.generation.strategies.email_strategy import EmailStrategy
from app.generation.strategies.string_strategy import StringStrategy
from app.generation.strategies.text_strategy import TextStrategy
from app.generation.strategies.integer_strategy import IntegerStrategy
from app.generation.strategies.float_strategy import FloatStrategy


class TestGenerationRobustness(unittest.TestCase):

    def setUp(self):
        self.provider = FakerProvider()
        self.registry = StrategyRegistry()
        self.registry.register(NameStrategy(self.provider))
        self.registry.register(FirstNameStrategy(self.provider))
        self.registry.register(LastNameStrategy(self.provider))
        self.registry.register(EmailStrategy(self.provider))
        self.registry.register(StringStrategy(self.provider))
        self.registry.register(IntegerStrategy(self.provider))

    def test_first_and_last_name_generation(self):
        plan_first = GenerationPlan(
            column_name="Customer First Name",
            strategy=StrategyType.NAME,
            parameters={},
            dependencies=[],
        )
        plan_last = GenerationPlan(
            column_name="Customer Last Name",
            strategy=StrategyType.NAME,
            parameters={},
            dependencies=[],
        )

        name_strat = NameStrategy(self.provider)
        context = GenerationContext(current_row={}, generated_rows=[])

        first_name = name_strat.generate(plan_first, context)
        last_name = name_strat.generate(plan_last, context)

        # First and last names should be single words without spaces
        self.assertNotIn(" ", first_name.strip())
        self.assertNotIn(" ", last_name.strip())
        self.assertTrue(len(first_name) > 0)
        self.assertTrue(len(last_name) > 0)

    def test_contextual_email_generation(self):
        email_strat = EmailStrategy(self.provider)
        row = {
            "Customer First Name": "Jessica",
            "Customer Last Name": "Chambers",
        }
        context = GenerationContext(current_row=row, generated_rows=[])
        plan = GenerationPlan(
            column_name="Customer Email",
            strategy=StrategyType.EMAIL,
            parameters={},
            dependencies=[],
        )

        email = email_strat.generate(plan, context)
        self.assertIn("@", email)
        # Email should contain either first_name or last_name in lowercase
        email_lower = email.lower()
        self.assertTrue("jessica" in email_lower or "chambers" in email_lower)

    def test_rule_based_planner_strategy_inference(self):
        planner = RuleBasedPlanner()
        spec = DatasetSpecification(
            rows=5,
            columns=[
                Column(name="Customer Id", type=ColumnType.INTEGER, constraints=[], description="", example="1"),
                Column(name="Customer First Name", type=ColumnType.STRING, constraints=[], description="", example="Jessica"),
                Column(name="Customer Last Name", type=ColumnType.STRING, constraints=[], description="", example="Chambers"),
                Column(name="Customer Email", type=ColumnType.STRING, constraints=[], description="", example="jessica@example.com"),
                Column(name="Product Review", type=ColumnType.STRING, constraints=[], description="", example="Great product!"),
            ],
            relationships=[],
            metadata={},
        )

        plans = planner.create_plan(spec)
        plan_map = {p.column_name: p.strategy for p in plans}

        self.assertEqual(plan_map["Customer First Name"], StrategyType.FIRST_NAME)
        self.assertEqual(plan_map["Customer Last Name"], StrategyType.LAST_NAME)
        self.assertEqual(plan_map["Customer Email"], StrategyType.EMAIL)
        self.assertEqual(plan_map["Product Review"], StrategyType.TEXT)

    def test_orchestrator_full_generation(self):
        planner = RuleBasedPlanner()
        orchestrator = GenerationOrchestrator(
            registry=self.registry,
            planner=planner,
        )

        spec = DatasetSpecification(
            rows=3,
            columns=[
                Column(name="Customer Id", type=ColumnType.INTEGER, constraints=[], description="", example="1"),
                Column(name="Customer First Name", type=ColumnType.NAME, constraints=[], description="", example="Jessica"),
                Column(name="Customer Last Name", type=ColumnType.NAME, constraints=[], description="", example="Chambers"),
                Column(name="Customer Email", type=ColumnType.EMAIL, constraints=[], description="", example="jessica@example.com"),
            ],
            relationships=[],
            metadata={},
        )

        rows = orchestrator.generate(spec)
        self.assertEqual(len(rows), 3)

        for r in rows:
            self.assertNotIn(" ", r["Customer First Name"].strip())
            self.assertNotIn(" ", r["Customer Last Name"].strip())
            self.assertIn("@", r["Customer Email"])
            # Verify email matches first or last name
            fn = r["Customer First Name"].lower()
            ln = r["Customer Last Name"].lower()
            em = r["Customer Email"].lower()
            self.assertTrue(fn in em or ln in em)

    def test_text_and_description_generation(self):
        text_content = self.provider.generate_text_content(column_name="description")
        self.assertTrue(len(text_content.split()) >= 3)

    def test_roll_number_and_code_generation(self):
        roll_num = self.provider.generate_string(column_name="roll_number")
        sku = self.provider.generate_string(column_name="sku")
        student_id = self.provider.generate_string(column_name="student_id")

        self.assertRegex(roll_num, r"^\d{4}-[A-Z]+-\d{3}$")
    def test_null_parameter_resilience(self):
        plan_int = GenerationPlan(
            column_name="manager_id",
            strategy=StrategyType.INTEGER,
            parameters={"minimum": None, "maximum": None},
            dependencies=[],
        )
        context = GenerationContext(current_row={}, generated_rows=[])
        int_strat = IntegerStrategy(self.provider)
        val_int = int_strat.generate(plan_int, context)
        self.assertIsInstance(val_int, int)
        self.assertTrue(1000 <= val_int <= 9999)

        plan_float = GenerationPlan(
            column_name="cgpa",
            strategy=StrategyType.FLOAT,
            parameters={"minimum": None, "maximum": None},
            dependencies=[],
        )
        float_strat = FloatStrategy(self.provider)
        val_float = float_strat.generate(plan_float, context)
        self.assertIsInstance(val_float, float)
        self.assertTrue(0.0 <= val_float <= 4.0)


if __name__ == "__main__":
    unittest.main()

from app.generation.llm.llm_generator import LLMGenerator
from app.generation.orchestrator import GenerationOrchestrator
from app.generation.planners.llm_planner import LLMPlanner
from app.generation.providers.faker_provider import FakerProvider
from app.generation.registry import StrategyRegistry

from app.generation.strategies.integer_strategy import IntegerStrategy
from app.generation.strategies.float_strategy import FloatStrategy
from app.generation.strategies.boolean_strategy import BooleanStrategy
from app.generation.strategies.string_strategy import StringStrategy
from app.generation.strategies.name_strategy import NameStrategy
from app.generation.strategies.first_name_strategy import FirstNameStrategy
from app.generation.strategies.last_name_strategy import LastNameStrategy
from app.generation.strategies.email_strategy import EmailStrategy

from app.generation.strategies.uuid_strategy import UUIDStrategy
from app.generation.strategies.date_strategy import DateStrategy
from app.generation.strategies.text_strategy import TextStrategy
from app.generation.schema.schema_generator import SchemaGenerator
from app.generation.strategies.phone_strategy import PhoneStrategy
from app.generation.strategies.address_strategy import AddressStrategy
from app.generation.strategies.company_strategy import CompanyStrategy
from app.generation.strategies.salary_strategy import SalaryStrategy
from app.generation.strategies.datetime_strategy import DatetimeStrategy

def get_orchestrator() -> GenerationOrchestrator:

    provider = FakerProvider()

    llm = LLMGenerator()

    registry = StrategyRegistry()

    registry.register(IntegerStrategy(provider))
    registry.register(FloatStrategy(provider))
    registry.register(BooleanStrategy(provider))
    registry.register(StringStrategy(provider))
    registry.register(NameStrategy(provider))
    registry.register(FirstNameStrategy(provider))
    registry.register(LastNameStrategy(provider))
    registry.register(EmailStrategy(provider))
    registry.register(PhoneStrategy(provider))
    registry.register(UUIDStrategy(provider))
    registry.register(DateStrategy(provider))
    registry.register(AddressStrategy(provider))
    registry.register(CompanyStrategy(provider))
    registry.register(SalaryStrategy(provider))
    registry.register(DatetimeStrategy(provider))
    registry.register(TextStrategy(llm, provider))

    planner = LLMPlanner()

    return GenerationOrchestrator(
        registry=registry,
        planner=planner,
    )

_schema_generator = SchemaGenerator()
def get_schema_generator():

    return _schema_generator
from enum import Enum,StrEnum


class ColumnType(StrEnum):
    NAME = "name"
    FIRST_NAME = "first_name"
    LAST_NAME = "last_name"
    EMAIL = "email"
    PHONE = "phone"

    ADDRESS = "address"
    COMPANY = "company"

    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"

    STRING = "string"

    DATE = "date"
    DATETIME = "datetime"

    SALARY = "salary"

    TEXT = "text"

class ConstraintType(str, Enum):
    MINIMUM = "minimum"
    MAXIMUM = "maximum"
    REGEX = "regex"
    UNIQUE = "unique"
    NULLABLE = "nullable"
    CHOICES = "choices"


class OutputFormat(str, Enum):
    CSV = "csv"
    JSON = "json"
    EXCEL = "excel"
    PARQUET = "parquet"

class RelationshipType(str, Enum):
    LOOKUP = "lookup"
    DEPENDENCY = "dependency"
    REFERENCE = "reference"


class StrategyType(StrEnum):
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"

    STRING = "string"

    NAME = "name"
    FIRST_NAME = "first_name"
    LAST_NAME = "last_name"
    EMAIL = "email"
    PHONE = "phone"

    ADDRESS = "address"
    COMPANY = "company"

    UUID = "uuid"

    DATE = "date"
    DATETIME = "datetime"

    TEXT = "text"

    SALARY = "salary"
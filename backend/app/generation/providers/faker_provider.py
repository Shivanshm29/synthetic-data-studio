from datetime import date

from faker import Faker

from app.generation.providers.base_provider import BaseProvider


class FakerProvider(BaseProvider):

    def __init__(self) -> None:
        self.fake = Faker()

    def generate_integer(
        self,
        min_value: int | None = None,
        max_value: int | None = None,
    ) -> int:
        if min_value is None:
            min_value = 0
        if max_value is None:
            max_value = 100
        if min_value > max_value:
            min_value, max_value = max_value, min_value

        return self.fake.random_int(
            min=min_value,
            max=max_value,
        )

    def generate_float(
        self,
        min_value: float | None = None,
        max_value: float | None = None,
    ) -> float:
        if min_value is None:
            min_value = 0.0
        if max_value is None:
            max_value = 100.0
        if min_value > max_value:
            min_value, max_value = max_value, min_value

        return self.fake.pyfloat(
            min_value=min_value,
            max_value=max_value,
            right_digits=2,
        )

    def generate_boolean(self) -> bool:
        return self.fake.boolean()

    def generate_string(
        self,
        min_length: int | None = None,
        max_length: int | None = None,
        column_name: str | None = None,
    ) -> str:
        col_lower = (column_name or "").lower().replace(" ", "_")

        if any(k in col_lower for k in ["first_name", "firstname", "first", "fname", "given_name"]):
            return self.generate_first_name()
        if any(k in col_lower for k in ["last_name", "lastname", "lname", "surname", "family_name"]):
            return self.generate_last_name()
        if any(k in col_lower for k in ["description", "review", "comment", "feedback", "summary", "bio", "details", "notes", "article"]):
            return self.generate_text_content(column_name)
        if any(k in col_lower for k in ["roll_number", "roll_no", "rollno", "registration_no", "reg_no", "enrollment_no"]):
            year = self.fake.random_int(2021, 2024)
            dept = self.fake.random_element(["CS", "EE", "ME", "CE", "BA", "PHY", "EC"])
            num = self.fake.random_int(100, 999)
            return f"{year}-{dept}-{num}"

        if any(k in col_lower for k in ["sku", "serial_no", "serial_number", "ticket_no", "invoice_no", "account_no", "order_no", "order_id", "transaction_id", "code"]):
            return self.fake.bothify(text="??-#####").upper()

        if any(k in col_lower for k in ["student_id", "advisor_id", "emp_id", "employee_id", "user_id", "customer_id"]):
            prefix = self.fake.random_int(2020, 2024) if "student" in col_lower else self.fake.random_int(1000, 9999)
            suffix = self.fake.random_int(100, 999) if "student" in col_lower else ""
            return f"{prefix}{suffix}" if suffix else str(prefix)

        if any(k in col_lower for k in ["department", "dept"]):
            return self.fake.random_element([
                "Engineering", "Human Resources", "Finance", "Marketing",
                "Sales", "Operations", "Product Management", "Legal", "Customer Support", "R&D"
            ])
        if any(k in col_lower for k in ["designation", "job", "title", "role", "position"]):
            return self.fake.job()
        if any(k in col_lower for k in ["employment", "job_type", "work_type", "contract"]):
            return self.fake.random_element(["Full-time", "Part-time", "Contract", "Remote", "Internship"])
        if any(k in col_lower for k in ["location", "city", "office", "site", "work_location"]):
            return self.fake.city()
        if any(k in col_lower for k in ["country", "nation"]):
            return self.fake.country()
        if any(k in col_lower for k in ["status", "state"]):
            return self.fake.random_element(["Active", "Inactive", "Pending", "Approved", "Completed"])

        if max_length and max_length < 15:
            return self.fake.word()[:max_length].capitalize()

        return self.fake.word().capitalize()

    def generate_name(self) -> str:
        return self.fake.name()

    def generate_first_name(self) -> str:
        return self.fake.first_name()

    def generate_last_name(self) -> str:
        return self.fake.last_name()

    def generate_email(
        self,
        first_name: str | None = None,
        last_name: str | None = None,
    ) -> str:
        import re
        f_clean = re.sub(r"[^a-zA-Z]", "", first_name or "").lower()
        l_clean = re.sub(r"[^a-zA-Z]", "", last_name or "").lower()

        if f_clean or l_clean:
            domains = ["example.com", "example.org", "example.net", "gmail.com", "yahoo.com", "outlook.com"]
            domain = self.fake.random_element(domains)
            formats = []
            if f_clean and l_clean:
                formats.extend([
                    f"{f_clean}.{l_clean}@{domain}",
                    f"{f_clean}{l_clean}@{domain}",
                    f"{f_clean}_{l_clean}@{domain}",
                    f"{f_clean[0]}{l_clean}@{domain}",
                ])
            elif f_clean:
                formats.append(f"{f_clean}{self.fake.random_int(10, 99)}@{domain}")
            elif l_clean:
                formats.append(f"{l_clean}{self.fake.random_int(10, 99)}@{domain}")

            if formats:
                return self.fake.random_element(formats)

        return self.fake.email()

    def generate_text_content(
        self,
        column_name: str | None = None,
    ) -> str:
        return self.fake.paragraph(nb_sentences=3)

    def generate_phone(self) -> str:
        return self.fake.phone_number()

    def generate_uuid(self) -> str:
        return str(self.fake.uuid4())

    def generate_date(
        self,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> date:

        return self.fake.date_between(
            start_date=start_date or "-30y",
            end_date=end_date or "today",
        )
    def phone(self) -> str:
        return self.fake.phone_number()

    def generate_address(self) -> str:
        return self.fake.address()

    def generate_company(self) -> str:
        return self.fake.company()

    def generate_datetime(self) -> str:
        return str(self.fake.date_time_between(
            start_date="-30y",
            end_date="now",
        ))
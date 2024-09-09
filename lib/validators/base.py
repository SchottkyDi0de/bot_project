class Validator:
    min = max = 0

    def __init__(self, data: str | None=None):
        try:
            self.data = int(data)
        except (ValueError, TypeError):
            self.data = data

    @property
    def limits(self) -> str:
        return f"{self.min} ≤ x ≤ {self.max}"

    def validate(self) -> bool:
        return self.min <= self.data <= self.max

    def post_procces(self):
        return self.data

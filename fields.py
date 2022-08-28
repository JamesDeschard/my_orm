class CharField:
    def __init__(self, max_length) -> None:
        self.max_length = max_length
    
    def create_migration(self) -> str:
        return f'varchar ({self.max_length})'


class IntegerField:
    def create_migration(self) -> str:
        return f'numeric (10, 2)'
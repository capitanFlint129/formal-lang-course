class Type:
    def __init__(self, params=None):
        self.params = params or []

    def __eq__(self, other):
        return (
            isinstance(other, Type)
            and self.__class__ == other.__class__
            and self.params == other.params
        )


class StringType(Type):
    pass


class IntType(Type):
    pass


class BoolType(Type):
    pass


class FAType(Type):
    pass

class Type:
    """
    Base class for query language types
    """

    def __eq__(self, other):
        return isinstance(other, Type) and self.__class__ == other.__class__

    def __str__(self):
        return self.__class__.__name__


class StringType(Type):
    pass


class IntType(Type):
    pass


class BoolType(Type):
    pass


class AutomataType(Type):
    """
    Base class for query language automata types
    """

    pass


class FAType(AutomataType):
    pass


class RSMType(AutomataType):
    pass


class ContainerType(Type):
    """
    Base class for query language container types
    """

    def __init__(self, params=None):
        self.params: tuple[Type] = params or []

    def __eq__(self, other):
        return super().__eq__(other) and self.params == other.params

    def __str__(self):
        return f"{self.__class__.__name__}{self.params}"


class ListType(ContainerType):
    pass


class SetType(ContainerType):
    def __eq__(self, other):
        return super().__eq__(other) and set(self.params) == set(other.params)


class LambdaType(Type):
    pass
    # def __init__(self, params=None, result=None):
    #     self.params: list[Type] = params or []
    #     self.result: typing.Optional[Type] = result

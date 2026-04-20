from enum import Enum, auto


class WinKind(Enum):
    FOUGHT = auto()
    FUSENSHO = auto()


class WinPolicy(Enum):
    FOUGHT_ONLY = auto()
    CREDITED = auto()

    def includes(self) -> set[WinKind]:
        if self is WinPolicy.FOUGHT_ONLY:
            return {WinKind.FOUGHT}
        if self is WinPolicy.CREDITED:
            return {WinKind.FOUGHT, WinKind.FUSENSHO}
        raise ValueError(f"Unsupported win policy: {self}")


class BashoBasis(Enum):
    SELECTED = auto()
    CONTAINING = auto()


class BoutBasis(Enum):
    EXPECTED = auto()
    AVAILABLE = auto()

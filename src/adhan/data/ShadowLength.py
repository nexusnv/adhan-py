class ShadowLength:
    SINGLE = 1.0
    DOUBLE = 2.0

    def __init__(self, shadow_length: float):
        self._shadow_length = shadow_length

    @property
    def shadow_length(self) -> float:
        return self._shadow_length

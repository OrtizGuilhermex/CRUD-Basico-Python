from abc import ABC, abstractmethod

class Sensor(ABC):
    def __init__(self, codigo: str, nome_equipamento: str, tipo: str):
        self.codigo = codigo
        self.nome_equipamento = nome_equipamento
        self.tipo = tipo

    @abstractmethod
    def verificar_alerta(self, valor: float) -> bool:
        pass

    def __str__(self):
        return f"Código: {self.codigo} | Tipo: {self.tipo} | Equipamento: {self.nome_equipamento}"

class SensorTemperatura(Sensor):
    LIMITE = 80.0

    def __init__(self, codigo: str, nome_equipamento: str):
        super().__init__(codigo, nome_equipamento, "Temperatura")

    def verificar_alerta(self, valor: float) -> bool:
        return valor > self.LIMITE

class SensorVibracao(Sensor):
    FREQUENCIA_ESPERADA = 60.0

    def __init__(self, codigo: str, nome_equipamento: str):
        super().__init__(codigo, nome_equipamento, "Vibração")

    def verificar_alerta(self, valor: float) -> bool:
        return valor != self.FREQUENCIA_ESPERADA

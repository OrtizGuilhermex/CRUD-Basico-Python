class Medicao:
    def __init__(self, valor: float, data_hora: str, alerta: bool = False, prioridade: str = "BAIXA"):
        self.valor = valor
        self.data_hora = data_hora
        self.alerta = alerta
        self.prioridade = prioridade

    def __str__(self):
        alerta_str = f" ⚠️ ALERTA [{self.prioridade}]" if self.alerta else ""
        return f"Valor: {self.valor:.2f} | Data: {self.data_hora}{alerta_str}"

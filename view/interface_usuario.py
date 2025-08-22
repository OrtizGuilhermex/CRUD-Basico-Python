from service.sensor_service import SensorService
from datetime import datetime

class InterfaceUsuario:
    def __init__(self):
        self.service = SensorService()

    def exibir_menu(self):
        while True:
            print("""
=========================================
 Sistema de Monitoramento WEG – Versão 3.0
=========================================

1 - Cadastrar Sensor
2 - Listar Sensores
3 - Registrar Medição
4 - Histórico
5 - Alertas por Sensor
6 - Sensores Críticos
7 - Exportar CSV
8 - Exportar PDF
9 - Plotar Gráfico
0 - Sair
""")
            try:
                opcao = int(input("Digite a opção: "))
                if opcao == 0:
                    print("Encerrando sistema!")
                    break
                self.executar_opcao(opcao)
            except Exception as e:
                print(f"❌ Erro: {e}")

    def executar_opcao(self, opcao):
        if opcao == 1:
            codigo = input("Código do sensor: ")
            nome = input("Nome do equipamento: ")
            tipo = int(input("Tipo (1-Temperatura / 2-Vibração): "))
            s = self.service.cadastrar_sensor(codigo, nome, tipo)
            print(f"✅ Sensor cadastrado: {s}")
        elif opcao == 2:
            for s in self.service.listar_sensores():
                print(f"Código: {s[0]} | Nome: {s[1]} | Tipo: {s[2]}")
        elif opcao == 3:
            codigo = input("Código: ")
            valor = float(input("Valor: "))
            data = input("Data e hora (dd/MM/yyyy HH:mm): ")
            med = self.service.registrar_medicao(codigo, valor, data)
            print(f"✅ Medição registrada: {med}")
        elif opcao == 4:
            codigo = input("Código: ")
            for m in self.service.listar_medicoes(codigo):
                print(m)
        elif opcao == 5:
            for s in self.service.listar_sensores():
                qtd = self.service.contar_alertas(s[0])
                print(f"Código: {s[0]} | Alertas: {qtd}")
        elif opcao == 6:
            criticos = self.service.sensores_criticos()
            if criticos:
                for c, total in criticos:
                    print(f"Sensor {c} possui {total} alertas!")
            else:
                print("Nenhum sensor crítico.")
        elif opcao == 7:
            caminho = input("Nome do CSV: ")
            self.service.exportar_csv(caminho)
            print("✅ CSV exportado!")
        elif opcao == 8:
            caminho = input("Nome do PDF: ")
            self.service.exportar_pdf(caminho)
            print("✅ PDF exportado!")
        elif opcao == 9:
            codigo = input("Código do sensor: ")
            self.service.plotar_historico(codigo)
        else:
            print("Opção inválida!")

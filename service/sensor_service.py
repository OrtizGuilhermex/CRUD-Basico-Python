import sqlite3
from model.sensor import SensorTemperatura, SensorVibracao
from model.medicao import Medicao
import logging
from datetime import datetime
import matplotlib.pyplot as plt
import csv
from fpdf import FPDF

# Logging
logging.basicConfig(filename="weg.log", level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")

class SensorService:
    def __init__(self, db_path="weg.db"):
        self.conn = sqlite3.connect(db_path)
        self._criar_tabelas()

    def _criar_tabelas(self):
        c = self.conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS sensores (
                        codigo TEXT PRIMARY KEY,
                        nome TEXT,
                        tipo TEXT
                    )""")
        c.execute("""CREATE TABLE IF NOT EXISTS medicoes (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        codigo_sensor TEXT,
                        valor REAL,
                        data_hora TEXT,
                        alerta INTEGER,
                        prioridade TEXT,
                        FOREIGN KEY(codigo_sensor) REFERENCES sensores(codigo)
                    )""")
        self.conn.commit()

    # CADASTRO
    def cadastrar_sensor(self, codigo, nome, tipo):
        c = self.conn.cursor()
        if tipo == 1:
            sensor = SensorTemperatura(codigo, nome)
        elif tipo == 2:
            sensor = SensorVibracao(codigo, nome)
        else:
            raise ValueError("Tipo inválido!")
        try:
            c.execute("INSERT INTO sensores VALUES (?, ?, ?)",
                      (sensor.codigo, sensor.nome_equipamento, sensor.tipo))
            self.conn.commit()
            logging.info(f"Sensor cadastrado: {sensor}")
            return sensor
        except sqlite3.IntegrityError:
            raise ValueError("Código de sensor já existe!")

    # LISTAR SENSORES
    def listar_sensores(self):
        c = self.conn.cursor()
        c.execute("SELECT codigo, nome, tipo FROM sensores")
        return c.fetchall()

    # REGISTRAR MEDIÇÃO
    def registrar_medicao(self, codigo, valor, data_hora):
        c = self.conn.cursor()
        c.execute("SELECT tipo FROM sensores WHERE codigo=?", (codigo,))
        row = c.fetchone()
        if not row:
            raise KeyError("Sensor não encontrado!")
        tipo = row[0]
        if tipo == "Temperatura":
            alerta = valor > 80.0
        else:
            alerta = valor != 60.0

        # Prioridade
        if alerta:
            prioridade = "ALTA" if (tipo=="Temperatura" and valor>90) else "MÉDIA"
        else:
            prioridade = "BAIXA"

        c.execute("INSERT INTO medicoes (codigo_sensor, valor, data_hora, alerta, prioridade) VALUES (?,?,?,?,?)",
                  (codigo, valor, data_hora, int(alerta), prioridade))
        self.conn.commit()

        med = Medicao(valor, data_hora, alerta, prioridade)
        logging.info(f"Medição registrada: Sensor={codigo}, Valor={valor}, Alerta={alerta}, Prioridade={prioridade}")
        return med

    # LISTAR MEDIÇÕES
    def listar_medicoes(self, codigo):
        c = self.conn.cursor()
        c.execute("SELECT valor, data_hora, alerta, prioridade FROM medicoes WHERE codigo_sensor=? ORDER BY data_hora", (codigo,))
        rows = c.fetchall()
        return [Medicao(v, d, bool(a), p) for v,d,a,p in rows]

    # CONTAR ALERTAS
    def contar_alertas(self, codigo):
        c = self.conn.cursor()
        c.execute("SELECT COUNT(*) FROM medicoes WHERE codigo_sensor=? AND alerta=1", (codigo,))
        return c.fetchone()[0]

    # SENSORES CRÍTICOS
    def sensores_criticos(self):
        c = self.conn.cursor()
        c.execute("""SELECT codigo_sensor, COUNT(*) as total_alertas
                     FROM medicoes
                     WHERE alerta=1
                     GROUP BY codigo_sensor
                     HAVING total_alertas>3""")
        return c.fetchall()

    # EXPORTAR CSV
    def exportar_csv(self, caminho="medicoes.csv"):
        c = self.conn.cursor()
        c.execute("SELECT codigo_sensor, valor, data_hora, alerta, prioridade FROM medicoes")
        rows = c.fetchall()
        with open(caminho, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Codigo", "Valor", "DataHora", "Alerta", "Prioridade"])
            writer.writerows(rows)
        logging.info(f"CSV exportado: {caminho}")

    # EXPORTAR PDF
    def exportar_pdf(self, caminho="medicoes.pdf"):
        c = self.conn.cursor()
        c.execute("SELECT codigo_sensor, valor, data_hora, alerta, prioridade FROM medicoes")
        rows = c.fetchall()
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200,10,"Relatorio de Medicoes", ln=True, align="C")
        pdf.ln(5)
        for r in rows:
            alerta = "⚠️" if r[3] else ""
            pdf.cell(0,10,f"{r[0]} | Valor: {r[1]:.2f} | {r[2]} | {r[4]} {alerta}", ln=True)
        pdf.output(caminho)
        logging.info(f"PDF exportado: {caminho}")

    # GRÁFICO
    def plotar_historico(self, codigo):
        c = self.conn.cursor()
        c.execute("SELECT data_hora, valor FROM medicoes WHERE codigo_sensor=? ORDER BY data_hora", (codigo,))
        dados = c.fetchall()
        if not dados:
            print("Sem dados para gráfico!")
            return
        datas = [datetime.strptime(d[0], "%d/%m/%Y %H:%M") for d in dados]
        valores = [d[1] for d in dados]
        import matplotlib.pyplot as plt
        plt.plot(datas, valores, marker='o')
        plt.title(f"Histórico de Medições - Sensor {codigo}")
        plt.xlabel("Data/Hora")
        plt.ylabel("Valor")
        plt.grid(True)
        plt.show()

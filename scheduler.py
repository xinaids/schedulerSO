import tkinter as tk
from tkinter import ttk, messagebox

class Escalonador:
    def __init__(self):
        self.processos = []

    def adicionar_processo(self, pid, chegada, execucao):
        self.processos.append((pid, int(chegada), int(execucao)))

    def fcfs(self, ttc):
        self.processos.sort(key=lambda p: p[1])
        tempo = 0
        resultados = []
        espera_total = 0
        for pid, chegada, execucao in self.processos:
            if tempo < chegada:
                tempo = chegada
            inicio = tempo
            fim = tempo + execucao
            espera = tempo - chegada
            tempo = fim + ttc
            espera_total += espera
            resultados.append((pid, inicio, fim, espera))
        return resultados, espera_total / len(self.processos)

    def sjf_np(self, ttc):
        processos = self.processos[:]
        processos.sort(key=lambda x: (x[1], x[2]))
        tempo = 0
        prontos = []
        resultados = []
        espera_total = 0
        while processos or prontos:
            while processos and processos[0][1] <= tempo:
                prontos.append(processos.pop(0))
            if prontos:
                prontos.sort(key=lambda x: x[2])
                pid, chegada, execucao = prontos.pop(0)
                inicio = tempo
                fim = tempo + execucao
                espera = tempo - chegada
                tempo = fim + ttc
                espera_total += espera
                resultados.append((pid, inicio, fim, espera))
            else:
                tempo += 1
        return resultados, espera_total / len(self.processos)

    def sjf_preemptivo(self, ttc):
        processos = sorted(self.processos, key=lambda x: x[1])
        tempo = 0
        prontos = []
        resultados = []
        restantes = {pid: burst for pid, _, burst in processos}
        chegada = {pid: arr for pid, arr, _ in processos}
        inicio_exec = {}
        completo = set()

        index = 0
        processo_atual = None

        while len(completo) < len(processos):
            while index < len(processos) and processos[index][1] <= tempo:
                prontos.append(processos[index][0])
                index += 1

            if prontos:
                processo_atual = min(prontos, key=lambda p: restantes[p])
                if processo_atual not in inicio_exec:
                    inicio_exec[processo_atual] = tempo
                restantes[processo_atual] -= 1

                if restantes[processo_atual] == 0:
                    fim = tempo + 1
                    espera = fim - chegada[processo_atual] - sum([p[2] for p in self.processos if p[0] == processo_atual])
                    resultados.append((processo_atual, inicio_exec[processo_atual], fim, espera))
                    prontos.remove(processo_atual)
                    completo.add(processo_atual)
                    tempo += ttc
            tempo += 1

        media_espera = sum(p[3] for p in resultados) / len(resultados)
        return resultados, media_espera

    def round_robin(self, quantum, ttc):
        fila = []
        processos = sorted(self.processos, key=lambda x: x[1])
        tempo = 0
        index = 0
        restantes = {p[0]: p[2] for p in processos}
        chegada = {p[0]: p[1] for p in processos}
        resultados = []
        completados = {}
        fila = [p[0] for p in processos if p[1] == 0]

        while fila or index < len(processos):
            if not fila and index < len(processos):
                if processos[index][1] > tempo:
                    tempo = processos[index][1]
                fila.append(processos[index][0])
                index += 1

            pid = fila.pop(0)
            if pid not in completados:
                inicio = tempo
            else:
                inicio = tempo
            exec_time = min(quantum, restantes[pid])
            tempo += exec_time
            restantes[pid] -= exec_time

            for i in range(index, len(processos)):
                if processos[i][1] <= tempo:
                    fila.append(processos[i][0])
                    index += 1

            if restantes[pid] > 0:
                fila.append(pid)
                tempo += ttc
            else:
                fim = tempo
                espera = fim - chegada[pid] - sum([p[2] for p in self.processos if p[0] == pid])
                completados[pid] = (pid, inicio, fim, espera)
                resultados.append(completados[pid])
        media_espera = sum(p[3] for p in resultados) / len(resultados)
        return resultados, media_espera

class IntroDialog(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Introdução")
        self.geometry("600x400")
        self.configure(bg="#f0f0f0")
        self.resizable(False, False)

        self.content = tk.Frame(self, bg="#f0f0f0", padx=20, pady=20)
        self.content.pack(expand=True, fill="both")

        tk.Label(self.content, text="TRABALHO 1 DE SISTEMAS OPERACIONAIS", font=("Helvetica", 16, "bold"), bg="#f0f0f0").pack(pady=10)
        tk.Label(self.content, text="Autores: Mateus Medeiros Schneider e Miguel Bohrz Vogel", font=("Helvetica", 12), bg="#f0f0f0").pack()
        tk.Label(self.content, text="Orientador: Prof. Dr. Luis Claudio Gubert", font=("Helvetica", 12), bg="#f0f0f0").pack()
        tk.Label(self.content, text="\nEste programa simula algoritmos de escalonamento de processos.", bg="#f0f0f0", justify="center").pack(pady=10)

        tk.Label (bg="#f0f0f0", justify="left", anchor="w").pack()

        tk.Button(self.content, text="Fechar e Iniciar", command=self.destroy).pack(pady=20)
        self.grab_set()
        self.wait_window(self)


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulador de Escalonamento")
        self.scheduler = Escalonador()

        self.setup_ui()

        menubar = tk.Menu(self.root)
        ajuda_menu = tk.Menu(menubar, tearoff=0)
        ajuda_menu.add_command(label="Informações do Programa", command=self.exibir_ajuda)
        menubar.add_cascade(label="Ajuda", menu=ajuda_menu)
        self.root.config(menu=menubar)

    def setup_ui(self):
        input_frame = tk.LabelFrame(self.root, text="Inserir Processos")
        input_frame.grid(row=0, column=0, padx=10, pady=5, sticky="ew", columnspan=6)

        tk.Label(input_frame, text="PID").grid(row=0, column=0)
        tk.Label(input_frame, text="Chegada").grid(row=0, column=1)
        tk.Label(input_frame, text="Execução").grid(row=0, column=2)

        self.pid = tk.Entry(input_frame)
        self.chegada = tk.Entry(input_frame)
        self.execucao = tk.Entry(input_frame)
        self.pid.grid(row=1, column=0)
        self.chegada.grid(row=1, column=1)
        self.execucao.grid(row=1, column=2)

        tk.Button(input_frame, text="Adicionar Processo", command=self.adicionar_processo).grid(row=1, column=3)

        self.policy = ttk.Combobox(input_frame, values=["FCFS", "SJF Não Preemptivo", "SJF Preemptivo", "Round Robin"])
        self.policy.grid(row=2, column=0)
        self.policy.set("FCFS")

        tk.Label(input_frame, text="Quantum").grid(row=2, column=1)
        self.quantum = tk.Entry(input_frame)
        self.quantum.grid(row=2, column=2)

        tk.Label(input_frame, text="TTC").grid(row=2, column=3)
        self.ttc = tk.Entry(input_frame)
        self.ttc.grid(row=2, column=4)

        tk.Button(input_frame, text="Simular", command=self.simular).grid(row=2, column=5)

        self.adicionados_frame = tk.LabelFrame(self.root, text="Processos Adicionados")
        self.adicionados_frame.grid(row=1, column=0, padx=10, pady=5, columnspan=6, sticky="ew")

        self.adicionados_output = tk.Text(self.adicionados_frame, height=6, width=90)
        self.adicionados_output.pack()
        tk.Button(self.adicionados_frame, text="Limpar Adicionados", command=self.limpar_adicionados).pack(pady=2)

        self.result_frame = tk.LabelFrame(self.root, text="Resultados da Simulação")
        self.result_frame.grid(row=2, column=0, padx=10, pady=5, columnspan=6, sticky="ew")

        self.output = tk.Text(self.result_frame, height=10, width=90)
        self.output.pack()
        tk.Button(self.result_frame, text="Limpar Resultados", command=self.limpar_resultados).pack(pady=2)

    def adicionar_processo(self):
        try:
            pid = self.pid.get()
            chegada = int(self.chegada.get())
            execucao = int(self.execucao.get())
            self.scheduler.adicionar_processo(pid, chegada, execucao)
            self.adicionados_output.insert(tk.END, f"Adicionado: PID={pid}, Chegada={chegada}, Execução={execucao}\n")
            self.pid.delete(0, tk.END)
            self.chegada.delete(0, tk.END)
            self.execucao.delete(0, tk.END)
        except:
            messagebox.showerror("Erro", "Dados inválidos")

    def simular(self):
        politica = self.policy.get()
        try:
            ttc = int(self.ttc.get()) if self.ttc.get() else 0
            quantum = int(self.quantum.get()) if self.quantum.get() else 1

            if politica == "FCFS":
                res, media = self.scheduler.fcfs(ttc)
            elif politica == "SJF Não Preemptivo":
                res, media = self.scheduler.sjf_np(ttc)
            elif politica == "SJF Preemptivo":
                res, media = self.scheduler.sjf_preemptivo(ttc)
            elif politica == "Round Robin":
                res, media = self.scheduler.round_robin(quantum, ttc)
            else:
                raise ValueError

            self.output.insert(tk.END, f"\nPolítica: {politica}\n")
            for pid, ini, fim, esp in res:
                self.output.insert(tk.END, f"{pid}: Início={ini}, Fim={fim}, Espera={esp}\n")
            self.output.insert(tk.END, f"Tempo médio de espera: {media:.2f}\n\n")

        except Exception as e:
            messagebox.showerror("Erro", f"Erro na simulação: {e}")

    def limpar_adicionados(self):
        self.adicionados_output.delete('1.0', tk.END)

    def limpar_resultados(self):
        self.output.delete('1.0', tk.END)

    def exibir_ajuda(self):
        texto = (
            "Simulador de Escalonamento de Processos\n\n"
            "Este programa permite simular quatro algoritmos clássicos de escalonamento:\n"
            "\U0001F539 FCFS: Ordem de chegada.\n"
            "\U0001F539 SJF Não Preemptivo: Executa o menor job entre os disponíveis.\n"
            "\U0001F539 SJF Preemptivo: Interrompe para executar o menor restante.\n"
            "\U0001F539 Round Robin: Executa por quantum e reentra na fila se necessário.\n\n"
            "Termos que são utilizados no simulador:\n\n"
            "\U0001F539 PID: Identificador do processo.\n"
            "\U0001F539 Tempo de Execução: Tempo total necessário para o processo.\n"
            "\U0001F539 Quantum: Tempo máximo de uso do processador por vez.\n"
            "\U0001F539 Troca de Contexto: Tempo para alternar entre processos.\n\n"
            "Parâmetros:\n"
            "- Quantum: necessário para Round Robin.\n"
            "- TTC: tempo de troca de contexto.\n"
        )
        messagebox.showinfo("Ajuda - Sobre o Programa", texto)

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
    app = App(root)
    root.mainloop()

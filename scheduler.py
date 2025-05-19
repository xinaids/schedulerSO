import tkinter as tk
from tkinter import ttk, messagebox

class Escalonador:
    def __init__(self):
        self.processos = []

    def adicionar_processo(self, pid, chegada, execucao):
        self.processos.append((pid, int(chegada), int(execucao)))

    def fcfs(self, ttc):
        self.processos.sort(key=lambda p: p[1])  # ordenar por tempo de chegada
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

        termos = (
            "🔹 PID: Identificador do processo.\n"
            "🔹 Tempo de Execução: Tempo total necessário para o processo.\n"
            "🔹 Quantum: Tempo máximo de uso do processador por vez.\n"
            "🔹 Troca de Contexto: Tempo para alternar entre processos."
        )
        tk.Label(self.content, text=termos, bg="#f0f0f0", justify="left", anchor="w").pack()

        tk.Button(self.content, text="Fechar e Iniciar", command=self.destroy).pack(pady=20)
        self.grab_set()
        self.wait_window(self)


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulador de Escalonamento")
        self.scheduler = Escalonador()

        self.setup_ui()

            # Menu Ajuda
        menubar = tk.Menu(self.root)
        ajuda_menu = tk.Menu(menubar, tearoff=0)
        ajuda_menu.add_command(label="Informações do Programa", command=self.exibir_ajuda)
        menubar.add_cascade(label="Ajuda", menu=ajuda_menu)
        self.root.config(menu=menubar)


    def setup_ui(self):
        tk.Label(self.root, text="PID").grid(row=0, column=0)
        tk.Label(self.root, text="Chegada").grid(row=0, column=1)
        tk.Label(self.root, text="Execução").grid(row=0, column=2)

        self.pid = tk.Entry(self.root)
        self.chegada = tk.Entry(self.root)
        self.execucao = tk.Entry(self.root)
        self.pid.grid(row=1, column=0)
        self.chegada.grid(row=1, column=1)
        self.execucao.grid(row=1, column=2)

        tk.Button(self.root, text="Adicionar Processo", command=self.adicionar_processo).grid(row=1, column=3)

        self.policy = ttk.Combobox(self.root, values=["FCFS", "SJF", "Round Robin"])
        self.policy.grid(row=2, column=0)
        self.policy.set("FCFS")

        tk.Label(self.root, text="Quantum").grid(row=2, column=1)
        self.quantum = tk.Entry(self.root)
        self.quantum.grid(row=2, column=2)

        tk.Label(self.root, text="TTC").grid(row=2, column=3)
        self.ttc = tk.Entry(self.root)
        self.ttc.grid(row=2, column=4)

        tk.Button(self.root, text="Simular", command=self.simular).grid(row=2, column=5)

        self.output = tk.Text(self.root, height=15, width=80)
        self.output.grid(row=3, column=0, columnspan=6, pady=10)

    def adicionar_processo(self):
        try:
            pid = self.pid.get()
            chegada = int(self.chegada.get())
            execucao = int(self.execucao.get())
            self.scheduler.adicionar_processo(pid, chegada, execucao)
            self.output.insert(tk.END, f"Adicionado: PID={pid}, Chegada={chegada}, Execução={execucao}\n")
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
            elif politica == "SJF":
                res, media = self.scheduler.sjf_np(ttc)
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

    def exibir_ajuda(self):
        texto = (
            "Simulador de Escalonamento de Processos\n\n"
            "Este programa permite simular três algoritmos clássicos de escalonamento:\n"
            "🔹 FCFS (First Come, First Served)\n"
            "- Executa os processos na ordem de chegada.\n\n"
            "🔹 SJF (Shortest Job First - Não Preemptivo)\n"
            "- Executa o processo com menor tempo de execução disponível.\n\n"
            "🔹 Round Robin\n"
            "- Cada processo é executado por um quantum e volta para o final da fila, se necessário.\n\n"
            "Outros parâmetros:\n"
            "🔹 Quantum: tempo fixo para Round Robin.\n"
            "🔹 TTC (Tempo de Troca de Contexto): tempo extra entre trocas de processo.\n\n"
        )
        messagebox.showinfo("Ajuda - Sobre o Programa", texto)


if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # Esconde a janela principal temporariamente
    IntroDialog(root)
    root.deiconify()  # Mostra a janela principal depois de fechar a introdução
    app = App(root)
    root.mainloop()


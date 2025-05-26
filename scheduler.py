import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

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

    def sjf_preemptivo(self, ttc, pedir_novo_processo_callback=None):
        processos = sorted(self.processos, key=lambda x: x[1])
        tempo = 0
        prontos = []
        resultados = []
        restantes = {pid: burst for pid, _, burst in processos}
        chegada = {pid: arr for pid, arr, _ in processos}
        inicio_exec = {}
        completo = set()
        index = 0
        perguntou_novo_processo = False

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
            else:
                tempo += 1

            if not perguntou_novo_processo and tempo % 5 == 0 and pedir_novo_processo_callback:
                perguntou_novo_processo = True
                if messagebox.askyesno("Novo Processo", "Deseja adicionar um novo processo?"):
                    novo = pedir_novo_processo_callback()
                    if novo:
                        pid, chegada_n, execucao_n = novo
                        if not any(p[0] == pid for p in self.processos):
                            self.processos.append((pid, chegada_n, execucao_n))
                            processos.append((pid, chegada_n, execucao_n))
                            processos.sort(key=lambda x: x[1])
                            restantes[pid] = execucao_n
                            chegada[pid] = chegada_n

        media_espera = sum(p[3] for p in resultados) / len(resultados)
        return resultados, media_espera

    def round_robin(self, quantum, ttc):
        processos = sorted(self.processos, key=lambda x: x[1])
        tempo = 0
        fila = []
        index = 0
        restantes = {p[0]: p[2] for p in processos}
        chegada = {p[0]: p[1] for p in processos}
        primeiros = {}
        resultados = []
        completados = {}

        while len(completados) < len(processos):
            while index < len(processos) and processos[index][1] <= tempo:
                pid = processos[index][0]
                if pid not in fila and pid not in completados:
                    fila.append(pid)
                index += 1

            if not fila:
                tempo += 1
                continue

            pid = fila.pop(0)

            if pid not in primeiros:
                primeiros[pid] = tempo

            exec_time = min(quantum, restantes[pid])
            tempo += exec_time
            restantes[pid] -= exec_time

            while index < len(processos) and processos[index][1] <= tempo:
                novo_pid = processos[index][0]
                if novo_pid not in fila and novo_pid not in completados:
                    fila.append(novo_pid)
                index += 1

            if restantes[pid] > 0:
                fila.append(pid)
                tempo += ttc
            else:
                fim = tempo
                espera = fim - chegada[pid] - sum(p[2] for p in self.processos if p[0] == pid)
                resultados.append((pid, primeiros[pid], fim, espera))
                completados[pid] = True

        media_espera = sum(r[3] for r in resultados) / len(resultados)
        return resultados, media_espera


class App:
    def __init__(self, root):
        self.tema_escuro = False
        self.root = root
        self.root.title("Simulador de Escalonamento")
        self.scheduler = Escalonador()
        self.setup_ui()

        menubar = tk.Menu(self.root)
        ajuda_menu = tk.Menu(menubar, tearoff=0)
        ajuda_menu.add_command(label="Informações do Programa", command=self.exibir_ajuda)
        menubar.add_cascade(label="Ajuda", menu=ajuda_menu)

        tema_menu = tk.Menu(menubar, tearoff=0)
        tema_menu.add_command(label="Alternar Tema Escuro", command=self.alternar_tema)
        menubar.add_cascade(label="Tema", menu=tema_menu)

        acoes_menu = tk.Menu(menubar, tearoff=0)
        acoes_menu.add_command(label="Resetar Simulação", command=self.resetar_simulacao)
        menubar.add_cascade(label="Ações", menu=acoes_menu)

        self.root.config(menu=menubar)

    def resetar_simulacao(self):
        self.scheduler.processos.clear()
        self.limpar_adicionados()
        self.limpar_resultados()
        if hasattr(self, 'grafico_canvas'):
            self.grafico_canvas.get_tk_widget().destroy()

    def setup_ui(self):
        input_frame = tk.LabelFrame(self.root, text="Inserir Processos")
        input_frame.grid(row=0, column=0, padx=10, pady=5, sticky="ew", columnspan=6)

        self.pid = tk.Entry(input_frame)
        self.chegada = tk.Entry(input_frame)
        self.execucao = tk.Entry(input_frame)

        tk.Label(input_frame, text="PID").grid(row=0, column=0, padx=5, pady=2)
        tk.Label(input_frame, text="Chegada").grid(row=0, column=1, padx=5, pady=2)
        tk.Label(input_frame, text="Execução").grid(row=0, column=2, padx=5, pady=2)

        self.pid.grid(row=1, column=0, padx=5)
        self.chegada.grid(row=1, column=1, padx=5)
        self.execucao.grid(row=1, column=2, padx=5)

        tk.Button(input_frame, text="Adicionar Processo", command=self.adicionar_processo).grid(row=1, column=3, padx=5)

        tk.Label(input_frame, text="Algoritmo").grid(row=2, column=0, sticky="e")
        self.policy = ttk.Combobox(input_frame, values=["FCFS", "SJF Não Preemptivo", "SJF Preemptivo", "Round Robin"], width=20)
        self.policy.grid(row=2, column=1)
        self.policy.set("FCFS")

        tk.Label(input_frame, text="Quantum").grid(row=2, column=2, padx=5)
        self.quantum = tk.Entry(input_frame)
        self.quantum.grid(row=2, column=3, padx=5)

        tk.Label(input_frame, text="TTC").grid(row=2, column=4, padx=5)
        self.ttc = tk.Entry(input_frame)
        self.ttc.grid(row=2, column=5, padx=5)

        tk.Button(input_frame, text="Simular", command=self.simular).grid(row=2, column=6, padx=5)

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

        self.grafico_frame = tk.Frame(self.root)
        self.grafico_frame.grid(row=0, column=7, rowspan=3, padx=10, pady=5, sticky="nsew")

    def solicitar_novo_processo(self):
        novo_pid = simpledialog.askstring("Novo Processo", "PID do novo processo:")
        if not novo_pid:
            return None
        try:
            chegada = int(simpledialog.askstring("Novo Processo", "Tempo de chegada:"))
            execucao = int(simpledialog.askstring("Novo Processo", "Tempo de execução:"))
            return (novo_pid, chegada, execucao)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro nos dados: {e}")
            return None

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
                res, media = self.scheduler.sjf_preemptivo(ttc, self.solicitar_novo_processo)
            elif politica == "Round Robin":
                res, media = self.scheduler.round_robin(quantum, ttc)
            else:
                raise ValueError
            self.output.insert(tk.END, f"\nPolítica: {politica}\n")
            for pid, ini, fim, esp in res:
                self.output.insert(tk.END, f"{pid}: Início={ini}, Fim={fim}, Espera={esp}\n")
            self.output.insert(tk.END, f"Tempo médio de espera (segundos): {media:.2f}\n\n")
            self.exibir_grafico(res, politica)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro na simulação: {e}")

    def exibir_grafico(self, resultados, politica):
        fig, ax = plt.subplots(figsize=(6, 2.5))
        for pid, inicio, fim, _ in resultados:
            ax.barh(f"P{pid}", fim - inicio, left=inicio, edgecolor='black')
        ax.set_xlabel("Tempo")
        ax.set_ylabel("Processo")
        ax.set_title(f"Gráfico de Execução - {politica}")
        ax.grid(True)
        tempo_max = max(fim for _, _, fim, _ in resultados)
        ax.set_xticks(range(0, tempo_max + 1))
        if hasattr(self, 'grafico_canvas'):
            self.grafico_canvas.get_tk_widget().destroy()
        self.grafico_canvas = FigureCanvasTkAgg(fig, master=self.grafico_frame)
        self.grafico_canvas.draw()
        self.grafico_canvas.get_tk_widget().pack(pady=10)

    def limpar_adicionados(self):
        self.adicionados_output.delete('1.0', tk.END)

    def limpar_resultados(self):
        self.output.delete('1.0', tk.END)

    def exibir_ajuda(self):
        texto = (
            "Simulador de Escalonamento de Processos\n\n"
            "Este programa permite simular quatro algoritmos de escalonamento:\n"
            "-> FCFS\n"
            "-> SJF Não Preemptivo\n"
            "-> SJF Preemptivo (permite entrada dinâmica de novos processos a cada 5 unidades de tempo)\n"
            "-> Round Robin\n\n"
            "Campos:\n"
            "-> PID\n"
            "-> Chegada\n"
            "-> Tempo de Execução\n"
            "-> Quantum\n"
            "-> TTC\n\n"
            "Programa feito por Mateus Schneider e Miguel Vogel\n"
        )
        messagebox.showinfo("Ajuda - Sobre o Programa", texto)

    def alternar_tema(self):
        self.tema_escuro = not self.tema_escuro
        bg = "#2e2e2e" if self.tema_escuro else "#f0f0f0"
        fg = "#ffffff" if self.tema_escuro else "#000000"
        self.root.configure(bg=bg)
        for frame in [self.adicionados_frame, self.result_frame]:
            frame.configure(bg=bg, fg=fg)
            for child in frame.winfo_children():
                if isinstance(child, tk.Text):
                    child.configure(bg="#3c3f41" if self.tema_escuro else "#ffffff", fg=fg, insertbackground=fg)
                elif isinstance(child, tk.Button):
                    child.configure(bg=bg, fg=fg, activebackground="#444" if self.tema_escuro else "#ddd")
        for widget in self.root.winfo_children():
            if isinstance(widget, tk.LabelFrame):
                widget.configure(bg=bg, fg=fg)
                for sub in widget.winfo_children():
                    if isinstance(sub, (tk.Label, tk.Entry, ttk.Combobox, tk.Button)):
                        try:
                            sub.configure(bg=bg, fg=fg)
                        except:
                            pass
                    if isinstance(sub, tk.Text):
                        sub.configure(bg="#3c3f41" if self.tema_escuro else "#ffffff", fg=fg, insertbackground=fg)
        messagebox.showinfo("Tema", "Tema escuro ativado!" if self.tema_escuro else "Tema claro ativado!")

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()

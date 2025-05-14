import tkinter as tk
from tkinter import ttk, messagebox

class SchedulerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulador de Escalonador de Processos")
        self.root.geometry("750x600")
        self.root.resizable(False, False)

        self.process_list = []

        self.setup_menu()
        self.setup_input_frame()
        self.setup_process_entry_frame()
        self.setup_process_table()
        self.setup_control_buttons()
        self.setup_output_display()

    def setup_menu(self):
        menubar = tk.Menu(self.root)
        ajuda_menu = tk.Menu(menubar, tearoff=0)
        ajuda_menu.add_command(label="Políticas de Escalonamento", command=self.show_policies)
        ajuda_menu.add_command(label="Conceitos Gerais", command=self.show_concepts)
        menubar.add_cascade(label="Ajuda", menu=ajuda_menu)
        self.root.config(menu=menubar)

    def show_policies(self):
        texto = (
            "🔷 FCFS (First Come, First Serve)\n"
            "- Executa os processos por ordem de chegada.\n"
            "- Simples, mas pode causar longas esperas se o primeiro for muito demorado.\n\n"
            "🔷 SJF Não-preemptivo (Shortest Job First)\n"
            "- Escolhe o processo com menor tempo de execução entre os disponíveis.\n"
            "- Uma vez iniciado, vai até o fim sem interrupções.\n\n"
            "🔷 SJF Preemptivo (Shortest Remaining Time First)\n"
            "- Como o anterior, mas pode interromper o processo atual se um menor chegar.\n"
            "- Reduz bastante o tempo médio de espera.\n\n"
            "🔷 Round Robin\n"
            "- Cada processo executa por um intervalo fixo (quantum).\n"
            "- Ideal para multitarefa. Após o quantum, o processo volta ao fim da fila."
        )
        messagebox.showinfo("Ajuda - Políticas de Escalonamento", texto)

    def show_concepts(self):
        texto = (
            "🔹 PID: identificador único do processo.\n"
            "🔹 Tempo de Chegada: instante em que o processo entra na fila de pronto.\n"
            "🔹 Tempo de Execução: quanto tempo o processo precisa para rodar (burst).\n"
            "🔹 Quantum: fatia de tempo fixa para cada processo no Round Robin.\n"
            "🔹 TTC (Tempo de Troca de Contexto): tempo gasto pelo SO ao trocar de processo ativo.\n"
            "- Inclui salvar/recuperar estados dos processos."
        )
        messagebox.showinfo("Ajuda - Conceitos Gerais", texto)

    def setup_input_frame(self):
        frame = tk.LabelFrame(self.root, text="Parâmetros do Escalonador", padx=10, pady=10)
        frame.pack(fill="x", padx=10, pady=5)

        tk.Label(frame, text="Política:").grid(row=0, column=0, sticky="e")
        self.policy_var = tk.StringVar()
        self.policy_combo = ttk.Combobox(frame, textvariable=self.policy_var, state="readonly",
                                         values=["FCFS", "SJF Não-preemptivo", "SJF Preemptivo", "Round Robin"])
        self.policy_combo.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(frame, text="Quantum:").grid(row=0, column=2, sticky="e")
        self.quantum_entry = tk.Entry(frame, width=10)
        self.quantum_entry.grid(row=0, column=3, padx=5)

        tk.Label(frame, text="Tempo de Troca de Contexto:").grid(row=0, column=4, sticky="e")
        self.context_switch_entry = tk.Entry(frame, width=10)
        self.context_switch_entry.grid(row=0, column=5, padx=5)

    def setup_process_entry_frame(self):
        frame = tk.LabelFrame(self.root, text="Adicionar Processo", padx=10, pady=10)
        frame.pack(fill="x", padx=10, pady=5)

        self.pid_entry = self.create_labeled_entry(frame, "PID", 0)
        self.arrival_entry = self.create_labeled_entry(frame, "Chegada", 1)
        self.burst_entry = self.create_labeled_entry(frame, "Execução", 2)

        self.add_button = tk.Button(frame, text="Adicionar", command=self.add_process, width=15)
        self.add_button.grid(row=0, column=6, padx=10)

    def create_labeled_entry(self, parent, label, col):
        tk.Label(parent, text=label).grid(row=0, column=col * 2)
        entry = tk.Entry(parent, width=10)
        entry.grid(row=0, column=col * 2 + 1, padx=5)
        return entry

    def setup_process_table(self):
        frame = tk.LabelFrame(self.root, text="Processos Adicionados")
        frame.pack(fill="both", padx=10, pady=5, expand=True)

        columns = ("PID", "Chegada", "Execução")
        self.tree = ttk.Treeview(frame, columns=columns, show="headings", height=6)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, anchor="center")
        self.tree.pack(fill="both", expand=True)

    def setup_control_buttons(self):
        frame = tk.Frame(self.root)
        frame.pack(pady=5)

        self.simulate_button = tk.Button(frame, text="Simular Escalonamento", command=self.simulate, width=25)
        self.simulate_button.pack(side="left", padx=10)

        self.clear_button = tk.Button(frame, text="Limpar Tudo", command=self.clear_all, width=15)
        self.clear_button.pack(side="left", padx=10)

    def setup_output_display(self):
        frame = tk.LabelFrame(self.root, text="Resultados da Simulação")
        frame.pack(fill="both", padx=10, pady=5, expand=True)

        self.output_display = tk.Text(frame, height=8, state="disabled", wrap="word")
        self.output_display.pack(fill="both", expand=True)

    def add_process(self):
        pid = self.pid_entry.get()
        arrival = self.arrival_entry.get()
        burst = self.burst_entry.get()

        if not pid or not arrival or not burst:
            messagebox.showerror("Erro", "Preencha todos os campos do processo.")
            return

        try:
            arrival = int(arrival)
            burst = int(burst)
        except ValueError:
            messagebox.showerror("Erro", "Chegada e Execução devem ser inteiros.")
            return

        self.process_list.append((pid, arrival, burst))
        self.tree.insert("", "end", values=(pid, arrival, burst))

        self.pid_entry.delete(0, tk.END)
        self.arrival_entry.delete(0, tk.END)
        self.burst_entry.delete(0, tk.END)

    def simulate(self):
        policy = self.policy_var.get()
        quantum = self.quantum_entry.get()
        context_switch = self.context_switch_entry.get()

        if not policy:
            messagebox.showerror("Erro", "Escolha uma política de escalonamento.")
            return

        self.output_display.config(state="normal")
        self.output_display.delete("1.0", tk.END)
        self.output_display.insert(tk.END, f"Política Selecionada: {policy}\n")
        self.output_display.insert(tk.END, f"Quantum: {quantum} | Troca de Contexto: {context_switch}\n")
        self.output_display.insert(tk.END, f"Processos: {len(self.process_list)}\n")

        for i, proc in enumerate(self.process_list):
            self.output_display.insert(tk.END, f"{i+1}) PID: {proc[0]}, Chegada: {proc[1]}, Execução: {proc[2]}\n")

        self.output_display.insert(tk.END, "\n[Simulação ainda não implementada]\n")
        self.output_display.config(state="disabled")

    def clear_all(self):
        self.process_list.clear()
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.output_display.config(state="normal")
        self.output_display.delete("1.0", tk.END)
        self.output_display.config(state="disabled")


if __name__ == "__main__":
    root = tk.Tk()
    app = SchedulerApp(root)
    root.mainloop()

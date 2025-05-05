import tkinter as tk
from tkinter import ttk, messagebox

class SchedulerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulador de Escalonador de Processos")
        self.root.geometry("600x500")

        self.process_list = []

        # Frame de entrada
        self.frame_inputs = tk.LabelFrame(root, text="Parâmetros", padx=10, pady=10)
        self.frame_inputs.pack(padx=10, pady=10, fill="x")

        tk.Label(self.frame_inputs, text="Política:").grid(row=0, column=0, sticky="w")
        self.policy_var = tk.StringVar()
        self.policy_combo = ttk.Combobox(self.frame_inputs, textvariable=self.policy_var,
                                         values=["FCFS", "SJF Não-preemptivo", "SJF Preemptivo", "Round Robin"])
        self.policy_combo.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(self.frame_inputs, text="Quantum:").grid(row=0, column=2)
        self.quantum_entry = tk.Entry(self.frame_inputs)
        self.quantum_entry.grid(row=0, column=3, padx=5)

        tk.Label(self.frame_inputs, text="Tempo de Troca de Contexto:").grid(row=1, column=0, sticky="w")
        self.context_switch_entry = tk.Entry(self.frame_inputs)
        self.context_switch_entry.grid(row=1, column=1, padx=5, pady=5)

        # Frame de inserção de processos
        self.frame_process = tk.LabelFrame(root, text="Adicionar Processo", padx=10, pady=10)
        self.frame_process.pack(padx=10, pady=5, fill="x")

        self.pid_entry = self.create_labeled_entry(self.frame_process, "PID", 0)
        self.arrival_entry = self.create_labeled_entry(self.frame_process, "Tempo de Chegada", 1)
        self.burst_entry = self.create_labeled_entry(self.frame_process, "Tempo de Execução", 2)

        self.add_button = tk.Button(self.frame_process, text="Adicionar Processo", command=self.add_process)
        self.add_button.grid(row=0, column=6, padx=10)

        # Lista de processos
        self.process_display = tk.Text(root, height=10)
        self.process_display.pack(padx=10, pady=10, fill="both", expand=True)

        # Botão de simulação
        self.simulate_button = tk.Button(root, text="Simular Escalonamento", command=self.simulate)
        self.simulate_button.pack(pady=10)

    def create_labeled_entry(self, parent, label, col):
        tk.Label(parent, text=label).grid(row=0, column=col * 2, padx=5)
        entry = tk.Entry(parent)
        entry.grid(row=0, column=col * 2 + 1, padx=5)
        return entry

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
            messagebox.showerror("Erro", "Tempo de chegada e execução devem ser números inteiros.")
            return

        self.process_list.append((pid, arrival, burst))
        self.process_display.insert(tk.END, f"PID: {pid}, Chegada: {arrival}, Execução: {burst}\n")

        # Limpar os campos
        self.pid_entry.delete(0, tk.END)
        self.arrival_entry.delete(0, tk.END)
        self.burst_entry.delete(0, tk.END)

    def simulate(self):
        # Apenas exibe os dados no momento
        policy = self.policy_var.get()
        quantum = self.quantum_entry.get()
        context_switch = self.context_switch_entry.get()

        msg = f"Política: {policy}\nQuantum: {quantum}\nContext Switch: {context_switch}\nProcessos:\n"
        for proc in self.process_list:
            msg += f"{proc}\n"

        messagebox.showinfo("Simulação", msg)


if __name__ == "__main__":
    root = tk.Tk()
    app = SchedulerApp(root)
    root.mainloop()

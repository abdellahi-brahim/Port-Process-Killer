import tkinter as tk
from tkinter import ttk, messagebox
from ttkthemes import ThemedTk
import psutil
from elevate import elevate

def get_ports_and_processes():
    """Return a sorted list of (port, process) tuples."""
    result = []
    for conn in psutil.net_connections(kind='inet'):
        if conn.status == 'LISTEN' and conn.laddr:
            process = psutil.Process(conn.pid)
            result.append((conn.laddr.port, process.name(), conn.pid))
    return sorted(result, key=lambda x: x[0])


class App:
    def __init__(self, root):
        self.root = root
        self.filter_var = tk.StringVar()
        self.start_port_var = tk.StringVar()
        self.end_port_var = tk.StringVar()
        self.active_filters_var = tk.StringVar(value="Active Filters: None")
        self.sort_reverse = False
        
        self.build_ui()

    def build_ui(self):
        self._build_filters_frame()._build_active_filters_label()._build_treeview()._build_end_process_btn()
        self.refresh_list()
        return self

    def _build_filters_frame(self):
        self.filters_frame = ttk.Frame(self.root)
        self.filters_frame.pack(pady=20, padx=20, fill=tk.X)
        self._build_filter_inputs()._build_port_range_inputs()._build_apply_button()
        return self

    def _build_filter_inputs(self):
        filter_label = ttk.Label(self.filters_frame, text="Name:")
        filter_label.grid(row=0, column=0, padx=(0, 10))
        filter_entry = ttk.Entry(self.filters_frame, textvariable=self.filter_var)
        filter_entry.grid(row=0, column=1, sticky=tk.W + tk.E)
        return self

    def _build_port_range_inputs(self):
        port_range_label = ttk.Label(self.filters_frame, text="Port Range:")
        port_range_label.grid(row=0, column=2, padx=(20, 10))
        start_port_entry = ttk.Entry(self.filters_frame, textvariable=self.start_port_var, width=5)
        start_port_entry.grid(row=0, column=3)
        dash_label = ttk.Label(self.filters_frame, text="-")
        dash_label.grid(row=0, column=4, padx=(5, 5))
        end_port_entry = ttk.Entry(self.filters_frame, textvariable=self.end_port_var, width=5)
        end_port_entry.grid(row=0, column=5)
        return self

    def _build_apply_button(self):
        filter_button = ttk.Button(self.filters_frame, text="Apply Filters", command=self.apply_filters)
        filter_button.grid(row=0, column=6, padx=(20, 0))
        return self

    def _build_active_filters_label(self):
        self.active_filters_label = ttk.Label(self.root, textvariable=self.active_filters_var)
        self.active_filters_label.pack(pady=(0, 20))
        return self

    def _build_treeview(self):
        self.tree = ttk.Treeview(self.root, columns=("Port", "Process"), show="headings")
        self.tree.heading("Port", text="Port", command=lambda: self.sort_data("Port"))
        self.tree.heading("Process", text="Process", command=lambda: self.sort_data("Process"))
        self.tree.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)
        return self

    def _build_end_process_btn(self):
        end_process_btn = ttk.Button(self.root, text="End Process", command=self.end_process)
        end_process_btn.pack(pady=10)
        return self

    def apply_filters(self):
        self.refresh_list()
        return self

    def refresh_list(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        
        data = get_ports_and_processes()
        filter_val = self.filter_var.get()
        start_port = self.start_port_var.get()
        end_port = self.end_port_var.get()

        filters_applied = []
        if filter_val:
            filters_applied.append(f"Name/Port: {filter_val}")
            data = [item for item in data if filter_val.lower() in item[1].lower() or filter_val == str(item[0])]
        
        if start_port.isdigit() and end_port.isdigit():
            start_port, end_port = int(start_port), int(end_port)
            filters_applied.append(f"Port Range: {start_port}-{end_port}")
            data = [item for item in data if start_port <= item[0] <= end_port]

        if filters_applied:
            self.active_filters_var.set(f"Active Filters: {', '.join(filters_applied)}")
        else:
            self.active_filters_var.set("Active Filters: None")
        
        for port, process, pid in data:
            self.tree.insert("", "end", values=(port, process))

    def sort_data(self, column):
        data = [(self.tree.set(child, column), child) for child in self.tree.get_children()]
        data.sort(reverse=True if self.sort_reverse else False)

        for index, (_, child) in enumerate(data):
            self.tree.move(child, '', index)

        self.sort_reverse = not self.sort_reverse

    def end_process(self):
        selected_item = self.tree.selection()[0]
        port, process = self.tree.item(selected_item, "values")
        for conn in psutil.net_connections(kind='inet'):
            if conn.status == 'LISTEN' and conn.laddr and conn.laddr.port == int(port):
                psutil.Process(conn.pid).terminate()
                messagebox.showinfo("Info", f"Process {process} on port {port} has been terminated!")
                self.refresh_list()
                return

if __name__ == "__main__":
    elevate(show_console=False)
    app = ThemedTk(theme="arc")
    app.title("Port Process Killer")
    # app.iconbitmap('app_icon.ico')
    App(app)
    app.mainloop()


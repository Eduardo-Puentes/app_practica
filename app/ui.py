import tkinter as tk
from tkinter import ttk, messagebox

from app.services import (
    list_machines,
    create_machine,
    update_machine,
    delete_machine,
    get_machine,
)

STATUS_OPTIONS = ("operational", "maintenance", "offline")


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Manufacturing Control - Desktop CRUD (Subgrupo 2)")
        self.geometry("820x480")
        self.minsize(820, 480)

        self._build_layout()
        self.refresh()

    def _build_layout(self):
        container = ttk.Frame(self, padding=12)
        container.pack(fill="both", expand=True)

        # Left: table
        left = ttk.Frame(container)
        left.pack(side="left", fill="both", expand=True)

        cols = ("id", "name", "line", "status")
        self.tree = ttk.Treeview(left, columns=cols, show="headings", height=16)
        for c in cols:
            self.tree.heading(c, text=c.upper())
        self.tree.column("id", width=60, anchor="center")
        self.tree.column("name", width=260)
        self.tree.column("line", width=160)
        self.tree.column("status", width=140, anchor="center")
        self.tree.pack(fill="both", expand=True)

        self.tree.bind("<<TreeviewSelect>>", lambda e: self._load_selected())

        # Right: form
        right = ttk.Frame(container, padding=(12, 0, 0, 0))
        right.pack(side="right", fill="y")

        ttk.Label(right, text="Machine Form", font=("Arial", 14, "bold")).pack(anchor="w", pady=(0, 10))

        self.var_id = tk.StringVar(value="")
        self.var_name = tk.StringVar(value="")
        self.var_line = tk.StringVar(value="")
        self.var_status = tk.StringVar(value=STATUS_OPTIONS[0])

        ttk.Label(right, text="ID (auto)").pack(anchor="w")
        self.entry_id = ttk.Entry(right, textvariable=self.var_id, state="readonly", width=28)
        self.entry_id.pack(anchor="w", pady=(0, 10))

        ttk.Label(right, text="Name").pack(anchor="w")
        ttk.Entry(right, textvariable=self.var_name, width=28).pack(anchor="w", pady=(0, 10))

        ttk.Label(right, text="Line").pack(anchor="w")
        ttk.Entry(right, textvariable=self.var_line, width=28).pack(anchor="w", pady=(0, 10))

        ttk.Label(right, text="Status").pack(anchor="w")
        ttk.Combobox(
            right, textvariable=self.var_status, values=STATUS_OPTIONS, state="readonly", width=26
        ).pack(anchor="w", pady=(0, 16))

        btns = ttk.Frame(right)
        btns.pack(anchor="w", pady=(0, 8))

        ttk.Button(btns, text="Create", command=self.on_create).grid(row=0, column=0, padx=(0, 8))
        ttk.Button(btns, text="Update", command=self.on_update).grid(row=0, column=1, padx=(0, 8))
        ttk.Button(btns, text="Delete", command=self.on_delete).grid(row=0, column=2)

        ttk.Button(right, text="Refresh", command=self.refresh).pack(anchor="w", pady=(8, 0))
        ttk.Button(right, text="Clear Form", command=self.clear_form).pack(anchor="w", pady=(8, 0))

        ttk.Label(
            right,
            text="Tip: select a row to load it.\nCRUD uses SQLite (data.db).",
            foreground="#444",
        ).pack(anchor="w", pady=(18, 0))

    def refresh(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            rows = list_machines()
            for m in rows:
                self.tree.insert("", "end", values=(m.id, m.name, m.line, m.status))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def clear_form(self):
        self.var_id.set("")
        self.var_name.set("")
        self.var_line.set("")
        self.var_status.set(STATUS_OPTIONS[0])

    def _load_selected(self):
        sel = self.tree.selection()
        if not sel:
            return
        values = self.tree.item(sel[0], "values")
        if not values:
            return
        machine_id = int(values[0])
        m = get_machine(machine_id)
        if not m:
            return
        self.var_id.set(str(m.id))
        self.var_name.set(m.name)
        self.var_line.set(m.line)
        self.var_status.set(m.status)

    def on_create(self):
        try:
            new_id = create_machine(self.var_name.get(), self.var_line.get(), self.var_status.get())
            self.refresh()
            self.var_id.set(str(new_id))
            messagebox.showinfo("OK", f"Machine created (id={new_id}).")
        except Exception as e:
            messagebox.showerror("Validation/Error", str(e))

    def on_update(self):
        if not self.var_id.get():
            messagebox.showwarning("Missing", "Select a machine first.")
            return
        try:
            update_machine(int(self.var_id.get()), self.var_name.get(), self.var_line.get(), self.var_status.get())
            self.refresh()
            messagebox.showinfo("OK", "Machine updated.")
        except Exception as e:
            messagebox.showerror("Validation/Error", str(e))

    def on_delete(self):
        if not self.var_id.get():
            messagebox.showwarning("Missing", "Select a machine first.")
            return
        if not messagebox.askyesno("Confirm", "Delete this machine?"):
            return
        try:
            delete_machine(int(self.var_id.get()))
            self.refresh()
            self.clear_form()
            messagebox.showinfo("OK", "Machine deleted.")
        except Exception as e:
            messagebox.showerror("Error", str(e))
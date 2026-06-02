import tkinter as tk
from tkinter import ttk
import math


class PowerCalculator:

    @staticmethod
    def total_power(power_list):
        """
        Total Power = 10*log10(sum(10^(P/10)))
        """
        if not power_list:
            return 0

        linear_sum = sum(10 ** (p / 10) for p in power_list)
        return round(10 * math.log10(linear_sum), 2)


class USPowerVerifyApp:

    def __init__(self, root):

        self.root = root
        self.root.title("US Power Verify")
        self.root.geometry("1200x700")

        notebook = ttk.Notebook(root)
        notebook.pack(fill="both", expand=True)

        self.ofdma_tab = ttk.Frame(notebook)
        self.scqam_tab = ttk.Frame(notebook)
        self.multi_tab = ttk.Frame(notebook)

        notebook.add(self.ofdma_tab, text="OFDMA")
        notebook.add(self.scqam_tab, text="SC-QAM")
        notebook.add(self.multi_tab, text="MULTI")

        self.create_ofdma_tab()
        self.create_scqam_tab()
        self.create_multi_tab()

    # =====================================
    # OFDMA TAB
    # =====================================
    def create_ofdma_tab(self):

        columns = (
            "TxID",
            "Power(dBmV)",
            "Frequency(MHz)",
            "BW(MHz)"
        )

        self.ofdma_tree = ttk.Treeview(
            self.ofdma_tab,
            columns=columns,
            show="headings"
        )

        for col in columns:
            self.ofdma_tree.heading(col, text=col)
            self.ofdma_tree.column(col, width=150)

        self.ofdma_tree.pack(fill="both", expand=True)

        self.ofdma_tree.insert("", "end",
                               values=(0, 29.25, 21, 96))
        self.ofdma_tree.insert("", "end",
                               values=(1, 30.25, 45, 192))

        frame = ttk.Frame(self.ofdma_tab)
        frame.pack(fill="x")

        ttk.Button(
            frame,
            text="Calculate Total",
            command=self.calc_ofdma
        ).pack(side="left", padx=10)

        self.ofdma_result = ttk.Label(
            frame,
            text="Total OFDMA Power = "
        )
        self.ofdma_result.pack(side="left")

    def calc_ofdma(self):

        power_list = []

        for item in self.ofdma_tree.get_children():
            values = self.ofdma_tree.item(item)["values"]
            power_list.append(float(values[1]))

        total = PowerCalculator.total_power(power_list)

        self.ofdma_result.config(
            text=f"Total OFDMA Power = {total:.2f} dBmV"
        )

    # =====================================
    # SC-QAM TAB
    # =====================================
    def create_scqam_tab(self):

        columns = (
            "TxID",
            "Power(dBmV)",
            "Frequency(MHz)",
            "Symbol Rate"
        )

        self.scqam_tree = ttk.Treeview(
            self.scqam_tab,
            columns=columns,
            show="headings"
        )

        for col in columns:
            self.scqam_tree.heading(col, text=col)
            self.scqam_tree.column(col, width=150)

        self.scqam_tree.pack(fill="both", expand=True)

        sample = [
            (0, 32.25, 15, 5120000),
            (1, 32.25, 21, 5120000),
            (2, 32.25, 28, 5120000),
            (3, 29.75, 34, 5120000),
        ]

        for row in sample:
            self.scqam_tree.insert("", "end", values=row)

        frame = ttk.Frame(self.scqam_tab)
        frame.pack(fill="x")

        ttk.Button(
            frame,
            text="Calculate Total",
            command=self.calc_scqam
        ).pack(side="left", padx=10)

        self.scqam_result = ttk.Label(
            frame,
            text="Total SC-QAM Power = "
        )
        self.scqam_result.pack(side="left")

    def calc_scqam(self):

        power_list = []

        for item in self.scqam_tree.get_children():
            values = self.scqam_tree.item(item)["values"]
            power_list.append(float(values[1]))

        total = PowerCalculator.total_power(power_list)

        self.scqam_result.config(
            text=f"Total SC-QAM Power = {total:.2f} dBmV"
        )

    # =====================================
    # MULTI TAB
    # =====================================
    def create_multi_tab(self):

        columns = (
            "Type",
            "Channel Count",
            "Total Power"
        )

        self.multi_tree = ttk.Treeview(
            self.multi_tab,
            columns=columns,
            show="headings"
        )

        for col in columns:
            self.multi_tree.heading(col, text=col)
            self.multi_tree.column(col, width=250)

        self.multi_tree.pack(fill="both", expand=True)

        ttk.Button(
            self.multi_tab,
            text="Refresh Summary",
            command=self.refresh_multi
        ).pack(pady=10)

        self.multi_result = ttk.Label(
            self.multi_tab,
            text="Combined Output Power = "
        )

        self.multi_result.pack()

    def refresh_multi(self):

        for item in self.multi_tree.get_children():
            self.multi_tree.delete(item)

        ofdma_powers = []
        scqam_powers = []

        for item in self.ofdma_tree.get_children():
            ofdma_powers.append(
                float(self.ofdma_tree.item(item)["values"][1])
            )

        for item in self.scqam_tree.get_children():
            scqam_powers.append(
                float(self.scqam_tree.item(item)["values"][1])
            )

        ofdma_total = PowerCalculator.total_power(ofdma_powers)
        scqam_total = PowerCalculator.total_power(scqam_powers)

        self.multi_tree.insert(
            "",
            "end",
            values=("OFDMA",
                    len(ofdma_powers),
                    ofdma_total)
        )

        self.multi_tree.insert(
            "",
            "end",
            values=("SC-QAM",
                    len(scqam_powers),
                    scqam_total)
        )

        combined = PowerCalculator.total_power(
            [ofdma_total, scqam_total]
        )

        self.multi_result.config(
            text=f"Combined Output Power = {combined:.2f} dBmV"
        )


if __name__ == "__main__":

    root = tk.Tk()
    app = USPowerVerifyApp(root)

    root.mainloop()

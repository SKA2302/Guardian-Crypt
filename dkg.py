import tkinter as tk
from tkinter import simpledialog, messagebox
import sympy
import random

class DKGDisplay(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Distributed Key Generation - By SAKET KUMAR AMRIT")
        self.output_text = tk.Text(self, height=40, width=100, font=("Courier", 12))
        self.output_text.pack(padx=10, pady=10)
        self.create_widgets()

    def create_widgets(self):
        self.execute_button = tk.Button(self, text="Execute DKG", command=self.execute_dkg)
        self.execute_button.pack(pady=5)

    def execute_dkg(self):
        self.output_text.delete("1.0", tk.END)  # Clear previous output

        try:
            t = int(simpledialog.askstring("Threshold", "Enter the threshold (t):"))
            n = int(simpledialog.askstring("Total Shareholders", "Enter the total number of shareholders (n):"))
        except ValueError:
            messagebox.showerror("Error", "Please enter valid threshold and total shareholders values.")
            return

        if not 1 <= t <= n:
            messagebox.showerror("Error", "Threshold (t) must be in the range [1, n].")
            return

        participants = []
        for i in range(n):
            name = simpledialog.askstring("Participant Name", f"Enter the name of participant {i + 1}:")
            if not name:
                messagebox.showerror("Error", "Participant name cannot be empty.")
                return
            participants.append(name)

        self.dkg(t, participants)

    def dkg(self, t, participants):
        self.write_output(f"Participants: {participants}\n\n")

        # Each participant generates a polynomial of degree t - 1
        polynomials = {name: self.polynomial(t - 1) for name in participants}

        for name, poly in polynomials.items():
            self.write_output(f"{name}'s Polynomial: {poly.as_expr()}\n")

        # Each participant generates shares for all the others and themselves using their polynomial
        shares = {name: [(x, self.evaluate_polynomial(poly, x)) for x in range(1, len(participants) + 1)] for name, poly in polynomials.items()}

        for name, share in shares.items():
            self.write_output(f"\n{name}'s shares: {share}\n")

        # Initialization of sum_poly
        sum_poly = None

        while True:
            removed_participant = simpledialog.askstring("Remove Participant", "Enter the name of the participant to remove (or 'done' to finish):")
            if not removed_participant:
                return
            removed_participant = removed_participant.capitalize()  # Ensure first letter is capitalized
            if removed_participant.lower() == 'done':
                break
            elif removed_participant.lower() not in [name.lower() for name in participants]:
                messagebox.showerror("Error", f"No participant named {removed_participant}. Please try again.")
                continue

            participant_to_remove = [name for name in participants if name.lower() == removed_participant.lower()][0]
            participants.remove(participant_to_remove)
            del shares[participant_to_remove]

            # Each participant sums their shares to compute a point on the sum polynomial
            points = {name: (i + 1, sum(shares[participants[j - 1]][i][1] for j in range(len(participants)))) for i, name in enumerate(participants)}

            for name, point in points.items():
                self.write_output(f"\n{name}'s point on the sum polynomial: {point}\n")

            # The participants pool their points and use Lagrange interpolation to reconstruct the sum polynomial
            sum_points = list(points.values())
            sum_poly = self.lagrange_interpolation(sum_points)

            self.write_output(f"\nReconstructed sum polynomial after removing {removed_participant}: {sum_poly.as_expr()}\n")
            self.write_output(f"Intermediate DKG Secret key (known to no one): {sum_poly.coeffs()[0]}\n")

        # Compute sum_poly in case no participant is removed
        if sum_poly is None:
            points = {name: (i + 1, sum(shares[participants[j - 1]][i][1] for j in range(len(participants)))) for i, name in enumerate(participants)}
            sum_points = list(points.values())
            sum_poly = self.lagrange_interpolation(sum_points)
        self.write_output(f"\nReconstructed sum polynomial: {sum_poly.as_expr()}\n")
        self.write_output(f"Final DKG Secret key (known to no one): {sum_poly.coeffs()[-1]}\n\n")

    def polynomial(self, degree):
        secret = random.randint(1, 1000)
        coeffs = [random.randint(1, 1000) for _ in range(degree)]
        coeffs.append(secret)
        return sympy.Poly(coeffs, sympy.symbols('x'))

    def evaluate_polynomial(self, poly, x):
        return poly.subs(sympy.symbols('x'), x)

    def lagrange_interpolation(self, points):
        x_values, y_values = zip(*points)
        poly = sympy.Poly([0], sympy.symbols('x'))
        for j in range(len(y_values)):
            term = sympy.Poly([y_values[j]], sympy.symbols('x'))
            for m in range(len(x_values)):
                if m != j:
                    term *= sympy.Poly([1, -x_values[m]], sympy.symbols('x')) / (x_values[j] - x_values[m])
            poly += term
        return sympy.simplify(poly)

    def write_output(self, text):
        self.output_text.insert(tk.END, text)

if __name__ == "__main__":
    app = DKGDisplay()
    app.mainloop()

import customtkinter as ctk
from tkinter import messagebox, filedialog
import math
from datetime import datetime

# Set appearance mode and color theme
ctk.set_appearance_mode("system")
ctk.set_default_color_theme("blue")

# Predefined functions and their derivatives for Newton-Raphson
PREDEFINED_FUNCTIONS = {
    "x^2 - 2": (lambda x: x**2 - 2, lambda x: 2*x),
    "cos(x) - x": (lambda x: math.cos(x) - x, lambda x: -math.sin(x) - 1),
    "x^3 - 3x + 1": (lambda x: x**3 - 3*x + 1, lambda x: 3*x**2 - 3),
    # Add more as needed
}

APP_VERSION = "v1.0"

class SolutionTrail:
    """Manage the step-by-step trail with theme-aware colored text."""  

    def __init__(self, text_widget: ctk.CTkTextbox):
        self.text_widget = text_widget
        self.step_counter = 0
        self._setup_tags()
        self.clear()

    def _setup_tags(self):
        mode = ctk.get_appearance_mode().lower()  # 'light', 'dark', or 'system'

        if mode == "light":
            # Colors for WHITE background
            heading = "#1d4ed8"   # darker blue
            step = "#111827"      # near black
            success = "#15803d"   # darker green
            error = "#b91c1c"     # darker red
            info = "#92400e"      # dark yellow/brown
        else:
            # Colors for DARK background
            heading = "#3b82f6"   # bright blue
            step = "#e2e8f0"      # light gray
            success = "#22c55e"   # bright green
            error = "#ef4444"     # bright red
            info = "#facc15"      # bright yellow

        # Apply colors
        self.text_widget.tag_config("heading", foreground=heading)
        self.text_widget.tag_config("step", foreground=step)
        self.text_widget.tag_config("success", foreground=success)
        self.text_widget.tag_config("error", foreground=error)
        self.text_widget.tag_config("info", foreground=info)

    def refresh_theme(self):
        """Call this when theme changes"""
        self._setup_tags()

    def clear(self):
        self.step_counter = 0
        self.text_widget.configure(state="normal")
        self.text_widget.delete("1.0", "end")
        self.text_widget.configure(state="disabled")

    def add_heading(self, heading: str):
        # Append a colon so export parsers can reliably detect section headers
        self._write(f"\n{'='*60}\n", "heading")
        self._write(f"  {heading.upper()}:\n", "heading")
        self._write(f"{'='*60}\n", "heading")

    def add_step(self, content: str):
        self.step_counter += 1
        self._write(f"  {self.step_counter}. {content}\n", "step")

    def log(self, content: str, tag="info"):
        self._write(f"  {content}\n", tag)

    def log_success(self, content: str):
        self._write(f"  ✓ {content}\n", "success")

    def log_error(self, content: str):
        self._write(f"  ⚠ {content}\n", "error")

    def _write(self, msg: str, tag: str):
        self.text_widget.configure(state="normal")
        self.text_widget.insert("end", msg, tag)
        self.text_widget.see("end")
        self.text_widget.configure(state="disabled")

    def export(self, filepath: str):
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(self.text_widget.get("1.0", "end"))

class NewtonRaphsonApp:
    def __init__(self, root: ctk.CTk):
        self.root = root
        root.title(f"🧮 Newton-Raphson Root Finder {APP_VERSION} [TESTED & VERIFIED]")
        root.geometry("1400x750")
        root.minsize(1200, 700)

        self.create_widgets()

    def create_widgets(self):
        """Create all UI widgets using customtkinter."""
        
        # ============ MAIN CONTAINER ============
        main_container = ctk.CTkFrame(self.root)
        main_container.pack(fill="both", expand=True, padx=0, pady=0)
        
        # ============ HEADER ============
        header = ctk.CTkFrame(main_container, fg_color=("#2563eb", "#1e40af"), height=80)
        header.pack(fill="x", padx=0, pady=0)
        
        title_label = ctk.CTkLabel(
            header,
            text="🧮 Newton-Raphson Root Finder",
            font=("Arial", 22, "bold"),
            text_color="white"
        )
        title_label.pack(pady=20)
        
        # ============ CONTENT AREA ============
        content_frame = ctk.CTkFrame(main_container)
        content_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Configure grid layout: 2 columns (input panel and trail panel)
        content_frame.columnconfigure(0, weight=0)  # Input column
        content_frame.columnconfigure(1, weight=1)  # Trail column (expandable)
        content_frame.rowconfigure(0, weight=1)
        
        # ============ LEFT PANEL (INPUTS) ============
        left_panel = ctk.CTkFrame(content_frame, fg_color=("white", "#1e293b"))
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 15))
        left_panel.grid_propagate(False)  # Prevent auto-sizing
        left_panel.configure(width=400)  # Fixed width for consistent alignment
        
        # Input Card
        input_card = ctk.CTkFrame(left_panel, fg_color=("white", "#1e293b"), corner_radius=10)
        input_card.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Configure grid layout for input card
        input_card.columnconfigure(0, weight=0)  # Labels column
        input_card.columnconfigure(1, weight=1)  # Inputs column
        input_card.rowconfigure((0,1,2,3,4,5,6,7,8,9), weight=0)  # Rows for each input
        
        # Input Title
        input_title = ctk.CTkLabel(
            input_card,
            text="Solver Configuration",
            font=("Arial", 14, "bold"),
            text_color=("#1e293b", "#e2e8f0")
        )
        input_title.grid(row=0, column=0, columnspan=2, pady=(15, 10), padx=15, sticky="w")
        
        # Row counter
        row = 1
        
        # Method Selection
        method_label = ctk.CTkLabel(
            input_card,
            text="Method:",
            font=("Arial", 11, "bold"),
            text_color=("#1e293b", "#e2e8f0")
        )
        method_label.grid(row=row, column=0, padx=(15, 10), pady=5, sticky="w")
        
        self.method_var = ctk.StringVar(value="Newton-Raphson")
        self.method_cb = ctk.CTkComboBox(
            input_card,
            values=["Newton-Raphson", "Secant"],
            variable=self.method_var,
            state="readonly",
            font=("Arial", 10),
            command=self._on_method_change
        )
        self.method_cb.grid(row=row, column=1, padx=(0, 15), pady=5, sticky="ew")
        # Add tooltip
        self._create_tooltip(self.method_cb, "Choose the root-finding method to use")
        row += 1
        
        # Function Selection
        func_label = ctk.CTkLabel(
            input_card,
            text="Function:",
            font=("Arial", 11, "bold"),
            text_color=("#1e293b", "#e2e8f0")
        )
        func_label.grid(row=row, column=0, padx=(15, 10), pady=5, sticky="w")
        
        self.function_var = ctk.StringVar(value=list(PREDEFINED_FUNCTIONS.keys())[0])
        self.function_cb = ctk.CTkComboBox(
            input_card,
            values=list(PREDEFINED_FUNCTIONS.keys()),
            variable=self.function_var,
            state="readonly",
            font=("Arial", 10)
        )
        self.function_cb.grid(row=row, column=1, padx=(0, 15), pady=5, sticky="ew")
        self._create_tooltip(self.function_cb, "Select the mathematical function to find roots for")
        row += 1
        
        # Initial Guess
        guess_label = ctk.CTkLabel(
            input_card,
            text="Initial Guess:",
            font=("Arial", 11, "bold"),
            text_color=("#1e293b", "#e2e8f0")
        )
        guess_label.grid(row=row, column=0, padx=(15, 10), pady=5, sticky="w")
        
        self.guess_var = ctk.StringVar(value="1.5")
        self.guess_entry = ctk.CTkEntry(
            input_card,
            textvariable=self.guess_var,
            font=("Arial", 10),
            placeholder_text="e.g., 1.5"
        )
        self.guess_entry.grid(row=row, column=1, padx=(0, 15), pady=5, sticky="ew")
        self._create_tooltip(self.guess_entry, "Starting point for the root-finding algorithm")
        row += 1
        
        # Second Guess (Secant method) - initially hidden
        self.guess2_label = ctk.CTkLabel(
            input_card,
            text="Second Guess:",
            font=("Arial", 11, "bold"),
            text_color=("#1e293b", "#e2e8f0")
        )
        
        self.guess2_var = ctk.StringVar(value="2.0")
        self.guess2_entry = ctk.CTkEntry(
            input_card,
            textvariable=self.guess2_var,
            font=("Arial", 10),
            placeholder_text="e.g., 2.0"
        )
        self._create_tooltip(self.guess2_entry, "Second starting point required for Secant method")
        
        # Tolerance
        tol_label = ctk.CTkLabel(
            input_card,
            text="Tolerance:",
            font=("Arial", 11, "bold"),
            text_color=("#1e293b", "#e2e8f0")
        )
        tol_label.grid(row=row, column=0, padx=(15, 10), pady=5, sticky="w")
        
        self.tol_var = ctk.StringVar(value="1e-6")
        self.tol_entry = ctk.CTkEntry(
            input_card,
            textvariable=self.tol_var,
            font=("Arial", 10),
            placeholder_text="e.g., 1e-6"
        )
        self.tol_entry.grid(row=row, column=1, padx=(0, 15), pady=5, sticky="ew")
        self._create_tooltip(self.tol_entry, "Convergence tolerance (smaller = more precise)")
        row += 1
        
        # Max Iterations
        maxiter_label = ctk.CTkLabel(
            input_card,
            text="Max Iterations:",
            font=("Arial", 11, "bold"),
            text_color=("#1e293b", "#e2e8f0")
        )
        maxiter_label.grid(row=row, column=0, padx=(15, 10), pady=5, sticky="w")
        
        self.maxiter_var = ctk.StringVar(value="50")
        self.maxiter_entry = ctk.CTkEntry(
            input_card,
            textvariable=self.maxiter_var,
            font=("Arial", 10),
            placeholder_text="e.g., 50"
        )
        self.maxiter_entry.grid(row=row, column=1, padx=(0, 15), pady=5, sticky="ew")
        self._create_tooltip(self.maxiter_entry, "Maximum number of iterations before stopping")
        row += 1
        
        # ============ BUTTONS ============
        button_frame = ctk.CTkFrame(input_card, fg_color=("white", "#1e293b"))
        button_frame.grid(row=row, column=0, columnspan=2, padx=15, pady=(20, 15), sticky="ew")
        
        # Configure button frame grid
        button_frame.columnconfigure((0,1,2), weight=1)
        button_frame.rowconfigure(0, weight=0)
        
        compute_btn = ctk.CTkButton(
            button_frame,
            text="🔍 Compute\n(Ctrl+Enter)",
            command=self.compute,
            font=("Arial", 11, "bold"),
            height=50,
            corner_radius=8,
            border_width=2,
            border_color=("#1d4ed8", "#3b82f6")
        )
        compute_btn.grid(row=0, column=0, padx=(0, 5), sticky="ew")
        self._create_tooltip(compute_btn, "Start the root-finding computation (Ctrl+Enter)")
        
        clear_btn = ctk.CTkButton(
            button_frame,
            text="🧹 Clear\n(Ctrl+L)",
            command=self.clear_all,
            font=("Arial", 11, "bold"),
            height=50,
            corner_radius=8,
            fg_color=("#888888", "#555555"),
            hover_color=("#666666", "#333333")
        )
        clear_btn.grid(row=0, column=1, padx=5, sticky="ew")
        self._create_tooltip(clear_btn, "Clear all inputs and results (Ctrl+L)")
        
        export_btn = ctk.CTkButton(
            button_frame,
            text="💾 Export\n(Ctrl+E)",
            command=self.export_trail,
            font=("Arial", 11, "bold"),
            height=50,
            corner_radius=8,
            fg_color=("#16a34a", "#15803d"),
            hover_color=("#22c55e", "#16a34a")
        )
        export_btn.grid(row=0, column=2, padx=(5, 0), sticky="ew")
        self._create_tooltip(export_btn, "Export solution trail to file (Ctrl+E)")
        
        # Add keyboard shortcuts
        self.root.bind('<Control-Return>', lambda e: self.compute())
        self.root.bind('<Control-l>', lambda e: self.clear_all())
        self.root.bind('<Control-e>', lambda e: self.export_trail())
        
        # ============ STATUS BAR ============
        status_frame = ctk.CTkFrame(left_panel, fg_color=("#fff3cd", "#1c1917"), corner_radius=8)
        status_frame.pack(fill="x", padx=10, pady=(5, 10))
        
        # Status label
        self.status_var = ctk.StringVar(value="Ready")
        self.status_label = ctk.CTkLabel(
            status_frame,
            textvariable=self.status_var,
            font=("Arial", 10, "bold"),
            text_color=("#856404", "#fbbf24")
        )
        self.status_label.pack(pady=8, padx=15)
        
        # Progress bar (initially hidden)
        self.progress_bar = ctk.CTkProgressBar(
            status_frame,
            width=300,
            height=8,
            corner_radius=4
        )
        # Don't pack initially - will be shown during computation
        
        # ============ RESULT CARD ============
        result_card = ctk.CTkFrame(left_panel, fg_color=("#e0f2fe", "#0c4a6e"), corner_radius=10)
        result_card.pack(fill="x", padx=10, pady=(0, 10))
        
        # Configure grid layout for result card
        result_card.columnconfigure(0, weight=1)
        result_card.rowconfigure((0,1,2), weight=0)
        
        result_label = ctk.CTkLabel(
            result_card,
            text="Final Root:",
            font=("Arial", 12, "bold"),
            text_color=("#0c4a6e", "#e0f2fe")
        )
        result_label.grid(row=0, column=0, pady=(15, 5), padx=15, sticky="w")
        
        self.final_var = ctk.StringVar(value="")
        self.final_label = ctk.CTkLabel(
            result_card,
            textvariable=self.final_var,
            font=("Arial", 18, "bold"),
            text_color=("#16a34a", "#22c55e")
        )
        self.final_label.grid(row=1, column=0, pady=(0, 5), padx=15, sticky="w")
        
        # Computation time display
        self.time_var = ctk.StringVar(value="")
        self.time_label = ctk.CTkLabel(
            result_card,
            textvariable=self.time_var,
            font=("Arial", 10),
            text_color=("#64748b", "#94a3b8")
        )
        self.time_label.grid(row=2, column=0, pady=(0, 15), padx=15, sticky="w")
        
        # ============ RIGHT PANEL (TRAIL) ============
        right_panel = ctk.CTkFrame(content_frame, fg_color=("white", "#1e293b"))
        right_panel.grid(row=0, column=1, sticky="nsew")
        
        # Configure right panel grid
        right_panel.rowconfigure(1, weight=1)
        right_panel.columnconfigure(0, weight=1)
        
        trail_title = ctk.CTkLabel(
            right_panel,
            text="📋 Solution Trail",
            font=("Arial", 18, "bold"),
            text_color=("#1e293b", "#e2e8f0")
        )
        trail_title.grid(row=0, column=0, pady=(15, 10), padx=15, sticky="w")
        
        # Solution Trail Text Box
        self.trail_text = ctk.CTkTextbox(
            right_panel,
            font=("Consolas", 11),
            corner_radius=8,
            wrap="word"
        )
        self.trail_text.grid(row=1, column=0, padx=15, pady=(0, 15), sticky="nsew")
        
        # Initialize trail
        self.trail = SolutionTrail(self.trail_text)
        
        # ============ FOOTER ============
        footer = ctk.CTkFrame(self.root, fg_color=("#f0f4f8", "#0f172a"))
        footer.pack(fill="x", padx=0, pady=0)
        
        # Configure footer grid
        footer.columnconfigure((0,1,2,4), weight=0)
        footer.columnconfigure(3, weight=1)  # Spacer
        footer.rowconfigure(0, weight=0)
        
        appearance_label = ctk.CTkLabel(
            footer,
            text="Theme:",
            font=("Arial", 10),
            text_color=("#1e293b", "#e2e8f0")
        )
        appearance_label.grid(row=0, column=0, padx=(15, 5), pady=12)
        
        appearance_menu = ctk.CTkOptionMenu(
            footer,
            values=["System", "Light", "Dark"],
            command=self.change_appearance_mode,
            font=("Arial", 10),
            width=80
        )
        appearance_menu.set("System")
        appearance_menu.grid(row=0, column=1, padx=5, pady=12)

        version_label = ctk.CTkLabel(
            footer,
            text=f"Version: {APP_VERSION}",
            font=("Arial", 9),
            text_color=("#475569", "#d1d5db")
        )
        version_label.grid(row=0, column=2, padx=(15, 5), pady=12)

        warning_info = ctk.CTkLabel(
            footer,
            text="Legend: ✓ Success | ⚠ Warning/Error | → Steps | ⏱️ Time",
            font=("Arial", 9),
            text_color=("#555555", "#999999")
        )
        warning_info.grid(row=0, column=4, padx=15, pady=12)

        # Spacer
        spacer = ctk.CTkFrame(footer, fg_color=("#f0f4f8", "#0f172a"))
        spacer.grid(row=0, column=3, sticky="ew")

        about_btn = ctk.CTkButton(
            footer,
            text="About",
            command=self.show_about,
            font=("Arial", 10),
            width=60
        )
        about_btn.grid(row=0, column=5, padx=(0, 15), pady=12)
        
        
        # Initially hide second guess
        self._on_method_change()

    def _create_tooltip(self, widget, text):
        """Create a tooltip for a widget."""
        def enter(event):
            self.tooltip = ctk.CTkToplevel(widget)
            self.tooltip.wm_overrideredirect(True)
            self.tooltip.wm_geometry("+0+0")
            
            label = ctk.CTkLabel(
                self.tooltip,
                text=text,
                font=("Arial", 9),
                corner_radius=6,
                fg_color=("#333333", "#cccccc"),
                text_color=("white", "black")
            )
            label.pack(padx=8, pady=4)
            
            # Position tooltip near widget
            x = widget.winfo_rootx() + 20
            y = widget.winfo_rooty() + widget.winfo_height() + 5
            self.tooltip.wm_geometry(f"+{x}+{y}")
            
        def leave(event):
            if hasattr(self, 'tooltip'):
                self.tooltip.destroy()
                
        widget.bind('<Enter>', enter)
        widget.bind('<Leave>', leave)

    def _on_method_change(self, value=None):
        if self.method_var.get() == "Secant":
            self.guess2_label.grid(row=4, column=0, padx=(15, 10), pady=5, sticky="w")
            self.guess2_entry.grid(row=4, column=1, padx=(0, 15), pady=5, sticky="ew")
        else:
            self.guess2_label.grid_forget()
            self.guess2_entry.grid_forget()

    def change_appearance_mode(self, mode: str):
        ctk.set_appearance_mode(mode.lower())
        self.trail.refresh_theme()  # 🔥 refresh colors

    def show_about(self):
        """Show about dialog."""
        messagebox.showinfo(
            "About",
            f"🧮 Newton-Raphson Root Finder {APP_VERSION}\n\n"
            "Purpose:\n"
            "This system helps users explore numerical root-finding techniques and generate evidence-quality reports.\n\n"
            "Main Features:\n"
            "• Newton-Raphson and Secant solution methods\n"
            "• Predefined function selection with derivative support\n"
            "• Step-by-step solution trail with edge-case analysis\n"
            "• TXT and HTML export of computation reports\n"
            "• Light/Dark theme support and version display\n\n"
            "Usage Notes:\n"
            "• Use the compute button or Ctrl+Enter to run a calculation.\n"
            "• Use the export button or Ctrl+E to save your trail.\n"
            "• Review the generated report for required documentation sections.\n\n"
            "Documentation:\n"
            "• See week13_testing_report.md for full tests, bug summaries, and reflections.\n"
            "• See README.md for setup, usage, features, and limitations.\n\n"
            "Developed by:\n"
            "• Charles Russel San Juan\n"
            "• Christina Gomba\n"
            "• John Michael Tulalian\n\n"
            f"Version: {APP_VERSION}"
        )

    def _finish_computation(self):
        """Hide progress bar and reset status after computation."""
        self.progress_bar.pack_forget()
        self.status_var.set("Ready")

    def clear_all(self):
        """Clear all inputs and results."""
        self.guess_var.set("1.5")
        self.guess2_var.set("2.0")
        self.tol_var.set("1e-6")
        self.maxiter_var.set("50")
        self.final_var.set("")
        self.time_var.set("")
        self.status_var.set("Ready")
        self.progress_bar.pack_forget()
        self.trail.clear()

    def validate_inputs(self):
        """Validate user inputs; return tuple(valid, errors_list, ...)"""
        errors = []
        method = self.method_var.get()
        if method not in ("Newton-Raphson", "Secant"):
            errors.append("Please select a valid method.")

        # function
        func = self.function_var.get()
        if func not in PREDEFINED_FUNCTIONS:
            errors.append("Please select a valid predefined function.")

        # initial guess
        try:
            x0 = float(self.guess_var.get())
        except ValueError:
            errors.append("Initial guess must be a number.")
            x0 = None

        x1 = None
        if method == "Secant":
            try:
                x1 = float(self.guess2_var.get())
            except ValueError:
                errors.append("Second guess must be a number for Secant method.")

        # tolerance
        try:
            tol = float(self.tol_var.get())
            if tol <= 0:
                errors.append("Tolerance must be positive.")
        except ValueError:
            errors.append("Tolerance must be a number.")
            tol = None

        # max iterations
        try:
            maxiter = int(self.maxiter_var.get())
            if maxiter <= 0:
                errors.append("Max iterations must be a positive integer.")
        except ValueError:
            errors.append("Max iterations must be an integer.")
            maxiter = None

        valid = len(errors) == 0
        return valid, errors, method, func, x0, x1, tol, maxiter

    def detect_edge_cases(self, method, func_name, x0, x1, tol, maxiter, f, df):
        """
        Detect potential edge cases and return list of warnings.
        
        EDGE CASES DETECTED:
        1. Initial guess outside reasonable range (-1e10 to 1e10)
        2. Extreme tolerance values (very large or very small)
        3. Max iterations too low for convergence
        4. Equal guesses in Secant method
        5. Function values near discontinuity or singularity
        6. Derivative very close to zero at initial guess (Newton-Raphson)
        7. Extremely large function values (overflow risk)
        8. Oscillating convergence pattern risk
        9. Very small step changes expected
        """
        warnings = []
        
        # EC1: Initial guess outside reasonable range
        if abs(x0) > 1e10:
            warnings.append(
                f"⚠ EC1: Initial guess ({x0}) is extremely large. "
                f"This may cause overflow or divergence."
            )
        
        # EC2: Extreme tolerance values
        if tol > 0.1:
            warnings.append(
                f"⚠ EC2: Tolerance ({tol}) is very large. "
                f"Solution may be inaccurate. Consider using 1e-6 or smaller."
            )
        if tol < 1e-15:
            warnings.append(
                f"⚠ EC3: Tolerance ({tol}) is extremely small. "
                f"May not be achievable due to floating-point precision limits."
            )
        
        # EC4: Max iterations too low
        if maxiter < 5:
            warnings.append(
                f"⚠ EC4: Max iterations ({maxiter}) is very low. "
                f"May not converge. Consider using at least 10."
            )
        if maxiter > 10000:
            warnings.append(
                f"⚠ EC5: Max iterations ({maxiter}) is very high. "
                f"Computation may be slow."
            )
        
        # EC6: Secant method - equal guesses
        if method == "Secant" and x1 is not None:
            if abs(x1 - x0) < 1e-10:
                warnings.append(
                    f"⚠ EC6: Secant method: initial guesses are too close ({abs(x1 - x0):.2e}). "
                    f"Denominator may become zero. Use more different guesses."
                )
        
        # EC7: Check function value at initial guess
        try:
            fx0 = f(x0)
            if math.isnan(fx0) or math.isinf(fx0):
                warnings.append(
                    f"⚠ EC7: Function value at initial guess is {fx0}. "
                    f"Initial guess may be at a discontinuity or singularity."
                )
            elif abs(fx0) > 1e15:
                warnings.append(
                    f"⚠ EC8: Function value at initial guess is extremely large ({fx0:.3e}). "
                    f"Risk of overflow during computation."
                )
        except (ValueError, ZeroDivisionError):
            warnings.append(
                f"⚠ EC9: Cannot evaluate function at initial guess ({x0}). "
                f"This point may be a discontinuity."
            )
        
        # EC8: Newton-Raphson - derivative at initial guess
        if method == "Newton-Raphson":
            try:
                dfx0 = df(x0)
                if math.isnan(dfx0) or math.isinf(dfx0):
                    warnings.append(
                        f"⚠ EC10: Derivative at initial guess is {dfx0}. "
                        f"Initial guess may be at a critical point."
                    )
                elif abs(dfx0) < 1e-10:
                    warnings.append(
                        f"⚠ EC11: Derivative at initial guess is very close to zero ({dfx0:.3e}). "
                        f"Newton-Raphson may diverge or converge very slowly."
                    )
            except (ValueError, ZeroDivisionError):
                warnings.append(
                    f"⚠ EC12: Cannot evaluate derivative at initial guess ({x0}). "
                    f"Initial guess may cause computational errors."
                )
        
        return warnings

    def compute(self):
        """Perform the root-finding computation with clear stopping rules."""
        # Clear previous results
        self.trail.clear()
        self.final_var.set("")
        self.time_var.set("")
        
        # Show progress bar and update status
        self.status_var.set("🔄 Computing...")
        self.progress_bar.pack(pady=(0, 8), padx=15)
        self.progress_bar.set(0)
        self.root.update()

        valid, errors, method, func_name, x0, x1, tol, maxiter = self.validate_inputs()

        # GIVEN
        self.trail.add_heading("GIVEN")
        self.trail.log(f"Method: {method}")
        self.trail.log(f"Function: {func_name}")
        self.trail.log(f"Initial guess: {self.guess_var.get()}")
        if method == "Secant":
            self.trail.log(f"Second guess: {self.guess2_var.get()}")
        self.trail.log(f"Tolerance: {tol}")
        self.trail.log(f"Max iterations: {maxiter}")

        # VALIDATION
        self.trail.add_heading("VALIDATION")
        if not valid:
            for err in errors:
                self.trail.add_step("ERROR: " + err)
            messagebox.showerror("Input Error", "\n".join(errors))
            self._finish_computation()
            return
        else:
            self.trail.add_step("All inputs valid.")

        f, df = PREDEFINED_FUNCTIONS[func_name]

        # 🔥 NEW: EDGE CASE DETECTION
        self.trail.add_heading("EDGE CASE ANALYSIS")
        edge_warnings = self.detect_edge_cases(method, func_name, x0, x1, tol, maxiter, f, df)
        
        if edge_warnings:
            self.trail.log_error("⚠️  WARNINGS DETECTED:")
            for warning in edge_warnings:
                self.trail.log(warning, "error")
        else:
            self.trail.log_success("✓ No edge cases detected. Configuration looks safe.")

        # METHOD
        self.trail.add_heading("METHOD")
        self.trail.log(f"{method}")

        # 🔥 NEW: STOPPING RULES (VISIBLE)
        self.trail.add_heading("STOPPING RULES")
        self.trail.log(f"1. Stop if |x_new - x| < tolerance ({tol})")
        self.trail.log(f"2. Stop if iterations exceed max ({maxiter})")
        if method == "Newton-Raphson":
            self.trail.log("3. Stop if derivative = 0")
        else:
            self.trail.log("3. Stop if denominator = 0")

        # STEPS
        self.trail.add_heading("STEPS")

        start_time = datetime.now()
        reason = ""
        converged = False

        if method == "Newton-Raphson":
            x = x0
            for i in range(1, maxiter + 1):
                try:
                    fx = f(x)
                    dfx = df(x)
                    
                    # Check for NaN or Inf
                    if math.isnan(fx) or math.isinf(fx):
                        reason = f"STOP: f(x) = {fx} at iteration {i} (computational error)"
                        self.trail.add_step(reason)
                        self.trail.log_error("⚠ WARNING: Function value became NaN/Inf. Halting computation.")
                        break
                    
                    if math.isnan(dfx) or math.isinf(dfx):
                        reason = f"STOP: Derivative = {dfx} at iteration {i} (computational error)"
                        self.trail.add_step(reason)
                        self.trail.log_error("⚠ WARNING: Derivative became NaN/Inf. Halting computation.")
                        break

                    if dfx == 0:
                        reason = f"STOP: Derivative became zero at iteration {i}"
                        self.trail.add_step(reason)
                        self.trail.log_error("⚠ WARNING: Derivative is zero. Newton-Raphson cannot continue.")
                        break

                    x_new = x - fx / dfx
                    err = abs(x_new - x)

                    self.trail.add_step(
                        f"i={i}, x={x:.10f}, f(x)={fx:.3e}, x_next={x_new:.10f}, err={err:.3e}"
                    )

                    # Update progress
                    progress = min(i / maxiter, 0.95)  # Don't reach 100% until done
                    self.progress_bar.set(progress)
                    self.status_var.set(f"🔄 Computing... ({i}/{maxiter})")
                    self.root.update()

                    if err < tol:
                        reason = f"SUCCESS: Converged (error {err:.3e} < {tol})"
                        converged = True
                        x = x_new
                        break

                    x = x_new
                    
                except Exception as e:
                    reason = f"STOP: Runtime error at iteration {i}: {str(e)}"
                    self.trail.add_step(reason)
                    self.trail.log_error(f"⚠ WARNING: {str(e)}")
                    break

            if not converged and reason == "":
                reason = f"STOP: Reached max iterations ({maxiter})"

        else:  # Secant
            x_prev = x0
            x = x1

            for i in range(1, maxiter + 1):
                try:
                    f_prev = f(x_prev)
                    fx = f(x)
                    
                    # Check for NaN or Inf
                    if math.isnan(fx) or math.isinf(fx) or math.isnan(f_prev) or math.isinf(f_prev):
                        reason = f"STOP: Function value is NaN/Inf at iteration {i}"
                        self.trail.add_step(reason)
                        self.trail.log_error("⚠ WARNING: Function value became NaN/Inf. Halting computation.")
                        break

                    denom = fx - f_prev
                    if denom == 0:
                        reason = f"STOP: Zero denominator at iteration {i}"
                        self.trail.add_step(reason)
                        self.trail.log_error("⚠ WARNING: f(x) - f(x_prev) = 0. Secant method cannot continue.")
                        break
                    
                    if abs(denom) < 1e-15:
                        self.trail.log("ℹ INFO: Denominator is very small (sec. EC edge case risk)")

                    x_new = x - fx * (x - x_prev) / denom
                    err = abs(x_new - x)

                    self.trail.add_step(
                        f"i={i}, x_prev={x_prev:.10f}, x={x:.10f}, x_next={x_new:.10f}, err={err:.3e}"
                    )

                    # Update progress
                    progress = min(i / maxiter, 0.95)
                    self.progress_bar.set(progress)
                    self.status_var.set(f"🔄 Computing... ({i}/{maxiter})")
                    self.root.update()

                    if err < tol:
                        reason = f"SUCCESS: Converged (error {err:.3e} < {tol})"
                        converged = True
                        x = x_new
                        break

                    x_prev, x = x, x_new
                    
                except Exception as e:
                    reason = f"STOP: Runtime error at iteration {i}: {str(e)}"
                    self.trail.add_step(reason)
                    self.trail.log_error(f"⚠ WARNING: {str(e)}")
                    break

            if not converged and reason == "":
                reason = f"STOP: Reached max iterations ({maxiter})"

        end_time = datetime.now()
        computation_time = end_time - start_time

        # Update final results
        self.final_var.set(f"{x:.12g}")
        self.time_var.set(f"⏱️ {computation_time.total_seconds():.4f}s")

        # Complete progress bar
        self.progress_bar.set(1.0)
        self.status_var.set("✅ Complete")
        self.root.update()

        # FINAL ANSWER
        self.trail.add_heading("FINAL ANSWER")
        self.trail.log(f"Method Used: {method}")
        self.trail.log(f"x ≈ {x:.12g}")
        
        # 🔥 NEW: CLEAR STOPPING REASON
        self.trail.add_heading("STOPPING CONDITION")
        self.trail.log(reason)

        # SUMMARY
        self.trail.add_heading("SUMMARY")
        self.trail.log(f"Method: {method}")
        self.trail.log(f"Iterations: {i}")
        self.trail.log(f"Time: {computation_time.total_seconds():.4f}s")
        self.trail.log(f"Timestamp: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")

        # Hide progress bar after a short delay
        self.root.after(2000, self._finish_computation)

    def export_trail(self):
        """Export the solution trail to a text or HTML file."""
        if not self.trail_text.get("1.0", "end-1c").strip():
            messagebox.showinfo("Export", "Nothing to export (trail is empty).")
            return
        
        # Ask user for export format
        format_choice = messagebox.askquestion(
            "Export Format",
            "Click YES for HTML report\nClick NO for TXT report",
            type=messagebox.YESNO
        )
        
        if format_choice == messagebox.YES:
            # HTML Export
            filetypes = [("HTML files", "*.html"), ("All files", "*")]
            fname = filedialog.asksaveasfilename(
                title="Export solution trail as HTML",
                defaultextension=".html",
                filetypes=filetypes,
            )
            if fname:
                try:
                    self.export_as_html(fname)
                    messagebox.showinfo("Export", "HTML Report exported to %s" % fname)
                except Exception as e:
                    messagebox.showerror("Export Error", str(e))
        else:
            # TXT Export (enhanced format)
            filetypes = [("Text files", "*.txt"), ("All files", "*")]
            fname = filedialog.asksaveasfilename(
                title="Export solution trail",
                defaultextension=".txt",
                filetypes=filetypes,
            )
            if fname:
                try:
                    self.export_as_txt(fname)
                    messagebox.showinfo("Export", "Trail exported to %s" % fname)
                except Exception as e:
                    messagebox.showerror("Export Error", str(e))

    def export_as_txt(self, filepath: str):
        """Export solution trail as a formatted TXT report."""
        trail_content = self.trail_text.get("1.0", "end-1c")
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("=" * 80 + "\n")
            f.write("NEWTON-RAPHSON ROOT FINDER - SOLUTION REPORT\n")
            f.write("=" * 80 + "\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 80 + "\n\n")
            
            # Parse and organize content by sections
            lines = trail_content.split('\n')
            current_section = ""
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                # Detect section headers
                if line.endswith(':') and line.replace(':', '').isupper():
                    current_section = line
                    f.write(f"\n{'─' * 60}\n")
                    f.write(f"  {line}\n")
                    f.write(f"{'─' * 60}\n")
                elif current_section:
                    f.write(f"  {line}\n")
                else:
                    f.write(f"{line}\n")
            
            f.write("\n" + "=" * 80 + "\n")
            f.write("END OF REPORT\n")
            f.write("=" * 80 + "\n")

    def export_as_html(self, filepath: str):
        """Export solution trail as a formatted HTML report."""
        trail_content = self.trail_text.get("1.0", "end-1c")
        
        # Parse content by sections
        lines = trail_content.split('\n')
        sections = {}
        current_section = ""
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Detect section headers
            if line.endswith(':') and line.replace(':', '').isupper():
                current_section = line.replace(':', '')
                sections[current_section] = []
            elif current_section:
                sections[current_section].append(line)
        
        # Generate HTML
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Newton-Raphson Solution Report</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .header {{
            background: linear-gradient(135deg, #1e40af, #3b82f6);
            color: white;
            padding: 30px;
            border-radius: 10px;
            text-align: center;
            margin-bottom: 20px;
        }}
        .header h1 {{
            margin: 0;
            font-size: 28px;
        }}
        .header p {{
            margin: 10px 0 0 0;
            opacity: 0.9;
        }}
        .section {{
            background: white;
            margin-bottom: 15px;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .section-header {{
            background: #2563eb;
            color: white;
            padding: 12px 20px;
            font-weight: bold;
            font-size: 16px;
        }}
        .section-content {{
            padding: 15px 20px;
            line-height: 1.6;
        }}
        .step {{
            padding: 5px 0;
            border-bottom: 1px solid #eee;
        }}
        .step:last-child {{
            border-bottom: none;
        }}
        .success {{
            color: #15803d;
            font-weight: 500;
        }}
        .error {{
            color: #b91c1c;
            font-weight: 500;
        }}
        .info {{
            color: #92400e;
        }}
        .footer {{
            text-align: center;
            color: #666;
            margin-top: 30px;
            padding: 20px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🧮 Newton-Raphson Root Finder</h1>
        <p>Solution Report - Generated {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
"""
        
        # Add sections in order
        section_order = ['GIVEN', 'VALIDATION', 'EDGE CASE ANALYSIS', 'METHOD', 
                        'STOPPING RULES', 'STEPS', 'FINAL ANSWER', 'STOPPING CONDITION', 
                        'VERIFICATION', 'SUMMARY']
        
        for section_name in section_order:
            if section_name in sections and sections[section_name]:
                html_content += f"""
    <div class="section">
        <div class="section-header">{section_name}</div>
        <div class="section-content">
"""
                for line in sections[section_name]:
                    # Determine styling based on content
                    if '✓' in line or 'SUCCESS' in line:
                        html_content += f'            <div class="step success">✓ {self._escape_html(line)}</div>\n'
                    elif '⚠' in line or 'ERROR' in line or '✗' in line:
                        html_content += f'            <div class="step error">⚠ {self._escape_html(line)}</div>\n'
                    elif line.startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.', '10.')):
                        html_content += f'            <div class="step">{self._escape_html(line)}</div>\n'
                    else:
                        html_content += f'            <div class="step info">{self._escape_html(line)}</div>\n'
                
                html_content += """        </div>
    </div>
"""
        
        html_content += f"""
    <div class="footer">
        <p>Report generated by Newton-Raphson Root Finder {APP_VERSION}</p>
        <p>Developed by: Charles Russel San Juan, Christina Gomba, John Michael Tulalian</p>
    </div>
</body>
</html>
"""
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html_content)

    def _escape_html(self, text: str):
        """Escape HTML special characters."""
        return (text.replace('&', '&amp;')
                    .replace('<', '&lt;')
                    .replace('>', '&gt;')
                    .replace('"', '&quot;')
                    .replace("'", '&#39;'))


if __name__ == "__main__":
    root = ctk.CTk()
    app = NewtonRaphsonApp(root)
    root.mainloop()

import os
import tkinter as tk
from tkinter import filedialog, messagebox
from ttkbootstrap import Style
from ttkbootstrap.widgets import Frame, Label, Button, Entry, Checkbutton, Combobox
import getdist
import getdist.plots as plots
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

plt.rc('text', usetex=True)
plt.rc('font', family='serif')

# Get all the available color names from matplotlib
preset_colors = list(mcolors.CSS4_COLORS.keys())

# Function to load chains and create the plots
def generate_plots():
    try:
        # Show "Plotting, please wait" message
        status_label.config(text="Plotting, please wait...")
        root.update_idletasks()

        root_paths = [
            os.path.join(entry.get().strip(), subdir.get().strip())
            for entry, subdir in zip(root_entries, subdir_entries)
            if entry.get().strip()
        ]
        param_list = param_entries.get().split(',')
        legend_labels = legend_entries.get().split(',')

        if len(root_paths) != len(legend_labels):
            messagebox.showerror("Error", "Number of root directories and legend labels must match.")
            return

        # Get user-defined settings
        font_family = font_entry.get().strip()
        font_size = int(fontsize_entry.get().strip())
        line_width = float(linewidth_entry.get().strip())
        filled = fill_var.get()

        plt.rc('font', family=font_family)
        plt.rcParams.update({'font.size': font_size})

        # Load MCMC samples with individual ignore_rows values
        samples = [
            getdist.mcsamples.loadMCSamples(root, settings={'ignore_rows': float(ignore.get().strip())})
            for root, ignore in zip(root_paths, ignore_rows_entries)
        ]

        g = plots.get_subplot_plotter(width_inch=10)
        g.settings.linewidth_contour = line_width
        g.settings.linewidth = line_width
        g.settings.fontsize = font_size
        g.settings.alpha_filled_add = 0.95

        plot_colors = [color.get() if color.get() else None for color in color_entries]

        # Generate the triangle plot with the specified colors
        g.triangle_plot(samples, param_list, filled=filled, legend_labels=legend_labels, contour_colors=plot_colors)

        # Display the plot in a separate window
        plt.show()

        # Clear the status message
        status_label.config(text="")

    except Exception as e:
        status_label.config(text="")
        messagebox.showerror("Error", str(e))

# Function to add a new root entry
def add_root_entry():
    row = len(root_entries) + 2

    Label(frame, text="Select a Root:", font=('Helvetica', 12)).grid(row=row, column=0, sticky=tk.W)
    entry = Entry(frame, width=60)
    entry.grid(row=row, column=1, padx=10, pady=2, sticky=tk.W)
    root_entries.append(entry)
    Button(frame, text="Browse", command=lambda: browse_root(entry)).grid(row=row, column=2, padx=10, sticky=tk.E)

    # Add subdirectory entry for each root
    subdir_entry = Entry(frame, width=20)
    subdir_entry.grid(row=row, column=3, padx=10, pady=2)
    subdir_entry.insert(0, "test")  # Default subdirectory name
    subdir_entries.append(subdir_entry)

    # Add color selection for each entry
    color_combobox = Combobox(frame, values=preset_colors, width=15)
    color_combobox.grid(row=row, column=4, padx=10, pady=2)
    color_entries.append(color_combobox)

    # Add individual ignore_rows entry for each root
    ignore_entry = Entry(frame, width=10)
    ignore_entry.grid(row=row, column=5, padx=10, pady=2)
    ignore_entry.insert(0, "0")  # Default value for ignore_rows
    ignore_rows_entries.append(ignore_entry)

# Function to browse for root directories
def browse_root(entry):
    path = filedialog.askdirectory(title="Select Root Directory")
    if path:
        entry.delete(0, tk.END)
        entry.insert(0, path)

# Function to clear all input fields
def clear_fields():
    for entry in root_entries:
        entry.delete(0, tk.END)
    for subdir in subdir_entries:
        subdir.delete(0, tk.END)
        subdir.insert(0, "test")
    param_entries.delete(0, tk.END)
    legend_entries.delete(0, tk.END)
    font_entry.delete(0, tk.END)
    fontsize_entry.delete(0, tk.END)
    linewidth_entry.delete(0, tk.END)
    for color in color_entries:
        color.set("")
    for ignore in ignore_rows_entries:
        ignore.delete(0, tk.END)
        ignore.insert(0, "0")

# Setting up the main window
root = tk.Tk()
style = Style(theme='cosmo')
root.title("MCMC Chains Plotter")

frame = Frame(root, padding=(20, 20))
frame.pack(fill=tk.BOTH, expand=True)

# Initial root entry
root_entries = []
subdir_entries = []
color_entries = []
ignore_rows_entries = []
add_root_entry()

Button(frame, text="Add Another Chain", command=add_root_entry).grid(row=1, column=2, pady=10, sticky=tk.E)

# Subdirectory name label (global setting removed, now per root)
Label(frame, text="Parameters (Separate with ','):", font=('Helvetica', 12)).grid(row=100, column=0, sticky=tk.W)
param_entries = Entry(frame, width=80)
param_entries.grid(row=100, column=1, columnspan=3, padx=10, pady=10, sticky=tk.W)

Label(frame, text="Legend Labels (Separate with ','):", font=('Helvetica', 12)).grid(row=101, column=0, sticky=tk.W)
legend_entries = Entry(frame, width=80)
legend_entries.grid(row=101, column=1, columnspan=3, padx=10, pady=10, sticky=tk.W)

# Adding input fields for font, fontsize, and linewidth
Label(frame, text="Font Family:", font=('Helvetica', 12)).grid(row=102, column=0, sticky=tk.W)
font_entry = Entry(frame, width=40)
font_entry.grid(row=102, column=1, columnspan=3, padx=10, pady=10, sticky=tk.W)
font_entry.insert(0, "serif")  # Default font

Label(frame, text="Font Size:", font=('Helvetica', 12)).grid(row=103, column=0, sticky=tk.W)
fontsize_entry = Entry(frame, width=40)
fontsize_entry.grid(row=103, column=1, columnspan=3, padx=10, pady=10, sticky=tk.W)
fontsize_entry.insert(0, "30")  # Default font size

Label(frame, text="Line Width:", font=('Helvetica', 12)).grid(row=104, column=0, sticky=tk.W)
linewidth_entry = Entry(frame, width=40)
linewidth_entry.grid(row=104, column=1, columnspan=3, padx=10, pady=10, sticky=tk.W)
linewidth_entry.insert(0, "2.0")  # Default line width

# Adding checkbox for filled option
fill_var = tk.BooleanVar(value=True)
fill_check = Checkbutton(frame, text="Filled Contour Plots", variable=fill_var, onvalue=True, offvalue=False)
fill_check.grid(row=106, column=0, columnspan=2, pady=10, sticky=tk.W)

Button(frame, text="Generate Plot", command=generate_plots).grid(row=107, column=1, pady=20, sticky=tk.W)
Button(frame, text="Clear", command=clear_fields).grid(row=107, column=2, pady=20, sticky=tk.E)

# Status label for showing messages
status_label = Label(frame, text="", font=('Helvetica', 12))
status_label.grid(row=108, column=0, columnspan=6, pady=10, sticky=tk.W)

# Close the application when the main window is closed
root.protocol("WM_DELETE_WINDOW", root.quit)

root.mainloop()

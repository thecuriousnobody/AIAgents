import tkinter as tk
from tkinter import ttk, filedialog, simpledialog
from agent_manager import AgentManager
import io
import sys
import json
import threading

class GUIApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("AI Agent Manager")
        self.geometry("800x600")
        # self.agent_manager = AgentManager()

        self.stdout = sys.stdout

        # Create a notebook for different sections
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True)

        # Create the Agents tab
        agents_frame = ttk.Frame(notebook)
        notebook.add(agents_frame, text="Agents")
        self.create_agents_tab(agents_frame)

        # Create the Output tab
        output_frame = ttk.Frame(notebook)
        notebook.add(output_frame, text="Output")
        self.create_output_tab(output_frame)


        # Redirect stdout to a custom TextIOWrapper
        self.redirect_stdout()

    def add_agent(self):
        # Create a dialog to get the agent details
        agent_dialog = tk.Toplevel(self)
        agent_dialog.title("Add Agent")

        # Add input fields for agent and role
        agent_label = ttk.Label(agent_dialog, text="Agent:")
        agent_label.pack(pady=5)

        agent_entry = ttk.Entry(agent_dialog)
        agent_entry.pack(pady=5)

        role_label = ttk.Label(agent_dialog, text="Role:")
        role_label.pack(pady=5)

        role_entry = ttk.Entry(agent_dialog)
        role_entry.pack(pady=5)

        # Add buttons to create or cancel the agent
        button_frame = ttk.Frame(agent_dialog)
        button_frame.pack(pady=5)

        create_button = ttk.Button(button_frame, text="Create",
                                   command=lambda: self.create_agent(agent_entry.get(), role_entry.get(), agent_dialog))
        create_button.pack(side="left", padx=5)

        cancel_button = ttk.Button(button_frame, text="Cancel", command=agent_dialog.destroy)
        cancel_button.pack(side="left", padx=5)

        # Wait for the dialog to be closed
        self.wait_window(agent_dialog)

    def run_agents(self):
        self.agent_output_text.delete("1.0", "end")
        self.output_text.delete("1.0", "end")

        # Clear the abort flag before running the agents
        # self.agent_manager.abort_flag = False

        # Run the agents in a separate thread
        thread = threading.Thread(target=self.run_agents_thread)
        thread.start()

    def create_agents_tab(self, agents_frame):
        # Create a frame for the goal input
        goal_frame = ttk.Frame(agents_frame)
        goal_frame.pack(side="top", fill="x", padx=5, pady=5)

        goal_label = ttk.Label(goal_frame, text="Goal:")
        goal_label.pack(side="left")

        self.goal_entry = ttk.Entry(goal_frame)
        self.goal_entry.pack(side="left", fill="x", expand=True)

        self.set_goal_button = ttk.Button(goal_frame, text="Set Goal", command=self.set_goal)
        self.set_goal_button.pack(side="right")

        self.goal_status_label = ttk.Label(goal_frame, text="")
        self.goal_status_label.pack(side="bottom")

        # Create a treeview to display agents
        self.agents_treeview = ttk.Treeview(agents_frame)
        self.agents_treeview["columns"] = ("Role",)
        self.agents_treeview.column("#0", width=200, minwidth=200, anchor="w")
        self.agents_treeview.column("Role", width=400, minwidth=400, anchor="w")
        self.agents_treeview.heading("#0", text="Agent", anchor="w")
        self.agents_treeview.heading("Role", text="Role", anchor="w")
        self.agents_treeview.pack(side="top", fill="both", expand=True)
        self.agents_treeview.bind("<Double-1>", self.edit_agent_role)

        # Add buttons to create, run, save, and load agents
        button_frame = ttk.Frame(agents_frame)
        button_frame.pack(side="bottom", fill="x")

        add_agent_button = ttk.Button(button_frame, text="Add Agent", command=None)
        add_agent_button.pack(side="left", padx=5, pady=5)

        run_agents_button = ttk.Button(button_frame, text="Run Agents", command=self.run_agents)
        run_agents_button.pack(side="left", padx=5, pady=5)

        # save_agents_button = ttk.Button(button_frame, text="Save Agents", command=self.show_save_dialog)
        # save_agents_button.pack(side="left", padx=5, pady=5)

        # load_agents_button = ttk.Button(button_frame, text="Load Agents", command=self.load_agents)
        # load_agents_button.pack(side="left", padx=5, pady=5)

        # Create a frame to hold the agent output label and text area
        output_frame = ttk.Frame(agents_frame)
        output_frame.pack(side="bottom", fill="both", expand=True)

        # Add the agent output label
        workflow_label = ttk.Label(output_frame, text="Active Workflow:")
        workflow_label.pack(side="top", anchor="w", padx=5, pady=5)

        # Add the agent output text area
        self.agent_output_text = tk.Text(output_frame, wrap="word")
        self.agent_output_text.pack(side="top", fill="both", expand=True)


    # def load_agents(self):
    #         # Load the agent data from a file
    #         file_path = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
    #         if file_path:
    #             with open(file_path, "r") as file:
    #                 agent_data = json.load(file)
    #
    #             # Clear the current agents and populate with loaded data
    #             # self.agent_manager.agents.clear()
    #             # self.agents_treeview.delete(*self.agents_treeview.get_children())
    #             for agent in agent_data:
    #                 # self.agent_manager.create_agent(agent["name"], agent["role"])
    #                 self.agents_treeview.insert("", "end", text=agent["name"], values=(agent["role"],))
    #                 self.goal_entry.delete(0, "end")
    #                 self.goal_entry.insert(0, agent["goal"])
    #                 self.output_text.delete("1.0", "end")
    #                 self.output_text.insert("end", agent["output"])

    # def save_agents(self):
    #     if self.agent_manager.agents:  # Check if there are agents to save
    #         # Get the current agent set data
    #         agent_data = []
    #         for agent in self.agent_manager.agents:
    #             agent_data.append({
    #                 "name": agent.agent_name,  # Use agent.agent_name instead of agent.name
    #                 "role": agent.role,
    #                 "goal": self.agent_manager.goal
    #             })
    #
    #         # Get the output data
    #         output_data = {
    #             "agent_output": self.agent_output_text.get("1.0", "end-1c"),
    #             "final_output": self.output_text.get("1.0", "end-1c")
    #         }
    #
    #         # Combine the agent data and output data
    #         save_data = {
    #             "agents": agent_data,
    #             "output": output_data
    #         }
    #
    #         # Call the show_save_dialog method with the save_data as an argument
    #         self.show_save_dialog(save_data)
    #     else:
    #         print("No agents to save.")


    # def show_save_dialog(self, save_data):
    #     # Open a file dialog to choose the save location
    #     print("Show save dialog called")  # Add this print statement
    #     # Open a file dialog to choose the save location
    #     file_path = filedialog.asksaveasfilename(
    #         defaultextension=".json",
    #         filetypes=[("JSON Files", "*.json")],
    #         title="Save Agents"
    #     )
    #
    #     # Save the data to the selected file
    #     if file_path:
    #         with open(file_path, "w") as file:
    #             json.dump(save_data, file)
    #         print("Agents and output saved successfully.")
    #
    #     # Destroy the file dialog
    #     self.focus_set()

    def create_output_tab(self, output_frame):
        # Create a text area to display the output
        self.output_text = tk.Text(output_frame, wrap="word")
        self.output_text.pack(side="top", fill="both", expand=True)

        # Add a button to save the output
        save_button = ttk.Button(output_frame, text="Save Output", command=self.save_output)
        save_button.pack(side="bottom", fill="x", padx=5, pady=5)

    def create_agent_output_tab(self, agent_output_frame):
        # Create a text area to display the agent output
        self.agent_output_text = tk.Text(agent_output_frame, wrap="word")
        self.agent_output_text.pack(side="top", fill="both", expand=True)

    def update_agent_output_text(self, text):
        self.agent_output_text.insert("end", text)
        self.agent_output_text.see("end")

    def redirect_stdout(self):
        sys.stdout = TextIOWrapper(self.update_agent_output_text)

    style = ttk.Style()
    style.configure("Green.TButton", background="green")

    def set_goal(self):
        goal = self.goal_entry.get()
        # self.agent_manager.set_goal(goal)

        # Display the "Goal Set!" message
        self.goal_status_label.configure(text="Goal Set!", foreground="green")

        # Schedule the message to disappear after 2 seconds
        self.after(2000, self.clear_goal_status_message)

    def clear_goal_status_message(self):
        self.goal_status_label.configure(text="")

    # def create_agent(self, agent_name, role, dialog):
    #     # self.agent_manager.create_agent(agent_name, role)
    #     self.agents_treeview.insert("", "end", text=agent_name, values=(role,))
    #     dialog.destroy()
    #     self.wait_window(dialog)


    # def run_agents_thread(self):
    #     for output in self.agent_manager.run_agents():
    #         if self.agent_manager.abort_flag:
    #             break
    #         self.agent_output_text.insert("end", output)  # Insert output as a single line
    #         self.agent_output_text.see("end")
    #         self.agent_output_text.update_idletasks()
    #
    #     if not self.agent_manager.abort_flag:
    #         final_output = self.agent_manager.get_final_output()
    #         self.output_text.insert("end", final_output)
    #     else:
    #         self.output_text.insert("end", "Agents aborted.")
    #     sys.stdout = self.stdout

    def edit_agent_role(self, event):
        # Get the selected agent
        selected_item = self.agents_treeview.focus()
        if selected_item:
            agent_name = self.agents_treeview.item(selected_item)["text"]
            agent_role = self.agents_treeview.item(selected_item)["values"][0]

            # Create a dialog to edit the agent's role
            edit_dialog = tk.Toplevel(self)
            edit_dialog.title("Edit Agent Role")

            role_label = ttk.Label(edit_dialog, text="Role:")
            role_label.pack(pady=5)

            role_entry = ttk.Entry(edit_dialog)
            role_entry.insert(0, agent_role)
            role_entry.pack(pady=5)

            # Add buttons to save or cancel the edit
            button_frame = ttk.Frame(edit_dialog)
            button_frame.pack(pady=5)

            save_button = ttk.Button(button_frame, text="Save",
                                     command=lambda: self.save_agent_role(selected_item, role_entry.get(), edit_dialog))
            save_button.pack(side="left", padx=5)

            cancel_button = ttk.Button(button_frame, text="Cancel", command=edit_dialog.destroy)
            cancel_button.pack(side="left", padx=5)

    # def save_agent_role(self, selected_item, new_role, dialog):
    #     # Update the agent's role
    #     agent_name = self.agents_treeview.item(selected_item)["text"]
    #     self.agent_manager.update_agent_role(agent_name, new_role)
    #
    #     # Update the treeview
    #     self.agents_treeview.item(selected_item, values=(new_role,))
    #
    #     # Close the dialog
    #     dialog.destroy()

    def save_output(self):
        # Placeholder for saving output
        pass

    # def abort_agents(self):
    #     # Implement the logic to abort the running agents
    #     # For example, you can set a flag to indicate that the agents should stop
    #     self.agent_manager.abort_flag = True
    #     print("Aborting agents...")

class TextIOWrapper(io.TextIOBase):
    def __init__(self, update_func):
        self.update_func = update_func

    def write(self, s):
        self.update_func(s)
        return len(s)

if __name__ == '__main__':
    app = GUIApp()
    app.mainloop()
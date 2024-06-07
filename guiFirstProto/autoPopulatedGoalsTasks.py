import tkinter as tk
from tkinter import ttk, filedialog, simpledialog
from crewai import Agent, Task, Crew, Process
import tkinter as tk
from tkinter import ttk, filedialog, simpledialog
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
import os
# print ("script started")
import io

os.environ["GROQ_API_KEY"] = config.GROQ_API_KEY

class GUIApp(tk.Tk):
    def __init__(self):
        print("Initializing GUIApp")
        super().__init__()
        # print("After super().__init__()")
        self.title("AI Agent Manager")
        # print("After setting title")
        self.geometry("800x600")
        # print("After setting geometry")  
        self.llms = {
            "GPT4o": ChatOpenAI(
                openai_api_base="https://api.openai.com/v1",
                openai_api_key=config.ANTHROPIC_API_KEY,
                model_name="gpt-3.5-turbo"
            ),
            "Claude": ChatOpenAI(
                openai_api_base="https://api.claude.com/v1",
                openai_api_key=config.ANTHROPIC_API_KEY,
                model_name="claude-1.0"
            ),
            "GROQ": ChatOpenAI(
                openai_api_base="https://api.groq.com/openai/v1",
                openai_api_key=config.GROQ_API_KEY,
                model_name="llama3-70b-8192"
            )
        }
        self.agents = []
        self.goal = ""

        self.agent_output_text = tk.Text(self, wrap="word")
        # print("creating notebook")
        self.create_notebook()

        # Redirect stdout to a custom TextIOWrapper
        # self.stdout = sys.stdout
        # # print("stdout set")
        # sys.stdout = TextIOWrapper(self.agent_output_text)


    def create_notebook(self):
    # Create a notebook for different sections
        # print("Notebook created")
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

        # Create the Agent Output tab
        agent_output_frame = ttk.Frame(notebook)
        notebook.add(agent_output_frame, text="Agent Output")
        self.create_agent_output_tab(agent_output_frame)

    def create_agents_tab(self, agents_frame):
        # Create a frame for the goal input
        # print("Creating Agent Output tab")
        goal_frame = ttk.Frame(agents_frame)
        goal_frame.pack(side="top", fill="x", padx=5, pady=5)

        goal_label = ttk.Label(goal_frame, text="Goal:")
        goal_label.pack(side="left")

        goal_entry = ttk.Entry(goal_frame, textvariable=tk.StringVar(value=self.goal))
        goal_entry.pack(side="left", fill="x", expand=True)

        set_goal_button = ttk.Button(goal_frame, text="Set Goal", command=lambda: self.set_goal(goal_entry.get()))
        set_goal_button.pack(side="right")

        # In the create_agents_tab method
        self.agents_treeview = ttk.Treeview(agents_frame, columns=("Agent", "Role", "LLM"), show="headings")
        self.agents_treeview.column("Agent", width=200, minwidth=200, anchor="w")
        self.agents_treeview.column("Role", width=200, minwidth=200, anchor="w")
        self.agents_treeview.column("LLM", width=200, minwidth=200, anchor="w")
        self.agents_treeview.heading("Agent", text="Agent", anchor="w")
        self.agents_treeview.heading("Role", text="Role", anchor="w")
        self.agents_treeview.heading("LLM", text="LLM", anchor="w")
        self.agents_treeview.pack(side="top", fill="both", expand=True)
        self.agents_treeview.bind("<Double-1>", self.edit_agent_role)


        # Create the treeview
        self.agents_treeview = ttk.Treeview(agents_frame, columns=("Role", "LLM"), show="headings")
        self.agents_treeview.heading("Role", text="Role")
        self.agents_treeview.heading("LLM", text="LLM")

        # Add buttons to create and run agents
        # print("Before creating button frame")
        button_frame = ttk.Frame(agents_frame)
        # print("After creating button frame")
        button_frame.pack(side="bottom", fill="x")
        
        # print("Creating Add Agents button")
        add_agent_button = ttk.Button(button_frame, text="Add Agent", command=self.add_agent)
        add_agent_button.pack(side="left", padx=5, pady=5)

        run_agents_button = ttk.Button(button_frame, text="Run Agents", command=self.run_agents)
        run_agents_button.pack(side="left", padx=5, pady=5)

    def create_output_tab(self, output_frame):
        # Create a text area to display the output
        # print("Creating Output tab")
        self.output_text = tk.Text(output_frame, wrap="word")
        self.output_text.pack(side="top", fill="both", expand=True)

        # Add a button to save the output
        save_button = ttk.Button(output_frame, text="Save Output", command=self.save_output)
        save_button.pack(side="bottom", fill="x", padx=5, pady=5)

    def create_agent_output_tab(self, agent_output_frame):
        # print("Creating Agent Output tab")
        # Pack the existing agent_output_text widget
        self.agent_output_text.pack(side="top", fill="both", expand=True)

    def set_goal(self, goal):
        self.goal = goal

    def add_agent(self):
        # Create a dialog to get the agent details
        print("Inside add_agent method")
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

         # Add a dropdown list for LLMs
        llm_label = ttk.Label(agent_dialog, text="LLM:")
        llm_label.pack(pady=5)

        # print("just above the LLM Combobox")

        llm_combobox = ttk.Combobox(agent_dialog, values=["GPT4o", "Claude", "GROQ"])
        llm_combobox.pack(pady=5)
        
        # print(f"Agent details: {agent_entry.get()}, {role_entry.get()}, {llm_combobox.get()}")  # Add this print statement

        def create_agent_handler():
            agent_name = agent_entry.get()
            role = role_entry.get()
            llm = llm_combobox.get()
            print(f"Agent details: {agent_name}, {role}, {llm}")  # Add this print statement
            self.create_agent(agent_name, role, llm, agent_dialog)


        create_button = ttk.Button(button_frame, text="Create", command=create_agent_handler)
        create_button.pack(side="left", padx=5)

        # create_button = ttk.Button(button_frame, text="Create", command=lambda: self.create_agent(agent_entry.get(), role_entry.get(), llm_combobox.get(), agent_dialog))
        # create_button.pack(side="left", padx=5)

        # print(f"Agent details: {agent_entry.get()}, {role_entry.get()}, {llm_combobox.get()}")  # Add this print statement
    
        cancel_button = ttk.Button(button_frame, text="Cancel", command=agent_dialog.destroy)
        cancel_button.pack(side="left", padx=5)



    def create_agent(self, agent_name, role, llm, dialog):
        try:
        # Create an Agent instance
            print(f"LLM: {llm}")
            print(f"self.llms: {self.llms}")
            agent = Agent(
                role=role,
                goal=self.goal,
                backstory=f"You are an AI agent named {agent_name} working on the goal: {self.goal}",
                verbose=False,
                allow_delegation=False,
                llm=self.llms[llm],  # Use the selected LLM
                name=agent_name  # Add the name attribute
            )
            print(f"Agent created: {agent}")  # Add this print statement

            # Add the agent to the treeview
            self.agents.append(agent)
            print("Agents list:")
            for a in self.agents:
                print(a)

            self.agents_treeview.insert("", "end", values=(agent_name, role, llm))  # Insert name, role and llm
            # self.agents_treeview.insert("", "end", values=(agent_name, role))  # Insert name, role and llm
            self.agents_treeview.update_idletasks()
            self.agents_treeview.update()

            self.after(100, self.agents_treeview.update)
            print("Dialog box should be displayed")

            print(f"Inserted values: {agent_name}, {role}, {llm}")
            print("Treeview contents:")
            inserted_item = self.agents_treeview.get_children()[-1]  # Get the ID of the last inserted item
            item_details = self.agents_treeview.item(inserted_item)
            print(item_details)
            # Update the treeview
            self.agents_treeview.update_idletasks()
            # self.agents_treeview.print_tree()
            dialog.destroy()

        except Exception as e:
            print(f"Error creating agent: {e}")
            return

    # Close the dialog

    
        
    def edit_agent_role(self, event):
        # Get the selected agent
        selected_item = self.agents_treeview.focus()
        if selected_item:
            agent_name, agent_role = self.agents_treeview.item(selected_item)["values"]

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

            save_button = ttk.Button(button_frame, text="Save", command=lambda: self.save_agent_role(selected_item, role_entry.get(), edit_dialog))
            save_button.pack(side="left", padx=5)

            cancel_button = ttk.Button(button_frame, text="Cancel", command=edit_dialog.destroy)
            cancel_button.pack(side="left", padx=5)

    def save_agent_role(self, selected_item, new_role, dialog):
        # Update the agent's role
        agent_name, _ = self.agents_treeview.item(selected_item)["values"]
        for agent in self.agents:
            if agent_name == agent.name:  # Check against the name attribute
                agent.role = new_role
                agent.backstory = f"You are an AI agent named {agent_name} working on the goal: {self.goal}"
                break

        # Update the treeview
        self.agents_treeview.item(selected_item, values=(agent_name, new_role))

        # Close the dialog
        dialog.destroy()

    def create_agent_output_tab(self, agent_output_frame):
        # Create a text area to display the agent output
        self.agent_output_text = tk.Text(agent_output_frame, wrap="word")
        self.agent_output_text.pack(side="top", fill="both", expand=True)

    def update_agent_output_text(self, text):
        self.agent_output_text.insert("end", text)
        self.agent_output_text.see("end")

    def run_agents(self):
        # Clear the output text area
        self.output_text.delete("1.0", "end")
        self.agent_output_text.delete("1.0", "end")  # Clear the agent output text area

        # Create Task instances for each agent
        tasks = []
        for agent in self.agents:
            task = Task(
                description=agent.goal,
                agent=agent,
                expected_output=f"Output for {agent.role}"
            )
            tasks.append(task)

        # Create a Crew instance and execute the tasks
        crew = Crew(
            agents=self.agents,
            tasks=tasks,
            verbose=1,
            process=Process.sequential
        )
        final_output = crew.kickoff()

        # Display the final output in the output text area
        self.output_text.insert("end", final_output)

        # Reset stdout to its original value
        # sys.stdout = self.stdout

    def save_output(self):
        # Placeholder for saving output
        pass

class TextIOWrapper(io.TextIOBase):
    def __init__(self, output_text):
        self.output_text = output_text

    def write(self, s):
        self.output_text.insert("end", s)
        self.output_text.see("end")
        return len(s)

if __name__ == '__main__':
    app = GUIApp()
    app.mainloop()
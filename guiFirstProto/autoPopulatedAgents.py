import tkinter as tk
from tkinter import ttk, filedialog, simpledialog
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
import io
# from generate_agent_details import generate_agent_details
from agentAggregator import *
from tkinter import messagebox

OPENAI_API_KEY = config.OPENAI_API_KEY

os.environ["GROQ_API_KEY"] =config.GROQ_API_KEY

llm_GROQ= ChatOpenAI(
    openai_api_base = "https://api.groq.com/openai/v1",
    openai_api_key =  os.getenv("GROQ_API_KEY"),
    model_name = "llama3-70b-8192"
)


os.environ["GROQ_API_KEY"] = config.GROQ_API_KEY

class GUIApp(tk.Tk):
    def __init__(self):
        print("Initializing GUIApp")
        super().__init__()
        print("After super().__init__()")
        self.title("AI Agent Manager")
        print("After setting title")
        self.geometry("800x600")
        print("After setting geometry")
        self.llms = {
            "GPT4o": ChatOpenAI(
                openai_api_base="https://api.openai.com/v1/chat/completions",
                openai_api_key=config.OPENAI_API_KEY,
                model_name="gpt-4o"
            ),
            "Claude": ChatOpenAI(
                openai_api_base="https://api.claude.com/v1",
                openai_api_key=config.ANTHROPIC_API_KEY,
                model_name="claude-3-haiku-20240307"
            ),
            "GROQ": ChatOpenAI(
                openai_api_base="https://api.groq.com/openai/v1",
                openai_api_key=config.ANTHROPIC_API_KEY,
                model_name="llama3-70b-8192"
            )
        }
        self.agents = []
        self.goal = "Get a couple experts who can speak about the evolution of European sexuality over the last 500 years on my podcast"
        self.context = "I'm a podcaster wanting to interview experts in european sexuality and history of european sexuality"
        print("creating notebook")
        self.create_notebook()

        

    def create_notebook(self):
        # Create a notebook for different sections
        print("Notebook created")
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

        # # Create the Agent Output tab
        # agent_output_frame = ttk.Frame(notebook)
        # notebook.add(agent_output_frame, text="Agent Output")
        # self.create_agent_output_tab(agent_output_frame)

    def create_agents_tab(self, agents_frame):
        # Create a frame for the goal input
        print("Creating Agents tab")
        goal_frame = ttk.Frame(agents_frame)
        goal_frame.pack(side="top", fill="x", padx=5, pady=5)

        goal_label = ttk.Label(goal_frame, text="Goal:")
        goal_label.pack(side="left")

        default_goal ="Get a couple experts who can speak about the evolution of European sexuality over the last 500 years on my podcast"
        goal_entry = ttk.Entry(goal_frame, textvariable=tk.StringVar(value=default_goal))
        # goal_entry.insert("1.0", default_goal)
        goal_entry.pack(side="left", fill="x", expand=True)

        # Create a frame for the context input
        context_frame = ttk.Frame(agents_frame)
        context_frame.pack(side="top", fill="x", padx=5, pady=5)

        context_label = ttk.Label(context_frame, text="Context:")
        context_label.pack(side="left")

        default_context = "I'm a podcaster wanting to interview experts in european sexuality and history of european sexuality"
        context_entry = tk.Text(context_frame, height=5, wrap="word")
        context_entry.insert("1.0", default_context)
        context_entry.pack(side="left", fill="both", expand=True)

        set_button = ttk.Button(agents_frame, text="Set Goal and Context", command=lambda: self.set_goal_and_context(goal_entry.get(), context_entry.get("1.0", "end-1c")))
        set_button.pack(side="top", padx=5, pady=5)

        self.confirmation_label = ttk.Label(agents_frame, text="", foreground="green")
        self.confirmation_label.pack(side="top", padx=5, pady=5)

        # Create a treeview to display agents
        self.agents_treeview = ttk.Treeview(agents_frame)
        self.agents_treeview["columns"] = ("Role", "LLM")  # Add the "LLM" column
        self.agents_treeview.column("#0", width=200, minwidth=200, anchor="w")
        self.agents_treeview.column("Role", width=200, minwidth=200, anchor="w")
        self.agents_treeview.column("LLM", width=200, minwidth=200, anchor="w")  # Configure the "LLM" column
        self.agents_treeview.heading("#0", text="Agent", anchor="w")
        self.agents_treeview.heading("Role", text="Role", anchor="w")
        self.agents_treeview.heading("LLM", text="LLM", anchor="w")  # Add a heading for the "LLM" column
        self.agents_treeview.pack(side="top", fill="both", expand=True)
        self.agents_treeview.bind("<Double-1>", self.edit_agent_role)

        # Create a new frame to hold the agents treeview and the agent output frame
        agents_output_frame = ttk.Frame(agents_frame)
        agents_output_frame.pack(side="top", fill="both", expand=True)
        self.agents_treeview.pack(side="left", fill="both", expand=True)

        self.agent_output_frame = ttk.Frame(agents_output_frame)
        self.agent_output_frame.pack(side="right", fill="both", expand=True)

        # Create a text widget to display the agent output
        self.agent_output_text = tk.Text(self.agent_output_frame, wrap="word")
        self.agent_output_text.pack(side="top", fill="both", expand=True)

        # Create a scrollbar for the agent output text widget
        scrollbar = ttk.Scrollbar(self.agent_output_frame, command=self.agent_output_text.yview)
        scrollbar.pack(side="right", fill="y")
        self.agent_output_text.config(yscrollcommand=scrollbar.set)

        # Redirect stdout to a custom TextIOWrapper
        
        self.stdout = sys.stdout
        sys.stdout = TextIOWrapper(self.agent_output_text)

        # Add buttons to create and run agents
        button_frame = ttk.Frame(agents_frame)
        button_frame.pack(side="bottom", fill="x")

        add_agent_button = ttk.Button(button_frame, text="Add Agent", command=self.add_agent)
        add_agent_button.pack(side="left", padx=5, pady=5)

        create_infra_button = ttk.Button(button_frame, text="Create Agent Infrastructure", command=self.create_agent_infrastructure)
        create_infra_button.pack(side="left", padx=5, pady=5)

        run_agents_button = ttk.Button(button_frame, text="Run Agents", command=self.run_agents)
        run_agents_button.pack(side="left", padx=5, pady=5)

    def create_agent_infrastructure(self):
        print("create_agent_infrastructure called")
        goal = self.goal
        context = self.context
        
        # goal ="Get a couple experts who can speak about the evolution of European sexuality over the last 500 years on my podcast"
        # context = "I'm a podcaster wanting to interview experts in european sexuality and history of european sexuality"

        if not goal or not context:
            messagebox.showwarning("Missing Goal or Context", "Please provide both the goal and context before creating the agent infrastructure.")
            return

        num_agents, agent_details_list = generate_agent_details(goal, context)
        print("Number of agents:", num_agents)
        print("Agent details:", agent_details_list)
        self.agents_treeview.delete(*self.agents_treeview.get_children())
       
        for agent_details in agent_details_list:
            name = agent_details["title"].split(": ")[-1].strip('"')
            role = agent_details["role"].split(": ")[-1].strip('"')
            backstory = agent_details["backstory"].strip()
            llm_name = llm_GROQ  # You can set a default LLM or provide an option to select one
            self.create_agent(name, role, llm_name, None, backstory=backstory)
            
        
    
    def create_output_tab(self, output_frame):
        # Create a text area to display the output
        print("Creating Output tab")
        self.output_text = tk.Text(output_frame, wrap="word")
        self.output_text.pack(side="top", fill="both", expand=True)

        # Add a button to save the output
        save_button = ttk.Button(output_frame, text="Save Output", command=self.save_output)
        save_button.pack(side="bottom", fill="x", padx=5, pady=5)

    def create_agent_output_tab(self, agent_output_frame):
        print("Creating Agent Output tab")
        # Pack the existing agent_output_text widget
        self.agent_output_text.pack(side="top", fill="both", expand=True)

    def set_goal_and_context(self, goal, context):
        self.goal = goal
        self.context = context
        self.confirmation_label.config(text="Goal and context are set.")

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

        # Add a dropdown list for LLMs
        llm_label = ttk.Label(agent_dialog, text="LLM:")
        llm_label.pack(pady=5)

        llm_combobox = ttk.Combobox(agent_dialog, values=["GPT4o", "Claude", "GROQ"])
        llm_combobox.pack(pady=5)

        # Add buttons to create or cancel the agent
        button_frame = ttk.Frame(agent_dialog)
        button_frame.pack(pady=5)

        def create_agent_handler():
            agent_name = agent_entry.get()
            llm_name = llm_combobox.get()

            # Generate role and backstory using Claude Anthropic LLM
            role = generate_agent_details(agent_name)

            print(f"Agent details: {agent_name}, {role}, {llm_name}")
            self.create_agent(agent_name, role, llm_name, agent_dialog)
            

        # create_button = ttk.Button(button_frame, text="Create", command=lambda: self.create_agent(agent_entry.get(), role_entry.get(), llm_combobox.get(), agent_dialog))
        create_button = ttk.Button(button_frame, text="Create", command=create_agent_handler)
        create_button.pack(side="left", padx=5)

        cancel_button = ttk.Button(button_frame, text="Cancel", command=agent_dialog.destroy)
        cancel_button.pack(side="left", padx=5)


    def create_agent(self, agent_name, role, llm_name, dialog, backstory=None):
        # If backstory is not provided, use the default backstory
        if backstory is None:
            backstory = f"You are an AI agent named {agent_name}, whose role is {role}, working on the goal: {self.goal}"
        
        # Create an Agent instance
        agent = Agent(
            role=role,
            goal=self.goal,
            backstory=backstory,
            verbose=False,
            allow_delegation=False,
            llm=llm_GROQ,  # Use the selected LLM
            name=agent_name  # Add the name attribute
        )
        self.agent_output_text.see("end")  # Scroll to the end of the text widget

        try:
            self.agents_treeview.insert("", "end", text=agent_name, values=(role, llm_name))
        except Exception as e:
        # Handle the exception
            print(f"Error occurred while inserting into treeview: {e}")
        self.agents.append(agent)

        if dialog is not None:
            dialog.destroy()



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

            save_button = ttk.Button(button_frame, text="Save", command=lambda: self.save_agent_role(selected_item, role_entry.get(), edit_dialog))
            save_button.pack(side="left", padx=5)

            cancel_button = ttk.Button(button_frame, text="Cancel", command=edit_dialog.destroy)
            cancel_button.pack(side="left", padx=5)

    def save_agent_role(self, selected_item, new_role, dialog):
        # Update the agent's role
        agent_name = self.agents_treeview.item(selected_item)["text"]
        for agent in self.agents:
            if agent_name == agent.name:  # Check against the name attribute
                agent.role = new_role
                agent.backstory = f"You are an AI agent named {agent_name} working on the goal: {self.goal}"
                break

        # Update the treeview
        self.agents_treeview.item(selected_item, values=(new_role,))

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
        sys.stdout = self.stdout

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
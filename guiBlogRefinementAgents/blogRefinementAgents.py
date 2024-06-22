import tkinter as tk
from tkinter import ttk, simpledialog
from tkinter import scrolledtext  # Import the ScrolledText module from tkinter
from tavily import TavilyClient
import requests
import sys
import os
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from tkinter import messagebox
# from tavilySearchEngine import process_search_results
import io
from blogRefinementAgentSpawner import generate_agent_details
import config

# Existing configurations and API keys
OPENAI_API_KEY = config.OPENAI_API_KEY
os.environ["GROQ_API_KEY"] = config.GROQ_API_KEY

llm_GROQ = ChatOpenAI(
    openai_api_base="https://api.groq.com/openai/v1",
    openai_api_key=os.getenv("GROQ_API_KEY"),
    model_name="llama3-70b-8192"
)

class GUIApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("AI Agent Manager")
        self.geometry("800x600")
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
        self.blog_rough_cut = ""
        self.custom_instructions = ""
        # self.goal = "Get a couple experts who can speak about the evolution of European sexuality over the last 500 years on my podcast"
        # self.context = "I'm a podcaster wanting to interview experts in european sexuality and history of european sexuality"
        self.create_notebook()

    def create_notebook(self):
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True)

        agents_frame = ttk.Frame(notebook)
        notebook.add(agents_frame, text="Agents")
        self.create_agents_tab(agents_frame)

        output_frame = ttk.Frame(notebook)
        notebook.add(output_frame, text="Output")
        self.create_output_tab(output_frame)

        self.search_results_frame = ttk.Frame(notebook)
        notebook.add(self.search_results_frame, text="Search Results")
        self.create_search_results_tab(self.search_results_frame)

        blog_input_frame = ttk.Frame(notebook)
        notebook.add(blog_input_frame, text="Blog Rough Cut Input")
        self.create_blog_input_tab(blog_input_frame)

        refined_blog_frame = ttk.Frame(notebook)
        notebook.add(refined_blog_frame, text="Refined Blog")
        self.create_refined_blog_tab(refined_blog_frame)

    def create_agents_tab(self, agents_frame):
        goal_frame = ttk.Frame(agents_frame)
        goal_frame.pack(side="top", fill="x", padx=5, pady=5)

        goal_label = ttk.Label(goal_frame, text="Goal:")
        goal_label.pack(side="left", anchor="n")

        default_goal = "Refine the rough cut blog on arranged marriages in India to create a compelling, nuanced, and factually accurate piece that: [Your detailed goal here]"
        
        goal_text_frame = ttk.Frame(goal_frame)
        goal_text_frame.pack(side="left", fill="both", expand=True)

        self.goal_text = tk.Text(goal_text_frame, wrap="word", height=8)
        self.goal_text.insert("1.0", default_goal)
        self.goal_text.pack(side="left", fill="both", expand=True)

        goal_scrollbar = ttk.Scrollbar(goal_text_frame, orient="vertical", command=self.goal_text.yview)
        goal_scrollbar.pack(side="right", fill="y")
        self.goal_text.configure(yscrollcommand=goal_scrollbar.set)

        context_frame = ttk.Frame(agents_frame)
        context_frame.pack(side="top", fill="x", padx=5, pady=5)

        context_label = ttk.Label(context_frame, text="Context:")
        context_label.pack(side="left", anchor="n")

        default_context = "I am a blogger who deeply cares about the subject matter that I create. I want to be as neutral as possible and make the most compelling argument as I see fit. I'm an optimist in general and tend not to look at the world through cynical eyes. Through this writing, I aim to make the world a better place by spreading good ideas and honest ideas, and by tackling problems in a very nuanced manner without trying to color it with my personal agenda. I don't have an agenda; my agenda is for human flourishing. That is the whole point of the Idea Sandbox podcast as well as the blog. If it becomes an oasis of truth, I would love for that to be the ultimate goal. I'm not looking to make a lot of money; I just want to sustain and see the world evolve to much greater heights."
        self.context_text = tk.Text(context_frame, wrap="word", height=8)
        self.context_text.insert("1.0", default_context)
        self.context_text.pack(side="left", fill="both", expand=True)

        context_scrollbar = ttk.Scrollbar(context_frame, orient="vertical", command=self.context_text.yview)
        context_scrollbar.pack(side="right", fill="y")
        self.context_text.configure(yscrollcommand=context_scrollbar.set)


        set_button = ttk.Button(agents_frame, text="Set Goal and Context",
                        command=lambda: self.set_goal_and_context(self.goal_text.get('1.0', 'end-1c'), self.context_text.get('1.0', 'end-1c')))
        set_button.pack(side="top", padx=5, pady=5)

        self.confirmation_label = ttk.Label(agents_frame, text="", foreground="green")
        self.confirmation_label.pack(side="top", padx=5, pady=5)

        self.agents_treeview = ttk.Treeview(agents_frame)
        self.agents_treeview["columns"] = ("Role", "LLM")
        self.agents_treeview.column("#0", width=200, minwidth=200, anchor="w")
        self.agents_treeview.column("Role", width=200, minwidth=200, anchor="w")
        self.agents_treeview.column("LLM", width=200, minwidth=200, anchor="w")
        self.agents_treeview.heading("#0", text="Agent", anchor="w")
        self.agents_treeview.heading("Role", text="Role", anchor="w")
        self.agents_treeview.heading("LLM", text="LLM", anchor="w")
        self.agents_treeview.pack(side="top", fill="both", expand=True)
        self.agents_treeview.bind("<Double-1>", self.edit_agent_role)

        agents_output_frame = ttk.Frame(agents_frame)
        agents_output_frame.pack(side="top", fill="both", expand=True)
        self.agents_treeview.pack(side="left", fill="both", expand=True)

        self.agent_output_frame = ttk.Frame(agents_output_frame)
        self.agent_output_frame.pack(side="right", fill="both", expand=True)

        self.agent_output_text = tk.Text(self.agent_output_frame, wrap="word")
        self.agent_output_text.pack(side="top", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(self.agent_output_frame, command=self.agent_output_text.yview)
        scrollbar.pack(side="right", fill="y")
        self.agent_output_text.config(yscrollcommand=scrollbar.set)

        self.stdout = sys.stdout
        sys.stdout = TextIOWrapper(self.agent_output_text)

        button_frame = ttk.Frame(agents_frame)
        button_frame.pack(side="bottom", fill="x")

        add_agent_button = ttk.Button(button_frame, text="Add Agent", command=self.add_agent)
        add_agent_button.pack(side="left", padx=5, pady=5)

        create_infra_button = ttk.Button(button_frame, text="Create Agent Infrastructure", command=self.create_agent_infrastructure)
        create_infra_button.pack(side="left", padx=5, pady=5)

        run_agents_button = ttk.Button(button_frame, text="Run Agents", command=self.run_agents)
        run_agents_button.pack(side="left", padx=5, pady=5)

        search_button = ttk.Button(button_frame, text="Search", command=self.open_search_dialog)
        search_button.pack(side="left", padx=5, pady=5)

        custom_instructions_frame = ttk.Frame(agents_frame)
        custom_instructions_frame.pack(side="top", fill="x", padx=5, pady=5)

        custom_instructions_label = ttk.Label(custom_instructions_frame, text="Custom Instructions:")
        custom_instructions_label.pack(side="left")

        custom_instructions_entry = tk.Text(custom_instructions_frame, height=5, wrap="word")
        custom_instructions_entry.pack(side="left", fill="both", expand=True)

        create_refined_blog_button = ttk.Button(button_frame, text="Create Refined Blog", command=self.run_agents)
        create_refined_blog_button.pack(side="left", padx=5, pady=5)

         # Add a frame for the '+' and '-' buttons
        button_frame = ttk.Frame(agents_frame)
        button_frame.pack(side="bottom", fill="x", padx=5, pady=5)

        # Add agent button
        add_button = ttk.Button(button_frame, text="+", width=3, command=self.add_agent)
        add_button.pack(side="left", padx=5)

        # Delete agent button
        delete_button = ttk.Button(button_frame, text="-", width=3, command=self.delete_agent)
        delete_button.pack(side="left", padx=5)

    def create_blog_input_tab(self, blog_input_frame):
        blog_input_text = tk.Text(blog_input_frame, wrap="word")
        blog_input_text.pack(side="top", fill="both", expand=True)

        def set_blog_rough_cut():
            self.blog_rough_cut = blog_input_text.get("1.0", "end-1c")

        set_blog_button = ttk.Button(blog_input_frame, text="Set Blog Rough Cut", command=set_blog_rough_cut)
        set_blog_button.pack(side="bottom", fill="x", padx=5, pady=5)

    def create_refined_blog_tab(self, refined_blog_frame):
        self.refined_blog_text = tk.Text(refined_blog_frame, wrap="word")
        self.refined_blog_text.pack(side="top", fill="both", expand=True)

    def refine_blog(self):
        # Implement the blog refinement process using the agents
        # Update the refined_blog_text with the refined blog content
        pass

    def create_agent_infrastructure(self):
        print("create_agent_infrastructure called")
        goal = self.goal_text.get('1.0', tk.END).strip() 
        context = self.context_text.get('1.0', tk.END).strip()
        
        # goal ="Get a couple experts who can speak about the evolution of European sexuality over the last 500 years on my podcast"
        # context = "I'm a podcaster wanting to interview experts in european sexuality and history of european sexuality"

        if not goal or not context:
            messagebox.showwarning("Missing Goal or Context", "Please provide both the goal and context before creating the agent infrastructure.")
            return

        num_agents, agent_details_list, blog_analysis = generate_agent_details(self.blog_rough_cut, goal, context)
   
        print("Number of agents:", num_agents)
        print("Agent details:", agent_details_list)
        self.agents_treeview.delete(*self.agents_treeview.get_children())
        
        for agent_details in agent_details_list:
            # name = agent_details["title"].split(": ")[-1].strip('"')
            role = agent_details["role"].split(": ")[-1].strip('"')
            backstory = agent_details["backstory"].strip()
            llm_name = llm_GROQ  # You can set a default LLM or provide an option to select one
            self.create_agent(role, llm_name, None, backstory=backstory)

        messagebox.showinfo("Blog Analysis", blog_analysis)
        self.confirmation_label.config(text="Agent infrastructure created successfully.")
            

    def open_search_dialog(self):
        dialog = LargeTextInputDialog(self, title="Search")
        self.wait_window(dialog)
        query = dialog.result
        if query:
            results = process_search_results(query, self.context_text.get('1.0', tk.END).strip(),self.goal_var.get())
            if results:
                self.display_search_results(results)

    def create_search_results_tab(self, search_results_frame):
        self.search_results_text = tk.Text(search_results_frame, wrap="word")
        self.search_results_text.pack(side="top", fill="both", expand=True)

    def display_search_results(self, results):
        self.search_results_text.delete("1.0", "end")
        self.search_results_text.insert("end", results)

    def create_output_tab(self, output_frame):
        self.output_text = tk.Text(output_frame, wrap="word")
        self.output_text.pack(side="top", fill="both", expand=True)

        save_button = ttk.Button(output_frame, text="Save Output", command=self.save_output)
        save_button.pack(side="bottom", fill="x", padx=5, pady=5)

    def set_goal_and_context(self, goal, context):
        self.goal_text.delete('1.0', tk.END)
        self.goal_text.insert(tk.END, goal)
        self.context_text.delete('1.0', tk.END)
        self.context_text.insert(tk.END, context)
        self.confirmation_label.config(text="Goal and context are set.")

    def add_agent(self):
        agent_dialog = tk.Toplevel(self)
        agent_dialog.title("Add Agent")
        agent_dialog.geometry("500x500")  # Adjusted size for the dialog

        # Role field
        role_label = ttk.Label(agent_dialog, text="Role:")
        role_label.pack(pady=5)
        role_text = scrolledtext.ScrolledText(agent_dialog, wrap=tk.WORD, width=50, height=5)
        role_text.pack(pady=5)

        # Backstory field
        backstory_label = ttk.Label(agent_dialog, text="Backstory:")
        backstory_label.pack(pady=5)
        backstory_text = scrolledtext.ScrolledText(agent_dialog, wrap=tk.WORD, width=50, height=10)
        backstory_text.pack(pady=5)

        # LLM selection
        llm_label = ttk.Label(agent_dialog, text="LLM:")
        llm_label.pack(pady=5)
        llm_combobox = ttk.Combobox(agent_dialog, values=list(self.llms.keys()))
        llm_combobox.pack(pady=5)

        button_frame = ttk.Frame(agent_dialog)
        button_frame.pack(pady=5)

        def create_agent_handler():
            role = role_text.get("1.0", tk.END).strip()
            backstory = backstory_text.get("1.0", tk.END).strip()
            llm_key = llm_combobox.get()
            llm = self.llms.get(llm_key, llm_GROQ)  # Default to GROQ if not found

            if not role or not backstory or not llm_key:
                messagebox.showerror("Error", "All fields must be filled")
                return

            agent = self.create_agent(role, llm, agent_dialog, backstory=backstory)
            if agent:
                messagebox.showinfo("Success", f"Agent '{role}' created successfully.")

        create_button = ttk.Button(button_frame, text="Create", command=create_agent_handler)
        create_button.pack(side="left", padx=5)

        cancel_button = ttk.Button(button_frame, text="Cancel", command=agent_dialog.destroy)
        cancel_button.pack(side="left", padx=5)
    
    def delete_agent(self):
        selected_item = self.agents_treeview.selection()
        if not selected_item:
            messagebox.showwarning("No Selection", "Please select an agent to delete.")
            return

        if messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete this agent?"):
            for item in selected_item:
                index = self.agents_treeview.index(item)
                self.agents_treeview.delete(item)
                del self.agents[index]
            messagebox.showinfo("Success", "Agent(s) deleted successfully.")

    def create_agent(self, role, llm, dialog, backstory=None):
        agent = Agent(
            role=role,
            goal=self.goal_text.get('1.0', tk.END).strip(),  # Updated this line
            backstory=backstory,
            verbose=False,
            allow_delegation=False,
            llm=llm,
        )
        self.agent_output_text.see("end")

        try:
            # Use the model name from the LLM object for display in the treeview
            llm_name = llm.model_name if hasattr(llm, 'model_name') else str(llm)
            self.agents_treeview.insert("", "end", text=role, values=(backstory, llm_name))
        except Exception as e:
            print(f"Error occurred while inserting into treeview: {e}")
        self.agents.append(agent)

        if dialog is not None:
            dialog.destroy()
        
        return agent  # Return the created agent
    
    def edit_agent_role(self, event):
        selected_item = self.agents_treeview.focus()
        if selected_item:
            # Get the index of the selected item
            agent_index = self.agents_treeview.index(selected_item)
            agent_role = self.agents_treeview.item(selected_item)["values"][0]

            edit_dialog = tk.Toplevel(self)
            edit_dialog.title("Edit Agent Role")
            edit_dialog.geometry("400x300")

            role_label = ttk.Label(edit_dialog, text="Role:")
            role_label.pack(pady=5)

            role_text = scrolledtext.ScrolledText(edit_dialog, wrap=tk.WORD, width=50, height=10)
            role_text.insert(tk.END, agent_role)
            role_text.pack(pady=5, padx=10, expand=True, fill=tk.BOTH)

            button_frame = ttk.Frame(edit_dialog)
            button_frame.pack(pady=5)

            save_button = ttk.Button(button_frame, text="Save", 
                                     command=lambda: self.save_agent_role(selected_item, role_text.get("1.0", tk.END).strip(), edit_dialog, agent_index))
            save_button.pack(side="left", padx=5)

            cancel_button = ttk.Button(button_frame, text="Cancel", command=edit_dialog.destroy)
            cancel_button.pack(side="left", padx=5)


    def save_agent_role(self, item, new_role, dialog, agent_index):
        # Update the agent's role
        self.agents[int(agent_index)].role = new_role
        
        # Update the treeview
        self.agents_treeview.item(item, values=(new_role,))
        
        dialog.destroy()

    def populate_agents_treeview(self):
        for i, agent in enumerate(self.agents):
            self.agents_treeview.insert("", "end", text=f"Agent {i+1}", values=(agent.role,), tags=(str(i),))

    def create_agent_output_tab(self, agent_output_frame):
        self.agent_output_text = tk.Text(agent_output_frame, wrap="word")
        self.agent_output_text.pack(side="top", fill="both", expand=True)

    def update_agent_output_text(self, text):
        self.agent_output_text.insert("end", text)
        self.agent_output_text.see("end")

    def run_agents(self):
        self.output_text.delete("1.0", "end")
        self.agent_output_text.delete("1.0", "end")

        tasks = []
        for agent in self.agents:
            try:
                task = Task(
                    description=f"Refine the rough cut blog based on your role: {agent.role}",
                    agent=agent,
                    expected_output=f"Refined blog content from {agent.role}"
                )
                tasks.append(task)
            except Exception as e:
                print(f"Error occurred while creating tasks: {e}")  

        crew = Crew(
            agents=self.agents,
            tasks=tasks,
            verbose=1,
            process=Process.sequential
        )
        final_output = crew.kickoff()

        self.refined_blog_text.delete("1.0", "end")
        self.refined_blog_text.insert("end", final_output)
        sys.stdout = self.stdout
    
    def save_output(self):
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

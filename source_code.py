import sqlite3
import tkinter as tk
from tkinter import ttk, scrolledtext
from datetime import datetime
import re

class DatabaseManager:
    def __init__(self):
        self.conn = sqlite3.connect('company.db')
        self.cursor = self.conn.cursor()
        self.setup_database()

    def setup_database(self):
        # Create Employees table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS Employees (
            ID INTEGER PRIMARY KEY,
            Name TEXT NOT NULL,
            Department TEXT NOT NULL,
            Salary INTEGER NOT NULL,
            Hire_Date DATE NOT NULL
        )
        ''')

        # Create Departments table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS Departments (
            ID INTEGER PRIMARY KEY,
            Name TEXT NOT NULL,
            Manager TEXT NOT NULL
        )
        ''')

        # Insert sample data if tables are empty
        self.cursor.execute('SELECT COUNT(*) FROM Employees')
        if self.cursor.fetchone()[0] == 0:
            employees_data = [
                (1, 'Alice', 'Sales', 50000, '2021-01-15'),
                (2, 'Bob', 'Engineering', 70000, '2020-06-10'),
                (3, 'Charlie', 'Marketing', 60000, '2022-03-20')
            ]
            self.cursor.executemany('INSERT INTO Employees VALUES (?,?,?,?,?)', employees_data)

            departments_data = [
                (1, 'Sales', 'Alice'),
                (2, 'Engineering', 'Bob'),
                (3, 'Marketing', 'Charlie')
            ]
            self.cursor.executemany('INSERT INTO Departments VALUES (?,?,?)', departments_data)

        self.conn.commit()

class QueryHandler:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def parse_query(self, query):
        query = query.lower().strip()
        
        try:
            if "show me all employees in" in query or "list all employees in" in query:
                department = re.search(r'in the (\w+) department', query)
                if department:
                    sql = f"""
                    SELECT Name, Department, Salary, Hire_Date 
                    FROM Employees 
                    WHERE LOWER(Department) = LOWER('{department.group(1)}')
                    """
                    return self.execute_query(sql)

            elif "who is the manager of" in query:
                department = re.search(r'of the (\w+) department', query)
                if department:
                    sql = f"""
                    SELECT Manager 
                    FROM Departments 
                    WHERE LOWER(Name) = LOWER('{department.group(1)}')
                    """
                    return self.execute_query(sql)

            elif "list all employees hired after" in query:
                date_match = re.search(r'hired after (\d{4}-\d{2}-\d{2})', query)
                if date_match:
                    sql = f"""
                    SELECT Name, Department, Hire_Date 
                    FROM Employees 
                    WHERE Hire_Date > '{date_match.group(1)}'
                    """
                    return self.execute_query(sql)

            elif "total salary expense for" in query:
                department = re.search(r'for the (\w+) department', query)
                if department:
                    sql = f"""
                    SELECT SUM(Salary) as Total_Salary 
                    FROM Employees 
                    WHERE LOWER(Department) = LOWER('{department.group(1)}')
                    """
                    return self.execute_query(sql)

            return "I don't understand that query. Please try one of the example queries shown above."

        except Exception as e:
            return f"Error processing query: {str(e)}"

    def execute_query(self, sql):
        try:
            self.db_manager.cursor.execute(sql)
            results = self.db_manager.cursor.fetchall()
            if not results:
                return "No results found."

            # Get column names
            columns = [description[0] for description in self.db_manager.cursor.description]
            
            # Format results
            output = []
            for row in results:
                formatted_row = []
                for col, val in zip(columns, row):
                    formatted_col = col.replace('_', ' ').title()
                    formatted_row.append(f"{formatted_col}: {val}")
                output.append(', '.join(formatted_row))
            
            return '\n'.join(output)

        except sqlite3.Error as e:
            return f"Database error: {str(e)}"

class ChatAssistant:
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.query_handler = QueryHandler(self.db_manager)
        
        # Create main window
        self.root = tk.Tk()
        self.root.title("SQLite Database Chat Assistant")
        self.root.geometry("800x600")
        
        self.create_widgets()

    def create_widgets(self):
        # Example queries label
        examples = tk.Label(self.root, text="Example Queries:", font=('Arial', 12, 'bold'))
        examples.pack(pady=10)

        example_queries = [
            "Show me all employees in the Sales department.",
            "Who is the manager of the Engineering department?",
            "List all employees hired after 2021-01-01",
            "What is the total salary expense for the Marketing department?"
        ]

        for query in example_queries:
            example = tk.Label(self.root, text=f"• {query}", font=('Arial', 10, 'italic'))
            example.pack()

        # Query input
        self.query_input = ttk.Entry(self.root, width=70)
        self.query_input.pack(pady=20)
        self.query_input.bind('<Return>', lambda e: self.process_query())

        # Submit button
        submit_btn = ttk.Button(self.root, text="Send Query", command=self.process_query)
        submit_btn.pack()

        # Response area
        self.response_area = scrolledtext.ScrolledText(self.root, width=70, height=20)
        self.response_area.pack(pady=20)

    def process_query(self):
        query = self.query_input.get()
        if query:
            response = self.query_handler.parse_query(query)
            self.response_area.delete(1.0, tk.END)
            self.response_area.insert(tk.END, response)
            self.query_input.delete(0, tk.END)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = ChatAssistant()
    app.run()

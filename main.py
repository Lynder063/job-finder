import customtkinter as ctk
from tkinter import ttk, messagebox
import requests
from bs4 import BeautifulSoup
import json
import webbrowser

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

def scrape_jobstack():
    url = "https://www.jobstack.it/it-jobs?isDetail=1&leveljunior=1&educationhigh=1&educationundergraduate=1&offsite=1"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'lxml')

    jobs = []
    job_list = soup.select('.jobposts-list .jobposts-item')
    
    for job in job_list:
        title = job.select_one('h3').text.strip()
        link = "https://www.jobstack.it" + job.select_one('a')['href']
        jobs.append({"title": title, "link": link, "source": "JobStack"})
    
    return jobs

def scrape_startupjobs():
    url = "https://www.startupjobs.cz/nabidky/vyvoj/front-end-koder?seniorita=junior&forma-spoluprace=remote&lokalita=ChIJi3lwCZyTC0cRkEAWZg-vAAQ"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'lxml')

    jobs = []
    job_container = soup.select_one('div.max-md\:bleed-container.flex.flex-col')
    if job_container:
        for job_link in job_container.select('a'):
            title = job_link.select_one('h5')
            if title:
                title = title.text.strip()
                link = job_link['href']
                if not link.startswith('http'):
                    link = 'https://www.startupjobs.cz' + link
                jobs.append({"title": title, "link": link, "source": "StartupJobs"})
    return jobs

class JobScraperApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Modern Job Scraper")
        self.geometry("900x600")

        self.jobs = []
        self.applied_jobs = self.load_applied_jobs()

        self.create_widgets()

    def create_widgets(self):
        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.pack(side="left", fill="y", padx=0, pady=0)

        self.logo_label = ctk.CTkLabel(self.sidebar, text="Job Scraper", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.pack(padx=20, pady=20)

        self.scrape_button = ctk.CTkButton(self.sidebar, text="Scrape Jobs", command=self.scrape_jobs)
        self.scrape_button.pack(padx=20, pady=10)

        self.mark_applied_button = ctk.CTkButton(self.sidebar, text="Mark as Applied", command=self.mark_as_applied)
        self.mark_applied_button.pack(padx=20, pady=10)

        # Main content area
        self.main_content = ctk.CTkFrame(self)
        self.main_content.pack(side="right", fill="both", expand=True, padx=20, pady=20)

        # Treeview
        self.tree = ttk.Treeview(self.main_content, columns=('Title', 'Source', 'Applied'), show='headings')
        self.tree.heading('Title', text='Title')
        self.tree.heading('Source', text='Source')
        self.tree.heading('Applied', text='Applied')
        self.tree.column('Title', width=400)
        self.tree.column('Source', width=100)
        self.tree.column('Applied', width=100)
        self.tree.pack(fill="both", expand=True)

        self.tree.bind('<Double-1>', self.on_double_click)

        # Style the Treeview
        style = ttk.Style(self)
        style.theme_use("default")
        style.configure("Treeview", background="#2a2d2e", foreground="white", rowheight=25, fieldbackground="#343638")
        style.map('Treeview', background=[('selected', '#22559b')])
        style.configure("Treeview.Heading", background="#565b5e", foreground="white", relief="flat")
        style.map("Treeview.Heading", background=[('active', '#3484F0')])

    def scrape_jobs(self):
        self.jobs = scrape_jobstack() + scrape_startupjobs()
        self.update_treeview()

    def update_treeview(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        
        for job in self.jobs:
            applied = "Yes" if job['link'] in self.applied_jobs else "No"
            self.tree.insert('', 'end', values=(job['title'], job['source'], applied))

    def on_double_click(self, event):
        item = self.tree.selection()[0]
        job_title = self.tree.item(item, "values")[0]
        job_link = next(job['link'] for job in self.jobs if job['title'] == job_title)
        webbrowser.open(job_link)

    def mark_as_applied(self):
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("No Selection", "Please select a job to mark as applied.")
            return

        for item in selected_items:
            job_title = self.tree.item(item, "values")[0]
            job = next(job for job in self.jobs if job['title'] == job_title)
            self.applied_jobs[job['link']] = True

        self.save_applied_jobs()
        self.update_treeview()

    def load_applied_jobs(self):
        try:
            with open('applied_jobs.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def save_applied_jobs(self):
        with open('applied_jobs.json', 'w') as f:
            json.dump(self.applied_jobs, f)

if __name__ == "__main__":
    app = JobScraperApp()
    app.mainloop()
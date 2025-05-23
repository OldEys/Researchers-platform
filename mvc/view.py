import tkinter as tk
import customtkinter as ctk
from PIL import Image
from io import BytesIO
import requests
from tkcalendar import Calendar
from tkcalendar import DateEntry
from tkinter import filedialog #pentru salvarea sau incarcarea de fisiere
import os
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")
from datetime import datetime
import datetime
import utils
class LoginView:
    def __init__(self, root):
        self.root = root
        self.root.title("Researcher Platform")
        self.controller = None
        self.image_path = None
        self.current_frame = None
        self.build_ui()
    def pack(self, *args, **kwargs):
        return self.mainFrame.pack(*args, **kwargs)
    #construim metodele de pack pentru a le folosi pe toata clasa
    def pack_forget(self, *args, **kwargs):
        return self.mainFrame.pack_forget(*args, **kwargs)
    def build_ui(self):

        self.root.configure(fg_color=("#f2f2f2", "#1a1a1a"))

        self.mainFrame = ctk.CTkFrame(self.root)
        self.mainFrame.pack(fill="both", expand=True, padx=10, pady=10)

        self.mainFrame.grid_columnconfigure(0, weight=1)
        self.mainFrame.grid_columnconfigure(1, weight=1)
        self.mainFrame.grid_rowconfigure(0, weight=1)

        self.leftFrame = ctk.CTkFrame(self.mainFrame)
        self.leftFrame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))

        loginImageUrl = "https://researchersblob.blob.core.windows.net/filesblob/login_image2.jpg"
        #imaginea din login
        try:
            response = requests.get(loginImageUrl)
            img_data = Image.open(BytesIO(response.content)).resize((500, 600))
            self.loginImage = ctk.CTkImage(light_image=img_data, dark_image=img_data, size=(500, 600))
            image_frame = ctk.CTkFrame(self.leftFrame, corner_radius=30)
            image_frame.pack(fill="both", expand=True, padx=10, pady=10)

            loginImageLabel = ctk.CTkLabel(image_frame, image=self.loginImage, text="")
            loginImageLabel.pack(fill="both", expand=True)
        except Exception as e:
            print(f"Error loading image: {e}")
            fallback_label = ctk.CTkLabel(self.leftFrame, text="Welcome to Research Platform",
                                          font=ctk.CTkFont(size=20, weight="bold"))
            fallback_label.pack(fill="both", expand=True)

        self.rightFrame = ctk.CTkFrame(self.mainFrame)
        self.rightFrame.grid(row=0, column=1, sticky="nsew", padx=(5, 0))

        self.frames = {}

        self.create_login_frame()

        self.create_register_frame()

        self.show_frame("login")
        #alternarea intre frameul de login si de register

    def create_login_frame(self):
        #crearea frameului de login

        login_frame = ctk.CTkFrame(self.rightFrame)

        login_content = ctk.CTkFrame(login_frame, fg_color="transparent")
        login_content.pack(fill="both", expand=True, padx=40, pady=40)

        heading = ctk.CTkLabel(login_content, text="Sign In",
                               font=ctk.CTkFont(size=24, weight="bold"))
        heading.pack(pady=(0, 20))

        name_label = ctk.CTkLabel(login_content, text="Username:",
                                  anchor="w")
        name_label.pack(fill="x")
        self.name_entry_login = ctk.CTkEntry(login_content, height=32, placeholder_text="Enter your username")
        self.name_entry_login.pack(pady=(5, 15), fill="x")

        pw_label = ctk.CTkLabel(login_content, text="Password:",
                                anchor="w")
        pw_label.pack(fill="x")
        self.pw_entry_login = ctk.CTkEntry(login_content, height=32, show="*", placeholder_text="Enter your password")
        self.pw_entry_login.pack(pady=(5, 20), fill="x")

        buttons_frame = ctk.CTkFrame(login_content, fg_color="transparent")
        buttons_frame.pack(fill="x")
        buttons_frame.grid_columnconfigure((0,1), weight=1)

        self.login_button = ctk.CTkButton(buttons_frame, text="Login",
                                     height=35, fg_color="#3a7ebf", hover_color="#2b5e8c")
        self.login_button.grid(row=0, column=0, sticky="nsew",padx=(0, 5))

        register_button = ctk.CTkButton(buttons_frame, text="Register",
                                        height=35, fg_color="#555555", hover_color="#333333",
                                        command=lambda: self.show_frame("register"))

        register_button.grid(row=0, column=1, sticky="nsew",padx=(5, 0))

        self.frames["login"] = login_frame

    def create_register_frame(self):
        #crearea frameului de register

        register_frame = ctk.CTkFrame(self.rightFrame)

        scrollable_frame = ctk.CTkScrollableFrame(register_frame, fg_color="transparent")
        scrollable_frame.pack(fill="both", expand=True, padx=40, pady=40)

        heading = ctk.CTkLabel(scrollable_frame, text="Register Account",
                               font=ctk.CTkFont(size=24, weight="bold"))
        heading.pack(pady=(0, 20))

        name_label = ctk.CTkLabel(scrollable_frame, text="Username:", anchor="w")
        name_label.pack(fill="x")
        self.name_entry = ctk.CTkEntry(scrollable_frame, height=32, placeholder_text="Enter your username")
        self.name_entry.pack(pady=(5, 15), fill="x")

        pw_label = ctk.CTkLabel(scrollable_frame, text="Password:", anchor="w")
        pw_label.pack(fill="x")
        self.pw_entry = ctk.CTkEntry(scrollable_frame, height=32, show="*", placeholder_text="Enter your password")
        self.pw_entry.pack(pady=(5, 15), fill="x")

        pw_confirm_label = ctk.CTkLabel(scrollable_frame, text="Confirm Password:", anchor="w")
        pw_confirm_label.pack(fill="x")
        self.pw_confirm_entry = ctk.CTkEntry(scrollable_frame, height=32, show="*",
                                             placeholder_text="Confirm your password")
        self.pw_confirm_entry.pack(pady=(5, 15), fill="x")

        email_label = ctk.CTkLabel(scrollable_frame, text="Email:", anchor="w")
        email_label.pack(fill="x")
        self.email_entry = ctk.CTkEntry(scrollable_frame, height=32, placeholder_text="Enter your email")
        self.email_entry.pack(pady=(5, 15), fill="x")

        inst_label = ctk.CTkLabel(scrollable_frame, text="Institution:", anchor="w")
        inst_label.pack(fill="x")
        self.inst_entry = ctk.CTkEntry(scrollable_frame, height=32, placeholder_text="Enter your institution")
        self.inst_entry.pack(pady=(5, 15), fill="x")

        field_label = ctk.CTkLabel(scrollable_frame, text="Field of Research:", anchor="w")
        field_label.pack(fill="x")
        self.field_entry = ctk.CTkEntry(scrollable_frame, height=32, placeholder_text="Enter your field of research")
        self.field_entry.pack(pady=(5, 15), fill="x")

        bio_label = ctk.CTkLabel(scrollable_frame, text="Biography:", anchor="w")
        bio_label.pack(fill="x")

        bio_frame = ctk.CTkFrame(scrollable_frame, fg_color=("#f0f0f0", "#333333"))
        bio_frame.pack(pady=(5, 15), fill="x")

        self.bio_entry = ctk.CTkTextbox(bio_frame, height=100)
        self.bio_entry.pack(fill="both", expand=True, padx=1, pady=1)

        date_label = ctk.CTkLabel(scrollable_frame, text="Start Date:", anchor="w")
        date_label.pack(fill="x")

        calendar_frame = ctk.CTkFrame(scrollable_frame, fg_color=("#f0f0f0", "#333333"))
        calendar_frame.pack(pady=(5, 15), fill="x")

        self.calendar = Calendar(calendar_frame, selectmode="day", year=2025, month=5, day=1,
                                 background="#333333", foreground="white"
                                 )
        self.calendar.pack(pady=10, padx=10, fill="x")

        image_label = ctk.CTkLabel(scrollable_frame, text="Profile Image:", anchor="w")
        image_label.pack(fill="x", pady=(10, 5))

        self.profile_image_label = ctk.CTkLabel(scrollable_frame, text="No image selected")
        self.profile_image_label.pack(pady=(0, 5))

        self.select_image_btn = ctk.CTkButton(
            scrollable_frame,
            text="Choose Profile Image",
            height=32,
            fg_color="#555555", hover_color="#333333",
            command=self.browse_image
        )
        self.select_image_btn.pack(pady=(0, 15))

        buttons_frame = ctk.CTkFrame(scrollable_frame, fg_color="transparent")
        buttons_frame.pack(fill="x", pady=(10, 0))

        buttons_frame.grid_columnconfigure((0, 1), weight=1)




        back_button = ctk.CTkButton(
            buttons_frame,
            text="Back to Login",
            height=35,
            fg_color="#555555",
            hover_color="#333333",
            command=lambda: self.show_frame("login")
        )
        back_button.grid(row=0, column=0, padx=(0, 5), sticky="ew")

        self.register_button = ctk.CTkButton(
            buttons_frame,
            text="Create Account",
            height=35,
            fg_color="#2d9a47",
            hover_color="#1f7a32"
        )
        self.register_button.grid(row=0, column=1, padx=(5, 0), sticky="ew")

        self.frames["register"] = register_frame

    def show_frame(self, frame_name):
        if self.current_frame:
            self.current_frame.pack_forget()
        #frameul curent il distruge si il inlocuieste cu cel nou caruia ii da pack
        frame = self.frames.get(frame_name)
        if frame:
            frame.pack(fill="both", expand=True)
            self.current_frame = frame
    def clearLogin(self):
        self.name_entry_login.delete(0, tk.END)
        self.pw_entry_login.delete(0, tk.END)
    def clearRegister(self):
        pass
        self.name_entry.delete(0, tk.END)
        self.pw_entry.delete(0, tk.END)
        self.email_entry.delete(0, tk.END)
        self.pw_confirm_entry.delete(0, tk.END)
        self.inst_entry.delete(0, tk.END)
        self.field_entry.delete(0, tk.END)
        self.bio_entry.delete(1.0, tk.END)
        self.profile_image_label.configure(text="No image selected",image=None)
    def browse_image(self):
        #pentru alegerea imaginii de profil
        self.image_path = filedialog.askopenfilename(
            title="Select Profile Image",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.gif *.webp" )]
        )
        if self.image_path:
            self.profile_image_label.configure(text=f"Selected: {self.image_path.split('/')[-1]}")
            try:
                img = Image.open(self.image_path)
                img.thumbnail((100, 100))
                photo = ctk.CTkImage(light_image=img, dark_image=img, size=(100, 100))
                self.profile_image_label.configure(image=photo, text="")
            except Exception as e:
                print(f"Error loading thumbnail: {e}")
    def register_get_data(self):
        #getter pentru campurile din register
        if not self.controller:
            self.show_frame("login")
            return
        else:
            registration_data = {
                "name": self.name_entry.get(),
                "email": self.email_entry.get(),
                "password": self.pw_entry.get(),
                "institution": self.inst_entry.get(),
                "field_of_research": self.field_entry.get(),
                "biography": self.bio_entry.get("1.0", tk.END),
                "researcher_start_date": datetime.strptime(self.calendar.get_date(), "%m/%d/%y").strftime("%Y-%m-%d"),
                "image_path": self.image_path
            }
            return registration_data
    def login_get_data(self):
        #getter pentru campurile din login

        if not self.controller:
            return
        else:
            login_data = {
                "name": self.name_entry_login.get(),
                "password": self.pw_entry_login.get(),
            }
            return login_data
    def set_controller(self, controller:dict):
        self.controller = controller
        self.register_button.configure(command=self.controller['register'].register)
        self.login_button.configure(command=self.controller['login'].login)
class MainAppView(ctk.CTkFrame):
    def __init__(self,root,username):
        super().__init__(root)
        self.username = username
        self.current_view=None
        self.sections={}

        self.controller=None

        self.section_names=["Dashboard","AddProject","UserSearch","Statistics","Settings","Logout"]
        #numele tuturor taburilor din mainapp pe care le schimbam
        self.build_ui()
        self.switch_section("Dashboard")
    def build_ui(self):
        self.pack(fill="both", expand=True)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.sidebar=ctk.CTkFrame(self,width=200)
        self.sidebar.grid(row=0, column=0, sticky="ns")

        title=ctk.CTkLabel(self.sidebar,text="Researcher Hub",font=ctk.CTkFont(size=18,weight="bold"))
        title.pack(pady=(20,10))

        self.nav_buttons={}

        for name in self.section_names:
            btn=ctk.CTkButton(self.sidebar,text=name,width=150,command=lambda n=name:self.switch_section(n))
            btn.pack(pady=5)
            self.nav_buttons[name] = btn
            #toate butoanele din bara de navigare
        self.content_frame=ctk.CTkFrame(self)
        self.content_frame.grid(row=0,column=1,sticky="nsew",padx=10,pady=10)
        self.create_sections()
    def create_sections(self):
        #creeaza toate sectiunile iar in functie de sectiunea pe care o schimbam se va afisa
        #viewul respectiv
        self.sections["Dashboard"]=DashboardView(self.content_frame,self.username)
        self.sections["AddProject"]=AddProjectView(self.content_frame)
        self.sections["ProjectPage"]=ProjectPageView(self.content_frame)
        self.sections["UserSearch"]=UserSearchView(self.content_frame)
        self.sections["Statistics"]=StatisticsView(self.content_frame)
        self.sections["Settings"]=SettingsView(self.content_frame)
        self.sections["Logout"] = self.create_label_section("Te-ai delogat.")
    def switch_section(self,name):
        if name=="Logout":
            if self.controller:
                self.controller.logout()
            return
        if self.current_view:
            self.current_view.pack_forget()
        #distrugem viewul anterior si il inlocuim apoi ii dam pack dupa care ii atribuim controllerul
        self.current_view=self.sections[name]
        self.current_view.pack(in_=self.content_frame,fill="both", expand=True)
        if self.controller:
            self.controller.on_section_switched(name)
    def create_label_section(self,text):
        frame=ctk.CTkFrame(self.content_frame)
        label=ctk.CTkLabel(frame,text=text,font=ctk.CTkFont(size=18,weight="bold"))
        label.pack(pady=(20,10))
        return frame
    def set_controller(self, controller):
        self.controller = controller
        for name, btn in self.nav_buttons.items():
            if name == "Logout":
                btn.configure(command=self.controller.logout)
            else:
                btn.configure(command=lambda n=name: self.switch_section(n))
        #leaga toate butoanele
        if hasattr(self.sections["Dashboard"], 'set_on_open_project'):
            self.sections["Dashboard"].set_on_open_project(
                controller.on_open_project
            )
        #daca deschidem un proiect se apeleaza metoda din on_open_project din controller
class DashboardView(ctk.CTkFrame):
    def __init__(self,root,username):
        super().__init__(root)
        self.username=username
        self.controller=None
        self.build_ui()
        self._on_open_project=lambda p:None
        #functia trimisa de la main app pentru deschideerea proiectului e nula momentan
    def build_ui(self):
        self.info_title=ctk.CTkLabel(self,width=200,text="User profile",font=ctk.CTkFont(size=20, weight="bold"))
        self.info_title.pack(pady=(10,5))

        self.info_container=ctk.CTkScrollableFrame(self)
        self.info_container.pack(fill="both", expand=True,pady=(10,10))
        self.info_container.grid_columnconfigure((0,1), weight=1)
        self.list_title=ctk.CTkLabel(self,text="Your Projects",font=ctk.CTkFont(size=18, weight="bold"))
        self.list_title.pack(pady=(10,5))

        self.list_container=ctk.CTkScrollableFrame(self)
        self.list_container.pack(fill="both", expand=True,pady=(10,10))
    def display_information(self,info,profile_image=None):
        #arata informatiile in containerul coresp
        profile_pic_frame = ctk.CTkFrame(self.info_container, width=120, height=120, corner_radius=100)
        profile_pic_frame.grid(row=0, column=0, padx=20, pady=10)
        profile_pic_frame.grid_propagate(False)

        if profile_image:
            profile_pic_label = ctk.CTkLabel(profile_pic_frame, image=profile_image, text="")
            profile_pic_label.pack(expand=True)


        info_frame = ctk.CTkFrame(self.info_container)
        info_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        info_frame.grid_propagate(False)
        #luam datele din model si afisam o parte din ele construind cate un frame,labelsi value
        for key, value in info[0].items():
            if (key == "password_hash" or key == "profile_picture_url"):
                continue
            row = ctk.CTkFrame(info_frame)
            row.pack(fill="x", pady=2)

            label = ctk.CTkLabel(row, text=f"{key}:", text_color="#888")
            label.pack(side="left", padx=(0, 5))

            value_label = ctk.CTkLabel(row, text=str(value), font=ctk.CTkFont(weight="bold"))
            value_label.pack(side="left")
        self.delete_account_button = ctk.CTkButton(
            info_frame,
            text="Delete Account",
            fg_color="red",
            hover_color="#cc0000",
        )
        self.delete_account_button.pack(pady=(0, 10))

    def display_projects(self, projects):
        #la fel ca la display inforamtion
        for widget in self.list_container.winfo_children():
            widget.destroy()
        if not projects:
            no_proj_label=ctk.CTkLabel(self.list_container,text="You don't have any projects yet")
            no_proj_label.pack(pady=(10, 5))
            return
        for project in projects:
            project_frame=ctk.CTkFrame(self.list_container)
            project_frame.pack(fill="both", padx=10,pady=10)


            title_label=ctk.CTkLabel(project_frame,text=project["title"],font=ctk.CTkFont(weight="bold",size=20),cursor="hand2")
            title_label.grid(row=0,column=0,sticky="w",columnspan=2,pady=(0,5),padx=(20,0))
            title_label.bind(
                "<Button-1>",
                lambda e, p=project: self._on_open_project(p)
            )#apeleaza functia de intrare pe pagina proiectului

            domain_label=ctk.CTkLabel(project_frame,text="Domain:",text_color="#888")
            domain_label.grid(row=1,column=0,sticky="w",pady=(0,10),padx=(5,0))
            domain_value=ctk.CTkLabel(project_frame,text=project["domain"])
            domain_value.grid(row=1,column=1,sticky="w")

            start_label=ctk.CTkLabel(project_frame,text="Start Date:",text_color="#888")
            start_label.grid(row=2,column=0,sticky="w",pady=(0,10),padx=(5,0))
            start_value=ctk.CTkLabel(project_frame,text=project["start_date"])
            start_value.grid(row=2,column=1,sticky="w")

            desc_label=ctk.CTkLabel(project_frame,text="Description:",text_color="#888")
            desc_label.grid(row=3,column=0,sticky="w",pady=(0,10),padx=(5,0))
            desc_value=ctk.CTkTextbox(project_frame)
            desc_value.insert("1.0",str(project["description"]))
            desc_value.configure(state="disabled")
            desc_value.grid(row=3,column=1,sticky="w")
            delete_btn = ctk.CTkButton(project_frame, text="Delete Project", fg_color="red", width=80,hover_color="#C31F1F",
                                       command=lambda p=project: self.controller.delete_project(p))
            delete_btn.grid(row=0, column=2, padx=10, sticky="e")

            project_frame.grid_columnconfigure(1,weight=1)

    def set_on_open_project(self, callback):
        self._on_open_project = callback
        #cand se apeleaza _on_open_project de fapt se apeleaza callbackul
    def set_controller(self,controller):
        self.controller = controller
        self.delete_account_button.configure(command=self.controller.delete_account)
class ProjectPageView(ctk.CTkFrame):
    def __init__(self, root):
        super().__init__(root)
        self.controller=None
        self.build_ui()

    def build_ui(self):
        self.post_frames = {}
        self.title_label = ctk.CTkLabel(self, text="Project Page", font=ctk.CTkFont(weight="bold", size=22))
        self.title_label.pack(pady=(10, 10))

        self.info_container = ctk.CTkScrollableFrame(self)
        self.info_container.pack(fill="both", expand=True, pady=(10, 10))

        self.file_container = ctk.CTkScrollableFrame(self)
        self.file_container.pack(fill="both", expand=True, pady=(10, 10))

        self.posts_container = ctk.CTkScrollableFrame(self)
        self.posts_container.pack(fill="both", expand=True, pady=(10, 10))

        self.post_frames = {}
        self.comment_input_frames = {}
        #memoram frameurile cu postari si comentarii pentru a le accesa butoanele

    def display_project(self, project):
        for widget in self.info_container.winfo_children():
            widget.destroy()
        title_frame = ctk.CTkFrame(self.info_container)
        title_frame.pack(fill="both", expand=True, pady=(10, 10), padx=(20, 0))
        title_label = ctk.CTkLabel(title_frame, text="Title:", font=ctk.CTkFont(weight="bold", size=20),
                                   text_color="#888")
        title_label.pack(side="left", padx=(5, 0))
        title_value = ctk.CTkLabel(title_frame, text=project["title"], font=ctk.CTkFont(weight="bold", size=20))
        title_value.pack(side="left", padx=(5, 0))

        domain_frame = ctk.CTkFrame(self.info_container)
        domain_frame.pack(fill="both", expand=True, pady=(10, 10))
        domain_label = ctk.CTkLabel(domain_frame, text="Domain:", text_color="#888")
        domain_label.pack(side="left", padx=5)
        domain_value = ctk.CTkLabel(domain_frame, text=project["domain"])
        domain_value.pack(side="left", padx=5)

        start_date_frame = ctk.CTkFrame(self.info_container)
        start_date_frame.pack(fill="both", expand=True, pady=(10, 10))
        start_date_label = ctk.CTkLabel(start_date_frame, text="Start Date:", text_color="#888")
        start_date_label.pack(side="left", padx=5)
        start_date_value = ctk.CTkLabel(start_date_frame, text=project["start_date"])
        start_date_value.pack(side="left", padx=5)

        desc_frame = ctk.CTkFrame(self.info_container)
        desc_frame.pack(fill="both", expand=True, pady=(10, 10))
        desc_label = ctk.CTkLabel(desc_frame, text="Description:", text_color="#888")
        desc_label.pack(side="left", padx=5)
        desc_value = ctk.CTkTextbox(desc_frame)
        desc_value.insert("1.0", str(project["description"]))
        desc_value.configure(state="disabled")
        desc_value.pack(side="left", padx=5)

        self.back_button = ctk.CTkButton(self.info_container, text="Back to Dashboard")
        self.back_button.pack(pady=(0, 20), padx=20, anchor=tk.W)

    def display_files(self, files):
        for widget in self.file_container.winfo_children():
            widget.destroy()
        if not files:
            no_files = ctk.CTkLabel(self.file_container, text="No Files", font=ctk.CTkFont(weight="bold", size=20))
            no_files.pack()
            return
        for file in files:
            row_frame = ctk.CTkFrame(self.file_container)
            row_frame.pack(fill="x", pady=10)

            name_value = ctk.CTkLabel(row_frame, text=file["file_name"])
            name_value.pack(side="left", padx=(0, 5))

            type_value = ctk.CTkLabel(row_frame, text=file["file_type"])
            type_value.pack(side="left", padx=(0, 15))

            size_value = ctk.CTkLabel(row_frame, text=f"{file['file_size']}mb")
            size_value.pack(side="left", padx=(0, 5))
            download_button = ctk.CTkButton(row_frame, text="Download",
                                                        command=lambda blob_name=f"{file['file_name']}.{file['file_type']}": self.controller.download_file(
                                                        blob_name,file))
            download_button.pack(side="right", padx=5)

    def display_comments_and_posts(self, posts, comments):
        for widget in self.posts_container.winfo_children():
            widget.destroy()

        self.post_frames = {}
        self.comment_input_frames = {}
        self.buttons_frame=ctk.CTkFrame(self.posts_container)
        self.buttons_frame.pack(fill="x", expand=True, padx=(5, 0))
        self.refresh_btn = ctk.CTkButton(
            self.buttons_frame,
            text="Refresh"
        )
        self.refresh_btn.pack(side="left",pady=10)

        if not posts:
            no_posts = ctk.CTkLabel(self.posts_container, text="No posts available.")
            no_posts.pack(pady=10)

        self.add_post_button = ctk.CTkButton(self.buttons_frame, text="Add Post")
        self.add_post_button.pack(side="left",pady=10)

        comments_by_post = {}
        for comment in comments:
            comments_by_post.setdefault(comment["post_id"], []).append(comment)
        #grupeaza comentariile dupa posturi
        for post in posts:
            self._create_post_frame(post, comments_by_post.get(post["post_id"], []))

    def _create_post_frame(self, post, comments):
        post_id = post["post_id"]
        post_frame = ctk.CTkFrame(self.posts_container)
        post_frame.pack(fill="x", pady=15, padx=20)
        self.post_frames[post_id] = post_frame

        author_label = ctk.CTkLabel(post_frame, text=f"{post['name']} - {post['created_at']}",
                                    font=ctk.CTkFont(weight="bold", size=14))
        author_label.pack(anchor="w", pady=(5, 0))

        title_label = ctk.CTkLabel(post_frame, text=post["title"],
                                   font=ctk.CTkFont(weight="bold", size=16))
        title_label.pack(anchor="w", pady=(5, 0))

        content_label = ctk.CTkLabel(post_frame, text=post["body"], wraplength=700, justify="left",
                                     font=ctk.CTkFont(size=13))
        content_label.pack(anchor="w", pady=(5, 10))



        if comments:
            comments_section = ctk.CTkFrame(post_frame)
            comments_section.pack(fill="x", pady=(5, 0))
            post_frame.comments_section = comments_section
            for c in comments:
                self._create_comment_frame(comments_section, c)

        add_comment_btn = ctk.CTkButton(
            post_frame,
            text="Add Comment",
            command=lambda pid=post_id: self.controller.open_comment_dialog(pid)
        )
        add_comment_btn.pack(anchor="w", padx=20, pady=(5, 10))
    def _create_comment_frame(self, parent, comment):
        comment_frame = ctk.CTkFrame(parent, fg_color="#2a2a2a")
        comment_frame.pack(fill="x", padx=20, pady=3)

        c_author = ctk.CTkLabel(comment_frame, text=f"{comment['name']} - {comment['created_at']}",
                                font=ctk.CTkFont(size=11, weight="bold"), text_color="#ccc")
        c_author.pack(anchor="w", padx=5)

        c_text = ctk.CTkLabel(comment_frame, text=comment["body"], wraplength=650, justify="left",
                              font=ctk.CTkFont(size=12))
        c_text.pack(anchor="w", padx=10, pady=(0, 5))

        return comment_frame

    def add_single_comment(self, post_id, comment_data):
        post_frame = self.post_frames.get(post_id)
        if not post_frame or not hasattr(post_frame, 'comments_section'):
            return

        self._create_comment_frame(post_frame.comments_section, comment_data)

    def add_single_post(self, post_data):
        if not hasattr(self, 'refresh_btn') or not self.refresh_btn.winfo_exists():
            self.refresh_btn = ctk.CTkButton(self.buttons_frame, text="Refresh")
            self.refresh_btn.pack(pady=10)
            self.refresh_btn.configure(command=self.controller.refresh_comments)

        if not hasattr(self, 'add_post_button') or not self.add_post_button.winfo_exists():
            self.add_post_button = ctk.CTkButton(self.buttons_frame, text="Add Post")
            self.add_post_button.pack(pady=10,padx=10)
            self.add_post_button.configure(command=self.controller.open_post_dialog)

        else:
            self.refresh_btn.pack_forget()
            self.refresh_btn.pack(pady=(0, 10))

            self.add_post_button.pack_forget()
            self.add_post_button.pack(pady=10)
        self._create_post_frame(post_data, [])
        self.posts_container.update_idletasks()
        self.posts_container.update()
        post_id = post_data["post_id"]
        post_frame = self.post_frames.get(post_id)
        if post_frame:
            for widget in post_frame.winfo_children():
                if isinstance(widget, ctk.CTkButton) and widget.cget("text") == "Add Comment":
                    widget.configure(command=lambda pid=post_id: self.controller.open_comment_dialog(pid))

    def create_comment_input(self, post_id):
        for pid, frame in self.comment_input_frames.items():
            if frame and frame.winfo_exists():
                frame.destroy()
        self.comment_input_frames = {}
        #sterge butoanele de add si cancel
        post_frame = self.post_frames.get(post_id)
        if not post_frame:
            return

        input_frame = ctk.CTkFrame(post_frame)
        input_frame.pack(fill="x", pady=5, padx=20)
        self.comment_input_frames[post_id] = input_frame

        textbox = ctk.CTkTextbox(input_frame, height=80)
        textbox.pack(fill="x", padx=5, pady=5)

        buttons_frame = ctk.CTkFrame(input_frame)
        buttons_frame.pack(fill="x", pady=5)

        submit_btn = ctk.CTkButton(buttons_frame, text="Send")
        submit_btn.pack(side="left", padx=5)

        submit_btn.configure(command=lambda: self.controller.submit_comment(post_id, textbox))

        cancel_btn = ctk.CTkButton(buttons_frame, text="Cancel",
                                   command=lambda: input_frame.destroy())
        cancel_btn.pack(side="left", padx=5)
        #creeaza inputurile pentru noul comentariu
        return textbox

    def create_post_input(self):
        dialog_frame = ctk.CTkFrame(self.posts_container)
        dialog_frame.pack(fill="x", pady=10, padx=20, after=self.add_post_button)

        title_entry = ctk.CTkEntry(dialog_frame, placeholder_text="Titlu")
        title_entry.pack(fill="x", padx=5, pady=(5, 2))

        textbox = ctk.CTkTextbox(dialog_frame, height=100)
        textbox.pack(fill="x", padx=5, pady=5)

        buttons_frame = ctk.CTkFrame(dialog_frame)
        buttons_frame.pack(fill="x", pady=5)

        submit_btn = ctk.CTkButton(buttons_frame, text="Send",
                                   command=lambda: self.controller.submit_post(title_entry, textbox, dialog_frame))
        submit_btn.pack(side="left", padx=5)

        cancel_btn = ctk.CTkButton(buttons_frame, text="Cancel",
                                   command=lambda: dialog_frame.destroy())
        cancel_btn.pack(side="left", padx=5)

        return dialog_frame, title_entry, textbox

    def set_controller(self, controller):
        self.controller = controller

        if hasattr(self, 'add_post_button'):
            self.add_post_button.configure(command=self.controller.open_post_dialog)

        if hasattr(self, 'back_button'):
            self.back_button.configure(command=self.controller.back)

        if hasattr(self,'refresh_btn'):
            self.refresh_btn.configure(command=self.controller.refresh_comments)
        for post_id, post_frame in self.post_frames.items():
            #toate postarile
            for widget in post_frame.winfo_children():
                #toate widgeturile care au textul add comment primesc functia din controller
                if isinstance(widget, ctk.CTkButton) and widget.cget("text") == "Add Comment":
                    widget.configure(command=lambda pid=post_id: self.controller.open_comment_dialog(pid))
class AddProjectView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.files = []
        self.build_ui()
        self.controller=None
        self.collaborators = []

    def build_ui(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.content_frame = ctk.CTkFrame(self)
        self.content_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.content_frame.grid_columnconfigure(0, weight=1)

        self.build_add_project_ui(self.content_frame)

    def build_add_project_ui(self, parent):
        parent.grid_columnconfigure(0, weight=1)

        self.title_label = ctk.CTkLabel(parent, text="Create New Project", font=ctk.CTkFont(size=18, weight="bold"))
        self.title_label.grid(row=0, column=0, pady=(5, 5), padx=20, sticky="w")

        self.title_entry = self._create_labeled_entry(parent, "Title", row=1)
        self.domain_entry = self._create_labeled_entry(parent, "Domain", row=3)

        start_date_label = ctk.CTkLabel(parent, text="Start Date:")
        start_date_label.grid(row=5, column=0, padx=20, pady=(5, 0), sticky="w")

        date_frame = ctk.CTkFrame(parent, fg_color="transparent")
        date_frame.grid(row=6, column=0, padx=20, sticky="ew")
        self.start_date_entry = DateEntry(date_frame, width=12, background='darkblue',
                                          foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        self.start_date_entry.pack(fill="x")

        desc_files_frame = ctk.CTkFrame(parent)
        desc_files_frame.grid(row=7, column=0, padx=20, pady=(0, 0), sticky="ew")
        desc_files_frame.grid_columnconfigure(0, weight=2)
        desc_files_frame.grid_columnconfigure(1, weight=1)
        desc_files_frame.grid_propagate(False)

        desc_label = ctk.CTkLabel(desc_files_frame, text="Description:", height=80)
        desc_label.grid(row=0, column=0, sticky="w", pady=(0, 5))
        self.desc_entry = ctk.CTkTextbox(desc_files_frame, height=80)
        self.desc_entry.grid(row=1, column=0, sticky="nsew", padx=(0, 10))

        files_frame = ctk.CTkFrame(desc_files_frame, fg_color="transparent")
        files_frame.grid(row=1, column=1, sticky="nsew")
        file_label = ctk.CTkLabel(files_frame, text="Files:", font=ctk.CTkFont(weight="bold"))
        file_label.pack(anchor="w")
        self.add_file_button = ctk.CTkButton(files_frame, text="Add File", command=self.add_file)
        self.add_file_button.pack(anchor="w", pady=(5, 5))
        self.file_list_frame = ctk.CTkScrollableFrame(files_frame)
        self.file_list_frame.pack(fill="both", expand=True)

        self.submit_button = ctk.CTkButton(parent, text="Create Project")
        self.submit_button.grid(row=9, column=0, pady=(5, 5), sticky="e", padx=20)

        collab_section_label = ctk.CTkLabel(parent, text="Collaborators:", font=ctk.CTkFont(weight="bold"))
        collab_section_label.grid(row=10, column=0, padx=20, pady=(5, 5), sticky="w")

        collab_frame = ctk.CTkFrame(parent, fg_color="transparent")
        collab_frame.grid(row=11, column=0, padx=20, sticky="ew")
        collab_frame.grid_columnconfigure(0, weight=1)

        self.collab_entry = ctk.CTkEntry(collab_frame, placeholder_text="Enter username")
        self.collab_entry.grid(row=0, column=0, padx=(0, 10), sticky="ew")

        self.add_collab_button = ctk.CTkButton(collab_frame, text="Add User", command=self.add_collaborator, width=80)
        self.add_collab_button.grid(row=0, column=1)

        self.collab_list_frame = ctk.CTkScrollableFrame(parent, height=50)
        self.collab_list_frame.grid(row=12, column=0, padx=20, pady=(5, 5), sticky="ew")

    def _create_labeled_entry(self, parent, label_text, row):
        #functie pentru a crea entryurile default(care nu au nimic special cum ar fi date entry)
        label = ctk.CTkLabel(parent, text=f"{label_text}:")
        label.grid(row=row, column=0, padx=20, pady=(5, 0), sticky="w")
        entry = ctk.CTkEntry(parent)
        entry.grid(row=row + 1, column=0, padx=20, sticky="ew")
        return entry

    def add_file(self):
        #selecteaza un fisier pe care il trimite la controller
        file_path = filedialog.askopenfilename()
        if not file_path:
            return

        file_name = os.path.basename(file_path)
        file_type = os.path.splitext(file_name)[1][1:]
        file_size = round(os.path.getsize(file_path) / (1024 * 1024), 2)

        file_data = {
            "file_name": os.path.splitext(file_name)[0],
            "file_type": file_type,
            "file_size": file_size,
            "file_path": file_path
        }

        self.controller.handle_new_file(file_data)
    def display_files(self):
        #afiseaza proiectele formatat
        for widget in self.file_list_frame.winfo_children():
            widget.destroy()

        for f in self.files:
            file_label = ctk.CTkLabel(self.file_list_frame,
                                      text=f"{f['file_name']}.{f['file_type']} - {f['file_size']} MB")
            file_label.pack(anchor="w", padx=5, pady=2)

    def get_project_form_data(self):
        #getter pentru dateele noului proiect
        return {
            "title": self.title_entry.get(),
            "start_date": self.start_date_entry.get(),
            "domain": self.domain_entry.get(),
            "description": self.desc_entry.get("1.0", "end").strip()
        }

    def clear_project_form(self):
        #functie de clear a campurilor
        self.title_entry.delete(0, "end")
        self.start_date_entry.delete(0, "end")
        self.domain_entry.delete(0, "end")
        self.desc_entry.delete("1.0", "end")
        for widget in self.collab_list_frame.winfo_children():
            widget.destroy()
        self.collaborators = []
        for widget in self.file_list_frame.winfo_children():
            widget.destroy()

    def set_controller(self, controller):
        self.controller = controller
        self.submit_button.configure(command=self.controller.submit_project)


    def add_collaborator(self):
        #apeleaza functia din controller pentru noi utilizatori preluand numele din view
        username = self.collab_entry.get().strip()
        if username and self.controller:
            self.controller.handle_new_collaborator(username)
            self.collab_entry.delete(0, "end")

    def display_collaborators(self):
        for widget in self.collab_list_frame.winfo_children():
            widget.destroy()

        for username in getattr(self, 'collaborators', []):
            collab_frame = ctk.CTkFrame(self.collab_list_frame, fg_color="transparent")
            collab_frame.pack(fill="x", padx=5, pady=2)

            label = ctk.CTkLabel(collab_frame, text=username)
            label.pack(side="left")

            remove_btn = ctk.CTkButton(collab_frame, text="Remove", width=60, height=24,
                                       command=lambda u=username: self.remove_collaborator(u))
            remove_btn.pack(side="right")
    #afieaza colaboratorii proiectului
    def remove_collaborator(self, username):
        if self.controller:
            self.controller.remove_collaborator(username)

class UserSearchView(ctk.CTkFrame):
    def __init__(self, root):
        super().__init__(root)
        self.controller = None
        self.user_frames = {}
        self.build_ui()
    def build_ui(self):
        self.search_frame = ctk.CTkFrame(self)
        self.search_frame.pack(fill="x", pady=(10, 5), padx=10)

        self.search_label = ctk.CTkLabel(self.search_frame, text="Search Researchers:",
                                         font=ctk.CTkFont(size=16, weight="bold"))
        self.search_label.pack(side="left", padx=(10, 5))

        self.search_entry = ctk.CTkEntry(self.search_frame, width=300 , placeholder_text="Enter name,institution or field of research")
        self.search_entry.pack(side="left", padx=5)
        self.search_entry.bind("<Return>", lambda event: self.controller.find_user())

        self.search_button = ctk.CTkButton(self.search_frame, text="Search")
        self.search_button.pack(side="left", padx=5)

        self.results_label = ctk.CTkLabel(self, text="Search Results",
                                          font=ctk.CTkFont(size=18, weight="bold"))
        self.results_label.pack(pady=(15, 5))

        self.results_container = ctk.CTkScrollableFrame(self)
        self.results_container.pack(fill="both", expand=True, padx=10, pady=10)

    def on_search(self):
        search_term = self.search_entry.get()
        return search_term
        #preia datele din entry ,apelat de controller
    def display_results(self, users):
        for widget in self.results_container.winfo_children():
            widget.destroy()
        #curata si reafiseaza
        self.user_frames = {}

        if not users:
            no_results = ctk.CTkLabel(self.results_container, text="No users found")
            no_results.pack(pady=20)
            return

        for user in users:
            self._create_user_frame(user)

    def _create_user_frame(self, user):
        user_id = user["user_id"]
        user_frame = ctk.CTkFrame(self.results_container)
        user_frame.pack(fill="x", pady=10, padx=5)
        self.user_frames[user_id] = user_frame

        profile_pic_frame = ctk.CTkFrame(user_frame, width=80, height=80)
        profile_pic_frame.grid(row=0, column=0, rowspan=3, padx=(10, 15), pady=10)
        profile_pic_frame.grid_propagate(False)
        if user.get("profile_picture_url"):
            try:
                response = requests.get(user["profile_picture_url"])
                img_data = Image.open(BytesIO(response.content)).resize((80, 80))
                img_data = utils.round_image(img_data, 40)
                profile_image = ctk.CTkImage(light_image=img_data, dark_image=img_data, size=(80, 80))
                profile_pic_label = ctk.CTkLabel(profile_pic_frame, image=profile_image, text="")
                profile_pic_label.pack(expand=True)
            except Exception:
                placeholder = ctk.CTkLabel(profile_pic_frame, text="Profile", font=ctk.CTkFont(size=10))
                placeholder.pack(expand=True)
        else:
            placeholder = ctk.CTkLabel(profile_pic_frame, text="Profile", font=ctk.CTkFont(size=10))
            placeholder.pack(expand=True)

        name_label = ctk.CTkLabel(user_frame, text=user["name"],
                                  font=ctk.CTkFont(size=16, weight="bold"))
        name_label.grid(row=0, column=1, sticky="w")

        institution_frame = ctk.CTkFrame(user_frame)
        institution_frame.grid(row=1, column=1, sticky="w")
        institution_label = ctk.CTkLabel(institution_frame, text="Institution:", text_color="#888")
        institution_label.pack(side="left", padx=(0, 5))
        institution_value = ctk.CTkLabel(institution_frame, text=user["institution"])
        institution_value.pack(side="left")

        field_frame = ctk.CTkFrame(user_frame)
        field_frame.grid(row=2, column=1, sticky="w")
        field_label = ctk.CTkLabel(field_frame, text="Field:", text_color="#888")
        field_label.pack(side="left", padx=(0, 5))
        field_value = ctk.CTkLabel(field_frame, text=user["field_of_research"])
        field_value.pack(side="left")

        view_profile_btn = ctk.CTkButton(user_frame, text="View Profile",
                                         command=lambda uid=user_id: self.controller.view_user_profile(uid))
        view_profile_btn.grid(row=1, column=2, padx=10)

        user_frame.grid_columnconfigure(1, weight=1)

    def display_user_profile(self, user, projects):
        #top level creeaza alt window in care sa apara informatii despre user
        profile_dialog = ctk.CTkToplevel(self)
        profile_dialog.title(f"User Profile: {user['name']}")
        profile_dialog.geometry("650x600")
        profile_dialog.minsize(600, 600)
        profile_dialog.grab_set()
        close_button = ctk.CTkButton(profile_dialog, text="Close",
                                     command=profile_dialog.destroy)
        close_button.pack(pady=20)

        header_frame = ctk.CTkFrame(profile_dialog)
        header_frame.pack(fill="x", padx=20, pady=20)

        if user.get("profile_picture_url"):
            try:
                response = requests.get(user["profile_picture_url"])
                img_data = Image.open(BytesIO(response.content)).resize((100, 100))
                img_data = utils.round_image(img_data, 50)
                profile_image = ctk.CTkImage(light_image=img_data, dark_image=img_data, size=(100, 100))

                pic_label = ctk.CTkLabel(header_frame, image=profile_image, text="")
                pic_label.pack(side="left", padx=(0, 20))
            except Exception:
                pass

        info_frame = ctk.CTkFrame(header_frame)
        info_frame.pack(side="left", fill="y")

        name_label = ctk.CTkLabel(info_frame, text=user["name"],
                                  font=ctk.CTkFont(size=20, weight="bold"))
        name_label.pack(anchor="w", pady=(0, 5))

        email_label=ctk.CTkLabel(info_frame, text=f"Email: {user['email']}")
        email_label.pack(anchor="w")

        institution_label = ctk.CTkLabel(info_frame, text=f"Institution: {user['institution']}")
        institution_label.pack(anchor="w")

        field_label = ctk.CTkLabel(info_frame, text=f"Field: {user['field_of_research']}")
        field_label.pack(anchor="w")

        start_date_label = ctk.CTkLabel(info_frame, text=f"Researcher since: {user['researcher_start_date']}")
        start_date_label.pack(anchor="w")

        bio_label = ctk.CTkLabel(profile_dialog, text="Biography",
                                 font=ctk.CTkFont(size=16, weight="bold"))
        bio_label.pack(anchor="w", padx=20, pady=(20, 5))

        bio_text = ctk.CTkTextbox(profile_dialog, height=100)
        bio_text.pack(fill="x", padx=20, pady=(0, 20))
        bio_text.insert("1.0", user["biography"] if user["biography"] else "No biography available.")
        bio_text.configure(state="disabled")

        projects_label = ctk.CTkLabel(profile_dialog, text="Projects",
                                      font=ctk.CTkFont(size=16, weight="bold"))
        projects_label.pack(anchor="w", padx=20, pady=(0, 5))

        projects_frame = ctk.CTkScrollableFrame(profile_dialog, height=150)
        projects_frame.pack(fill="x", padx=20, pady=(0, 20))

        if not projects:
            no_projects = ctk.CTkLabel(projects_frame, text="No projects available")
            no_projects.pack(pady=10)
        else:
            for project in projects:
                project_frame = ctk.CTkFrame(projects_frame)
                project_frame.pack(fill="x", pady=5)

                title_label = ctk.CTkLabel(project_frame, text=project["title"],
                                           font=ctk.CTkFont(weight="bold"))
                title_label.pack(anchor="w", padx=10, pady=(5, 0))

                domain_frame = ctk.CTkFrame(project_frame)
                domain_frame.pack(fill="x", padx=10)
                domain_label = ctk.CTkLabel(domain_frame, text="Domain:", text_color="#888")
                domain_label.pack(side="left", padx=(0, 5))
                domain_value = ctk.CTkLabel(domain_frame, text=project["domain"])
                domain_value.pack(side="left")

                date_frame = ctk.CTkFrame(project_frame)
                date_frame.pack(fill="x", padx=10, pady=(0, 5))
                date_label = ctk.CTkLabel(date_frame, text="Start Date:", text_color="#888")
                date_label.pack(side="left", padx=(0, 5))
                date_value = ctk.CTkLabel(date_frame, text=project["start_date"])
                date_value.pack(side="left")

                description_frame=ctk.CTkFrame(project_frame)
                description_frame.pack(fill="x", padx=10, pady=(0, 5))
                description_label = ctk.CTkLabel(description_frame, text="Description:", text_color="#888")
                description_label.pack(side="left", padx=(0, 5))
                description_value = ctk.CTkLabel(description_frame, text=project["description"])
                description_value.pack(side="left")
    def set_controller(self, controller):
        self.controller = controller
        self.search_button.configure(command=self.controller.find_user)


class SettingsView(ctk.CTkFrame):
    def __init__(self, root):
        super().__init__(root)
        self.controller = None
        self.selected_project = None
        self.build_ui()
        self.selected_profile_pic_path=None
    def build_ui(self):
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)

        self.tabview.add("Profile")
        self.tabview.add("Projects")
        self.tabview.add("Files")
        #3 taburi in functie de tipul modificarii
        self.build_profile_tab()

        self.build_projects_tab()

        self.build_files_tab()

    def browse_profile_picture(self):
        #schimbarea imaginii de profil, o afiseaza  sub fomra de thumbnail
        file_path = filedialog.askopenfilename(
            title="Select Profile Picture",
            filetypes=(("Image files", "*.png;*.jpg;*.jpeg;*.webp"), ("All files", "*.*"))
        )
        if file_path:
            self.profile_pic_path.delete(0, "end")
            self.profile_pic_path.insert(0, file_path)
            try:
                img = Image.open(file_path)
                img.thumbnail((100, 100))
                photo = ctk.CTkImage(light_image=img, dark_image=img, size=(100, 100))
                self.profile_pic_label.configure(image=photo, text="")

                self.selected_profile_pic_path = file_path
            except Exception as e:
                print(f"Error loading thumbnail: {e}")
    def build_profile_tab(self):
        profile_frame = self.tabview.tab("Profile")

        title = ctk.CTkLabel(profile_frame, text="Update Profile Information",
                             font=ctk.CTkFont(size=18, weight="bold"))
        title.pack(pady=(10, 20))

        form_frame = ctk.CTkFrame(profile_frame)
        form_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.profile_fields = {}
        fields = ["name", "email", "institution", "field_of_research", "biography","researcher_start_date"]
        #un vector in care sunt retinute numele campurilor,creeaza frame,label si value pe baza lui
        for i, field in enumerate(fields):
            row = ctk.CTkFrame(form_frame)
            row.pack(fill="x", pady=10)

            label = ctk.CTkLabel(row, text=f'{field.replace("_"," ").capitalize()}:', width=100, anchor="w")
            label.pack(side="left", padx=(10, 10))

            if field == "biography":
                entry = ctk.CTkTextbox(row, height=100)
                entry.pack(side="left", fill="both", expand=True, padx=(0, 10))
            elif field == "researcher_start_date":
                entry = DateEntry(row, width=12, background='darkblue',
                                          foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
                entry.pack(side="left", padx=(0, 10))
            else:
                entry = ctk.CTkEntry(row, width=300)
                entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

            self.profile_fields[field] = entry

        pic_frame = ctk.CTkFrame(form_frame)
        pic_frame.pack(fill="x", pady=10)

        pic_label = ctk.CTkLabel(pic_frame, text="Profile Picture:", width=100, anchor="w")
        pic_label.pack(side="left", padx=(10, 10))

        self.profile_pic_path = ctk.CTkEntry(pic_frame, width=220)
        self.profile_pic_path.pack(side="left", fill="x", expand=True, padx=(0, 10))

        self.browse_pic_btn = ctk.CTkButton(pic_frame, text="Browse", width=70)
        self.browse_pic_btn.pack(side="left", padx=(0, 10))

        self.profile_pic_label=ctk.CTkLabel(profile_frame,text="")
        self.profile_pic_label.pack()

        self.save_profile_btn = ctk.CTkButton(profile_frame, text="Save Profile Changes")
        self.save_profile_btn.pack(pady=20)

    def build_projects_tab(self):
        projects_frame = self.tabview.tab("Projects")

        title = ctk.CTkLabel(projects_frame, text="Manage Your Projects",
                             font=ctk.CTkFont(size=18, weight="bold"))
        title.pack(pady=(10, 20))

        selection_frame = ctk.CTkFrame(projects_frame)
        selection_frame.pack(fill="x", pady=10, padx=20)

        select_label = ctk.CTkLabel(selection_frame, text="Select Project:", anchor="w")
        select_label.pack(side="left", padx=(10, 10))

        self.project_selector = ctk.CTkComboBox(selection_frame, width=300, state="readonly")
        self.project_selector.pack(side="left", padx=(0, 10))

        self.project_details_frame = ctk.CTkFrame(projects_frame)
        self.project_details_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.project_fields = {}
        fields = ["title","start_date","domain","description"]

        for i,field in enumerate(fields):
            row = ctk.CTkFrame(self.project_details_frame)
            row.pack(fill="x", pady=10)

            label = ctk.CTkLabel(row, text=f"{field.replace("_"," ").capitalize()}:", width=100, anchor="w")
            label.pack(side="left", padx=(10, 10))

            if field == "description":
                entry = ctk.CTkTextbox(row, height=100)
                entry.pack(side="left", fill="both", expand=True, padx=(0, 10))
            elif field == "start_date":
                entry = DateEntry(row, width=12, background='darkblue',foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
                entry.pack(side="left", padx=(0, 10))
            else:
                entry = ctk.CTkEntry(row, width=300)
                entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

            self.project_fields[field] = entry

        button_frame = ctk.CTkFrame(projects_frame)
        button_frame.pack(fill="x", pady=10, padx=20)

        self.save_project_btn = ctk.CTkButton(button_frame, text="Save Project Changes")
        self.save_project_btn.pack(side="left", padx=(10, 10))

    def build_files_tab(self):
        files_frame = self.tabview.tab("Files")

        title = ctk.CTkLabel(files_frame, text="Manage Project Files",
                             font=ctk.CTkFont(size=18, weight="bold"))
        title.pack(pady=(10, 20))

        selection_frame = ctk.CTkFrame(files_frame)
        selection_frame.pack(fill="x", pady=10, padx=20)

        select_label = ctk.CTkLabel(selection_frame, text="Select Project:", anchor="w")
        select_label.pack(side="left", padx=(10, 10))

        self.files_project_selector = ctk.CTkComboBox(selection_frame, width=300, state="readonly")
        self.files_project_selector.pack(side="left", padx=(0, 10))

        list_frame = ctk.CTkFrame(files_frame)
        list_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.files_container = ctk.CTkScrollableFrame(list_frame)
        self.files_container.pack(fill="both", expand=True, padx=10, pady=10)

        add_file_frame = ctk.CTkFrame(files_frame)
        add_file_frame.pack(fill="x", padx=20, pady=10)

        add_label = ctk.CTkLabel(add_file_frame, text="Add New File:", font=ctk.CTkFont(weight="bold"))
        add_label.pack(anchor="w", padx=10, pady=(10, 5))

        file_path_frame = ctk.CTkFrame(add_file_frame)
        file_path_frame.pack(fill="x", pady=5)

        path_label = ctk.CTkLabel(file_path_frame, text="File Path:", width=80, anchor="w")
        path_label.pack(side="left", padx=(10, 10))

        self.new_file_path = ctk.CTkEntry(file_path_frame, width=220)
        self.new_file_path.pack(side="left", fill="x", expand=True, padx=(0, 10))

        self.browse_file_btn = ctk.CTkButton(file_path_frame, text="Browse", width=70)
        self.browse_file_btn.pack(side="left", padx=(0, 10))

        self.upload_file_btn = ctk.CTkButton(add_file_frame, text="Upload File")
        self.upload_file_btn.pack(pady=10, anchor="e", padx=10)


    def display_profile_info(self, info):
        user_info = info[0]
        #configureaza entryurile cu valorile deja existente din baza de date
        for field, entry in self.profile_fields.items():
            if field in user_info:
                if isinstance(entry, ctk.CTkTextbox):
                    entry.delete("1.0", "end")
                    entry.insert("1.0", str(user_info[field] or ""))
                else:
                    entry.delete(0, "end")
                    entry.insert(0, str(user_info[field] or ""))

    def get_profile_data(self):
        data = {}
        #returneaza campurile dupa ce se apasa pe salveaza
        for field, entry in self.profile_fields.items():
            if isinstance(entry, ctk.CTkTextbox):
                data[field] = entry.get("1.0", "end-1c")
            elif isinstance(entry, DateEntry):
                data[field] = entry.get_date().isoformat()
            else:
                data[field] = entry.get()
        data["profile_picture_url"] = self.selected_profile_pic_path

        return data

    def populate_project_selectors(self, projects):
        #populeaza comboboxurile din project
        if not projects:
            self.project_selector.configure(values=["No projects available"])
            self.files_project_selector.configure(values=["No projects available"])
            return

        project_titles = [p["title"] for p in projects]
        self.project_selector.configure(values=project_titles)
        self.files_project_selector.configure(values=project_titles)

        self.project_selector.set(project_titles[0])
        self.files_project_selector.set(project_titles[0])

    def display_project_info(self, project):
        self.selected_project = project
        #umple campurile cu valorile deja existente
        for field, entry in self.project_fields.items():
            if field in project:
                if isinstance(entry, ctk.CTkTextbox):
                    entry.delete("1.0", "end")
                    entry.insert("1.0", str(project[field] or ""))
                else:
                    entry.delete(0, "end")
                    entry.insert(0, str(project[field] or ""))

    def get_project_data(self):
        if not self.selected_project:
            return None

        data = {"project_id": self.selected_project["project_id"]}

        for field, entry in self.project_fields.items():
            if isinstance(entry, ctk.CTkTextbox):
                data[field] = entry.get("1.0", "end-1c")
            else:
                data[field] = entry.get()

        return data

    def display_files(self, files):
        for widget in self.files_container.winfo_children():
            widget.destroy()

        if not files:
            no_files_label = ctk.CTkLabel(self.files_container, text="No files available for this project")
            no_files_label.pack(pady=20)
            return

        for file in files:
            file_frame = ctk.CTkFrame(self.files_container)
            file_frame.pack(fill="x", pady=5, padx=5)

            file_name = ctk.CTkLabel(file_frame, text=file["file_name"], width=200, anchor="w")
            file_name.pack(side="left", padx=10, pady=10)

            file_type = ctk.CTkLabel(file_frame, text=file["file_type"], width=80)
            file_type.pack(side="left", padx=10, pady=10)

            file_size = ctk.CTkLabel(file_frame, text=f"{file['file_size']} MB", width=80)
            file_size.pack(side="left", padx=10, pady=10)

            download_btn = ctk.CTkButton(file_frame, text="Download", width=80,
                                         command=lambda f=file: self.controller.download_project_file(f))
            download_btn.pack(side="left", padx=10, pady=10)

            delete_btn = ctk.CTkButton(file_frame, text="Delete", width=80, fg_color="red",hover_color="#C31F1F",
                                       command=lambda f=file: self.controller.delete_file(f))
            delete_btn.pack(side="left", padx=10, pady=10)
    def set_controller(self, controller):
        self.controller = controller

        self.save_profile_btn.configure(command=self.controller.save_profile_changes)
        self.browse_pic_btn.configure(command=self.browse_profile_picture)
        self.project_selector.configure(command=self.controller.on_project_selected)
        self.files_project_selector.configure(command=self.controller.on_files_project_selected)
        self.save_project_btn.configure(command=self.controller.save_project_changes)
        self.browse_file_btn.configure(command=self.controller.browse_file)
        self.upload_file_btn.configure(command=self.controller.upload_file)

class StatisticsView(ctk.CTkFrame):
    def __init__(self, root):
        super().__init__(root)
        self.build_ui()

    def build_ui(self):
        self.container = ctk.CTkScrollableFrame(self)
        self.container.pack(fill="both", expand=True, padx=20, pady=20)

    def display_statistics(self, stats):
        for widget in self.container.winfo_children():
            widget.destroy()

        max_projects = 30
        max_posts = 20
        max_comments = 180
        max_files = 30

        def add_stat_line(label_text, count, max_val):
            label = ctk.CTkLabel(self.container, text=f"{label_text}: {count} / {max_val}")
            label.pack(pady=(10, 0))
            progress = ctk.CTkProgressBar(self.container)
            progress.set(min(count / max_val, 1.0))
            progress.pack(fill="x")

        add_stat_line("Projects Involved", stats.get("projects_count", 0), max_projects)
        add_stat_line("Posts Made", stats.get("posts_count", 0), max_posts)
        add_stat_line("Comments Made", stats.get("comments_count", 0), max_comments)
        add_stat_line("Files in Projects", stats.get("files_count", 0), max_files)

        rs_date = stats.get("research_start_date")
        if rs_date:
            if isinstance(rs_date, str):
                rs_date = datetime.datetime.strptime(rs_date, "%Y-%m-%d").date()
            duration = (datetime.date.today() - rs_date).days
            label = ctk.CTkLabel(self.container, text=f"Research started: {rs_date} ({duration} days ago)")
            label.pack(pady=20)

        summary = (
            f"You participate in {stats.get('projects_count',0)} projects.\n"
            f"You have made {stats.get('posts_count',0)} posts and {stats.get('comments_count',0)} comments.\n"
            f"There are {stats.get('files_count',0)} files across your projects.\n"
            f"Research start date: {rs_date if rs_date else 'N/A'}."
        )
        summary_box = ctk.CTkTextbox(self.container, height=120)
        summary_box.insert("1.0", summary)
        summary_box.configure(state="disabled")
        summary_box.pack(pady=20, fill="x")

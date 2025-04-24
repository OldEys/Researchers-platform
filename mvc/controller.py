from mysql.connector import IntegrityError # eroare de la mysqlconnector
from mvc.view import * #importam toate clasele din view si model
from mvc.model import *
from io import BytesIO #citeste binar dintr-un fisier imagine
import requests
from PIL import Image #python image library
import utils #fisier pentru rotunjirea colturilor
import customtkinter as ctk
import sys
class AppCoordinator:
    #clasa care gestioneaza toata aplicatia, face trecerea de la formularul de login la
    #mainapp atunci cand credentialele se potrivesc
    def __init__(self, root):
        #viewuri si modele pentru fiecare tip de clasa
        self.root = root
        #root e windowul
        self.login_view = LoginView(root)
        self.login_model = LoginModel()
        self.login_controller = LoginController(
            view=self.login_view,
            model=self.login_model,
            on_success=self.show_dashboard
            #daca credentialele sunt bune se apeleaza dashboard si se memoreaza numele utilizatorului
            #conectat
        )
        self.login_view.pack(fill="both", expand=True)
        self.register_model = RegisterModel()
        self.mainapp_view = None
        self.mainapp_controller = None
        self.user_search_model = UserSearchModel()

        self.login_view.set_controller({
            "login": self.login_controller,
            "register": RegisterController(self.login_view, self.register_model)
        })
        #loginview contine si viewul pentru login si cel pentru register asa ca in functie de tabul accesat
        #foloseste alt controller

    def show_dashboard(self, username):
        self.login_view.pack_forget()
        #dispare loginul
        self.mainapp_view = MainAppView(self.root, username)
        self.mainapp_view.pack(fill="both", expand=True)

        self.mainapp_controller = MainAppController(
            view=self.mainapp_view,
            model=MainAppModel(),
            username=username,
            on_logout=self.show_login
            #la delogare revine in login view
        )
        self.mainapp_view.set_controller(self.mainapp_controller)
        #apeleaza set_Controller ca butoanele sa beneficieze de functiile din controller

    def show_login(self):
        if self.mainapp_view:
            self.mainapp_view.pack_forget()

        self.login_view.pack(fill="both", expand=True)


class RegisterController:
    def __init__(self, view , model):
        self.view = view
        self.model = model
    def register(self):
        registration_data=self.view.register_get_data()
        #preia datele din view si adauga userul prin model
        try:
            self.model.add_user(**registration_data)
            self.view.clearRegister()
        except IntegrityError as e :
            messagebox.showerror("Error - User already exists",str(e))
        except Error as e :
            messagebox.showerror("Error - Database error",str(e))
        except Exception as e :
            messagebox.showerror("Error - Unexpected error",str(e))
class LoginController:
    def __init__(self, view , model,on_success=None):
        #are in plus o metoda in cazul in care are succes conectarea
        #ea primeste show_dashboard de la appinitiator
        self.view = view
        self.model = model
        self.on_login_success=on_success

    def login(self):
        login_data = self.view.login_get_data()
        #preia datele din view
        self.view.clearLogin()

        if len(login_data["name"]) <= 2 or len(login_data["password"]) <= 2:
            messagebox.showerror("Error", "Username and/or Password is too small")
            return

        try:
            authenticated = self.model.verify_user(**login_data)
            #verifica ca user sa fie in baza de date
            #daca e atunci atributul self.on_login_succesc se apeleaza
            if authenticated:
                if self.on_login_success:
                    self.on_login_success(login_data["name"])
            else:
                messagebox.showerror("Login Failed", "Name or password is incorrect.")
        except IntegrityError as e:
            messagebox.showerror("Error - Database integrity", str(e))
        except Error as e:
            messagebox.showerror("Error - Database error", str(e))
        except Exception as e:
            messagebox.showerror("Error - Unexpected error", str(e))

class MainAppController:
    def __init__(self,view,model,username,on_logout):
        self.view=view
        self.model=model
        self.username=username
        self.settings_model=SettingsModel()
        self.user_search_model=UserSearchModel()
        self.statistics_model=StatisticsModel()
        #modele pentru taburile din mainapp

        self.controllers={}
        #dictionar cu toate controllerele folosite in mainapp
        self.current_controller=None
        self.setup()
        self.view.set_controller(self)
        self.on_section_switched("Dashboard")
        self.on_logout=on_logout
    def logout(self):
        self.on_logout()
        #metoda apelata de butonul de logout
    def setup(self):
        self.controllers["Dashboard"]=DashboardController(self.view.sections["Dashboard"],self.model,self.username)
        self.controllers["AddProject"] =AddProjectController(self.view.sections["AddProject"],self.model,self.username)
        self.controllers["UserSearch"] = UserSearchController(self.view.sections["UserSearch"],self.user_search_model,self.username)
        self.controllers["Statistics"] = StatisticsController(self.view.sections["Statistics"],self.statistics_model,self.username)
        self.controllers["Settings"] = SettingsController(self.view.sections["Settings"],self.settings_model,self.username)
        #initiaza controlerele cu viewurile si modelele corespunzatoare fiecaruia
    def on_section_switched(self,section_name):
        self.current_controller=self.controllers.get(section_name)
        if self.current_controller:
            if hasattr(self.current_controller, 'load_data'):
                self.current_controller.load_data()
        #cand se schimba sectiunea controllerul curent ia valoarea din section_name
    def on_open_project(self, project_data):
        self.controllers["ProjectPage"] = ProjectPageController(
            view=self.view.sections["ProjectPage"],
            model=self.model,
            username=self.username,
            project_data=project_data,
            on_back=lambda: self.view.switch_section("Dashboard")
        )
        self.view.switch_section("ProjectPage")
        #daca se apasa ca sa se deschida un proiect se va crea controllerul avand ca functie de on back
        #sa se intra din nou in dashboard si se va afisa pagina proiectului
class DashboardController:
    def __init__(self,view,model,username):
        self.view=view
        self.model=model
        self.username=username
        self.profile_image=None
    def load_data(self):
        self.load_user_info()
        self.load_user_projects()
        self.view.set_controller(self)
    def load_user_info(self):
        #incarca informatiile din model si le afiseaza prin view
        try:
            info=self.model.get_information_by_user(self.username)
            if self.profile_image is None:
                try:
                    profile_image_url = info[0]["profile_picture_url"]
                    #response face un request in cloud pentru a obtine blobul
                    response = requests.get(profile_image_url)
                    #image.open deschide acel blob convertit intr-un format de fisier de bytesio
                    img_data = Image.open(BytesIO(response.content)).resize((150, 150))
                    #aplicam rotunjirea
                    img_data = utils.round_image(img_data, 100)
                    #cream un ctkimage pentru a contine imaginea
                    self.profile_image = ctk.CTkImage(light_image=img_data, dark_image=img_data, size=(150, 150))
                except Exception:
                    self.profile_image = None
            self.view.display_information(info, self.profile_image)

        except Error as e:
            print("Error displaying user information",e)
    def load_user_projects(self):
        try:
            projects=self.model.get_projects_by_user(self.username)
            self.view.display_projects(projects)
        except Error as e:
            print("Error displaying user projects",e)

    def delete_project(self, project):
        #afiseaza un box pentru confirmare, la acceptare se apeleaza stergerea
        confirm = messagebox.askyesno("Confirm Delete",
                                      f"Are you sure you want to delete the project '{project['title']}'?")
        if confirm:
            try:
                self.model.delete_project(project['project_id'],self.username)
                messagebox.showinfo("Deleted", f"Project '{project['title']}' was deleted.")
                self.load_user_projects()
            except Exception as e:
                messagebox.showerror("Error", f"Could not delete project: {e}")

    def delete_account(self):
        confirm = messagebox.askyesno("Confirm", "Are you sure you want to delete your account? This action is irreversible.")
        if not confirm:
            return

        try:
            self.model.delete_account(self.username)
            messagebox.showinfo("Account Deleted", "Your account has been successfully deleted.")
            sys.exit()
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while deleting your account: {e}")

class ProjectPageController:
    def __init__(self, view, model, username, project_data, on_back):
        self.view = view
        self.model = model
        self.project_data = project_data
        self.username = username
        self.on_back = on_back
        #callback catre functia de afisare a dashboardului

        self.comments = []
        self.posts = []
        #vectori care contin postarile si comentariile pe proiectul respectiv

        self.load_project()
        self.view.set_controller(self)

    def back(self):
        self.on_back()
        #apelata din view care apeleaza la randul ei show_dashboard

    def load_project(self):
        self.view.display_project(self.project_data)
        project_id = self.project_data["project_id"]


        files = self.model.get_files(project_id)
        self.view.display_files(files)

        self.posts = self.model.get_all_posts(project_id)
        #vectorul contine toate postarile
        #afiseaza informatiile ,fisierele si comentariile in containerele respective

        self.comments = []
        for post in self.posts:
            post_id = post["post_id"]
            comments = self.model.get_all_comments(post_id)
            if comments:
                self.comments.extend(comments)
        #adauga comentariile luate din model in vector
        self.view.display_comments_and_posts(self.posts, self.comments)

    def download_file(self, blob_name, file):
        file_type = file["file_type"]
        #preluam tipul fisierului
        default_extension = f".{file_type}"
        #extensia default
        filetypes = [(f"{file_type.upper()} files", f"*.{file_type}")]
        #numele pe care il arata in filedialog jos in dreapta

        file_path = filedialog.asksaveasfilename(
            defaultextension=default_extension,
            filetypes=filetypes,
            initialfile=file["file_name"]
        )
        if not file_path:
            return
        success, msg = self.model.download_file(blob_name, file_path)

        if success:
            messagebox.showinfo("Success", msg)
        else:
            messagebox.showerror("Error", f"Download failed: {msg}")

    def open_comment_dialog(self, post_id):
        textbox = self.view.create_comment_input(post_id)
        #apeleaza crearea de inputuri ale viewului , apelat atunci cand se apasa pe add_comment

        for pid, frame in self.view.comment_input_frames.items():
            #toate frameurile care apar cand apasam pe add comment
            if pid == post_id and frame.winfo_exists():
                #grupeaza comentariile dupa post_id
                for widget in frame.winfo_children():
                    #cauta toate widgeturile din frame
                    if isinstance(widget, ctk.CTkFrame):
                        #daca e de tip frame
                        for btn in widget.winfo_children():
                            #daca e buton cu textul send atunci apeleaza submit_comment in post_id
                            if isinstance(btn, ctk.CTkButton) and btn.cget("text") == "Send":
                                btn.configure(command=lambda: self.submit_comment(post_id, textbox))

    def open_post_dialog(self):
        dialog_frame, title_entry, textbox = self.view.create_post_input()
        #preia frameul , entryul pentru titlu si cel pentru mesaj
        for widget in dialog_frame.winfo_children():
            #toate widgeturile din dialog_frame
            if isinstance(widget, ctk.CTkFrame):
                #daca avem frame
                for btn in widget.winfo_children():
                    #configureaza butoanele sa apeleze submit_post
                    if isinstance(btn, ctk.CTkButton) and btn.cget("text") == "Send":
                        btn.configure(command=lambda: self.submit_post(title_entry, textbox, dialog_frame))

    def submit_comment(self, post_id, textbox):
        comment_text = textbox.get("1.0", "end").strip()
        if not comment_text:
            messagebox.showwarning("Warning", "Comment cannot be empty!")
            return
        #ia valoarea din text_box si insereaza in baza de date

        comment_data = self.model.add_comment(post_id, self.project_data["project_id"], self.username, comment_text)

        for pid, frame in self.view.comment_input_frames.items():
            if pid == post_id and frame.winfo_exists():
                frame.destroy()
        #distruge frameul in care introduci noul comment
        if comment_data:
            self.comments.append(comment_data)
            #insereaza in vectorul de comentarii apoi afiseaza noul comentariu
            self.view.add_single_comment(post_id, comment_data)

    def submit_post(self, title_entry, textbox, dialog_frame):
        title = title_entry.get().strip()
        body = textbox.get("1.0", "end").strip()
        #la fel ca la submit_comment
        if not title or not body:
            messagebox.showwarning("Warning", "Title or body cannot be empty!")
            return

        post_data = self.model.add_post(self.project_data["project_id"], self.username, title, body)

        dialog_frame.destroy()

        if post_data:
            self.posts.append(post_data)
            self.view.add_single_post(post_data)
            post_data["comments"] = []

    def refresh_comments(self):
        project_id = self.project_data["project_id"]
        posts = self.model.get_all_posts(project_id)
        #reinsereaza tot in comments si posts apoi reafiseaza comentariile si posturile
        comments = []
        for post in posts:
            comments.extend(self.model.get_all_comments(post["post_id"])) or []

        self.view.display_comments_and_posts(posts, comments)
        self.view.set_controller(self)
class AddProjectController:
    def __init__(self, view, model, username):
        self.view = view
        self.model = model
        self.username = username
        self.view.set_controller(self)
        self.temp_files = []
        self.temp_collaborators = []
        self.view.collaborators = []
        # self.all_projects=[]
        #salvam fisierele temporare pe care le introduce inainte de salvare,colaboratorii si vectorul
        #de proiecte


    def submit_project(self):
        project_data = self.view.get_project_form_data()
        if not self.validate_project_data(project_data):
            return
        #preia datele din view
        #insereaza in tabela de proiecte , leaga userul la proiect precum si colaboratorii


        try:
            project_id = self.model.insert_project(**project_data)
            self.model.assign_user_to_project(self.username, project_id)

            for collaborator in self.temp_collaborators:
                self.model.assign_user_to_project(collaborator, project_id)

            #introduce toate fisierele in tabela si le uploadeaza in azure
            for file_data in self.temp_files:
                file_url = self.model.upload_to_azure(
                    file_data["file_path"],
                    f"{file_data['file_name']}.{file_data['file_type']}"
                )
                self.model.insert_file_metadata(
                    project_id=project_id,
                    file_name=file_data["file_name"],
                    file_type=file_data["file_type"],
                    file_url=file_url,
                    file_size=file_data["file_size"]
                )

            self.temp_files.clear()

            messagebox.showinfo("Success", "Project added successfully!")
            self.view.clear_project_form()

        except Exception as e:
            messagebox.showerror("Error", f"Error saving the project: {str(e)}")

    def validate_project_data(self, data):
        title = data.get("title", "").strip()
        domain = data.get("domain", "").strip()
        start_date = data.get("start_date", "")

        #verifica daca campurile sunt de cel putin 3 caractere si daca data e in format bun

        if len(title) <= 2:
            messagebox.showerror("Error", "Title must be at least 3 characters long.")
            return False
        if len(domain) <= 2:
            messagebox.showerror("Error", "Domain must be at least 3 characters long.")
            return False
        try:
            datetime.strptime(start_date, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Error", "Date must be in YYYY-MM-DD format.")
            return False
        return True
    def handle_new_file(self, file_data):
        self.temp_files.append(file_data)
        self.view.files = self.temp_files
        self.view.display_files()
        #adauga la vectorul de fisiere temporar noul fisiere si il afiseaza
    def handle_new_collaborator(self, username):
        #verifica sa nu adauga un colaborator care e deja adaugat sau care nu exista
        if username == self.username:
            messagebox.showwarning("Warning", "You cannot add yourself.")
            return

        if username in self.temp_collaborators:
            messagebox.showwarning("Warning", f"User {username} is already a collaborator.")
            return

        if self.model.check_user_exists(username):
            self.temp_collaborators.append(username)
            self.view.collaborators = self.temp_collaborators
            self.view.display_collaborators()
        else:
            messagebox.showerror("Error", f"User {username} doesn't exist.")

    def remove_collaborator(self, username):
        if username in self.temp_collaborators:
            self.temp_collaborators.remove(username)
            self.view.collaborators = self.temp_collaborators
            self.view.display_collaborators()
        #scoate de la vectorul temporar si reafiseaza
class UserSearchController:
    def __init__(self, view, model, username):
        self.view = view
        self.model = model
        self.username = username
        self.view.set_controller(self)


    def find_user(self):
        search_term=self.view.on_search()
        #scoate datele din view si verifica dimensiunea
        if not search_term or len(search_term.strip()) < 2:
            messagebox.showinfo("Search", "Please enter at least 2 characters")
            return

        try:
            results = self.model.search_users(search_term)
            self.view.display_results(results)
            #cauta in model si afiseaza
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while searching: {str(e)}")

    def view_user_profile(self, user_id):
        try:
            search_results = self.model.search_users("")
            user = next((u for u in search_results if u["user_id"] == user_id), None)
            #cauta in toti userii pe cel care user_idul acela
            if not user:
                messagebox.showerror("Error", "User not found")
                return

            projects = self.model.get_user_projects(user_id)
            self.view.display_user_profile(user, projects)
            #afiseaza profilul intr un window nou
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
    def load_data(self):
        pass


class SettingsController:
    def __init__(self, view, model, username):
        self.view = view
        self.model = model
        self.username = username
        self.projects = None
        self.selected_project = None
        self.selected_files_project = None
        #memoram proiectele , si campurile selectate din combobox


        self.view.set_controller(self)

    def load_data(self):
        self.load_profile_info()
        self.load_user_projects()

    def load_profile_info(self):
        try:
            info = self.model.get_information_by_user(self.username)
            if info:
                self.view.display_profile_info(info)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load profile information: {str(e)}")

    def load_user_projects(self):
        try:
            projects = self.model.get_projects_by_user(self.username)
            self.projects = projects

            if projects:
                self.view.populate_project_selectors(projects)
                #daca exista priecte popouleaza comboboxul si actualizeaza in functie de proiectul ales
                self.on_project_selected(projects[0]["title"])
                self.on_files_project_selected(projects[0]["title"])
            else:
                messagebox.showinfo("No Projects", "You don't have any projects yet.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load projects: {str(e)}")

    def save_profile_changes(self):
        try:
            profile_data = self.view.get_profile_data()

            if not profile_data:
                return
            #ia datele din campuri iar imaginea o incarca in cloud obtinand url-ul
            profile_pic_path = profile_data.get("profile_picture_url")

            if profile_pic_path:
                blob_name = f"user_{self.username}_{os.path.basename(profile_pic_path)}"
                image_url = self.model.update_image_to_blob(profile_pic_path, blob_name)

                if image_url:
                    profile_data["profile_picture_url"] = image_url
                    #actualizam profile_picture incat sa contina url ul ca sa inseram in baza de date
                else:
                    messagebox.showerror("Error", "Failed to upload profile picture.")
                    return
            else:
                profile_data.pop("profile_picture_url", None)
            success = self.model.update_user_profile(self.username, profile_data)

            if success:
                messagebox.showinfo("Success", "Profile updated successfully!")
                self.load_profile_info()
            else:
                messagebox.showerror("Error", "Failed to update profile")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save profile changes: {str(e)}")

    def on_project_selected(self, project_title):
        if not self.projects:
            return

        for project in self.projects:
            if project["title"] == project_title:
                self.selected_project = project
                self.view.display_project_info(project)
                break
            #daca se schimba proiectul din combobox se vor afisa datele pentru acel proiect

    def on_files_project_selected(self, project_title):
        if not self.projects:
            return

        for project in self.projects:
            if project["title"] == project_title:
                self.selected_files_project = project
                self.load_project_files(project["project_id"])
                break
            #daca se schimba proiectul din combobox se vor afisa fisierele pentru acel proiect

    def load_project_files(self, project_id):
        try:
            files = self.model.get_files(project_id)
            self.view.display_files(files)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load project files: {str(e)}")

    def save_project_changes(self):
        try:
            project_data = self.view.get_project_data()

            if not project_data:
                return

            success = self.model.update_project(project_data)
            #se insereaza in model luand din view datele

            if success:
                messagebox.showinfo("Success", "Project updated successfully!")
                self.load_user_projects()
            else:
                messagebox.showerror("Error", "Failed to update project")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save project changes: {str(e)}")

    def browse_file(self):
        file_path = filedialog.askopenfilename(
            title="Select File to Upload",
            filetypes=(("All files", "*.*"),)
        )
        #afiseaza calea in entry
        if file_path:
            self.view.new_file_path.delete(0, "end")
            self.view.new_file_path.insert(0, file_path)

    def upload_file(self):
        if not self.selected_files_project:
            messagebox.showerror("Error", "No project selected")
            return

        file_path = self.view.new_file_path.get()
        if not file_path or not os.path.exists(file_path):
            messagebox.showerror("Error", "Please select a valid file")
            return
        #fisierul adaugat nou este uploada in azure si in baza de date preluand numele , tipul si dimensiunea
        #in kb in
        try:
            file_name = os.path.basename(file_path)
            file_size = os.path.getsize(file_path) / 1024
            file_type = os.path.splitext(file_name)[1][1:]

            file_url = self.model.upload_new_to_azure(file_path, file_name)
            #file url contine url-ul returnat de model pentru a insera in tabel
            if file_url:
                self.model.insert_new_file_metadata(
                    self.selected_files_project["project_id"],
                    file_name,
                    file_type,
                    file_url,
                    file_size
                )

                messagebox.showinfo("Success", f"File '{file_name}' uploaded successfully!")

                self.view.new_file_path.delete(0, "end")
                self.load_project_files(self.selected_files_project["project_id"])
            else:
                messagebox.showerror("Error", "Failed to upload file to storage")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to upload file: {str(e)}")

    def download_project_file(self, file):
        try:
            save_path = filedialog.asksaveasfilename(
                title="Save File As",
                defaultextension=f".{file['file_type']}",
                initialfile=file["file_name"],
                filetypes=[(f"{file['file_type'].upper()} files", f"*.{file['file_type']}"), ("All files", "*.*")]
            )
            #salvam calea in care vrem sa salvam si apelam modelul
            if save_path:
                success, message = self.model.download_file(file["file_name"], save_path)

                if success:
                    messagebox.showinfo("Success", message)
                else:
                    messagebox.showerror("Error", message)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to download file: {str(e)}")

    def delete_file(self, file):
        try:
            if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{file['file_name']}'?"):
                success = self.model.delete_file(file["file_id"])

                if success:
                    messagebox.showinfo("Success", f"File '{file['file_name']}' deleted successfully!")
                    self.load_project_files(self.selected_files_project["project_id"])
                else:
                    messagebox.showerror("Error", "Failed to delete file")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete file: {str(e)}")
class StatisticsController:
    def __init__(self, view, model, username):
        self.model = model
        self.view = view
        self.username = username

    def load_data(self):
        print("name",self.username)
        stats = self.model.get_user_statistics(self.username)
        self.view.display_statistics(stats)
    #preia datele din model si le afiseaza in view

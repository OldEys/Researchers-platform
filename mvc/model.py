from tkinter import messagebox # boxuri de mesaje
import os # pentru a identifica calea fisierelor sau a var de env
from mysql.connector.pooling import MySQLConnectionPool #connection pool pentru a permite multiple sesiuni
from dotenv import load_dotenv
import bcrypt # libraria de a cripta stringuri si a le encoda/decoda pe utf-8
from azure.storage.blob import BlobServiceClient #conectarea catre blob storageul din azure
from azure.core.exceptions import AzureError #eroare pentru excepturi
from mysql.connector import Error #.__,__
load_dotenv() # functie care incarca var din fis .env din proiect
from datetime import datetime # pentru transmiterea datei pentru a fi inserata in tabele
class ConnectionPoolManager:
    #clasa pentru a gestiona connection poolul din mysql
    _instance = None
    #variabila care primeste ca valoare clasa ConnectionPoolManager(utilizarea Patternului singleton)
    _pool = None
    def __new__(cls): #constructor care creaza o singura instanta din acea clasa
        #folosit pentru patternul singleton de care avem nevoie deoarece vrem un singur conn pool
        if cls._instance is None:
            #daca nu a fost creata o instanta atunci apelam super(clasa parinte) care apeleaza
            #metoda new rezultand intr-un obiect gol de tipul ConnectionPoolManager
            cls._instance = super(ConnectionPoolManager, cls).__new__(cls)
            cls._instance._create_pool()
            #instanta este asociata cu baza de date din cloud
        return cls._instance
    def _create_pool(self):
        try:
            db_config={
                'host': os.getenv("MYSQL_DB_CONN_HOST"),
                'user': os.getenv("MYSQL_DB_CONN_USER"),
                'password': os.getenv("MYSQL_DB_CONN_PW"),
                'database': os.getenv("MYSQL_DB_CONN_DBNAME"),
                'pool_name': 'research_platform_pool',
                'pool_size': 5,
                'pool_reset_session': True,
                'autocommit': False
            }
            #parametrii de conectare preluati din .env
            self._pool=MySQLConnectionPool(**db_config)
            #initializeaza poolul cu functia MySQLConnectionPool care primeste acesti parametrii
            print("Connection pool created")
        except Exception as e:
            print(f"Error creating connection pool: {e}")
            messagebox.showerror("Connection Pool Error",str(e))
            self._pool=None
    def get_connection(self):
        try:
            if self._pool:
                return self._pool.get_connection()
            #apelam get_connection din mysqlpool
            else:
                raise Exception("Connection pool not created")
        except Exception as e:
            print(f"Error creating connection pool: {e}")
            messagebox.showerror("Connection Pool Error",str(e))
            return None
    def close_connection(self,conn):
        if conn:
            try:
                conn.close()
                #inchidem conexiunea unei anumite sesiuni
            except Exception as e:
                print(f"Error closing connection pool: {e}")
class BaseModel:
    #clasa de baza a modelelor care contine functiile de baza necesare fiecarei dintre ele
    def __init__(self):
        self.pool_manager=ConnectionPoolManager()
        #pool manager va fi un singleton in aceasta clasa care gestioneaza conexiunea
        try:
            self.blob_service_client = BlobServiceClient.from_connection_string(os.getenv("BLOB_CONN_STRING"))
            #variabila care contine numele containerului in care stocam fisierele

            self.container_client = self.blob_service_client.get_container_client(os.getenv("BLOB_NAME"))
            #variabila pentru a avea acces la fisierele din blob
        except AzureError as err:
            messagebox.showerror("Azure Error", str(err))
    def execute_query(self,query,params=None,fetch=False,commit=False,lastrow_id=False):
        #metoda pentru executarea oricarui query,fetch pentru a memora rezultatul(pentru select)
        #commit pentru a le da commit in baza de date (pentru crud),lastrow_id pentru a returna indexul
        #ultimului element din select
        conn=None
        cursor=None
        try:
            #initializam o conexiune
            conn=self.pool_manager.get_connection()
            if not conn:
                return None
            cursor=conn.cursor(dictionary=True)
            #cursor e folosit pentru a executa operatiile pe baza de date returnand un rezultat
            #de tipul dictionar ({'cheie':'valoare'})
            if params:
                cursor.execute(query,params)
            else:
                cursor.execute(query)
            if fetch:
                return cursor.fetchall()
            if commit:
                conn.commit()
            if lastrow_id:
                return cursor.lastrowid
            return True
        except Error as e:
            if conn and commit:
                conn.rollback()
            raise e
        finally:
            self.pool_manager.close_connection(conn)
class LoginModel(BaseModel):
    #modelul pentru partea de login
    def verify_user(self,name,password):
        try:
            query="select password_hash from user where name=%s"
            #selectam hashul parolei utilizatorului memorat in baza de date
            result=self.execute_query(query,(name,),fetch=True)
            if not result:
                return False
            user=result[0]
            stored_hash=user['password_hash'].encode('utf-8')
            #encodam in blob pentru a compara cu bcrypt.checkpw
            if bcrypt.checkpw(password.encode('utf-8'),stored_hash):
                #comparam parolele(bcrypt.checkpw crypteaza automat parola introdusa pentru comparare
                messagebox.showinfo("Login Successful","Login successful")
                return True
            else:
                return False
        except Exception as e:
            print(f"Error verifying user: {e}")
            raise e
class RegisterModel(BaseModel):
    #model pentru inregistrare
    def add_user(self, name, email, password, institution, field_of_research,
                 biography, researcher_start_date, image_path=None):
        try:
            hashed_password=bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            #cripteaza cu algoritmul blowfish parola data ca parametru ,gensalt e folosit pentru a asigura
            #unicitatea parolei
            conn=self.pool_manager.get_connection()
            if not conn:
                return None
            try:
                insert_query="""
                   insert into user (name, email, password_hash, institution, \
                                     field_of_research, biography, researcher_start_date) \
                   values (%s, %s, %s, %s, %s, %s, %s) \
                   """
                self.execute_query(insert_query,(
                    name, email, hashed_password.decode('utf-8'),
                    institution, field_of_research, biography,
                    researcher_start_date
                ),commit=True,lastrow_id=True)
                #insereaza parola in baza de date
                #daca se furnizeaza o imagine (calea locala)
                if image_path:
                    blob_name=f"user_{name}_{os.path.basename(image_path)}"
                    #o uploadam sub forma de sus
                    image_url=self.upload_image_to_blob(image_path,blob_name)
                    #upload_image_to_blob returneaza url-ul din cloud
                    if image_url:
                        update_query="update user set profile_picture_url=%s where name=%s"
                        self.execute_query(update_query,(image_url,name),commit=True)
                messagebox.showinfo("User Registered","User registered successfully")
                return True
            except Error as e:
                conn.rollback()
                raise e
        except Exception as e:
            print(f"Error registering user: {e}")
    def upload_image_to_blob(self,image_path,blob_name):
        try:
            blob_client=self.container_client.get_blob_client(blob_name)
            with open(image_path, "rb") as data:
                blob_client.upload_blob(data,overwrite=True)
            #uploadeaza cu numele dat de blob_name datele binare din imagine si returneaza url-ul dupa
            #acest format
            return f"https://{self.blob_service_client.account_name}.blob.core.windows.net/{self.container_client.container_name}/{blob_name}"
        except Exception as e:
            print(f"Error uploading image: {e}")
            messagebox.showerror("Error uploading image",str(e))
            return None
class MainAppModel(BaseModel):
    #modelul din aplicatia principala cu majoritatea metodelor folosite
    def delete_account(self, username):
        #sterge cont cu tot ce are el(on delete cascade)
        query = "delete from user where name = %s"
        self.execute_query(query, (username,), commit=True)
    def delete_project(self, project_id,username):
        #sterge proiect cu tot ce are el(on delete cascade)
        query = "delete from Project where project_id = %s"
        self.execute_query(query, (project_id,), commit=True)
    def get_projects_by_user(self,username):
        #selectam toate datele proiectelor realizate de catre user
        query=("""
                select p.*
            from project p join works_on w on p.project_id=w.project_id\
            join user u on u.user_id=w.user_id\
            where name=%s\
            """)
        try:
            result=self.execute_query(query,(username,),fetch=True)
            if not result or len(result)==0:
                return None
            else:
                return result
        except Exception as e:
            print(f"Error getting projects: {e}")
            return None
    def get_information_by_user(self,username):
        #selectam informatiile dupa nume
        query=("""
            select * from user where name=%s\
            """)
        try:
            result=self.execute_query(query,(username,),fetch=True)
            if not result:
                return None
            else:
                return result
        except Exception as e:
            print(f"Error getting information: {e}")
    def get_files(self,project_id):
        #selectam toate fisierele utilizate de proiectul cu acel id
        query=("""
               select * from file where project_id=%s\
               """)
        try:
            result=self.execute_query(query,(project_id,),fetch=True)
            if not result:
                return None
            else:
                return result
        except Exception as e:
            print(f"Error getting files: {e}")

    def download_file(self, blob_name, save_path):
        #deschide folderul din save_path in modul scriere binara si descarca ce e in blob
        try:
            with open(save_path, "wb") as download_file:
                download_stream = self.container_client.download_blob(blob_name)
                download_file.write(download_stream.readall())
            return True, f"File '{blob_name}' downloaded successfully!"
        #returnam status si mesajul
        except Exception as e:
            return False, str(e)
    def get_all_posts(self,project_id):
        #selecteaza toate postarile cu toate informatiile precum si cine le a scris
        query="""
            select distinct p.*,u.name from post p join works_on w on p.user_id=w.user_id join user u on 
            u.user_id=w.user_id where p.project_id=%s order by created_at desc
               """
        try:
            result=self.execute_query(query,(project_id,),fetch=True)
            if not result:
                return []
            else:
                return result
        except Exception as e:
            print(f"Error getting posts: {e}")
            return []
    def get_all_comments(self,post_id):
        #la fel ca la get_all_posts doar ca pentru comentarii
        query="""
            select distinct c.*,u.name FROM comment c join post p on p.post_id=c.post_id join works_on w on p.user_id=w.user_id join
            user u on u.user_id=w.user_id
            where p.post_id =%s order by created_at desc
               """
        try:
            result=self.execute_query(query,(post_id,),fetch=True)
            if not result:
                return []
            else:
                return result
        except Exception as e:
            print(f"Error getting comments: {e}")
            return []
    def upload_to_azure(self, file_path, blob_name):
        #uploadeaza fisierele incarcate in aplicatie in cloud
        try:
            blob_client = self.container_client.get_blob_client(blob_name)
            #variabila care contine viitorul nume al fisierului
            #deschide calea locala in modul citire si scrie tot in cloud
            with open(file_path, "rb") as data:
                blob_client.upload_blob(data, overwrite=True)
            return blob_client.url
        except Exception as e:
            print(f"Error uploading to Azure: {e}")
            return None

    def insert_file_metadata(self, project_id, file_name, file_type, file_url, file_size):
        #insereaza in tabelul cu fisiere toate fisierele adaugate
        query = """
                insert into File (project_id, file_name, file_type, file_url, file_size)
                values (%s, %s, %s, %s, %s) \
                """
        try:
            self.execute_query(query, (project_id, file_name, file_type, file_url, file_size),commit=True)
        except Exception as e:
            print(f"Error inserting file metadata: {e}")

    def insert_project(self, title, start_date, domain, description):
        #insereaza proiectul dupa datele luate din view
        query = """
                insert into Project (title, start_date, domain, description)
                values (%s, %s, %s, %s) \
                """
        return self.execute_query(query, (title, start_date, domain, description),commit=True,lastrow_id=True)
    def assign_user_to_project(self, username, project_id):
        #insereaza in works_on in functie de userul care a creat proiectul si de colaboratorii pe acel proiect
        query_user_id="""
            select user_id from user where name=%s\
        """
        user_id_result = self.execute_query(query_user_id,(username,),fetch=True)
        if not user_id_result:
            return None
        else:
            user_id=user_id_result[0]['user_id']
            print(user_id)
            query = "insert into works_on (user_id, project_id,start_date) values (%s, %s ,%s)"
            self.execute_query(query, (user_id, project_id,datetime.today().date()),commit=True)
    def add_comment(self, post_id,project_id,username,body):
        #selecteaza idul dupa nume apoi insereaza in comment
        query_user_id = """ \
                        select user_id \
                        from user \
                        where name = %s \
                      """
        user_id_result = self.execute_query(query_user_id, (username,), fetch=True)
        if not user_id_result:
            return None
        else:
            user_id = user_id_result[0]['user_id']
            query = """
            insert into comment(post_id,project_id,user_id,body) values (%s,%s,%s, %s)
            """
            self.execute_query(query, (post_id,project_id,user_id,body),commit=True)
    def add_post(self, project_id, username, title, body):
        #selecteaza idul dupa nume apoi insereaza in post
        query_user_id = """ \
                        select user_id \
                        from user \
                        where name = %s \
                      """
        user_id_result = self.execute_query(query_user_id, (username,), fetch=True)
        if not user_id_result:
            return None
        else:
            user_id = user_id_result[0]['user_id']
            query = """
            insert into post(project_id,user_id,title,body) values (%s,%s, %s,%s)

            """
            self.execute_query(query, (project_id,user_id,title,body),commit=True)

    def check_user_exists(self, username):
        #verifica daca colaboratorul cu numele introdus chiar exista
        query = "select user_id from user where name = %s"
        try:
            result = self.execute_query(query, (username,), fetch=True)
            return result is not None and len(result) > 0
        except Exception as e:
            print(f"Error checking user existence: {e}")
            return False

class UserSearchModel(BaseModel):
    def search_users(self, search_term):
        #cauta dupa nume institutie sau domeniu userii
        query = """
                select user_id, \
                       name, \
                       email, \
                       institution, \
                       field_of_research,
                       biography, \
                       researcher_start_date, \
                       profile_picture_url
                from user
                where name like %s
                   or institution like %s
                   or field_of_research like %s
                order by name asc \
                """
        search_param = f"%{search_term}%"
        #formateaza pentru a fi folosit de keywordu like din sql (%-inlocuieste mai multe caractere sau niciunul)
        #ex: abcd like %bc% returneaza true
        try:
            result = self.execute_query(query, (search_param, search_param, search_param), fetch=True)
            if not result:
                return []
            else:
                return result
        except Exception as e:
            print(f"Error searching users: {e}")
            return []

    def get_user_projects(self, user_id):
        #preia toate proiectele de la userul cu acel id
        query = """
                select  p.*
                from project p
                         join works_on w on p.project_id = w.project_id
                where w.user_id = %s \
                """
        try:
            result = self.execute_query(query, (user_id,), fetch=True)
            if not result:
                return []
            else:
                return result
        except Exception as e:
            print(f"Error getting user projects: {e}")
            return []
class SettingsModel(BaseModel):
    def update_user_profile(self, username, profile_data):
        #modifica informatiile utilizatorului,profile data are ca cheie numele labelurilor si ca valoare
        #ce a introdus utiliztorul
        user_id_query = "select user_id from user where name = %s"
        try:
            result = self.execute_query(user_id_query, (username,), fetch=True)
            if not result:
                return False

            user_id = result[0]['user_id']
            #update fiels contine sintaxa de modificare (set name=%s) iar params valorile

            update_fields = []
            params = []

            for field, value in profile_data.items():
                if field != 'user_id':
                    update_fields.append(f"{field} = %s")
                    params.append(value)

            if not update_fields:
                return False

            params.append(user_id)

            update_query = f"""
                update user
                set {', '.join(update_fields)}
                where user_id = %s
            """
            #construieste querry ul unde metoda join uneste toate elementele intr un singur string
            #prin virgula

            self.execute_query(update_query, tuple(params), commit=True)
            return True

        except Exception as e:
            print(f"Error updating user profile: {e}")
            return False

    def update_project(self, project_data):
        #updateaza informatiile proiectului cu cele noi
        #restul e ca mai sus
        try:
            project_id = project_data.pop('project_id', None)
            if not project_id:
                return False

            update_fields = []
            params = []

            for field, value in project_data.items():
                update_fields.append(f"{field} = %s")
                params.append(value)

            if not update_fields:
                return False

            params.append(project_id)

            update_query = f"""
                update project
                set {', '.join(update_fields)}
                where project_id = %s
            """

            self.execute_query(update_query, tuple(params), commit=True)
            return True

        except Exception as e:
            print(f"Error updating project: {e}")
            return False

    def delete_file(self, file_id):
        #sterge un fisier din proiect
        try:
            query = "select file_name, file_url from file where file_id = %s"
            file_info = self.execute_query(query, (file_id,), fetch=True)

            if not file_info:
                return False

            file_name = file_info[0]["file_name"]

            try:
                blob_client = self.container_client.get_blob_client(file_name)
                blob_client.delete_blob()
                #sterge din cloud fis cu numele memorat in blob_client
            except Exception as e:
                print(f"Warning: Could not delete blob from storage: {e}")

            delete_query = "delete from file where file_id = %s"
            self.execute_query(delete_query, (file_id,), commit=True)

            return True

        except Exception as e:
            print(f"Error deleting file: {e}")
            return False
    def get_projects_by_user(self,username):
        #la fel ca in mainappmodel
        query=("""
                select p.*
            from project p join works_on w on p.project_id=w.project_id\
            join user u on u.user_id=w.user_id\
            where name=%s\
            """)
        try:
            result=self.execute_query(query,(username,),fetch=True)
            if not result or len(result)==0:
                return None
            else:
                return result
        except Exception as e:
            print(f"Error getting projects: {e}")
            return None
    def get_information_by_user(self,username):
        #la fel ca in mainappmodel

        query=("""
            select * from user where name=%s\
            """)
        try:
            result=self.execute_query(query,(username,),fetch=True)
            if not result:
                return None
            else:
                return result
        except Exception as e:
            print(f"Error getting information: {e}")
    def get_files(self,project_id):
        #la fel ca in mainappmodel

        query=("""
               select * from file where project_id=%s\
               """)
        try:
            result=self.execute_query(query,(project_id,),fetch=True)
            if not result:
                return None
            else:
                return result
        except Exception as e:
            print(f"Error getting files: {e}")

    def update_image_to_blob(self, image_path, blob_name):
        #la fel ca in mainappmodel

        try:
            blob_client = self.container_client.get_blob_client(blob_name)
            with open(image_path, "rb") as data:
                blob_client.upload_blob(data, overwrite=True)
            return f"https://{self.blob_service_client.account_name}.blob.core.windows.net/{self.container_client.container_name}/{blob_name}"
        except Exception as e:
            print(f"Error uploading image: {e}")
            messagebox.showerror("Error uploading image", str(e))
            return None
    def upload_new_to_azure(self, file_path, blob_name):
        #la fel ca in mainappmodel

        try:
            blob_client = self.container_client.get_blob_client(blob_name)
            with open(file_path, "rb") as data:
                blob_client.upload_blob(data, overwrite=True)
            return blob_client.url
        except Exception as e:
            print(f"Error uploading to Azure: {e}")
            return None
    def insert_new_file_metadata(self, project_id, file_name, file_type, file_url, file_size):
        #la fel ca in mainappmodel


        query = """
                insert into File (project_id, file_name, file_type, file_url, file_size)
                values (%s, %s, %s, %s, %s) \
                """
        try:
            self.execute_query(query, (project_id, file_name, file_type, file_url, file_size),commit=True)
        except Exception as e:
            print(f"Error inserting file metadata: {e}")
    def download_file(self, blob_name, save_path):
        #la fel ca in mainappmodel

        try:
            with open(save_path, "wb") as download_file:
                download_stream = self.container_client.download_blob(blob_name)
                download_file.write(download_stream.readall())
            return True, f"File '{blob_name}' downloaded successfully!"
        except Exception as e:
            return False, str(e)
class StatisticsModel(BaseModel):
    #selecteaza diferite statistici numar de proiecte,postari,comentarii,fisiere pe care le gestioneaza
    def get_projects_count(self, username):
        query = """
            select count(*) from works_on w
            join user u on w.user_id = u.user_id
            where u.name = %s
        """
        res = self.execute_query(query, (username,), fetch=True)
        if res:
            return res[0]['count(*)']
        else:
            return 0
    def get_posts_count(self, username):
        query = """
            select count(*) 
            from post p
            join user u on p.user_id = u.user_id
            where u.name = %s;
        """
        res = self.execute_query(query, (username,), fetch=True)
        if res:
            return res[0]['count(*)']
        else:
            return 0
    def get_comments_count(self, username):
        query = """
            select count(*) 
            from comment c
            join user u on c.user_id = u.user_id
            where u.name = %s;
        """
        res = self.execute_query(query, (username,), fetch=True)
        if res:
            return res[0]['count(*)']
        else:
            return 0
    def get_files_count(self, username):
        query = """
            select count(*) from file f
            join works_on w on f.project_id = w.project_id
            join user u on w.user_id = u.user_id
            where u.name = %s
        """
        res = self.execute_query(query, (username,), fetch=True)
        if res:
            return res[0]['count(*)']
        else:
            return 0

    def get_research_start_date(self, username):
        query = """
            select researcher_start_date from user where name = %s
        """
        res = self.execute_query(query, (username,), fetch=True)

        if res:
            return res[0]['researcher_start_date']
        else:
            return 0
    def get_user_statistics(self, username):
        #returnam un dictionar in care valorile sunt functiile apelate mai sus
        try:
            return {
                    "projects_count": self.get_projects_count(username),
                    "posts_count": self.get_posts_count(username),
                    "comments_count": self.get_comments_count(username),
                    "files_count": self.get_files_count(username),
                    "research_start_date": self.get_research_start_date(username)
                }
        except Exception as e:
            print(f"Error fetching user statistics: {e}")
            return {}

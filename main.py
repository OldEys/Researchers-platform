from mvc.controller import AppCoordinator
import customtkinter as ctk
# customtkinter - librarie derivata din tkinter care permite tema cromatica si
#mai multe customizari pentru widgeturi

def main():
    root = ctk.CTk()
    root.minsize(650, 600)

    def center(win):
        win.update_idletasks()# updateaza windowul cand se produce un eveniment idle
        w =win.winfo_screenwidth()
        x = (w - win.winfo_width()) /2
        y =0
        win.geometry(f"+{x}+{y}")

    center(root)

    AppCoordinator(root)#clasa care leaga toate celelalte clase definita in controller
    root.bind("<Escape>", lambda e: root.destroy())
    #inchide aplicatia la apasarea tastei escape
    root.mainloop()#metoda din tk esentiala pentru rularea windowului tk

if __name__ == '__main__':
    main()

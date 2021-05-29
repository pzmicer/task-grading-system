import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import dbmanager
from MainForm import MainForm


class SignInForm:

    def __init__(self):
        self.__connection = dbmanager.get_connection()
        self.__cursor = self.__connection.cursor()

        self.__root = tk.Tk()
        self.__root.title("NE.EDU.FPMI")
        self.__width = 400
        self.__height = 300
        self.__root.wm_minsize(self.__width, self.__height)
        self.__root.geometry("+{}+{}".
                             format(int(self.__root.winfo_screenwidth() / 2 - self.__width / 2),
                                    int(self.__root.winfo_screenheight() / 2 - self.__height / 2)))
        self.__root.resizable(False, False)
        frame = tk.Frame(master=self.__root)

        lbl_title = tk.Label(master=frame, text="Authorization", font="Times 16")
        lbl_title.grid(row=0, column=0, columnspan=2, pady="5")

        lbl_login = tk.Label(master=frame, text="Login", font="Times 16")
        lbl_login.grid(row=1, column=0, pady="5", padx="10")
        self.__login_message = tk.StringVar()
        self.__ent_login = tk.Entry(master=frame, textvariable=self.__login_message, font="Times 16")
        self.__ent_login.grid(row=1, column=1, pady="5")

        lbl_password = tk.Label(master=frame, text="Password", font="Times 16")
        lbl_password.grid(row=2, column=0, pady="5", padx="10")
        self.__password_message = tk.StringVar()
        self.__ent_password = tk.Entry(master=frame, textvariable=self.__password_message,
                                       font="Times 16", show="*")
        self.__ent_password.grid(row=2, column=1, pady="5")

        __sign_in = tk.Button(master=frame, text="Sign in",  background="#5b9bd5", foreground="white",
                              padx="10", pady="5", font="Times 14", command=self.__sign_in_handler)
        __sign_in.grid(row=3, column=0, padx="20", pady="20", columnspan=2)

        frame.place(relx=0.5, rely=0.5, anchor="c")

        self.__root.mainloop()

    def __sign_in_handler(self):
        try:
            if self.__login_message.get().replace(" ", "") == "" or \
                    self.__password_message.get().replace(" ", "") == "":
                raise Exception("Empty fields")

            self.__cursor.execute('select * from "user" where login=%s;', (self.__login_message.get().strip(),))
            user = self.__cursor.fetchone()

            if user is None:
                raise Exception("Invalid login")

            if user['password'] != self.__password_message.get().strip():
                raise Exception("Invalid password")

            self.__root.withdraw()
            self.__ent_login.delete(0, 'end')
            self.__ent_password.delete(0, 'end')

            MainForm(self.__root, self.__connection, self.__cursor, user)
        except Exception as e:
            messagebox.showinfo("Exception", e)

    def __del__(self):
        self.__connection.close()
        self.__cursor.close()

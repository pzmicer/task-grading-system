import tkinter as tk
from tkinter import messagebox
from tkinter import font
import tkcalendar


class MainForm:

    def __init__(self, root: tk.Tk, connection, cursor, user):
        self.connection = connection
        self.cursor = cursor
        self.user = user
        self.__root = root

        self.__form = tk.Toplevel(root)
        self.__width = 650
        self.__height = 550
        self.__form.wm_minsize(self.__width, self.__height)
        self.__form.geometry('+{}+{}'.
                             format(int(self.__form.winfo_screenwidth() / 2 - self.__width / 2),
                                    int(self.__form.winfo_screenheight() / 2 - self.__height / 2)))
        self.__form.protocol('WM_DELETE_WINDOW', lambda: root.destroy())

        self.title_font = tk.font.Font(family='Times', size=20, weight='bold')
        self.regular_font = tk.font.Font(family='Times', size=14)

        self.__form.grid_columnconfigure(0, weight=1)
        self.__form.grid_rowconfigure(0, weight=1)

        self.frames = []
        self.show_frame(CoursesFrame(self.__form, self))

        menu = tk.Menu()
        system_menu = tk.Menu(tearoff=0)
        system_menu.add_command(label="Exit", command=lambda: self.__exit())
        menu.add_cascade(label="System", menu=system_menu)
        self.__form.config(menu=menu)

    def show_frame(self, frame: tk.Frame):
        self.frames.append(frame)
        frame.grid(row=0, column=0, sticky='nsew')

    def __exit(self):
        self.__form.destroy()
        self.__root.deiconify()

    def back(self):
        self.frames.pop().destroy()


class CoursesFrame(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        label = tk.Label(self, text='Welcome, {name} {surname}!\nAvailable courses'
                         .format(name=controller.user['surname'], surname=controller.user['name']),
                         font=controller.title_font)
        label.grid(row=0, column=0)

        if controller.user['role'] == 0:
            controller.cursor.execute('select * from courses;')
        elif controller.user['role'] == 1:
            controller.cursor.execute('select * from courses where courses.teacher_id = %s;', (controller.user['id'],))
        courses = controller.cursor.fetchall()

        listbox = tk.Listbox(self, font=controller.regular_font)

        for i in range(len(courses)):
            listbox.insert(i, courses[i]['name'])

        listbox.bind('<Double-Button>',
                     lambda x:
                     controller.show_frame(TasksFrame(parent, controller, courses[listbox.curselection()[0]])))
        listbox.grid(row=1, column=0, sticky='nsew')


class TasksFrame(tk.Frame):

    def __init__(self, parent, controller, course):
        tk.Frame.__init__(self, parent)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        self.__parent = parent
        self.__controller = controller
        self.__course = course

        btn_back = tk.Button(self, text='Back', command=lambda: controller.back())
        btn_back.grid(row=0, column=0, sticky='nw')

        lbl_title = tk.Label(self, text='Course: ' + course['name'], font=controller.title_font)
        lbl_title.grid(row=1, column=0, sticky='n')

        lbl_description = tk.Label(self, text='Description: ' + course['description'], font=controller.regular_font)
        lbl_description.grid(row=2, column=0)

        controller.cursor.execute('select * from task where task.course_id = %s;', (course['id'],))
        tasks = controller.cursor.fetchall()

        listbox = tk.Listbox(self, font=controller.regular_font)

        for i in range(len(tasks)):
            listbox.insert(i, tasks[i]['name'])

        listbox.bind('<Double-Button>',
                     lambda x:
                     controller.show_frame(self.__choose_next(parent, controller, tasks[listbox.curselection()[0]])))
        listbox.grid(row=3, column=0, sticky='nsew')

        if self.__controller.user['role'] == 1:
            btn_create = tk.Button(self, text='Create', padx="5", pady="5",command=
                                   lambda: self.__controller.show_frame(CreateTaskFrame(parent, controller, course, self)))
            btn_create.grid(row=4)

        # btn_refresh = tk.Button(self, text='Refresh', command=self.refresh)
        # btn_refresh.grid(row=5)

    def refresh(self):
        # self.__controller.back()
        # self.__controller.show_frame(TasksFrame(self.__parent, self.__controller, self.__course))
        self.destroy()
        self.__init__(self.__parent, self.__controller, self.__course)
        self.grid(row=0, sticky='nsew')

    def __choose_next(self, parent, controller, task):
        if self.__controller.user['role'] == 0:
            return AnswerFrame(parent, controller, task)
        elif controller.user['role'] == 1:
            return ShowAllAnswersFrame(parent, controller, task)


class ShowAllAnswersFrame(tk.Frame):

    def __init__(self, parent, controller, task):
        tk.Frame.__init__(self, parent)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        btn_back = tk.Button(self, text='Back', command=lambda: controller.back())
        btn_back.grid(row=0, sticky='nw')

        lbl_title = tk.Label(self, text='Task: ' + task['name'], font=controller.title_font)
        lbl_title.grid(row=1, sticky='n')

        lbl_description = tk.Label(self, text='Description: ' + task['description'], font=controller.regular_font)
        lbl_description.grid(row=2)

        controller.cursor.execute('''
            select *
            from answer
                left join "user"
                    on answer.student_id="user".id
            where answer.task_id=%s''', (task['id'],))
        answers = controller.cursor.fetchall()

        listbox = tk.Listbox(self, font=controller.regular_font)

        for i in range(len(answers)):
            listbox.insert(i, f"{answers[i]['surname']} {answers[i]['name']}")

        listbox.bind('<Double-Button>',
                     lambda x:
                     controller.show_frame(ShowAnswerFrame(parent, controller,
                                                           task, answers[listbox.curselection()[0]])))
        listbox.grid(row=3, sticky='nsew')


class ShowAnswerFrame(tk.Frame):

    def __init__(self, parent, controller, task, answer):
        tk.Frame.__init__(self, parent)

        self.__controller = controller
        self.__answer = answer
        self.__task = task

        btn_back = tk.Button(self, text='Back', command=lambda: controller.back())
        btn_back.grid(row=0, column=0, sticky='nw')

        lbl_title = tk.Label(self, text=f"Student: {answer['surname']} {answer['name']}", font=controller.title_font)
        lbl_title.grid(row=1, columnspan=3, sticky='n')

        text_answer = tk.Text(self, font=controller.regular_font)
        text_answer.insert('1.0', answer['body'])
        text_answer.grid(row=2, columnspan=3)
        text_answer.config(state='disabled')

        self.__ent_mark = tk.Entry(self)
        self.__ent_mark.grid(row=3, column=0)

        if answer['score'] is not None:
            self.__ent_mark.config(text=answer['score'])

        btn_mark = tk.Button(self, text='Save mark', command=self.__mark)
        btn_mark.grid(row=3, column=1)

        btn_delete_mark = tk.Button(self, text='Delete mark', command=self.__delete_mark)
        btn_delete_mark.grid(row=3, column=2)

    def __mark(self):
        try:
            mark = int(self.__ent_mark.get())
            if mark < 0:
                messagebox.showwarning(message='Negative mark!')
            elif mark > self.__task['max_score']:
                messagebox.showwarning(message='Mark should be less than maximum')
            else:
                self.__controller.cursor.execute('update answer set score=%s '
                                                 'where answer.student_id=%s and answer.task_id=%s',
                                                 (mark, self.__answer['student_id'], self.__answer['task_id']))
                self.__controller.connection.commit()
                self.__controller.back()

        except ValueError:
            messagebox.showerror(message='Please, enter integer')

    def __delete_mark(self):
        self.__controller.cursor.execute('update answer set score = null;')


class AnswerFrame(tk.Frame):

    def __init__(self, parent, controller, task):
        tk.Frame.__init__(self, parent)
        # self.grid_columnconfigure(0, weight=1)
        # self.grid_rowconfigure(0, weight=1)

        self.__parent = parent
        self.__task = task
        self.__controller = controller

        btn_back = tk.Button(self, text='Back', command=lambda: controller.back())
        btn_back.grid(row=0, column=0, sticky='nw')

        lbl_title = tk.Label(self, text='Task: ' + task['name'], font=controller.title_font)
        lbl_title.grid(row=1, columnspan=2, sticky='n')

        lbl_description = tk.Label(self, text=f"Description: {task['description']}",
                                   font=controller.regular_font)
        lbl_description.grid(row=2, columnspan=2, sticky='w')

        lbl_deadline = tk.Label(self, text=f"Deadline: {task['deadline']}", font=controller.regular_font)
        lbl_deadline.grid(row=0, column=1, sticky='ne')

        self.__lbl_answer = tk.Label(self, text='Enter your answer', font=controller.regular_font)
        self.__lbl_answer.grid(row=3, columnspan=2)

        self.__text_answer = tk.Text(self, font=controller.regular_font)
        self.__text_answer.grid(row=4, columnspan=2)

        controller.cursor.execute('select * from answer where task_id=%s and student_id=%s',
                                  (task['id'], controller.user['id']))
        self.__answer = controller.cursor.fetchone()
        if self.__answer is not None:
            self.__text_answer.insert('1.0', self.__answer['body'])
            if self.__answer['score'] is None:
                self.__lbl_answer.config(text='Answered (You can change your answer)', bg='#95c551')
            else:
                self.__lbl_answer.config(text=f"Marked ({self.__answer['score']}/{task['max_score']})", bg='#716ddb')
                self.__text_answer.config(state='disabled')
                return

        btn_save = tk.Button(self, text='Save', padx="5", pady="5", width=50,
                             command=lambda: self.__save_answer(self.__text_answer.get('1.0', tk.END)))
        btn_save.grid(row=5, column=0)

        btn_delete = tk.Button(self, text='Delete', padx="5", pady="5", width=50, command=self.__delete_answer)
        btn_delete.grid(row=5, column=1)

    def __save_answer(self, new_body):
        if new_body == '\n':
            messagebox.showwarning(message='Empty answer')
            return
        if self.__answer is None:
            self.__controller.cursor.execute('insert into answer values(%s, %s, %s)',
                                             (self.__task['id'], self.__controller.user['id'], new_body))
        else:
            self.__controller.cursor.execute('update answer set body=%s where  task_id=%s and student_id=%s',
                                             (new_body, self.__task['id'], self.__controller.user['id']))
        self.__controller.connection.commit()
        self.__controller.back()

    def __delete_answer(self):
        if self.__answer is None:
            messagebox.showinfo(message='You haven\'t answered yet')
            return

        self.__controller.cursor.execute('delete from answer where task_id=%s and student_id=%s',
                                         (self.__task['id'], self.__controller.user['id']))
        self.__controller.connection.commit()

        self.__controller.back()
        self.__init__(self.__parent, self.__controller, self.__task)
        self.__controller.show_frame(self)

        # self.__lbl_answer.destroy()
        # self.__lbl_answer = tk.Label(text='Enter your answer')
        # self.__lbl_answer.grid(row=3, columnspan=2)
        # self.__text_answer.delete('1.0', 'end')


class CreateTaskFrame(tk.Frame):

    def __init__(self, parent, controller, course, tasks_frame):
        tk.Frame.__init__(self, parent)

        self.__controller = controller
        self.__course = course
        self.__tasks_frame = tasks_frame

        self.__btn_back = tk.Button(self, text='Back', command=lambda: controller.back())
        self.__btn_back.grid(row=0, column=0, sticky='nw')

        self.__lbl_title = tk.Label(self, text='Course: ' + course['name'], font=controller.title_font)
        self.__lbl_title.grid(row=1)

        self.__lbl_name = tk.Label(self, text='Name', font=controller.regular_font)
        self.__lbl_name.grid(row=2)

        self.__ent_name = tk.Entry(self, font=controller.regular_font)
        self.__ent_name.grid(row=3)

        self.__lbl_max_score = tk.Label(self, text='Max score', font=controller.regular_font)
        self.__lbl_max_score.grid(row=4)

        self.__ent_max_score = tk.Entry(self, font=controller.regular_font)
        self.__ent_max_score.grid(row=5)

        self.__lbl_description = tk.Label(self, text='Description', font=controller.regular_font)
        self.__lbl_description.grid(row=6)

        self.__text_description = tk.Text(self, font=controller.regular_font)
        self.__text_description.grid(row=7)

        self.__lbl_deadline = tk.Label(self, text='Deadline', font=controller.regular_font)
        self.__lbl_deadline.grid(row=8)

        self.__deadline = tkcalendar.DateEntry(self)
        self.__deadline.grid(row=9)

        self.__btn_create = tk.Button(self, text='Create', font=controller.regular_font, command=self.__create)
        self.__btn_create.grid(row=10)

    def __create(self):
        try:
            self.__controller.cursor.execute('select max(id) from task;')
            max_id = self.__controller.cursor.fetchone()
            self.__controller.cursor.execute('insert into task values(%s, %s, %s, %s, %s, %s);',
                                             (max_id[0]+1,
                                              self.__ent_name.get(),
                                              self.__text_description.get('1.0', 'end'),
                                              self.__deadline.get(),
                                              self.__course['id'],
                                              int(self.__ent_max_score.get())))
            self.__controller.back()
            self.__tasks_frame.refresh()
        except Exception as e:
            messagebox.showinfo(message=e)

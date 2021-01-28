from tkinter import messagebox
from tkinter import ttk
from tkinter import *

from datetime import datetime, timedelta

import sqlite3
import winsound as ws

con = sqlite3.connect('database.db')
cur = con.cursor()

_ALARM_GUI_RUNNING = False
_DISABLED_ALARM = False


class App(object):

    def __init__(self, master):
        self.root = master
        self.root.protocol('WM_DELETE_WINDOW', self.on_closing)

        # Style #
        style = styling()
        style.theme_use('dark')

        self.reset_handled = True

        # Validation #
        validateHr = self.root.register(self.validate_hr)
        validateHr12hrf = self.root.register(self.validate_hr_12hrf)
        validateMS = self.root.register(self.validate_min_sec)

        # Tabs #
        self.tabs = ttk.Notebook(self.root)
        self.tabs.pack(fill='both', expand=True)

        self.schedule_time_tab = ttk.Frame(self.tabs)
        self.no_disturb_time_tab = ttk.Frame(self.tabs)
        self.schedules_tab = ttk.Frame(self.tabs)

        self.tabs.add(self.schedule_time_tab, text='Schedule Timer')
        self.tabs.add(self.no_disturb_time_tab,
                      text='Do Not Disturb')
        self.tabs.add(self.schedules_tab, text='Schedules')

        # Frames #
        self.time_frame = Frame(
            self.schedule_time_tab, width=500, height=200, bg='#181818')
        self.time_frame.pack(fill=X)

        self.message_frame = Frame(
            self.schedule_time_tab, width=500, height=150, bg='#181818')
        self.message_frame.pack(fill=X)

        self.do_not_disturb_frame = Frame(
            self.no_disturb_time_tab, width=500, height=370, bg='#181818')
        self.do_not_disturb_frame.pack(fill=X)

        self.schedules_frame = Frame(
            self.schedules_tab, width=500, height=300, bg='#181818')
        self.schedules_frame.pack(fill=BOTH, expand=True)

        # Time Frame Components #
        # Sub Heading
        self.set_lbl = Label(
            self.time_frame, text='Set Time:', font=('Modern', 22, 'bold'), bg='#181818', fg='white')
        self.set_lbl.place(x=60, y=30)

        # Entries
        self.ent_hour = Entry(
            self.time_frame, font=('Modern', 20, 'bold'), insertbackground='white',
            fg='white', bg='#414141', width=4, justify='center', validate='key',
            validatecommand=(validateHr, '%P'), relief=RIDGE, bd=4)
        self.ent_hour.place(x=80, y=85)
        self.ent_hour.insert(INSERT, '0')
        self.ent_hour.bind('<FocusOut>', self.entry_focus_out_handler)

        self.ent_min = Entry(
            self.time_frame, font=('Modern', 20, 'bold'), insertbackground='white',
            fg='white', bg='#414141', width=4, justify='center', validate='key',
            validatecommand=(validateMS, '%P'), relief=RIDGE, bd=4)
        self.ent_min.place(x=250, y=85)
        self.ent_min.insert(INSERT, '0')
        self.ent_min.bind('<FocusOut>', self.entry_focus_out_handler)

        self.ent_sec = Entry(
            self.time_frame, font=('Modern', 20, 'bold'), insertbackground='white',
            fg='white', bg='#414141', width=4, justify='center', validate='key',
            validatecommand=(validateMS, '%P'), relief=RIDGE, bd=4)
        self.ent_sec.place(x=420, y=85)
        self.ent_sec.insert(INSERT, '0')
        self.ent_sec.bind('<FocusOut>', self.entry_focus_out_handler)

        # Entry Labels
        self.hour_lbl = Label(
            self.time_frame, text='Hours', fg='white', font='Modern 20 bold', bg='#181818')
        self.hour_lbl.place(x=82, y=135)

        self.min_lbl = Label(
            self.time_frame, text='Minutes', fg='white', font='Modern 20 bold', bg='#181818')
        self.min_lbl.place(x=242, y=135)

        self.sec_lbl = Label(
            self.time_frame, text='Seconds', fg='white', font='Modern 20 bold', bg='#181818')
        self.sec_lbl.place(x=410, y=135)

        # Colons
        self.colon = PhotoImage(file='Images/colon.png')
        self.colon_lbl1 = Label(
            self.time_frame, image=self.colon, bg='#181818')
        self.colon_lbl1.place(x=180, y=88)

        self.colon_lbl2 = Label(
            self.time_frame, image=self.colon, bg='#181818')
        self.colon_lbl2.place(x=350, y=88)

        #
        # Message Frame Components #
        # Sub Heading
        self.message_lbl = Label(
            self.message_frame, text='Message:', fg='white', font=('Modern', 22, 'bold'), bg='#181818')
        self.message_lbl.place(x=60, y=10)

        # Message Area
        self.message_area = Text(
            self.message_frame, width=40, height=6, bg='#414141',
            fg='white', font=('Modern', 18, 'bold'), wrap=WORD, insertbackground='white')
        self.message_area.place(x=60, y=50)

        # Do Not Disturb
        self.usr_do_not_disturb = BooleanVar()
        self.do_not_disturb_ckbox = ttk.Checkbutton(
            self.message_frame, text='Do Not Disturb', cursor='hand2', variable=self.usr_do_not_disturb)
        self.usr_do_not_disturb.set(False)
        self.do_not_disturb_ckbox.place(x=377, y=19)

        #
        # Buttons #
        self.save_btn = Button(
            self.schedule_time_tab, text='Save', font=('Modern', 15, 'bold'), bg='#414141', relief=FLAT, fg='white', width=13, command=self.Save)
        self.save_btn.pack(padx=(61, 0), pady=(20, 0), side='left')

        self.restart_alarm_btn = Button(
            self.schedule_time_tab, text='Restart Alarm', font=('Modern', 15, 'bold'), bg='#414141', relief=FLAT, fg='white', width=13, command=self.restart)
        self.restart_alarm_btn.pack(padx=(0, 67), pady=(20, 0), side='right')

        #
        # Do Not Disturb Frame #
        # "From" Heading
        self.from_lbl = Label(self.do_not_disturb_frame,
                              text='From:', font=('Modern', 22, 'bold'), bg='#181818', fg='white')
        self.from_lbl.place(x=60, y=30)

        # "From" Entries
        self.from_hr = Entry(self.do_not_disturb_frame, font=('Modern', 20, 'bold'), insertbackground='white',
                             fg='white', bg='#414141', width=4, justify='center', validate='key',
                             validatecommand=(validateHr12hrf, '%P'), relief=RIDGE, bd=4)
        self.from_hr.place(x=75, y=85)
        self.from_hr.insert(INSERT, '0')
        self.from_hr.bind('<FocusOut>', self.entry_focus_out_handler)

        self.from_min = Entry(self.do_not_disturb_frame, font=('Modern', 20, 'bold'), insertbackground='white',
                              fg='white', bg='#414141', width=4, justify='center', validate='key',
                              validatecommand=(validateMS, '%P'), relief=RIDGE, bd=4)
        self.from_min.place(x=245, y=85)
        self.from_min.insert(INSERT, '0')
        self.from_min.bind('<FocusOut>', self.entry_focus_out_handler)

        self.from_sec = Entry(self.do_not_disturb_frame, font=('Modern', 20, 'bold'), insertbackground='white',
                              fg='white', bg='#414141', width=4, justify='center', validate='key',
                              validatecommand=(validateMS, '%P'), relief=RIDGE, bd=4)
        self.from_sec.place(x=415, y=85)
        self.from_sec.insert(INSERT, '0')
        self.from_sec.bind('<FocusOut>', self.entry_focus_out_handler)

        # "From" Entry Labels
        self.from_hr_lbl = Label(
            self.do_not_disturb_frame, text='Hours', fg='white', font='Modern 20 bold', bg='#181818')
        self.from_hr_lbl.place(x=77, y=135)

        self.from_min_lbl = Label(
            self.do_not_disturb_frame, text='Minutes', fg='white', font='Modern 20 bold', bg='#181818')
        self.from_min_lbl.place(x=237, y=135)

        self.from_sec_lbl = Label(
            self.do_not_disturb_frame, text='Seconds', fg='white', font='Modern 20 bold', bg='#181818')
        self.from_sec_lbl.place(x=405, y=135)

        # "From" Colons
        self.from_colon_lbl1 = Label(
            self.do_not_disturb_frame, image=self.colon, bg='#181818')
        self.from_colon_lbl1.place(x=175, y=88)

        self.from_colon_lbl2 = Label(
            self.do_not_disturb_frame, image=self.colon, bg='#181818')
        self.from_colon_lbl2.place(x=345, y=88)

        # "From" 'AM' 'PM' Radiobuttons
        self.from_am_pm = StringVar()

        self.from_am_radio = ttk.Radiobutton(
            self.do_not_disturb_frame, text='AM', value='AM', cursor='hand2', var=self.from_am_pm)
        self.from_am_radio.place(x=500, y=80)

        self.from_pm_radio = ttk.Radiobutton(
            self.do_not_disturb_frame, text='PM', value='PM', cursor='hand2', var=self.from_am_pm)
        self.from_pm_radio.place(x=500, y=105)

        # "To" Heading
        self.to_lbl = Label(self.do_not_disturb_frame,
                            text='To:', font=('Modern', 22, 'bold'), bg='#181818', fg='white')
        self.to_lbl.place(x=60, y=190)

        # "To" Entries
        self.to_hr = Entry(self.do_not_disturb_frame, font=('Modern', 20, 'bold'), insertbackground='white',
                           fg='white', bg='#414141', width=4, justify='center', validate='key',
                           validatecommand=(validateHr12hrf, '%P'), relief=RIDGE, bd=4)
        self.to_hr.place(x=75, y=245)
        self.to_hr.insert(INSERT, '0')
        self.to_hr.bind('<FocusOut>', self.entry_focus_out_handler)

        self.to_min = Entry(self.do_not_disturb_frame, font=('Modern', 20, 'bold'), insertbackground='white',
                            fg='white', bg='#414141', width=4, justify='center', validate='key',
                            validatecommand=(validateMS, '%P'), relief=RIDGE, bd=4)
        self.to_min.place(x=245, y=245)
        self.to_min.insert(INSERT, '0')
        self.to_min.bind('<FocusOut>', self.entry_focus_out_handler)

        self.to_sec = Entry(self.do_not_disturb_frame, font=('Modern', 20, 'bold'), insertbackground='white',
                            fg='white', bg='#414141', width=4, justify='center', validate='key',
                            validatecommand=(validateMS, '%P'), relief=RIDGE, bd=4)
        self.to_sec.place(x=415, y=245)
        self.to_sec.insert(INSERT, '0')
        self.to_sec.bind('<FocusOut>', self.entry_focus_out_handler)

        # "To" Entry Labels
        self.to_hr_lbl = Label(
            self.do_not_disturb_frame, text='Hours', fg='white', font='Modern 20 bold', bg='#181818')
        self.to_hr_lbl.place(x=77, y=295)

        self.to_min_lbl = Label(
            self.do_not_disturb_frame, text='Minutes', fg='white', font='Modern 20 bold', bg='#181818')
        self.to_min_lbl.place(x=237, y=295)

        self.to_sec_lbl = Label(
            self.do_not_disturb_frame, text='Seconds', fg='white', font='Modern 20 bold', bg='#181818')
        self.to_sec_lbl.place(x=405, y=295)

        # "To" Colons
        self.to_colon_lbl1 = Label(
            self.do_not_disturb_frame, image=self.colon, bg='#181818')
        self.to_colon_lbl1.place(x=175, y=248)

        self.to_colon_lbl2 = Label(
            self.do_not_disturb_frame, image=self.colon, bg='#181818')
        self.to_colon_lbl2.place(x=345, y=248)

        # "To" 'AM' 'PM' Radiobuttons
        self.to_am_pm = StringVar()

        self.to_am_radio = ttk.Radiobutton(
            self.do_not_disturb_frame, text='AM', value='AM', cursor='hand2', var=self.to_am_pm)
        self.to_am_radio.place(x=500, y=240)

        self.to_pm_radio = ttk.Radiobutton(
            self.do_not_disturb_frame, text='PM', value='PM', cursor='hand2', var=self.to_am_pm)
        self.to_pm_radio.place(x=500, y=265)

        #
        # Do not Disturb save button #
        self.save_no_disturb_btn = Button(self.no_disturb_time_tab, text='Save', font=('Modern', 15, 'bold'),
                                          bg='#414141', relief=FLAT, fg='white', width=13,
                                          command=self.dont_disturb_schedule_save)
        self.save_no_disturb_btn.pack()

        #
        # Do Not Disturb variables #
        self.do_not_disturb = False
        self.saved_date = None

        #
        # Schedules Frame Components #
        # Headings Labels
        self.time_list_lbl = Label(
            self.schedules_frame, text='Time Schedules:', fg='white', font='Modern 15 bold', bg='#181818')
        self.time_list_lbl.grid(
            row=0, column=0, sticky=W, padx=15, pady=(10, 0))

        self.disturb_list_lbl = Label(
            self.schedules_frame, text='Do Not Disturb Schedules:', fg='white', font='Modern 15 bold', bg='#181818')
        self.disturb_list_lbl.grid(
            row=2, column=0, sticky=W, pady=(10, 0), padx=15)

        # Listboxes
        self.time_listbox = Listbox(
            self.schedules_frame, width=64, height=6, bg='#414141', fg='white', highlightbackground='black',
            font='Modern 13 bold', selectbackground='black', activestyle=NONE, selectmode=BROWSE)
        self.disturb_listbox = Listbox(
            self.schedules_frame, width=64, height=6, bg='#414141', fg='white', highlightbackground='black',
            font='Modern 13 bold', selectbackground='black', activestyle=NONE, selectmode=BROWSE)

        self.update_time_schedules()
        self.update_disturb_schedules()

        self.time_listbox.grid(row=1, column=0, padx=(15, 0), pady=(0, 10))
        self.disturb_listbox.grid(row=3, column=0, padx=(15, 0), pady=(0, 10))

        # Scroll Bars
        time_scroll = ttk.Scrollbar(
            self.schedules_frame, orient=VERTICAL, command=self.time_listbox.yview)
        time_scroll.grid(row=1, column=1, pady=(0, 10), sticky=NS)
        self.time_listbox.config(yscrollcommand=time_scroll.set)

        disturb_scroll = ttk.Scrollbar(
            self.schedules_frame, orient=VERTICAL, command=self.disturb_listbox.yview)
        disturb_scroll.grid(row=3, column=1, pady=(0, 10), sticky=NS)
        self.disturb_listbox.config(yscrollcommand=disturb_scroll.set)

        # Buttons
        self.update_any_schedule_btn = Button(self.schedules_frame, text='Update', font=('Modern', 14, 'bold'),
                                              bg='#414141', relief=FLAT, fg='white', width=13)
        self.update_any_schedule_btn.grid(
            row=4, column=0, sticky=W, padx=20, pady=20)

        self.delete_any_schedule_btn = Button(self.schedules_frame, text='Delete', font=('Modern', 14, 'bold'),
                                              bg='#414141', relief=FLAT, fg='white', width=13, command=self.delete_schedule)
        self.delete_any_schedule_btn.grid(row=4, column=0, sticky=E)

        #
        # Starting Alarm Timer #
        self.schedule_alarm()

    #
    # Methods #
    def delete_schedule(self):
        if self.time_listbox.curselection():
            answer = messagebox.askyesno(
                'Delete', 'Are you sure?', icon='info')
            if answer:
                selected = self.time_listbox.curselection()[0]
                selected_id = self.time_listbox.get(selected).split('|')[0]

                query = f'DELETE FROM alarm_info where alarm_id = {selected_id}'
                try:
                    cur.execute(query)
                    con.commit()
                    self.reset_handled = False
                    self.time_listbox.delete(selected)
                except:
                    messagebox.showerror(
                        'Failed.', 'Could Not Delete from Database.\nContact Developer.', icon='error')

        elif self.disturb_listbox.curselection():
            selected = self.disturb_listbox.curselection()[0]
            selected_id = self.disturb_listbox.get(selected).split('|')[0]

            query = f'DELETE FROM do_not_disturb where id = {selected_id}'
            try:
                cur.execute(query)
                con.commit()
                self.disturb_listbox.delete(selected)
            except:
                messagebox.showerror(
                    'Failed', 'Could Not Delete from Database./nContact Developer.', icon='error')

    def update_time_schedules(self):
        res = cur.execute('SELECT * FROM alarm_info').fetchall()
        if res:
            self.time_listbox.delete(0, END)

            ids, times, messages = zip(*res)

            separated_time = [[t for t in x.split(':')] for x in times]
            items = [f'{id_}| Time: {t[0]} Hr(s), {t[1]} Min(s), {t[2]} Sec(s). Message: {message}' for id_, message, t in zip(
                ids, messages, separated_time)]

            for i, item in enumerate(items):
                self.time_listbox.insert(i, item)

        else:
            self.time_listbox.delete(0, END)

    def update_disturb_schedules(self):
        res = cur.execute('SELECT * FROM do_not_disturb').fetchall()
        if res:
            self.disturb_listbox.delete(0, END)

            items = [f'{id_}| From: {from_}, To: {to}' for id_,
                     from_, to in res]

            for i, item in enumerate(items):
                self.disturb_listbox.insert(i, item)

        else:
            self.disturb_listbox.delete(0, END)

    def dont_disturb_schedule_save(self):
        """
        Stores the "Do Not Disturb" time schedules in the database

        """
        # Taking values from the entries
        if self.from_am_pm.get() and self.to_am_pm.get():
            from_time = f'{int(self.from_hr.get())}:{int(self.from_min.get())}:{int(self.from_sec.get())} {self.from_am_pm.get()}'
            to_time = f'{int(self.to_hr.get())}:{int(self.to_min.get())}:{int(self.to_sec.get())} {self.to_am_pm.get()}'

            query = f"INSERT INTO do_not_disturb(from_time, to_time) VALUES('{from_time}', '{to_time}')"
            try:
                # Inserting into database
                cur.execute(query)
                con.commit()

                # Updating the GUI
                self.update_disturb_schedules()

                # Changing entries back to default values
                self.from_hr.delete(0, END)
                self.from_min.delete(0, END)
                self.from_sec.delete(0, END)
                self.from_hr.insert(INSERT, '0')
                self.from_min.insert(INSERT, '0')
                self.from_sec.insert(INSERT, '0')
                self.from_am_pm.set('')

                self.to_hr.delete(0, END)
                self.to_min.delete(0, END)
                self.to_sec.delete(0, END)
                self.to_hr.insert(INSERT, '0')
                self.to_min.insert(INSERT, '0')
                self.to_sec.insert(INSERT, '0')
                self.to_am_pm.set('')

                messagebox.showinfo('Success', 'Schedule Set.')
            except:
                messagebox.showerror(
                    'Failed', 'Could Not Set Schedule.', icon='error')
        else:
            messagebox.showerror(
                'Warning', "You have to Select either 'AM' or 'PM'")

    def entry_focus_out_handler(self, event):
        """Enters a "0" in entries if the entry is empty when it is focused out

        Args:
            event (Tkinter.Event): contains the focus out event information
        """
        if event.widget.get() == '':
            event.widget.insert(INSERT, 0)

    def on_closing(self):
        """
        Confirms if the user actually wants to stop the Application.

        """
        answer = messagebox.askyesno(
            'Close', 'If You Close This Window, the Alarm will not Repeat.\nDo You Really Want to Quit?', icon='info')
        if answer:
            self.root.destroy()

    def restart(self):
        """
        Restarts the alarm if it is diasbled.

        """
        global _DISABLED_ALARM
        if _DISABLED_ALARM:
            _DISABLED_ALARM = False
            messagebox.showinfo('Restart', 'Alarm Restarted')

        else:
            messagebox.showinfo('Restart', 'Already Running')

    def Save(self):
        """
        Saves the given Scheduled Time

        """
        # Storing the time from the entries
        time = f'{int(self.ent_hour.get())}:{int(self.ent_min.get())}:{int(self.ent_sec.get())}'

        # Storing the message
        message = self.message_area.get(0.0, 'end-1c')

        # Query to insert info in the database
        query = f"INSERT INTO alarm_info(time, message) VALUES('{time}', '{message}');"
        try:
            # Executing the query
            cur.execute(query)
            con.commit()

            # Updating GUI
            self.update_time_schedules()

            # Clearing the entries and going back to default values
            self.ent_hour.delete(0, END)
            self.ent_min.delete(0, END)
            self.ent_sec.delete(0, END)
            self.ent_hour.insert(INSERT, '0')
            self.ent_min.insert(INSERT, '0')
            self.ent_sec.insert(INSERT, '0')

            self.message_area.delete(0.0, 'end-1c')

            messagebox.showinfo('Success', 'Schedule Set.')
        except:
            messagebox.showerror(
                'Warning', 'Could not Save to Database.', icon='warning')

    def validate_hr(self, input):
        """Validate if the correct type of input is given to the hours entry. For 24 hour format.

        Args:
            input (str): The string in the entry typed by the user

        Returns:
            boolean: True if character typed is currect, False otherwise
        """
        try:
            # Checks if the current string in the entry is less than 24 and does not contain space
            int(input)
            if int(input) < 24 and input[-1] != ' ':
                return True
            else:
                return False

        except ValueError:
            if input == '':
                return True
            else:
                return False

    def validate_hr_12hrf(self, input):
        """Validate if the correct type of input is given to the hours entry. For 12 hour format

        Args:
            input (str): The string in the entry typed by the user

        Returns:
            boolean: True if character typed is currect, False otherwise
        """
        try:
            # Checks if the current string in the entry is less than 13 and does not contain space
            int(input)
            if int(input) < 13 and input[-1] != ' ':
                return True
            else:
                return False

        except ValueError:
            if input == '':
                return True
            else:
                return False

    def validate_min_sec(self, input):
        """Validate if the correct type of input is given to the minutes and seconds entries

        Args:
            input (str): The string in the entries typed by the user

        Returns:
            boolean: True if character typed is currect, False otherwise
        """
        try:
            # Checks if the current string in the entry is less than 60 and does not contain space
            int(input)
            if int(input) <= 60 and input[-1] != ' ':
                return True
            else:
                return False

        except ValueError:
            if input == '':
                return True
            else:
                return False

    def schedule_alarm(self):
        """
        Checks if the database has schedules and if the alarm GUI is already running or not.
        If database has a schedule and alarm GUI is not currently running, then starts the process
        of running the alarm. Otherwise checks again in 5 seconds.

        """
        self.check_disturb_mode()
        # Checking for schedules in database
        result = cur.execute('SELECT time, message from alarm_info').fetchone()
        if result:
            global _ALARM_GUI_RUNNING, _DISABLED_ALARM
            # Splitting the time into hours, minutes and seconds
            time = result[0].split(':')
            scheduled_time = datetime.now(
            ) + timedelta(hours=int(time[0]), minutes=int(time[1]), seconds=int(time[2]))  # The time when the alarm should ring

            if not _ALARM_GUI_RUNNING and not _DISABLED_ALARM and not self.usr_do_not_disturb.get() and not self.do_not_disturb:
                self.validate_alarm(scheduled_time, result[1])
                return

        # Scheduling a recheck after 5 seconds
        self.root.after(1000, self.schedule_alarm)

    def check_disturb_mode(self):
        """
        Checks if do not disturb should be turned on based on scheduled time.

        """
        now = datetime.now()

        result = cur.execute(
            'SELECT from_time, to_time FROM do_not_disturb').fetchone()
        if result:
            if (result[0][-2:]+result[1][-2:]) != 'PMAM':
                # For "Do Not Disturb" schedules that start and end the same day
                time_format = '%I:%M:%S %p'
                from_time = datetime.strptime(result[0], time_format).time()
                to_time = datetime.strptime(result[1], time_format).time()
                now = now.time()

                if now >= from_time and now < to_time:
                    self.do_not_disturb = True
                else:
                    self.do_not_disturb = False
            else:
                # For "Do Not Disturb" schedules that start and end on different days
                if not self.do_not_disturb:
                    self.saved_date = now

                time_format = '%Y-%m-%d %I:%M:%S %p'
                from_time = datetime.strptime(
                    str(self.saved_date.date())+" "+result[0], time_format)
                to_time = datetime.strptime(
                    str((self.saved_date+timedelta(days=1)).date())+" "+result[1], time_format)

                if now >= from_time and now < to_time:
                    self.do_not_disturb = True
                else:
                    self.do_not_disturb = False

        else:
            self.do_not_disturb = False

    def validate_alarm(self, scheduled_time, message):
        """Checks if it is time to ring the alarm. Checks every 1 second. Also handles the reset event.

        Args:
            scheduled_time (datetime.datetime): The list that contains the hours, minutes and seconds of the schedule
            message (str): The message to be shown when alarm rings
        """
        if datetime.now() >= scheduled_time and self.reset_handled and not self.usr_do_not_disturb.get() and not self.do_not_disturb:
            self.sound_alarm(message)
            self.schedule_alarm()
            return
        elif not self.reset_handled or self.usr_do_not_disturb.get() or self.do_not_disturb:
            self.reset_handled = True
            self.schedule_alarm()
            return

        # Scheduling to recheck in 1 second
        self.root.after(1000, self.validate_alarm, scheduled_time, message)

    def sound_alarm(self, message):
        """Starts the alarm GUI.

        Args:
            message (str): The message to be shown when alarm rings
        """
        global _ALARM_GUI_RUNNING

        _ALARM_GUI_RUNNING = True
        alarm = Alarm(message)


# Slave Window
class Alarm(Toplevel):

    def __init__(self, message):
        Toplevel.__init__(self)

        # Root Configuration
        self.config(bg='#181818')
        self.title('Alarm')
        self.geometry('400x200+500+150')
        self.resizable(False, False)
        self.protocol('WM_DELETE_WINDOW', self.quit)

        # Label
        message_label = Label(
            self, text=message, font=('Modern', 22, 'bold'))
        message_label.pack(pady=30)
        message_label['background'] = '#181818'
        message_label['foreground'] = 'white'

        # Buttons
        stop_btn = Button(self, text='Stop!', font=('Modern', 14, 'bold'),
                          bg='#414141', relief=FLAT, fg='white', width=10, command=self.kill)
        stop_btn.pack(padx=20, pady=(20, 0), side='left')

        quit_btn = Button(self, text='Quit', font=('Modern', 14, 'bold'),
                          bg='#414141', relief=FLAT, fg='white', width=10, command=self.quit)
        quit_btn.pack(padx=20, pady=(20, 0), side='right')

        # Plays the alarm sound
        ws.PlaySound('tones/soft_sound.wav', ws.SND_LOOP+ws.SND_ASYNC)
        self.lift()

    def quit(self):
        """
        Stops the alarm from repeating until the alarm is restarted

        """
        global _ALARM_GUI_RUNNING, _DISABLED_ALARM
        _ALARM_GUI_RUNNING = False
        _DISABLED_ALARM = True
        ws.PlaySound(None, ws.SND_PURGE)
        self.destroy()

    def kill(self):
        """
        Stops the alarm from ringing.

        """
        global _ALARM_GUI_RUNNING
        _ALARM_GUI_RUNNING = False

        ws.PlaySound(None, ws.SND_PURGE)
        self.destroy()


def styling():
    style = ttk.Style()
    style.theme_create('dark', settings={
        ".": {
            "configure": {
                "background": '#181818',  # All except tabs
                "font": ('Modern', 12, 'bold')
            }
        },
        "TCheckbutton": {
            "configure": {
                "indicatorcolor": '#181818',
                "foreground": 'white',
                "focuscolor": '#181818',
                "font": ('Modern', 14, 'bold'),
                "indicatordiameter": 13,
                "borderwidth": 2
            },
            "map": {
                "foreground": [('pressed', '#303030'), ('active', '#414141')],
                "indicatorcolor": [('selected', '#d90909'), ('pressed', '#414141')]
            }
        },
        "TRadiobutton": {
            "configure": {
                "indicatorcolor": '#181818',
                "foreground": 'white',
                "focuscolor": '#181818',
                "font": ('Modern', 15, 'bold'),
                "indicatordiameter": 13,
                "borderwidth": 2
            },
            "map": {
                "foreground": [('pressed', '#303030'), ('active', '#414141')],
                "indicatorcolor": [('selected', '#d90909'), ('pressed', '#414141')]
            }
        },
        "TNotebook": {
            "configure": {
                "background": '#181818',  # Your margin color
                # margins: left, top, right, separator
                "tabmargins": [1, 5, 0, 0],
            }
        },
        "TNotebook.Tab": {
            "configure": {
                "background": '#414141',  # tab color when not selected
                # [space between text and horizontal tab-button border, space between text and vertical tab_button border]
                "padding": [10, 2],
                "font": ('Modern', 13, 'bold'),
                "foreground": 'white'
            },
            "map": {
                # Tab color when selected
                "background": [("selected", '#181818')],
                "expand": [("selected", [1, 1, 1, 0])]  # text margins
            }
        },
        "TScrollbar": {
            "configure": {
                "background": '#181818',
                "arrowcolor": 'white',
                "arrowsize": 12,
                "troughcolor": 'white'
            },
            "map": {
                "background": [('active', '#303030')]
            }
        }
    })
    return style


def main():
    root = Tk()
    root.config(bg='#181818')
    root.title('Scheduler')
    root.geometry('572x480+1200+250')
    root.resizable(False, False)
    root.iconbitmap('Images/icon.ico')

    app = App(root)

    root.mainloop()


if __name__ == '__main__':
    main()

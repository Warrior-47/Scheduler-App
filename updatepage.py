from tkinter import *

from re import split


def validate_hr(input):
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


def validate_hr_12hrf(input):
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


def validate_min_sec(input):
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


def entry_focus_out_handler(event):
    """Enters a "0" in entries if the entry is empty when it is focused out

    Args:
        event (Tkinter.Event): contains the focus out event information
    """
    if event.widget.get() == '':
        event.widget.insert(INSERT, 0)


class UpdateTimeGUI(Toplevel):

    def __init__(self, master, data):
        Toplevel.__init__(self)
        self.higher_level = master

        # Root Configuration #
        self.config(bg='#181818')
        self.title('Update')
        self.geometry('572x480+600+250')
        self.resizable(False, False)
        self.iconbitmap('Images/icon.ico')
        self.protocol('WM_DELETE_WINDOW', self.on_closing)

        # Data Parsing #
        time_data, message_data = data[0], data[1]
        self.id_ = time_data.split('|')[0]
        time = [x for x in time_data.split() if x.isnumeric()]
        message = message_data.split(':')[1].strip()

        # Validation #
        validateHr = self.register(validate_hr)
        validateHr12hrf = self.register(validate_hr_12hrf)
        validateMS = self.register(validate_min_sec)

        # Frames #
        self.time_frame = Frame(
            self, width=500, height=200, bg='#181818')
        self.time_frame.pack(fill=X)

        self.message_frame = Frame(
            self, width=500, height=150, bg='#181818')
        self.message_frame.pack(fill=X)

        # Time Frame Components #
        # Sub Heading
        self.set_lbl = Label(
            self.time_frame, text='Update Time:', font=('Modern', 22, 'bold'), bg='#181818', fg='white')
        self.set_lbl.place(x=60, y=30)

        # Entries
        self.ent_hour = Entry(
            self.time_frame, font=('Modern', 20, 'bold'), insertbackground='white',
            fg='white', bg='#414141', width=4, justify='center', validate='key',
            validatecommand=(validateHr, '%P'), relief=RIDGE, bd=4)
        self.ent_hour.place(x=80, y=85)
        self.ent_hour.insert(INSERT, time[0])
        self.ent_hour.bind('<FocusOut>', entry_focus_out_handler)

        self.ent_min = Entry(
            self.time_frame, font=('Modern', 20, 'bold'), insertbackground='white',
            fg='white', bg='#414141', width=4, justify='center', validate='key',
            validatecommand=(validateMS, '%P'), relief=RIDGE, bd=4)
        self.ent_min.place(x=250, y=85)
        self.ent_min.insert(INSERT, time[1])
        self.ent_min.bind('<FocusOut>', entry_focus_out_handler)

        self.ent_sec = Entry(
            self.time_frame, font=('Modern', 20, 'bold'), insertbackground='white',
            fg='white', bg='#414141', width=4, justify='center', validate='key',
            validatecommand=(validateMS, '%P'), relief=RIDGE, bd=4)
        self.ent_sec.place(x=420, y=85)
        self.ent_sec.insert(INSERT, time[2])
        self.ent_sec.bind('<FocusOut>', entry_focus_out_handler)

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
            self.message_frame, text='Update Message:', fg='white', font=('Modern', 22, 'bold'), bg='#181818')
        self.message_lbl.place(x=60, y=10)

        # Message Area
        self.message_area = Text(
            self.message_frame, width=40, height=6, bg='#414141',
            fg='white', font=('Modern', 18, 'bold'), wrap=WORD, insertbackground='white')
        self.message_area.insert(INSERT, message)
        self.message_area.place(x=60, y=50)

        # Update Button #
        self.update_btn = Button(
            self, text='Update', font=('Modern', 15, 'bold'), bg='#414141', relief=FLAT, fg='white', width=13, command=self.update)
        self.update_btn.pack(pady=(50, 0))

    # Methods #
    def update(self):
        """
        Updates the database data according to the input

        """
        # Making sure data is valid
        if self.ent_hour.get() == '0' and self.ent_min.get() == '0' and self.ent_sec.get() == '0':
            messagebox.showwarning(
                'Warning', 'Scheduled time Cannot be All Zero.', icon='warning')
            return

        time = f'{int(self.ent_hour.get())}:{int(self.ent_min.get())}:{int(self.ent_sec.get())}'
        message = self.message_area.get(0.0, 'end-1c')

        self.higher_level.update_database(
            'alarm_info', self.id_, time=time, message=message)
        self.higher_level.update_GUI_running = False
        self.destroy()

    def on_closing(self):
        self.higher_level.update_GUI_running = False
        self.destroy()


class UpdateDisturbGUI(Toplevel):

    def __init__(self, master, data):
        Toplevel.__init__(self)
        self.higher_level = master

        # Colon Image #
        self.colon = PhotoImage(file='Images/colon.png')

        # Root Configuration #
        self.config(bg='#181818')
        self.title('Update')
        self.geometry('572x480+600+250')
        self.resizable(False, False)
        self.iconbitmap('Images/icon.ico')
        self.protocol('WM_DELETE_WINDOW', self.on_closing)

        # Data Parsing #
        from_component, to_component = data[0], data[1]
        self.id_ = from_component.split('|')[0]
        from_radio_value = from_component[-2:]
        to_radio_value = to_component[-2:]
        from_time = [x for x in split(':| ', from_component) if x.isnumeric()]
        to_time = [x for x in split(':| ', to_component) if x.isnumeric()]

        # Validation #
        validateHr = self.register(validate_hr)
        validateHr12hrf = self.register(validate_hr_12hrf)
        validateMS = self.register(validate_min_sec)

        # Frame #
        self.do_not_disturb_frame = Frame(
            self, width=500, height=370, bg='#181818')
        self.do_not_disturb_frame.pack(fill=X)

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
        self.from_hr.insert(INSERT, from_time[0])
        self.from_hr.bind('<FocusOut>', entry_focus_out_handler)

        self.from_min = Entry(self.do_not_disturb_frame, font=('Modern', 20, 'bold'), insertbackground='white',
                              fg='white', bg='#414141', width=4, justify='center', validate='key',
                              validatecommand=(validateMS, '%P'), relief=RIDGE, bd=4)
        self.from_min.place(x=245, y=85)
        self.from_min.insert(INSERT, from_time[1])
        self.from_min.bind('<FocusOut>', entry_focus_out_handler)

        self.from_sec = Entry(self.do_not_disturb_frame, font=('Modern', 20, 'bold'), insertbackground='white',
                              fg='white', bg='#414141', width=4, justify='center', validate='key',
                              validatecommand=(validateMS, '%P'), relief=RIDGE, bd=4)
        self.from_sec.place(x=415, y=85)
        self.from_sec.insert(INSERT, from_time[2])
        self.from_sec.bind('<FocusOut>', entry_focus_out_handler)

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

        self.from_am_pm.set(from_radio_value)

        # "To" Heading
        self.to_lbl = Label(self.do_not_disturb_frame,
                            text='To:', font=('Modern', 22, 'bold'), bg='#181818', fg='white')
        self.to_lbl.place(x=60, y=190)

        # "To" Entries
        self.to_hr = Entry(self.do_not_disturb_frame, font=('Modern', 20, 'bold'), insertbackground='white',
                           fg='white', bg='#414141', width=4, justify='center', validate='key',
                           validatecommand=(validateHr12hrf, '%P'), relief=RIDGE, bd=4)
        self.to_hr.place(x=75, y=245)
        self.to_hr.insert(INSERT, to_time[0])
        self.to_hr.bind('<FocusOut>', entry_focus_out_handler)

        self.to_min = Entry(self.do_not_disturb_frame, font=('Modern', 20, 'bold'), insertbackground='white',
                            fg='white', bg='#414141', width=4, justify='center', validate='key',
                            validatecommand=(validateMS, '%P'), relief=RIDGE, bd=4)
        self.to_min.place(x=245, y=245)
        self.to_min.insert(INSERT, to_time[1])
        self.to_min.bind('<FocusOut>', entry_focus_out_handler)

        self.to_sec = Entry(self.do_not_disturb_frame, font=('Modern', 20, 'bold'), insertbackground='white',
                            fg='white', bg='#414141', width=4, justify='center', validate='key',
                            validatecommand=(validateMS, '%P'), relief=RIDGE, bd=4)
        self.to_sec.place(x=415, y=245)
        self.to_sec.insert(INSERT, to_time[2])
        self.to_sec.bind('<FocusOut>', entry_focus_out_handler)

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

        self.to_am_pm.set(to_radio_value)

        #
        # Do not Disturb Update button #
        self.update_btn = Button(self, text='Update', font=('Modern', 15, 'bold'),
                                 bg='#414141', relief=FLAT, fg='white', width=13,
                                 command=self.update)
        self.update_btn.pack()

    # Methods #
    def update(self):
        """
        Updates the database data according to the input

        """
        f_hr = int(self.from_hr.get()) if self.from_hr.get() != '0' else 12
        t_hr = int(self.to_hr.get()) if self.to_hr.get() != '0' else 12
        from_time = f'{f_hr}:{int(self.from_min.get())}:{int(self.from_sec.get())} {self.from_am_pm.get()}'
        to_time = f'{t_hr}:{int(self.to_min.get())}:{int(self.to_sec.get())} {self.to_am_pm.get()}'

        self.higher_level.update_database(
            'do_not_disturb', self.id_, from_time=from_time, to_time=to_time)
        self.higher_level.update_GUI_running = False
        self.destroy()

    def on_closing(self):
        self.higher_level.update_GUI_running = False
        self.destroy()

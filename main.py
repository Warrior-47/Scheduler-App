from tkinter import messagebox
from tkinter import ttk
from tkinter import *

from datetime import datetime, timedelta
from os import path

import winsound as ws
import updatepage
import traceback
import sqlite3

if path.exists('database.db'):
    con = sqlite3.connect('database.db')
    cur = con.cursor()
else:
    con = sqlite3.connect('database.db')
    cur = con.cursor()

    query = 'CREATE TABLE alarm_info (\
        id INTEGER PRIMARY KEY AUTOINCREMENT,\
        time Text,\
        message Text,\
        interval INTEGER,\
        state INTEGER\
    );'

    cur.execute(query)

    query = 'CREATE TABLE do_not_disturb (\
        id INTEGER PRIMARY KEY AUTOINCREMENT,\
        from_time Text,\
        to_time Text,\
        state INTEGER\
    );'

    cur.execute(query)
    con.commit()

_ALARM_GUI_RUNNING = {}


class App(object):

    def __init__(self, master):
        self.root = master
        self.root.protocol('WM_DELETE_WINDOW', self.on_closing)

        # Style #
        style = styling()
        style.theme_use('dark')

        # Boolean Flags #
        self.update_GUI_running = False

        # Validation #
        validateHr = self.root.register(self.validate_hr)
        validateHr12hrf = self.root.register(self.validate_hr_12hrf)
        validateMS = self.root.register(self.validate_min_sec)
        validateInterval = self.root.register(self.validate_interval)
        self.validating_schedule = {}
        self._disabled_alarm = {}
        self.disturb_disabled = {}

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
        self.ent_hour.place(x=70, y=85)
        self.ent_hour.insert(INSERT, '0')
        self.ent_hour.bind('<FocusOut>', self.entry_focus_out_handler)

        self.ent_min = Entry(
            self.time_frame, font=('Modern', 20, 'bold'), insertbackground='white',
            fg='white', bg='#414141', width=4, justify='center', validate='key',
            validatecommand=(validateMS, '%P'), relief=RIDGE, bd=4)
        self.ent_min.place(x=200, y=85)
        self.ent_min.insert(INSERT, '0')
        self.ent_min.bind('<FocusOut>', self.entry_focus_out_handler)

        self.ent_sec = Entry(
            self.time_frame, font=('Modern', 20, 'bold'), insertbackground='white',
            fg='white', bg='#414141', width=4, justify='center', validate='key',
            validatecommand=(validateMS, '%P'), relief=RIDGE, bd=4)
        self.ent_sec.place(x=330, y=85)
        self.ent_sec.insert(INSERT, '0')
        self.ent_sec.bind('<FocusOut>', self.entry_focus_out_handler)

        # Entry Labels
        self.hour_lbl = Label(
            self.time_frame, text='Hours', fg='white', font='Modern 20 bold', bg='#181818')
        self.hour_lbl.place(x=72, y=135)

        self.min_lbl = Label(
            self.time_frame, text='Minutes', fg='white', font='Modern 20 bold', bg='#181818')
        self.min_lbl.place(x=192, y=135)

        self.sec_lbl = Label(
            self.time_frame, text='Seconds', fg='white', font='Modern 20 bold', bg='#181818')
        self.sec_lbl.place(x=318, y=135)

        # Colons
        self.colon = PhotoImage(file='Images/colon.png')
        self.colon_lbl1 = Label(
            self.time_frame, image=self.colon, bg='#181818')
        self.colon_lbl1.place(x=148, y=88)

        self.colon_lbl2 = Label(
            self.time_frame, image=self.colon, bg='#181818')
        self.colon_lbl2.place(x=278, y=88)

        # Interval
        self.interval_lbl = Label(
            self.time_frame, text='Interval', fg='white', font='Modern 20 bold', bg='#181818')
        self.interval_lbl.place(x=430, y=43)

        self.ent_interval = Entry(
            self.time_frame, font=('Modern', 20, 'bold'), insertbackground='white',
            fg='white', bg='#414141', width=4, justify='center', relief=RIDGE, bd=4,
            validate='key', validatecommand=(validateInterval, '%P'))
        self.ent_interval.place(x=440, y=85)
        self.ent_interval.insert(INSERT, '0')
        self.ent_interval.bind('<FocusOut>', self.entry_focus_out_handler)

        self.interval_unit_lbl = Label(
            self.time_frame, text='Minutes', fg='white', font='Modern 20 bold', bg='#181818')
        self.interval_unit_lbl.place(x=430, y=135)

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
            self.schedule_time_tab, text='Save', font=('Modern', 15, 'bold'), bg='#414141', relief=FLAT, fg='white', width=13, command=self.save)
        self.save_btn.pack(pady=(30, 0))

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
            row=3, column=0, sticky=W, pady=(10, 0), padx=15)

        # Listboxes
        self.time_listbox = Listbox(
            self.schedules_frame, width=64, height=6, bg='#414141', fg='white', highlightbackground='black',
            font='Modern 13 bold', selectbackground='black', activestyle=NONE, selectmode=BROWSE)
        self.disturb_listbox = Listbox(
            self.schedules_frame, width=64, height=6, bg='#414141', fg='white', highlightbackground='black',
            font='Modern 13 bold', selectbackground='black', activestyle=NONE, selectmode=BROWSE)

        self.update_time_schedules()
        self.update_disturb_schedules()

        self.time_listbox.bind(
            '<<ListboxSelect>>', self.change_state_btn_text)
        self.disturb_listbox.bind(
            '<<ListboxSelect>>', self.change_state_btn_text)

        self.time_listbox.grid(row=1, column=0, padx=(15, 0))
        self.disturb_listbox.grid(row=4, column=0, padx=(15, 0))

        # Scroll Bars
        time_scroll_v = ttk.Scrollbar(
            self.schedules_frame, orient=VERTICAL, command=self.time_listbox.yview)
        time_scroll_v.grid(row=1, column=1, sticky=NS)
        self.time_listbox.config(yscrollcommand=time_scroll_v.set)

        time_scroll_h = ttk.Scrollbar(
            self.schedules_frame, orient=HORIZONTAL, command=self.time_listbox.xview)
        time_scroll_h.grid(row=2, column=0, padx=(
            15, 0), pady=(0, 10), sticky=EW)
        self.time_listbox.config(xscrollcommand=time_scroll_h.set)

        disturb_scroll_v = ttk.Scrollbar(
            self.schedules_frame, orient=VERTICAL, command=self.disturb_listbox.yview)
        disturb_scroll_v.grid(row=4, column=1, sticky=NS)
        self.disturb_listbox.config(yscrollcommand=disturb_scroll_v.set)

        # Buttons
        self.update_any_schedule_btn = Button(self.schedules_frame, text='Update', font=('Modern', 14, 'bold'),
                                              bg='#414141', relief=FLAT, fg='white', width=13, command=self.run_update_GUI)
        self.update_any_schedule_btn.grid(
            row=5, column=0, sticky=W, padx=20, pady=25)

        self.delete_any_schedule_btn = Button(self.schedules_frame, text='Delete', font=('Modern', 14, 'bold'),
                                              bg='#414141', relief=FLAT, fg='white', width=13, command=self.delete_schedule)
        self.delete_any_schedule_btn.grid(row=5, column=0, sticky=E)

        self.change_schedule_state_btn = Button(self.schedules_frame, text='Disable', font=('Modern', 14, 'bold'),
                                                bg='#414141', relief=FLAT, fg='white', width=13, command=self.change_schedule_state)
        self.change_schedule_state_btn.grid(row=5, column=0, padx=(20, 0))

        # Minimizing Window
        self.root.iconify()

        #
        # Starting Alarm Timer #
        self.schedule_alarm()

    #
    # Methods #
    def on_closing(self):
        """
        Confirms if the user actually wants to stop the Application.

        """
        answer = messagebox.askyesno(
            'Close', 'If You Close This Window, the Alarm will not Repeat.\nDo You Really Want to Quit?', icon='info')
        if answer:
            self.root.destroy()

    def update_database(self, table_name, id_, **kwargs):
        """Updates the database data.

        Args:
            table_name (str): The name of the table that has to be updated.
            id_ (int): The primary key value of the row of data being updated.
        """
        # Building the query
        query = f'UPDATE {table_name} SET '
        query += ', '.join([f"{attr} = '{value}'" for attr,
                            value in kwargs.items()]) + f'WHERE id = {int(id_)};'
        try:
            cur.execute(query)
            con.commit()

            # Checks and updates the correct listbox.
            if table_name == 'alarm_info':
                global _ALARM_GUI_RUNNING
                _ALARM_GUI_RUNNING.pop(int(id_), None)
                self.update_time_schedules()

            else:
                self.update_disturb_schedules()

            messagebox.showinfo('Success', 'Successfully Updated.')
        except:
            with open('error_log.txt', 'a') as f:
                f.write('['+str(datetime.now())+']\n')
                traceback.print_exc(file=f)
                f.write('\n')
            messagebox.showerror(
                'Failed', 'Could Not Update the Database. Contact Developer.', icon='error')

    def run_update_GUI(self):
        """
        Opens the updating GUI depending on which type of item was selected, Scheduler time or "Do Not Disturb" item.

        """
        # Makes sure there is only one Update GUI running at one time.
        if self.update_GUI_running:
            messagebox.showwarning(
                'Already Running', 'Another Update Interface is Active.\nClose Previous Window to Open Another.', icon='warning')
            return

        if self.time_listbox.curselection():
            self.update_GUI_running = True

            data = self.time_listbox.get(
                self.time_listbox.curselection()[0]).split('Message: ')
            time_update = updatepage.UpdateTimeGUI(self, data)

        elif self.disturb_listbox.curselection():
            self.update_GUI_running = True

            data = self.disturb_listbox.get(
                self.disturb_listbox.curselection()[0]).split(',')
            disturb_update = updatepage.UpdateDisturbGUI(self, data)

    def delete_schedule(self):
        """
        Deletes the selected listbox item from the database.

        """
        # Checks if a scheduler time was selected
        if self.time_listbox.curselection():
            answer = messagebox.askyesno(
                'Delete', 'Are you sure?', icon='info')
            if answer:
                # If user confirms deletion, first stores the id of the schedule
                selected = self.time_listbox.curselection()[0]
                selected_id = self.time_listbox.get(selected).split('|')[0]

                query = f'DELETE FROM alarm_info where id = {selected_id}'
                try:
                    # Deleting from database
                    cur.execute(query)
                    con.commit()

                    # Deleting from time schedule listbox
                    self.time_listbox.delete(selected)

                    # Removing from the shared control lists
                    global _ALARM_GUI_RUNNING
                    _ALARM_GUI_RUNNING.pop(int(selected_id), None)
                    self._disabled_alarm.pop(int(selected_id), None)
                    self.validating_schedule.pop(int(selected_id), None)

                except:
                    with open('error_log.txt', 'a') as f:
                        f.write('['+str(datetime.now())+']\n')
                        traceback.print_exc(file=f)
                        f.write('\n')
                    messagebox.showerror(
                        'Failed.', 'Could Not Delete from Database.\nContact Developer.', icon='error')

        # Checks if a 'Do Not Disturb' time was selected
        elif self.disturb_listbox.curselection():
            # First stores the id of the schedule
            selected = self.disturb_listbox.curselection()[0]
            selected_id = self.disturb_listbox.get(selected).split('|')[0]

            query = f'DELETE FROM do_not_disturb where id = {selected_id}'
            try:
                # Deleting from database
                cur.execute(query)
                con.commit()

                # Removing from disturb schedules listbox
                self.disturb_listbox.delete(selected)

                # Removing from the control list
                self.disturb_disabled.pop(int(selected_id), None)
            except:
                with open('error_log.txt', 'a') as f:
                    f.write('['+str(datetime.now())+']\n')
                    traceback.print_exc(file=f)
                    f.write('\n')
                messagebox.showerror(
                    'Failed', 'Could Not Delete from Database.\nContact Developer.', icon='error')

    def update_time_schedules(self):
        """
        Updates the Scheduler time listbox items if items are insert, deleted or updated.

        """
        res = cur.execute('SELECT * FROM alarm_info').fetchall()
        if res:
            # Deleting previous items as new items are concatenated to previous list.
            self.time_listbox.delete(0, END)

            # Parsing the data into a fixed format.
            ids, times, messages, intervals, states = zip(*res)

            separated_time = [[t for t in x.split(':')] for x in times]
            items = [(f'{id_}| Time: {t[0]} Hr(s), {t[1]} Min(s), {t[2]} Sec(s). Interval: {i} Mins. Message: {message}', state) for id_, message, t, i, state in zip(
                ids, messages, separated_time, intervals, states)]

            # Inserting data into the time listbox.
            for i, (item, state) in enumerate(items):
                self.time_listbox.insert(i, item)

                # Checking if the time schedule was enabled or disabled
                if state:
                    # Setting listbox item style for enabled item
                    self._disabled_alarm[ids[i]] = False
                    self.change_itembox_item_color(
                        self.time_listbox, i, 'white', 'white')
                else:
                    # Setting listbox item style for disabled item
                    self._disabled_alarm[ids[i]] = True
                    self.change_itembox_item_color(
                        self.time_listbox, i, '#181818', '#414141')

        else:
            # If there is nothing in the database, the listbox is cleared.
            self.time_listbox.delete(0, END)

    def update_disturb_schedules(self):
        """
        Updates the "Do Not Disturb" time listbox items if items are insert, deleted or updated.

        """
        res = cur.execute('SELECT * FROM do_not_disturb').fetchall()
        if res:
            # Deleting previous items as new items are concatenated to previous list.
            self.disturb_listbox.delete(0, END)

            # Parsing data into a fixed format
            items = [(id_, f'{id_}| From: {from_}, To: {to}', state) for id_,
                     from_, to, state in res]

            # Inserting data into the listbox.
            for i, (id_, item, state) in enumerate(items):
                self.disturb_listbox.insert(i, item)

                # Checking if the disturb schedule was enabled or disabled
                if state:
                    # Setting listbox item style for enabled item
                    self.disturb_disabled[id_] = False
                    self.change_itembox_item_color(
                        self.disturb_listbox, i, 'white', 'white')
                else:
                    # Setting listbox item style for disabled item
                    self.disturb_disabled[id_] = True
                    self.change_itembox_item_color(
                        self.disturb_listbox, i, '#181818', '#414141')

        else:
            # If there is nothing in the database, the listbox is cleared.
            self.disturb_listbox.delete(0, END)

    def entry_focus_out_handler(self, event):
        """Enters a "0" in entries if the entry is empty when it is focused out

        Args:
            event (Tkinter.Event): contains the focus out event information
        """
        if event.widget.get() == '':
            event.widget.insert(INSERT, 0)

    def change_schedule_state(self):
        """
        Reverts the state of the selected schedule depending on the 
        previous state.

        """
        if self.time_listbox.curselection():
            selected = self.time_listbox.curselection()[0]
            selected_id = int(self.time_listbox.get(selected).split('|')[0])

            if not self._disabled_alarm[selected_id]:
                # Disabling the schedule so that it does not run until re-enabled
                self._disabled_alarm[selected_id] = True

                # Changing the color of the listbox item to signify its state
                self.change_itembox_item_color(
                    self.time_listbox, selected, '#181818', '#414141')

                # Changing the button text
                self.change_schedule_state_btn['text'] = 'Enable'

                # Changing the state of the schedule to disabled in the database
                self.change_database_alarm_state('alarm_info', selected_id, 0)

            else:
                # Re-enabling the schedule
                self._disabled_alarm[selected_id] = False

                # Changing the color of the listbox item to signify its state
                self.change_itembox_item_color(
                    self.time_listbox, selected, 'white', 'white')

                # Changing the button text
                self.change_schedule_state_btn['text'] = 'Disable'

                # Change the state of the schedule to enabled in the database
                self.change_database_alarm_state('alarm_info', selected_id, 1)

        elif self.disturb_listbox.curselection():
            selected = self.disturb_listbox.curselection()[0]
            selected_id = int(self.disturb_listbox.get(selected).split('|')[0])

            if not self.disturb_disabled[selected_id]:
                # Disabling the schedule so that it does not run until re-enabled
                self.disturb_disabled[selected_id] = True

                # Changing the color of the listbox item to signify its state
                self.change_itembox_item_color(
                    self.disturb_listbox, selected, '#181818', '#414141')

                # Changing the button text
                self.change_schedule_state_btn['text'] = 'Enable'

                # Change the state of the schedule to disabled in the database
                self.change_database_alarm_state(
                    'do_not_disturb', selected_id, 0)

            else:
                # Re-enabling the schedule
                self.disturb_disabled[selected_id] = False

                # Changing the color of the listbox item to signify its state
                self.change_itembox_item_color(
                    self.disturb_listbox, selected, 'white', 'white')

                # Changing the button text
                self.change_schedule_state_btn['text'] = 'Disable'

                # Change the state of the schedule to enabled in the database
                self.change_database_alarm_state(
                    'do_not_disturb', selected_id, 1)

    def change_itembox_item_color(self, widget, item, fg_color, select_color):
        """Changes the itembox item colors to signify its current state

        Args:
            widget (Tkinter.Listbox): The listbox those item colors to change
            item (int): Index of the listbox item to change
            fg_color (str): Foreground color to set to the item
            select_color (str): Selection color to set the item
        """
        widget.itemconfig(item, fg=fg_color)
        widget.itemconfig(item, selectforeground=select_color)

    def change_database_alarm_state(self, table_name, id_, state):
        """Updates the state of the schedule in the database.

        Args:
            table_name (str): Name of the table whose schedule state to change
            id_ (int): The ID of the schedule
            state (int): Current state of the schedule
        """
        query = f'UPDATE {table_name} SET state={state} where id={id_};'

        try:
            cur.execute(query)
            con.commit()

        except:
            with open('error_log.txt', 'a') as f:
                f.write('['+str(datetime.now())+']\n')
                traceback.print_exc(file=f)
                f.write('\n')
            messagebox.showerror(
                'Failed', 'Could Not Update the Database. Contact Developer.', icon='error')

    def change_state_btn_text(self, event):
        """Changes the text of the change_schedule_state_btn button to 
        "Enable" or "Disable" depending on the state of the selected schedule

        Args:
            event ([Tkinter.Event]): Contains information of the ListboxSelect event
        """
        # Making sure the event is not called for focusing on an empty listbox
        if event.widget.curselection():
            if event.widget.winfo_name() == '!listbox':
                selected = self.time_listbox.curselection()[0]
                selected_id = int(
                    self.time_listbox.get(selected).split('|')[0])

                if self._disabled_alarm[selected_id]:
                    self.change_schedule_state_btn['text'] = 'Enable'
                else:
                    self.change_schedule_state_btn['text'] = 'Disable'

            elif event.widget.winfo_name() == '!listbox2':
                selected = self.disturb_listbox.curselection()[0]
                selected_id = int(
                    self.disturb_listbox.get(selected).split('|')[0])

                if self.disturb_disabled[selected_id]:
                    self.change_schedule_state_btn['text'] = 'Enable'
                else:
                    self.change_schedule_state_btn['text'] = 'Disable'

    def save(self):
        """
        Saves the given Scheduled Time

        """
        # Making sure data is valid
        if self.ent_hour.get() == '0' and self.ent_min.get() == '0' and self.ent_sec.get() == '0':
            messagebox.showwarning(
                'Warning', 'Scheduled time Cannot be All Zero.', icon='warning')
            return

        # For the rare chance of getting an empty string
        hr = int(self.ent_hour.get()) if self.ent_hour.get() != '' else 0
        min_ = int(self.ent_min.get()) if self.ent_min.get() != '' else 0
        sec = int(self.ent_sec.get()) if self.ent_sec.get() != '' else 0
        interval = float(self.ent_interval.get()
                         ) if self.ent_interval.get() != '' else 0

        # Storing the time from the entries
        time = f'{hr}:{min_}:{sec}'

        # Storing the message
        message = self.message_area.get(0.0, 'end-1c').strip()

        # Query to insert info in the database
        query = f"INSERT INTO alarm_info(time, message, interval, state) VALUES('{time}', '{message}', {interval}, 1);"
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
            self.ent_interval.delete(0, END)
            self.ent_hour.insert(INSERT, '0')
            self.ent_min.insert(INSERT, '0')
            self.ent_sec.insert(INSERT, '0')
            self.ent_interval.insert(INSERT, '0')

            self.message_area.delete(0.0, 'end-1c')

            messagebox.showinfo('Success', 'Schedule Set.')
            self.schedule_alarm()
        except:
            with open('error_log.txt', 'a') as f:
                f.write('['+str(datetime.now())+']\n')
                traceback.print_exc(file=f)
                f.write('\n')
            messagebox.showerror(
                'Warning', 'Could not Save to Database.', icon='warning')

    def dont_disturb_schedule_save(self):
        """
        Stores the "Do Not Disturb" time schedules in the database

        """
        # Taking values from the entries
        if self.from_am_pm.get() and self.to_am_pm.get():
            f_hr = int(self.from_hr.get()) if self.from_hr.get(
            ) != '0' and self.from_hr.get() != '' else 12
            t_hr = int(self.to_hr.get()) if self.to_hr.get(
            ) != '0' and self.to_hr.get() != '' else 12

            # For the rare chance of getting an empty string
            f_min = int(self.from_min.get()
                        ) if self.from_min.get() != '' else 0
            t_min = int(self.to_min.get()) if self.to_min.get() != '' else 0

            f_sec = int(self.from_sec.get()
                        ) if self.from_sec.get() != '' else 0
            t_sec = int(self.to_sec.get()) if self.to_sec.get() != '' else 0

            from_time = f'{f_hr}:{f_min}:{f_sec} {self.from_am_pm.get()}'
            to_time = f'{t_hr}:{t_min}:{t_sec} {self.to_am_pm.get()}'

            query = f"INSERT INTO do_not_disturb(from_time, to_time, state) VALUES('{from_time}', '{to_time}', 1)"
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
                with open('error_log.txt', 'a') as f:
                    f.write('['+str(datetime.now())+']\n')
                    traceback.print_exc(file=f)
                    f.write('\n')
                messagebox.showerror(
                    'Failed', 'Could Not Set Schedule.', icon='error')
        else:
            messagebox.showwarning(
                'Warning', "You have to Select either 'AM' or 'PM'", icon='warning')

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
            if int(input) < 24 and input[-1] != ' ' and input[0] != ' ':
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
            if int(input) < 13 and input[-1] != ' ' and input[0] != ' ':
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
            if int(input) <= 60 and input[-1] != ' ' and input[0] != ' ':
                return True
            else:
                return False

        except ValueError:
            if input == '':
                return True
            else:
                return False

    def validate_interval(self, input):
        """Validate if the correct type of input is given to the interval entries

        Args:
            input (str): The string in the entries typed by the user

        Returns:
            boolean: True if character typed is currect, False otherwise
        """
        # Checks if the current string in the entry is numeric
        if input == '':
            return True
        else:
            try:
                float(input)
                return True
            except:
                return False

    def check_disturb_mode(self):
        """
        Checks if do not disturb should be turned on based on scheduled time.

        """
        now = datetime.now()
        if datetime.strftime(now, '%p') == 'PM':
            self.saved_date = now
        else:
            self.saved_date = now - timedelta(days=1)

        results = cur.execute(
            'SELECT id, from_time, to_time FROM do_not_disturb').fetchall()
        if results:
            self.do_not_disturb = False
            for result in results:
                if self.disturb_disabled.get(result[0], -1) == -1:
                    self.disturb_disabled[result[0]] = False

                if not self.disturb_disabled[result[0]]:
                    if (result[1][-2:]+result[2][-2:]) != 'PMAM':
                        # For "Do Not Disturb" schedules that start and end the same day
                        time_format = '%I:%M:%S %p'
                        from_time = datetime.strptime(
                            result[1], time_format).time()
                        to_time = datetime.strptime(
                            result[2], time_format).time()
                        nowtime = now.time()

                        if nowtime >= from_time and nowtime < to_time:
                            self.do_not_disturb = True
                            break
                    else:
                        # For "Do Not Disturb" schedules that start and end on different day
                        time_format = '%Y-%m-%d %I:%M:%S %p'
                        from_time = datetime.strptime(
                            str(self.saved_date.date())+" "+result[1], time_format)
                        to_time = datetime.strptime(
                            str((self.saved_date+timedelta(days=1)).date())+" "+result[2], time_format)

                        if now >= from_time and now < to_time:
                            self.do_not_disturb = True
                            break
        else:
            self.do_not_disturb = False

    def schedule_alarm(self):
        """
        Checks if the database has schedules and if the alarm GUI is already running or not.
        If database has a schedule and alarm GUI is not currently running, then starts the process
        of running the alarm. Otherwise checks again in 5 seconds.

        """
        # Checking if "Do Not Disturb" mode is on or not
        self.check_disturb_mode()

        # Checking for schedules in database
        results = cur.execute(
            'SELECT id, time, message, interval from alarm_info').fetchall()
        if results:
            global _ALARM_GUI_RUNNING
            return_flag = False
            for result in results:
                # Unpacking the data
                id_, time_data, message, interval = result

                if _ALARM_GUI_RUNNING.get(id_, -1) == -1:
                    # Initializes dictionaries if key does not exist
                    _ALARM_GUI_RUNNING[id_] = False
                    self.validating_schedule[id_] = False

                if self.validating_schedule[id_]:
                    # If schedule is already in the validate_alarm function loop, does not allow another loop
                    continue

                time = time_data.split(':')

                scheduled_time = datetime.now(
                ) + timedelta(hours=int(time[0]), minutes=int(time[1]), seconds=int(time[2]))  # The time when the alarm should ring

                if not _ALARM_GUI_RUNNING[id_] and not self._disabled_alarm[id_] and not self.usr_do_not_disturb.get() and not self.do_not_disturb:
                    return_flag = True
                    self.validating_schedule[id_] = True
                    self.validate_alarm(
                        (scheduled_time, id_, message, interval))

            if return_flag:
                return
        # Scheduling a recheck after 5 seconds
        self.root.after(1000, self.schedule_alarm)

    def validate_alarm(self, data):
        """Checks if it is time to ring the alarm. Checks every 1 second. Also handles the reset event and "Do Not Disturb" schedules

        Args:
            data (tuple): The tuple that contains the scheduled time datetime object, its id and message
        """
        # Checking if "Do Not Disturb" mode is on or not
        self.check_disturb_mode()

        # Unpacking the data
        scheduled_time, id_, message, interval = data

        global _ALARM_GUI_RUNNING
        if datetime.now() >= scheduled_time and not _ALARM_GUI_RUNNING.get(id_, True) and not self._disabled_alarm[id_] and not self.usr_do_not_disturb.get() and not self.do_not_disturb:
            # Starts the alarm when the time is right
            self.sound_alarm((id_, message, interval))

            # Telling that this schedule is no longer in the validate_alarm function loop
            self.validating_schedule[id_] = False
            self.schedule_alarm()
            return

        elif self.usr_do_not_disturb.get() or self.do_not_disturb or _ALARM_GUI_RUNNING.get(id_, True) or self._disabled_alarm[id_]:
            # Telling that this schedule is no longer in the validate_alarm function loop
            self.validating_schedule[id_] = False
            self.schedule_alarm()
            return

        # Scheduling to recheck in 1 second
        self.root.after(1000, self.validate_alarm, data)

    def sound_alarm(self, id_message):
        """Starts the alarm GUI.

        Args:
            message (str): The message to be shown when alarm rings
        """
        global _ALARM_GUI_RUNNING
        if _ALARM_GUI_RUNNING.get(id_message[0], -1) != -1:
            _ALARM_GUI_RUNNING[id_message[0]] = True

        alarm = Alarm(id_message)


# Slave Window
class Alarm(Toplevel):

    def __init__(self, id_message):
        Toplevel.__init__(self)

        # Root Configuration
        self.config(bg='#181818')
        self.title('Alarm')
        self.geometry('400x200+500+150')
        self.resizable(False, False)
        self.iconbitmap('Images/icon.ico')
        self.protocol('WM_DELETE_WINDOW', self.kill)

        self.id_, message, self.interval = id_message
        # Label
        message_label = Label(
            self, text=message, font=('Modern', 22, 'bold'))
        message_label.pack(pady=30)
        message_label['background'] = '#181818'
        message_label['foreground'] = 'white'

        # Button
        stop_btn = Button(self, text='Stop!', font=('Modern', 14, 'bold'),
                          bg='#414141', relief=FLAT, fg='white', width=15, command=self.kill)
        stop_btn.pack(pady=(40, 0))

        # Plays the alarm sound
        ws.PlaySound('tones/soft_sound.wav', ws.SND_LOOP+ws.SND_ASYNC)
        self.lift()

    def kill(self):
        """
        Stops the alarm from ringing.

        """
        ws.PlaySound(None, ws.SND_PURGE)
        self.after(int(self.interval * 60000), self.interval_handling)
        self.withdraw()

    def interval_handling(self):
        """
        Kills the window after the fixed time interval.

        """
        global _ALARM_GUI_RUNNING
        _ALARM_GUI_RUNNING[self.id_] = False

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
        "Int.TCheckbutton": {
            "configure": {
                "indicatorcolor": '#181818',
                "foreground": '#d90909',
                "focuscolor": '#181818',
                "font": ('Modern', 17, 'bold'),
                "indicatordiameter": 0,
                "borderwidth": 0
            },
            "map": {
                "foreground": [('pressed', '#303030'), ('selected', 'green')],
                "indicatorcolor": [('selected', '#181818'), ('pressed', '#181818')]
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
    root.geometry('572x480+600+250')
    root.resizable(False, False)
    root.iconbitmap('Images/icon.ico')
    app = App(root)
    root.mainloop()


if __name__ == '__main__':
    main()

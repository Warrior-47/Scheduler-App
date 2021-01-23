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
        self.validateHr = self.root.register(self.validate_hr)
        self.validateMS = self.root.register(self.validate_min_sec)

        # Tabs #
        self.tabs = ttk.Notebook(self.root)
        self.tabs.pack(fill='both', expand=True)

        self.schedule_time_tab = ttk.Frame(self.tabs)
        self.no_disturb_time_tab = ttk.Frame(self.tabs)

        self.tabs.add(self.schedule_time_tab, text='Schedule Timer')
        self.tabs.add(self.no_disturb_time_tab,
                      text='Do Not Disturb')

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

        # Time Frame Components #
        # Sub Heading
        self.set_lbl = Label(
            self.time_frame, text='Set Time:', font=('Modern', 22, 'bold'), bg='#181818', fg='white')
        self.set_lbl.place(x=60, y=30)

        # Entries
        self.ent_hour = Entry(
            self.time_frame, font=('Modern', 20, 'bold'), insertbackground='white',
            fg='white', bg='#414141', width=4, justify='center', validate='key',
            validatecommand=(self.validateHr, '%P'), relief=RIDGE, bd=4)
        self.ent_hour.place(x=80, y=85)
        self.ent_hour.insert(INSERT, '0')

        self.ent_min = Entry(
            self.time_frame, font=('Modern', 20, 'bold'), insertbackground='white',
            fg='white', bg='#414141', width=4, justify='center', validate='key',
            validatecommand=(self.validateMS, '%P'), relief=RIDGE, bd=4)
        self.ent_min.place(x=250, y=85)
        self.ent_min.insert(INSERT, '0')

        self.ent_sec = Entry(
            self.time_frame, font=('Modern', 20, 'bold'), insertbackground='white',
            fg='white', bg='#414141', width=4, justify='center', validate='key',
            validatecommand=(self.validateMS, '%P'), relief=RIDGE, bd=4)
        self.ent_sec.place(x=420, y=85)
        self.ent_sec.insert(INSERT, '0')

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

        # Reset Timers
        self.reset_btn = Button(
            self.time_frame, text='Reset Schedules', font=('Modern', 12, 'bold'), bg='#414141', width=15, relief=FLAT, fg='white', command=self.reset)
        self.reset_btn.place(x=430, y=20)

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
        self.do_not_disturb = BooleanVar()
        self.do_not_disturb_ckbox = Checkbutton(self.message_frame, text='Do Not Disturb', activeforeground='white',
                                                activebackground='#181818', selectcolor='#181818', bg='#181818', fg='white', font=(
                                                    'Modern', 14, 'bold'), variable=self.do_not_disturb)
        self.do_not_disturb.set(False)
        self.do_not_disturb_ckbox.place(x=368, y=12)

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
                             validatecommand=(self.validateHr, '%P'), relief=RIDGE, bd=4)
        self.from_hr.place(x=80, y=85)
        self.from_hr.insert(INSERT, '0')

        self.from_min = Entry(self.do_not_disturb_frame, font=('Modern', 20, 'bold'), insertbackground='white',
                              fg='white', bg='#414141', width=4, justify='center', validate='key',
                              validatecommand=(self.validateMS, '%P'), relief=RIDGE, bd=4)
        self.from_min.place(x=250, y=85)
        self.from_min.insert(INSERT, '0')

        self.from_sec = Entry(self.do_not_disturb_frame, font=('Modern', 20, 'bold'), insertbackground='white',
                              fg='white', bg='#414141', width=4, justify='center', validate='key',
                              validatecommand=(self.validateMS, '%P'), relief=RIDGE, bd=4)
        self.from_sec.place(x=420, y=85)
        self.from_sec.insert(INSERT, '0')

        # "From" Entry Labels
        self.from_hr_lbl = Label(
            self.do_not_disturb_frame, text='Hours', fg='white', font='Modern 20 bold', bg='#181818')
        self.from_hr_lbl.place(x=82, y=135)

        self.from_min_lbl = Label(
            self.do_not_disturb_frame, text='Minutes', fg='white', font='Modern 20 bold', bg='#181818')
        self.from_min_lbl.place(x=242, y=135)

        self.from_sec_lbl = Label(
            self.do_not_disturb_frame, text='Seconds', fg='white', font='Modern 20 bold', bg='#181818')
        self.from_sec_lbl.place(x=410, y=135)

        # "From" Colons
        self.from_colon_lbl1 = Label(
            self.do_not_disturb_frame, image=self.colon, bg='#181818')
        self.from_colon_lbl1.place(x=180, y=88)

        self.from_colon_lbl2 = Label(
            self.do_not_disturb_frame, image=self.colon, bg='#181818')
        self.from_colon_lbl2.place(x=350, y=88)

        # "To" Heading
        self.to_lbl = Label(self.do_not_disturb_frame,
                            text='To:', font=('Modern', 22, 'bold'), bg='#181818', fg='white')
        self.to_lbl.place(x=60, y=190)

        # "To" Entries
        self.to_hr = Entry(self.do_not_disturb_frame, font=('Modern', 20, 'bold'), insertbackground='white',
                           fg='white', bg='#414141', width=4, justify='center', validate='key',
                           validatecommand=(self.validateHr, '%P'), relief=RIDGE, bd=4)
        self.to_hr.place(x=80, y=245)
        self.to_hr.insert(INSERT, '0')

        self.to_min = Entry(self.do_not_disturb_frame, font=('Modern', 20, 'bold'), insertbackground='white',
                            fg='white', bg='#414141', width=4, justify='center', validate='key',
                            validatecommand=(self.validateMS, '%P'), relief=RIDGE, bd=4)
        self.to_min.place(x=250, y=245)
        self.to_min.insert(INSERT, '0')

        self.to_sec = Entry(self.do_not_disturb_frame, font=('Modern', 20, 'bold'), insertbackground='white',
                            fg='white', bg='#414141', width=4, justify='center', validate='key',
                            validatecommand=(self.validateMS, '%P'), relief=RIDGE, bd=4)
        self.to_sec.place(x=420, y=245)
        self.to_sec.insert(INSERT, '0')

        # "To" Entry Labels
        self.to_hr_lbl = Label(
            self.do_not_disturb_frame, text='Hours', fg='white', font='Modern 20 bold', bg='#181818')
        self.to_hr_lbl.place(x=82, y=295)

        self.to_min_lbl = Label(
            self.do_not_disturb_frame, text='Minutes', fg='white', font='Modern 20 bold', bg='#181818')
        self.to_min_lbl.place(x=242, y=295)

        self.to_sec_lbl = Label(
            self.do_not_disturb_frame, text='Seconds', fg='white', font='Modern 20 bold', bg='#181818')
        self.to_sec_lbl.place(x=410, y=295)

        # "To" Colons
        self.to_colon_lbl1 = Label(
            self.do_not_disturb_frame, image=self.colon, bg='#181818')
        self.to_colon_lbl1.place(x=180, y=248)

        self.to_colon_lbl2 = Label(
            self.do_not_disturb_frame, image=self.colon, bg='#181818')
        self.to_colon_lbl2.place(x=350, y=248)

        self.save_no_disturb = Button(self.no_disturb_time_tab, text='Save', font=('Modern', 15, 'bold'),
                                      bg='#414141', relief=FLAT, fg='white', width=13,
                                      command=self.no_disturb_schedule_save)
        self.save_no_disturb.pack()

        #
        # Starting Alarm Timer #
        self.schedule_alarm()

    #
    # Methods #
    def no_disturb_schedule_save(self):
        pass

    def on_closing(self):
        answer = messagebox.askyesno(
            'Close', 'If You Close This Window, the Alarm will not Repeat.\nDo You Really Want to Quit?', icon='info')
        if answer:
            self.root.destroy()

    def restart(self):
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
        time = f'{self.ent_hour.get()}:{self.ent_min.get()}:{self.ent_sec.get()}'  # Storing the time from the entries
        # Storing the message
        message = self.message_area.get(0.0, 'end-1c')
        # Query to insert info in the database
        query = f"INSERT INTO alarm_info(time, message) VALUES('{time}', '{message}');"
        try:
            # Clearing the entries and going back to default values
            self.ent_hour.delete(0, END)
            self.ent_min.delete(0, END)
            self.ent_sec.delete(0, END)
            self.ent_hour.insert(INSERT, '0')
            self.ent_min.insert(INSERT, '0')
            self.ent_sec.insert(INSERT, '0')

            self.message_area.delete(0.0, 'end-1c')

            # Executing the query
            cur.execute(query)
            con.commit()

            messagebox.showinfo('Success', 'Schedule Set')
        except:
            messagebox.showerror(
                'Warning', 'Could not Save to Database', icon='warning')

    def reset(self):
        """
        Deletes all the scheduled times from the database

        """
        answer = messagebox.askyesno(
            'Reset', 'Are You Sure You Want to Delete All Your Schedules?', icon='info')
        if answer:
            query = 'DELETE FROM alarm_info'
            try:
                cur.execute(query)
                con.commit()
                # Setting the parameter to make sure the alarm is also resetted
                self.reset_handled = False
                messagebox.showinfo('Reset', 'All Schedules Cleared')
            except:
                messagebox.showerror(
                    'Reset', 'Failed to Clear Schedules. Contact Developer', icon='warning')

    def validate_hr(self, input):
        """Validate if the correct type of input is given to the hours entry

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
        # Checking for schedules in database
        result = cur.execute('SELECT time, message from alarm_info').fetchone()
        if result is not None:
            global _ALARM_GUI_RUNNING, _DISABLED_ALARM
            # Splitting the time into hours, minutes and seconds
            time = result[0].split(':')
            scheduled_time = datetime.now(
            ) + timedelta(hours=int(time[0]), minutes=int(time[1]), seconds=int(time[2]))  # The time when the alarm should ring

            if not _ALARM_GUI_RUNNING and not _DISABLED_ALARM and not self.do_not_disturb.get():
                self.validate_alarm(scheduled_time, result[1])
                return

        # Scheduling a recheck after 5 seconds
        self.root.after(5000, self.schedule_alarm)

    def validate_alarm(self, scheduled_time, message):
        """Checks if it is time to ring the alarm. Checks every 1 second. Also handles the reset event.

        Args:
            scheduled_time (datetime.datetime): The list that contains the hours, minutes and seconds of the schedule
            message (str): The message to be shown when alarm rings
        """
        if datetime.now() >= scheduled_time and self.reset_handled and not self.do_not_disturb.get():
            self.sound_alarm(message)
            self.schedule_alarm()
            return
        elif not self.reset_handled or self.do_not_disturb.get():
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
        "TNotebook": {
            "configure": {
                "background": '#181818',  # Your margin color
                # margins: left, top, right, separator
                "tabmargins": [2, 5, 0, 0],
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

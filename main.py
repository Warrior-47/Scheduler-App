from tkinter import messagebox
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

        self.reset_handled = True

        # Validation #
        self.validateHr = self.root.register(self.validate_hr)
        self.validateMS = self.root.register(self.validate_min_sec)

        # Frames #
        self.time_frame = Frame(
            self.root, width=500, height=200, bg='#181818')
        self.time_frame.pack(fill=X)

        self.message_frame = Frame(
            self.root, width=500, height=150, bg='#181818')
        self.message_frame.pack(fill=X)

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

        # Save Button #
        self.save_btn = Button(
            self.root, text='Save', font=('Modern', 15, 'bold'), bg='#414141', relief=FLAT, fg='white', width=13, command=self.Save)
        self.save_btn.pack(padx=(61, 0), pady=(20, 0), side='left')

        self.restart_alarm_btn = Button(
            self.root, text='Restart Alarm', font=('Modern', 15, 'bold'), bg='#414141', relief=FLAT, fg='white', width=13, command=self.restart)
        self.restart_alarm_btn.pack(padx=(0, 67), pady=(20, 0), side='right')

        # Starting Alarm Timer #
        self.schedule_alarm()

    #
    # Methods #
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

            # Success message
            messagebox.showinfo('Success', 'Schedule Set')
        except:
            messagebox.showerror(
                'Warning', 'Could not Save to Database', icon='warning')

    def reset(self):
        query = 'DELETE FROM alarm_info'
        try:
            cur.execute(query)
            con.commit()
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
            global _ALARM_GUI_RUNNING
            # Splitting the time into hours, minutes and seconds
            time = result[0].split(':')
            scheduled_time = datetime.now(
            ) + timedelta(hours=int(time[0]), minutes=int(time[1]), seconds=int(time[2]))  # The time when the alarm should ring

            if not _ALARM_GUI_RUNNING and not _DISABLED_ALARM:
                self.validate_alarm(scheduled_time, result[1])
                return

        # Scheduling a recheck after 5 seconds
        self.root.after(5000, self.schedule_alarm)

    def validate_alarm(self, scheduled_time, message):
        """Checks if it is time to ring the alarm. Checks every 1 second.

        Args:
            scheduled_time (list): The list that contains the hours, minutes and seconds of the schedule
            message (str): The message to be shown when alarm rings
        """
        if datetime.now() >= scheduled_time and self.reset_handled:
            self.sound_alarm(message)
            self.schedule_alarm()
            return
        elif not self.reset_handled:
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

        ws.PlaySound('tones/soft_sound.wav', ws.SND_LOOP+ws.SND_ASYNC)
        self.lift()

    def quit(self):
        global _ALARM_GUI_RUNNING, _DISABLED_ALARM
        _ALARM_GUI_RUNNING = False
        _DISABLED_ALARM = True
        ws.PlaySound(None, ws.SND_PURGE)
        self.destroy()

    def kill(self):
        global _ALARM_GUI_RUNNING
        _ALARM_GUI_RUNNING = False

        ws.PlaySound(None, ws.SND_PURGE)
        self.destroy()


def main():
    # erase_db()
    root = Tk()
    root.config(bg='#181818')
    root.title('Scheduler')
    root.geometry('572x442+1200+250')
    root.resizable(False, False)

    app = App(root)

    root.mainloop()


def erase_db():
    cur.execute('delete from alarm_info')
    con.commit()


if __name__ == '__main__':
    main()
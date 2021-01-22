import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from ttkthemes import themed_tk as thtk

import sqlite3
import threading
import alarm
from time import sleep

con = sqlite3.connect('database.db')
cur = con.cursor()


class Application(object):

    def __init__(self, master):
        self.master = master

        style = ttk.Style()
        style.configure('TButton', foreground='white',
                        font='Modern 15 bold')
        style.configure('reset.TButton', foreground='white',
                        font='Modern 12 bold')
        style.configure('TEntry', foreground='white', insertcolor='white')
        style.configure('TLabel', background='#181818', foreground='white')

        self.validateHr = self.master.register(self.validate_hr)
        self.validateMS = self.master.register(self.validate_min_sec)

        # Frames #
        self.time_frame = tk.Frame(
            self.master, width=500, height=200, bg='#181818')
        self.time_frame.pack(fill=tk.X)

        self.message_frame = tk.Frame(
            self.master, width=500, height=150, bg='#181818')
        self.message_frame.pack(fill=tk.X)

        # Time Frame Components #
        # Sub Heading
        self.set_lbl = ttk.Label(
            self.time_frame, text='Set Time:', font=('Modern', 22, 'bold'))
        self.set_lbl.place(x=60, y=30)

        # Entries
        self.ent_hour = ttk.Entry(
            self.time_frame, font=('Modern', 20, 'bold'), width=4, justify='center', validate='key', validatecommand=(self.validateHr, '%P'))
        self.ent_hour.place(x=80, y=85)
        self.ent_hour.insert(tk.INSERT, '0')

        self.ent_min = ttk.Entry(
            self.time_frame, font=('Modern', 20, 'bold'), width=4, justify='center', validate='key', validatecommand=(self.validateMS, '%P'))
        self.ent_min.place(x=250, y=85)
        self.ent_min.insert(tk.INSERT, '0')

        self.ent_sec = ttk.Entry(
            self.time_frame, font=('Modern', 20, 'bold'), width=4, justify='center', validate='key', validatecommand=(self.validateMS, '%P'))
        self.ent_sec.place(x=420, y=85)
        self.ent_sec.insert(tk.INSERT, '0')

        # Entry Labels
        self.hour_lbl = ttk.Label(
            self.time_frame, text='Hours',  font='Modern 20 bold')
        self.hour_lbl.place(x=82, y=135)

        self.min_lbl = ttk.Label(
            self.time_frame, text='Minutes',  font='Modern 20 bold')
        self.min_lbl.place(x=242, y=135)

        self.sec_lbl = ttk.Label(
            self.time_frame, text='Seconds',  font='Modern 20 bold')
        self.sec_lbl.place(x=410, y=135)

        # Colons
        self.colon = tk.PhotoImage(file='Images/colon.png')
        self.colon_lbl1 = tk.Label(
            self.time_frame, image=self.colon, bg='#181818')
        self.colon_lbl1.place(x=180, y=88)

        self.colon_lbl2 = tk.Label(
            self.time_frame, image=self.colon, bg='#181818')
        self.colon_lbl2.place(x=350, y=88)

        # Reset Timers
        self.reset_btn = ttk.Button(
            self.time_frame, text='Reset Schedules', style='reset.TButton', command=self.reset)
        self.reset_btn.place(x=430, y=20)

        # Message Frame Components #
        # Sub Heading
        self.message_lbl = ttk.Label(
            self.message_frame, text='Message:', font=('Modern', 22, 'bold'))
        self.message_lbl.place(x=60, y=10)

        # Message Area
        self.message_area = tk.Text(
            self.message_frame, width=40, height=6, bg='#414141',
            fg='white', font=('Modern', 18, 'bold'), wrap=tk.WORD, insertbackground='white')
        self.message_area.place(x=60, y=50)

        # Save Button #
        self.save_btn = ttk.Button(
            self.master, text='Save', command=self.Save)
        self.save_btn.pack(padx=(61, 0), pady=(20, 0), side='left')

        self.restart_alarm_btn = ttk.Button(
            self.master, text='Restart Alarm', command=self.restart)
        self.restart_alarm_btn.pack(padx=(0, 67), pady=(20, 0), side='right')

    def reset(self):
        try:
            cur.execute("DELETE FROM alarm_info")
            con.commit()
            messagebox.showinfo(
                'Success', "Successfully resetted all Schedules. Set a new Schedule")
            self.master.destroy()
            sleep(2)
            main()

        except:
            messagebox.showwarning(
                'Failed', 'Could not Delete Schedules. E ki Holo?', icon='warning')

    def restart(self):
        if not alarm.running:
            messagebox.showinfo('Restart', 'Alarm is Running Again')
            startAlarm()
        else:
            messagebox.showinfo('Restart', 'Alarm Already Running')

    def Save(self):
        time = f'{self.ent_hour.get()}:{self.ent_min.get()}:{self.ent_sec.get()}'
        message = self.message_area.get(0.0, 'end-1c')
        query = f"INSERT INTO alarm_info(time, message) VALUES('{time}', '{message}');"
        try:
            cur.execute(query)
            con.commit()

            self.ent_hour.delete(0, tk.END)
            self.ent_min.delete(0, tk.END)
            self.ent_sec.delete(0, tk.END)
            self.ent_hour.insert(tk.INSERT, '0')
            self.ent_min.insert(tk.INSERT, '0')
            self.ent_sec.insert(tk.INSERT, '0')

            self.message_area.delete(0.0, 'end-1c')

            messagebox.showinfo('Success', 'Schedule Set')
        except:
            messagebox.showerror(
                'Warning', 'Could not Save to Database', icon='warning')

    def validate_hr(self, input):
        try:
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
        try:
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


def startAlarm():
    process = threading.Thread(target=alarm.main)
    process.daemon = True
    process.start()


def main():
    root = thtk.ThemedTk()
    root.get_themes()
    root.set_theme('equilux')
    app = Application(root)
    root.config(bg='#181818')
    root.title('Scheduler')
    root.geometry("572x442+400+150")
    root.resizable(False, False)
    startAlarm()
    root.iconify()
    root.mainloop()


if __name__ == "__main__":
    main()

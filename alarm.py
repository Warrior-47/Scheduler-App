from tkinter import ttk
from ttkthemes import themed_tk as thtk
from datetime import datetime, timedelta

import winsound as ws
import sqlite3
import time

running = False


class Alarm(object):

    def __init__(self, root, message, time):
        self.master = root

        style = ttk.Style()
        style.configure('.!button', foreground='white', font='Modern 15 bold')
        style.configure(
            'TLabel', background='#181818', foreground='white')

        self.splitted_time = time

        message_label = ttk.Label(
            self.master, text=message, font=('Modern', 22, 'bold'))
        message_label.pack(pady=30)
        message_label['background'] = '#181818'
        message_label['foreground'] = 'white'

        stop_btn = ttk.Button(self.master, text='Stop!', command=self.kill)
        stop_btn.pack(padx=20, pady=(20, 0), side='left')

        quit_btn = ttk.Button(self.master, text='Quit', command=self.quit)
        quit_btn.pack(padx=20, pady=(20, 0), side='right')

        sound_alarm_time = datetime.now() + timedelta(hours=int(
            self.splitted_time[0]), minutes=int(self.splitted_time[1]), seconds=int(self.splitted_time[2]))

        while True:
            now = datetime.now()
            if now >= sound_alarm_time:
                break
        ws.PlaySound('tones/soft_sound.wav', ws.SND_LOOP+ws.SND_ASYNC)
        self.master.lift()
        self.master.deiconify()

    def quit(self):
        global running
        running = False
        ws.PlaySound(None, ws.SND_PURGE)
        self.master.destroy()

    def kill(self):
        ws.PlaySound(None, ws.SND_PURGE)
        self.master.withdraw()

        sound_alarm_time = datetime.now() + timedelta(hours=int(
            self.splitted_time[0]), minutes=int(self.splitted_time[1]), seconds=int(self.splitted_time[2]))

        while True:
            now = datetime.now()
            if now >= sound_alarm_time:
                break
        ws.PlaySound('tones/soft_sound.wav', ws.SND_LOOP+ws.SND_ASYNC)
        self.master.deiconify()


def on_closing():
    pass


def main():
    global running
    running = True
    root = thtk.ThemedTk()
    root.get_themes()
    root.set_theme('equilux')
    root.config(bg='#181818')
    root.title('Scheduler')
    root.geometry("400x200+500+150")
    root.resizable(False, False)

    while True:
        con = sqlite3.connect('database.db', check_same_thread=False)
        cur = con.cursor()
        query = f'SELECT time, message from alarm_info;'
        res = cur.execute(query).fetchone()
        con.close()
        if res is not None:
            break

    time_broken = res[0].split(':')
    root.protocol("WM_DELETE_WINDOW", on_closing)

    app = Alarm(root, res[1], time_broken)
    root.mainloop()


if __name__ == "__main__":
    main()

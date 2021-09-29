# Scheduler App

## Description

 A tkinter application that works like a reminder. Saves a time in hours, minutes and/or seconds, then sounds an alarm everytime that much time has passed.

## Usage

### **Schedule Timer Tab**

Users can set a specific amount of time here. Everytime this much time has passed, the alarm will ring. Users can also set an interval period. If set, after the user stops the alarm, the internal timer will pause for the interval period set.

For example, if I set a time of 30 mins and an interval of 10 mins, the first alarm will ring after 30 mins. After I stop the alarm, the next alarm will ring after 30 + 10 = 40 minutes.

![Schedule Time GUI](/images/alarm_gui.JPG)

In the message section, you can write a message and that message will be shown everytime the alarm rings.

There's also a **Do Not Disturb** checkbox. No alarm will ring as long as it is checked.

![Schedule Time GUI](/images/timer_setter.JPG)

### **Do Not Disturb Tab**

You can set a period of time here and no alarm will ring during this period of time. This period of time should be between 12:00:00 AM to 11:59:59 PM.

![Schedule Time GUI](/images/do_not_disturb_setter.JPG)

### **Schedules Tab**

Users can see all their saved Time Period schedules and Do Not Disturb schedules. Users can update existing schedules (both Time and Do Not Disturb) using the **Update** button and use the **Delete** button to delete any schedule.

The **Enable/Disable** button will either enable or disable the selected Time/Do Not Disturb schedule. Darkened schedules are disabled.

![Schedule Time GUI](/images/schedule_tab.JPG)

## Download

Go to https://warrior-47.github.io/Scheduler-App/dist/Scheduler.zip to download the app.

> If you want the app to run at startup, go to the folder "Start With Windows" in the main application folder, and run the python script.

## Project Status

The development of this project has stopped. If you want to contribute, you are free to volunteer.
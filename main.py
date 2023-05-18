import tkinter as tk
from tkinter import filedialog
from icalendar import Calendar, Event, Alarm
from datetime import datetime, timedelta, date, time
from threading import Thread
from bs4 import BeautifulSoup
import re

def parse_time(time_str):
    hours, minutes = re.findall(r'\d+', time_str)
    return time(hour=int(hours), minute=int(minutes))

def convert_timetable_to_ics(timetable_file, output_file):
    with open(timetable_file, 'r') as file:
        content = file.read()

    soup = BeautifulSoup(content, 'html.parser')
    table = soup.find('table', class_='exams')

    cal = Calendar()

    for row in table.find_all('tr'):
        cells = row.find_all('td')
        if len(cells) >= 4:
            event_date = datetime.strptime(cells[0].text.strip(), '%a %d/%m/%Y').date()
            start_time_str = cells[1].text.strip()
            end_time_str = cells[2].text.strip()
            event_name = cells[6].text.split(':', 1)[1].strip()
            event_location = cells[7].text.strip()  # Assuming the event location is in the 7th cell
            event_location += ', ' + cells[8].text.strip()  # Append the content of the 8th cell if available

            start_time = parse_time(start_time_str)
            end_time = parse_time(end_time_str)

            event = Event()
            event.add('summary', event_name)
            event.add('location', event_location)
            
            start_datetime = datetime.combine(event_date, start_time)
            end_datetime = datetime.combine(event_date, end_time)

            event.add('dtstart', start_datetime)
            event.add('dtend', end_datetime)
               
            night_before_alarm = Alarm()
            night_before_alarm.add('action', 'DISPLAY')
            night_before_alarm.add('trigger', timedelta(days=-1))
            night_before_alarm.add('description', 'Night before reminder')

            # Add reminder 30 minutes before
            minutes_before_alarm = Alarm()
            minutes_before_alarm.add('action', 'DISPLAY')
            minutes_before_alarm.add('trigger', timedelta(minutes=-30))
            minutes_before_alarm.add('description', '30 minutes before reminder')

            # Add alarms to the event
            event.add_component(night_before_alarm)
            event.add_component(minutes_before_alarm)
            cal.add_component(event)

    with open(output_file, 'wb') as file:
        file.write(cal.to_ical())

    print(f'Successfully converted timetable to {output_file}.')

def browse_folder():
    folder_path = filedialog.askdirectory()
    entry_folder.delete(0, tk.END)
    entry_folder.insert(tk.END, folder_path)
    
def browse_file():
    file_path = filedialog.askopenfilename(filetypes=[('HTML Files', '*.html')])
    entry_path.delete(0, tk.END)
    entry_path.insert(tk.END, file_path)


def convert():
    timetable_file = entry_path.get()
    output_folder = entry_folder.get()
    output_file = f'{output_folder}/timetable.ics'
    loading_label.config(text='Converting...', fg='blue')
    loading_label.update()

    def convert_thread():
        convert_timetable_to_ics(timetable_file, output_file)
        loading_label.config(text='Conversion complete', fg='green')

    thread = Thread(target=convert_thread)
    thread.start()


# Create the main window
window = tk.Tk()
window.title('Timetable Converter')

# Create and position the widgets
label_path = tk.Label(window, text='Timetable File:')
label_path.pack()

entry_path = tk.Entry(window, width=50)
entry_path.pack()

browse_button = tk.Button(window, text='Browse', command=browse_file)
browse_button.pack()

label_folder = tk.Label(window, text='Output Folder:')
label_folder.pack()

entry_folder = tk.Entry(window, width=50)
entry_folder.pack()

browse_folder_button = tk.Button(window, text='Browse', command=browse_folder)
browse_folder_button.pack()

convert_button = tk.Button(window, text='Convert', command=convert)
convert_button.pack()

loading_label = tk.Label(window, text='', fg='blue')
loading_label.pack()

# Start the main event loop
window.mainloop()

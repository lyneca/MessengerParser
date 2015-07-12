__author__ = 'wing2048'
import re
import os
import datetime

from bs4 import BeautifulSoup


def safe_print(m):
    try:
        print(m)
    except UnicodeEncodeError:
        for char in m.message:
            try:
                print(char, end='')
            except UnicodeEncodeError:
                pass
        print()


def verify(obj, typ):
    if type(obj) == typ:
        return 'good'
    else:
        return 'bad'


def verify_len_gtr(obj, ln):
    if len(obj) > ln:
        return 'good'
    else:
        return 'bad'


def pause():
    os.system('pause>nul')


def zero(s, n):
    return '0' * (n - len(s)) + str(s)


def plural(i):
    if i > 1 or i == 0:
        return 's'
    else:
        return ''


months = {
    'january': 1,
    'febuary': 2,
    'march': 3,
    'april': 4,
    'may': 5,
    'june': 6,
    'july': 7,
    'august': 8,
    'september': 9,
    'october': 10,
    'november': 11,
    'december': 12,
}
reversed_months = {}
for key in months:
    reversed_months[months[key]] = key


class Message():
    def __init__(self, n, t, m):
        self.sender = n
        self.time = t
        self.message = m
        if len(self.sender.split()) > 1:
            self.first_name = self.sender.split()[0]
        else:
            self.first_name = self.sender
        self.date = datetime.date(int(self.time.split()[2]),
                                  months[self.time.split()[0].lower()],
                                  int(self.time.split()[1]))
        self.time = self.time.split()[-1]
        self.hours = int(self.time.split(':')[0])
        self.minutes = int(self.time.split(':')[1][:-2])
        self.half = self.time.split(':')[1][-2:]
        if self.half == 'pm':
            self.hours += 12
        self.time = str(self.hours) + ':' + str(self.minutes)
        self.display = '%s %s %s: %s' % (self.date, self.time, self.first_name, self.message)

    def __str__(self):
        return self.display


print('1: Load from a messages.htm file')
print('2: Load from a cache file')
choice = int(input('> '))
if choice == 1:
    messages = {}
    print('Reading htm file into text... ', end='')
    with open('messages.htm', errors='ignore') as file:
        n = open('new_file.tmp', 'x')
        for line in file:
            line = line.replace('</p>', '</p>\n')
            line = line.replace('<p>', '<p>\n')
            line = line.replace('<\h1>', '<\h1>\n')
            line = line.replace('<span class="user">', '<span class="user">\n')
            line = line.replace('<div class="thread">', '<div class="thread">\n[[NEW|THREAD]] ')
            n.write(line + '\n')
        n.close()
        n = open('new_file.tmp')

        soup = BeautifulSoup(n, 'html.parser')
        n.close()
        os.remove(n.name)
        text = soup.get_text()
    print('done.')
    flag = False
    print('Splitting text... ', end='')
    text = text.split('\n')
    print('done.')
    name, send_time, message = ('', '', '')
    print('Regexing text... ', end='')
    i = 0
    out = []
    for line in text:
        n_line = re.sub(
            r'(\w+ \w+)(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday), (\w+) (\d+), (\d+) at (\d+:\d+\w+) \w+\+\d+',
            r'\1 - \3 \4 \5 at \6', line)
        out.append(n_line)
        i += 1
    text = out
    print('done. %s lines regexed.' % i)
    # f = open('text.txt', 'x')
    # for line in text:
    # f.write(line + '\n')
    # f.close()
    # os.remove(f.name)
    print('Variable is type %s (%s) and length %s (%s). ' % (
        type(text), verify(text, list), len(text), verify_len_gtr(text, 0)))
    print('Objectifying... ', end='')
    users = []
    for line in text:
        if re.search(r'\w+ \w+ - \w+ \d+ \d+ at \d+:\d+[ap]m', line):
            name, send_time = [x.strip() for x in line.split('-')]
            flag = True
        elif '[[NEW|THREAD]]' in line:
            users = line[15:]
            messages[users] = []
        else:
            if flag:
                message = line
                messages[users].append(Message(name, send_time, message.strip()))
    print('done.')
    print('Reversing order... ', end='')
    for x in messages:
        messages[x].reverse()
    print('done.')
    print('Removing blank and duplicate messages... ', end='')
    for user in messages:
        for message in messages[user]:
            if message.message == '':
                messages[user].remove(message)
    print('done.')
elif choice == 2:
    messages = {}
    with open('cache.db') as file:
        for line in file:
            if line.split()[0] == '[[NEW|THREAD]]':
                users = line[15:-1]
                messages[users] = []
            elif ':|:' in line:
                line_list = line.strip().split(':|:')
                name = line_list[0]
                date = line_list[1]
                time = line_list[2]
                hours = int(time.split(':')[0])
                minutes = time.split(':')[1]
                if hours > 12:
                    hours -= 12
                    end_str = 'pm'
                else:
                    end_str = 'am'
                t_str = str(hours) + ':' + minutes + end_str
                day = int(date.split('-')[2])
                month = reversed_months[int(date.split('-')[1])]
                year = int(date.split('-')[0])
                d_str = month.capitalize() + ' ' + str(day) + ' ' + str(year)
                message = line_list[3]
                messages[users].append(Message(name, d_str + ' at ' + t_str, message))

print('Ready to search.')
while True:
    print('1: Regex search')
    print('2: Date search')
    print('3: On this day')
    print('4: Cache and index files for faster loading time')
    choice = int(input())
    if choice == 1:
        print('\\Q to quit.')
        print('[username]:|:[regex] to limit search results to a user')
        while True:
            query = input('regex:: ')
            name = False
            if query == '\\Q':
                break
            elif ':|:' in query:
                name, query = query.split(':|:')
            i = 0
            user_list = {}
            for user in messages:
                first_time = True
                for message in messages[user]:
                    if re.search(query, message.message):
                        if name:
                            # print(message.sender, name)
                            if message.sender == name:
                                if first_time:
                                    print()
                                    print('Thread:', user + ':')
                                    first_time = False
                                if message.first_name in user_list:
                                    user_list[message.first_name] += 1
                                else:
                                    user_list[message.first_name] = 1
                                i += 1
                                safe_print(message)
                        else:
                            if first_time:
                                print()
                                print('Thread:', user + ':')
                                first_time = False
                            if message.first_name in user_list:
                                user_list[message.first_name] += 1
                            else:
                                user_list[message.first_name] = 1
                            i += 1
                            safe_print(message)
            print()
            print('Found %s message%s' % (i, plural(i)))
            for user in user_list:
                print('%s: %s' % (user, user_list[user]))
            print()
    if choice == 2:
        while True:
            d = input('Day: ')
            m = input('Month: ')
            y = input('Year: ')
            if not d:
                d = datetime.datetime.now().day
            if not m:
                m = datetime.datetime.now().month
            if not y:
                y = datetime.datetime.now().year
            date = datetime.date(int(y), int(m), int(d))
            print('Results for %s:' % date)
            for user in messages:
                first_time = True
                for message in messages[user]:
                    if message.date == date:
                        if first_time:
                            print()
                            print('Thread:', user + ':')
                            first_time = False
                        safe_print(message)
            print()
    if choice == 3:
        date = datetime.datetime.now()
        for user in messages:
            first_time = True
            for message in messages[user]:
                if (message.date.day, message.date.month) == (date.day, date.month):
                    if first_time:
                        print()
                        print('Thread:', user + ':')
                        first_time = False
                    safe_print(message)
        print()
    if choice == 4:
        if not os.path.exists('cache.db'):
            file = open('cache.db', 'x')
        else:
            file = open('cache.db', 'w')
        for user in messages:
            first_time = True
            file.write('[[NEW|THREAD]] ' + user + ':\n')
            for message in messages[user]:
                temp = '%s:|:%s-%s-%s:|:%s:|:%s' % (
                    message.sender,
                    message.date.year,
                    message.date.month,
                    message.date.day,
                    message.time,
                    message.message)
                file.write(temp + '\n')
        file.close()

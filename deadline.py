import datetime as dt


def deadline_list():
    inf = []
    with open('data/ica.ics', 'r', encoding='utf-8') as f:
        for row in f:
            if 'SUMMARY' in row:
                inf.append(row[8:-1])
            if 'DTEND' in row:
                year = int(row[6:10])
                month = int(row[10:12])
                day = int(row[12:14])
                hour = int(row[15:17]) + 3
                minute = int(row[17:19])
                dead = dt.datetime(year, month, day, hour, minute)
                inf.append(dead)


    ans = 'Список дедлайнов\n'
    for i in range(0, len(inf), 2):
        time = f" {inf[i + 1].day}.{inf[i + 1].month} {inf[i + 1].hour}:{inf[i + 1].minute}"
        ans += inf[i] + time + '\n'

    return ans


if __name__ == '__main__':
    print(deadline_list())

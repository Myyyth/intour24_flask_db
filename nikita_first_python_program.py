def convert(time):
    if type(time) == str:
        temp = time.split(' ')
        size = len(temp)
        time_in_minutes = 0

        if temp[1][0] == 'h':
            time_in_minutes += (int(temp[0])) * 60
        else:
            time_in_minutes += int(temp[0])

        if size == 4:
            time_in_minutes += int(temp[2])

        return time_in_minutes
    return -1

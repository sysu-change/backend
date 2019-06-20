

def sex_trans(sex):
    if sex == 0:
        return u'男'
    if sex == 1:
        return u'女'
    return u'未知'


def grade_trans(grade):
    if grade == 1:
        return u'大一'
    if grade == 2:
        return u'大二'
    if grade == 3:
        return u'大三'
    if grade == 4:
        return u'大四'
    if grade == 5:
        return u'研一'
    if grade == 6:
        return u'研二'
    if grade == 7:
        return u'研三'
    return u'未知'


def grade_trans_to_int(grade):
    if grade == u'大一':
        return 1
    if grade == u'大二':
        return 2
    if grade == u'大三':
        return 3
    if grade == u'大四':
        return 4
    if grade == u'研一':
        return 5
    if grade == u'研二':
        return 6
    if grade == u'研三':
        return 7
    return 0

from difflib import Differ

wikidatetime = '{{subst:LOCALTIME}} , {{subst:LOCALDAY}}. {{subst:LOCALMONTHABBREV}} {{subst:LOCALYEAR}}'

# User Choice functions

YES, NO, QUIT, SKIP = range(0,4)
user_options = {YES: ('Yes', 'y'),
                NO: ('No', 'n'),
                SKIP: ('Skip', 's'),
                QUIT: ('Quit', 'q'),
                }

user_responses = {}
for uo, uis in user_options.items():
    user_responses[uis[1]] = uo

def uo_display():
    string = ''
    for uo, uis in user_options.items():
        string += u'%s(%s)/' % uis
    return string[:-1]

def delta(old_text, new_text, surrounding_lines=0):
    result = list(Differ().compare(old_text.split(u'\n'), new_text.split(u'\n')))
    delta = ''
    lines_history = []
    lines_past_changed = surrounding_lines
    for line in result:
        lines_past_changed += 1
        if line[0] != ' ':
            for line_h in lines_history:
                delta += line_h + '\n'
            lines_history = []
            delta += line + '\n'
            lines_past_changed = 0
        elif lines_past_changed <= surrounding_lines:
            delta += line + '\n'
        elif surrounding_lines:
            lines_history.append(line)
            if len(lines_history) > surrounding_lines:
                lines_history = lines_history[-surrounding_lines:]
    return delta

def user_choice(delta):
    print delta
    while True:
        answer = raw_input(u"Do you want to apply this change to Wiktionary?\n(%s):" % uo_display())
        if answer in user_responses:
            return user_responses[answer]
        else:
            print u"Invalid response."



def key_release_event(event):

    return (event.type not in {'MIDDLEMOUSE', 'INBETWEEN_MOUSEMOVE', 'MOUSEMOVE', 'TIMER', 'TIMER_REPORT', 'WHEELDOWNMOUSE', 'WHEELUPMOUSE'} and event.value == 'PRESS')

def mouse_move_or_wheel_event(event):
    
    return event.type in {'MIDDLEMOUSE', 'INBETWEEN_MOUSEMOVE', 'MOUSEMOVE', 'TIMER', 'TIMER_REPORT', 'WHEELDOWNMOUSE', 'WHEELUPMOUSE'}

def esc_press_event(event):

    return (event.type in {'ESC'} and event.value == 'PRESS')



class EscPressFinishConditionMixin:

    def operation_done_finish_condition(self, event):

        return esc_press_event(event)

    def operation_done_hint(self):

        return 'press ESC to close the summary'


class DefaultFinishConditionMixin:

    def operation_done_finish_condition(self, event):

        return key_release_event(event)

    def operation_done_hint(self):

        return 'press any key to close the summary'

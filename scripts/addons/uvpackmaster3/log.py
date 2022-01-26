# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####


from .enums import UvpmLogType


class LogList:

    def __init__(self, max_log_count=0):

        self.max_log_count = max_log_count
        self.log_list = []

    def log(self, log_str):

        self.log_list.append(log_str)

        if self.max_log_count > 0 and len(self.log_list) > self.max_log_count:
            del self.log_list[0]

    def __iter__(self):
        return self.log_list.__iter__()

    def __len__(self):
        return len(self.log_list)

    def __getitem__(self, key):
        return self.log_list[key]



class LogManager:

    def __init__(self, post_log_op=None):
        # self.info_list = []
        # self.warning_list = []
        # self.error_list = []
        # self.status_history = []

        self.post_log_op = post_log_op

        self.log_lists = {
            UvpmLogType.STATUS :     LogList(max_log_count=0),
            UvpmLogType.INFO :       LogList(max_log_count=5),
            UvpmLogType.WARNING :    LogList(max_log_count=0),
            UvpmLogType.ERROR :      LogList(max_log_count=0),
            UvpmLogType.HINT :       LogList(max_log_count=0)
        }

    def log_list(self, log_type):

        log_list = self.log_lists.get(log_type, None)
        if log_list is None:
            raise RuntimeError('Unexpected log type')

        return log_list

    def log(self, log_type, log_str):

        self.log_list(log_type).log(log_str)

        if self.post_log_op is not None:
            post_log_op = self.post_log_op
            post_log_op(log_type, log_str)
        

    # def info_logged(self):
    #     return len(self.info_list) > 0

    # def warning_logged(self):
    #     return len(self.warning_list) > 0

    # def error_logged(self):
    #     return len(self.error_list) > 0

    def type_logged(self, log_type):

        return len(self.log_list(log_type)) > 0

    def last_log(self, log_type):
        log_list = self.log_list(log_type)
        return log_list[-1] if len(log_list) > 0 else None


class GetSetProperty():

    def __init__(self, get, set):
        self.fget = get
        self.fset = set
        del get, set  # don't use builtin python keywords
        self.prop = property(self.get_prop, self.set_prop)

    def get_prop(self, parent_cls):
        fget = self.fget
        if fget:
            return fget(parent_cls)

    def set_prop(self, parent_cls, value):
        fget, fset = self.fget, self.fset
        if fget and not fset:
            raise AttributeError("This property is read only")

        if fset:
            fset(self, parent_cls, value)

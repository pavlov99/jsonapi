class Choices(object):

    """ Choices."""

    def __init__(self, *choices):
        self._choices = []
        self._choice_dict = {}

        for choice in choices:
            if isinstance(choice, (list, tuple)):
                if len(choice) == 2:
                    choice = (choice[0], choice[1], choice[1])

                elif len(choice) != 3:
                    raise ValueError(
                        "Choices can't handle a list/tuple of length {0}, only\
                        2 or 3".format(choice))
            else:
                choice = (choice, choice, choice)

            self._choices.append((choice[0], choice[2]))
            self._choice_dict[choice[1]] = choice[0]

    def __getattr__(self, attname):
        try:
            return self._choice_dict[attname]
        except KeyError:
            raise AttributeError(attname)

    def __iter__(self):
        return iter(self._choices)

    def __getitem__(self, index):
        return self._choices[index]

    def __delitem__(self, index):
        del self._choices[index]

    def __setitem__(self, index, value):
        self._choices[index] = value

    def __repr__(self):
        return "{0}({1})".format(
            self.__class__.__name__,
            self._choices
        )

    def __len__(self):
        return len(self._choices)

    def __contains__(self, element):
        return element in self._choice_dict.values()
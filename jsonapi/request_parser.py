""" Parser for request parameters."""
import re
from collections import OrderedDict, namedtuple


JSONAPIQueryDict = namedtuple('JSONAPIQueryDict', [
    'distinct',
    'fields',
    'filter',
    'include',
    'page',
    'sort',
])


class RequestParser(object):

    """ Rarser for Django request.GET parameters."""

    RE_FIELDS = re.compile('^fields\[(?P<resource>\w+)\]$')

    @classmethod
    def parse(cls, querydict):
        """ Parse querydict data.

        There are expected agruments:
            distinct, fields, filter, include, page, sort

        Parameters
        ----------
        querydict : django.http.request.QueryDict
            MultiValueDict with query arguments.

        Returns
        -------
        result : dict
            dictionary in format {key: value}.

        Raises
        ------
        ValueError
            If args consist of not know key.

        """
        for key in querydict.keys():
            if not any((key in JSONAPIQueryDict._fields,
                        cls.RE_FIELDS.match(key))):

                msg = "Query parameter {} is not known".format(key)
                raise ValueError(msg)

        result = JSONAPIQueryDict(
            distinct=cls.prepare_values(querydict.getlist('distinct')),
            fields=cls.parse_fields(querydict),
            filter=querydict.getlist('filter'),
            include=cls.prepare_values(querydict.getlist('include')),
            page=int(querydict.get('page')) if querydict.get('page') else None,
            sort=cls.prepare_values(querydict.getlist('sort'))
        )

        return result

    @classmethod
    def prepare_values(cls, values):
        return [x for value in values for x in value.split(",")]

    @classmethod
    def parse_fields(cls, querydict):
        fields = cls.prepare_values(querydict.getlist('fields'))
        fields_typed = []

        for key in querydict.keys():
            fields_match = cls.RE_FIELDS.match(key)

            if fields_match is not None:
                resource_name = fields_match.group("resource")
                fields_typed.extend([
                    (resource_name, value)
                    for value in cls.prepare_values(querydict.getlist(key))
                ])

        if fields and fields_typed:
            raise ValueError("Either default or typed fields should be used")

        return fields or fields_typed

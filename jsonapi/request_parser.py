""" Parser for request parameters."""
import re
from collections import OrderedDict

from .django_utils import get_querydict


class RequestParser(object):

    """ Rarser for GET parameters.



    """

    RE_SORT = re.compile('^sort\[(?P<resource>\w+)\]$')
    RE_FIELDS = re.compile('^fields\[(?P<resource>\w+)\]$')

    @classmethod
    def parse(cls, query):
        """ Parse querydict data.

        Define, what parameters are general and what are resource specific,
        structure parameters. As far as common parameters for resources are
        defined, all of the query parametres which dont match them are
        resource specific. So parser is resource independend.

        :param str query: dictionary in format
            {param: [value]}. To get querydict in Django use
            querydict = dict(django.http.QueryDict('a=1&a=2').iterlists())
        :return dict result: dictionary in format {key: value}.
            key = [sort|include|page|filter]
            sort (None or list or dict)
                * If case of 'sort' key passed, value is a list of
                fields to sort.

                * In case of typed sort, such as sort[<resource>] passed, value
                is a dict with key <resource> and value list as in 'sort' key
                case

        """
        querydict = get_querydict(query)
        sort_params, querydict = cls.parse_sort(querydict)
        include_params, querydict = cls.parse_include(querydict)
        page, querydict = cls.parse_page(querydict)
        fields_params, querydict = cls.parse_fields(querydict)
        filters = {k: v[0] for k, v in querydict.items()}

        result = {
            "sort": sort_params,
            "include": include_params,
            "page": page,
            "fields": fields_params,
            "filters": filters,
        }

        return result

    @classmethod
    def prepare_values(cls, values):
        return [x for value in values for x in value.split(",")]

    @classmethod
    def parse_sort(cls, querydict):
        """ Return filtered querydict.

        Check for keys in format 'sort' or 'sort[<resource>]'

        """
        filtered_querydict_items = []
        sort_params_items = []
        sort_params = []

        for key, values in querydict.items():
            sort_match = cls.RE_SORT.match(key)

            if key == "sort":
                sort_params = cls.prepare_values(values)
            elif sort_match is not None:
                resource_name = sort_match.group("resource")
                sort_params_items.extend([
                    (resource_name, value)
                    for value in cls.prepare_values(values)
                ])
            else:
                filtered_querydict_items.append((key, values))

        filtered_querydict = OrderedDict(filtered_querydict_items)

        if sort_params_items and sort_params:
            raise ValueError("Either default or typed sort should be used")

        sort_params = sort_params_items or sort_params
        return sort_params, filtered_querydict

    @classmethod
    def parse_include(cls, querydict):
        """ Parse include resources."""
        include_params = []
        filtered_querydict_items = []
        for key, values in querydict.items():
            if key == "include":
                include_params = cls.prepare_values(values)
            else:
                filtered_querydict_items.append((key, values))

        filtered_querydict = OrderedDict(filtered_querydict_items)
        return include_params, filtered_querydict

    @classmethod
    def parse_page(cls, querydict):
        """ Parse page."""
        page = None
        filtered_querydict_items = []
        for key, values in querydict.items():
            if key == "page":
                page = int(cls.prepare_values(values)[0])
            else:
                filtered_querydict_items.append((key, values))

        filtered_querydict = OrderedDict(filtered_querydict_items)
        return page, filtered_querydict

    @classmethod
    def parse_fields(cls, querydict):
        filtered_querydict_items = []
        fields_params_items = []
        fields_params = []

        for key, values in querydict.items():
            fields_match = cls.RE_FIELDS.match(key)

            if key == "fields":
                fields_params = cls.prepare_values(values)
            elif fields_match is not None:
                resource_name = fields_match.group("resource")
                fields_params_items.extend([
                    (resource_name, value)
                    for value in cls.prepare_values(values)
                ])
            else:
                filtered_querydict_items.append((key, values))

        filtered_querydict = OrderedDict(filtered_querydict_items)

        if fields_params_items and fields_params:
            raise ValueError("Either default or typed fields should be used")

        fields_params = fields_params_items or fields_params
        return fields_params, filtered_querydict

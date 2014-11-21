""" Parser for request parameters."""
import re


class RequestParser(object):

    """ Rarser for GET parameters.



    """

    RE_SORT = re.compile('^sort\[(?P<resource>\w+)\]$')

    @classmethod
    def parse(cls, querydict):
        """ Parse querydict data.

        Define, what parameters are general and what are resource specific,
        structure parameters. As far as common parameters for resources are
        defined, all of the query parametres which dont match them are
        resource specific. So parser is resource independend.

        :param dict querydict: dictionary in format
            {param: [value]}. To get querydict in Django use
            querydict = dict(django.http.QueryDict('a=1&a=2').iterlists())
        :return dict result: dictionary in format {key: value}.
            key = [sort|include|page|filter]
            sort (list or dict)
                * If case of 'sort' key passed, value is a list of
                fields to sort.

                * In case of typed sort, such as sort[<resource>] passed, value
                is a dict with key <resource> and value list as in 'sort' key
                case

        """

        sort_params, querydict = cls.parse_sort(querydict)

        result = {
            "sort": sort_params or None,
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
        filtered_querydict = {}
        sort_params = {}

        for key, values in querydict.items():
            sort_match = cls.RE_SORT.match(key)

            if key == "sort":
                sort_params = cls.prepare_values(values)
            elif sort_match is not None:
                resource_name = sort_match.group("resource")
                sort_params[resource_name] = cls.prepare_values(values)
            else:
                filtered_querydict[key] = values

        return sort_params, filtered_querydict

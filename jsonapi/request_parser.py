""" Parser for request parameters."""


class RequestParser(object):

    """ Rarser for GET parameters.



    """
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
        result = {}
        return result

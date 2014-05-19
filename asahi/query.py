

class QueryOperation(object):
    normal_operation_mask = 0x3F
    unequal = 0x000
    equal = 0x001
    less = 0x002
    less_equal = 0x003
    greater = 0x004
    greater_equal = 0x005
    # empty 0x10U
    # empty 0x20U
    like = 0x030 # only for string

    intersection = 0x040
    union = 0x000
    all = 0x080
    order_asc = 0x100
    order_desc = 0x200


class QueryCell(object):
    def __init__(self, operation, member=None, value=None, sub_queries=None):
        self.member = member
        self.operation = operation
        self.value = value
        self.sub_queries = sub_queries


class Query(object):
    """
    An asahi query object.
    """
    def __init__(self, document):
        self.document = document
        self.items = [
            QueryCell(QueryOperation.all)
        ]

    def intersect(self, *args, **kwargs):
        """
        Intersect the query.
        :param args:
            The member's name of the document or
                the sub queries' lambda function.
        :param kwargs: [
            unequal,
            equal,
            less,
            less_equal,
            greater,
            greater_equal,
            like,
        ]
        """
        if isinstance(args[0], basestring):
            # .and('member', equal='')
            member = args[0]
            operation_code, value = self.__parse_operation(**kwargs)
            self.items.append(QueryCell(
                QueryOperation.intersection | operation_code,
                member=member,
                value=value,
            ))
        else:
            # .and(lambda x: x.where())
            func = args[0]
            queries = func(self.document).items
            self.items.append(QueryCell(
                QueryOperation.intersection,
                sub_queries=queries
            ))
        return self

    def union(self, *args, **kwargs):
        """
        Union the query.
        :param args:
            The member's name of the document or
                the sub queries' lambda function.
        :param kwargs: [
            unequal,
            equal,
            less,
            less_equal,
            greater,
            greater_equal,
            like,
        ]
        """
        if isinstance(args[0], basestring):
            # .or('member', equal='')
            member = args[0]
            operation_code, value = self.__parse_operation(**kwargs)
            self.items.append(QueryCell(
                QueryOperation.union | operation_code,
                member=member,
                value=value,
            ))
        else:
            # .or(lambda x: x.where())
            func = args[0]
            queries = func(self.document).items
            self.items.append(QueryCell(
                QueryOperation.union,
                sub_queries=queries
            ))
        return self

    def fetch(self):
        import logging
        for item in self.items:
            result = item.__dict__
            if item.sub_queries is not None:
                result['sub_queries'] = [x.__dict__ for x in item.sub_queries]
            logging.error(result)

    def __parse_operation(self, **kwargs):
        """
        Parse the operation and value of the query **kwargs.
        :returns: {QueryOperation}, {object}
            QueryOperation: The query operation code.
            object: The query operation value.
        """
        keys = kwargs.keys()
        if 'equal' in keys:
            return QueryOperation.equal, kwargs['equal']
        elif 'unequal' in keys:
            return QueryOperation.unequal, kwargs['unequal']
        elif 'less' in keys:
            return QueryOperation.less, kwargs['less']
        elif 'less_equal' in keys:
            return QueryOperation.less_equal, kwargs['less_equal']
        elif 'greater' in keys:
            return QueryOperation.greater, kwargs['greater']
        elif 'greater_equal' in keys:
            return QueryOperation.greater_equal, kwargs['greater_equal']
        elif 'like' in keys:
            return QueryOperation.like, kwargs['like']
        return None, None
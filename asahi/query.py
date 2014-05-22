import utils


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


    # -----------------------------------------------------
    # The methods for appending the query.
    # -----------------------------------------------------
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
        :return: {asahi.query.Query}
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
        :return: {asahi.query.Query}
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

    def order_by(self, member, descending=False):
        """
        Append the order query.
        :param member: {string} The property name of the document.
        :param descending: {bool} Is sorted by descending.
        :return: {asahi.query.Query}
        """
        if descending:
            operation_code = QueryOperation.order_desc
        else:
            operation_code = QueryOperation.order_asc
        self.items.append(QueryCell(
            operation_code,
            member=member
        ))
        return self


    # -----------------------------------------------------
    # The methods for fetch documents by the query.
    # -----------------------------------------------------
    def fetch(self, limit=1000, skip=0):
        """
        Fetch documents by the query.
        :param limit: {int} The size of the pagination. (The limit of the result items.)
        :param skip: {int} The offset of the pagination. (Skip x items.)
        :return: {list} The documents.
        """
        es = utils.get_elasticsearch()
        search_result = es.search(
            self.document.get_db().dbname,
            body=self.__generate_elasticsearch_search_body(self.items, limit, skip),
        )
        result = []
        for hits in search_result['hits']['hits']:
            result.append(self.document.wrap(hits['_source']))
        return result

    def count(self):
        """
        Count documents by the query.
        :return: {int}
        """
        query, sort = self.__compile_queries(self.items)
        es = utils.get_elasticsearch()
        if query is None:
            count_result = es.count(self.document.get_db().dbname)
        else:
            count_result = es.count(
                self.document.get_db().dbname,
                body={
                    'query': query
                },
            )
        return count_result['count']


    # -----------------------------------------------------
    # Private methods.
    # -----------------------------------------------------
    def __generate_elasticsearch_search_body(self, queries, limit=None, skip=None):
        es_query, sort_items = self.__compile_queries(queries)
        result = {
            'from': skip,
            'size': limit,
            'fields': ['_source'],
            'sort': sort_items,
        }
        if es_query is not None:
            result['query'] = es_query
        return result

    def __compile_queries(self, queries):
        """
        Compile asahi query cells to the elastic search query.
        :param queries: {list} The asahi query cells.
        :return: {dict or None}, {list}
            The elastic search query dict.
            The elastic search sort list.
        """
        should_items = []
        sort_items = []
        for query in queries:
            if query.sub_queries:
                # compile sub queries
                pass
            else:
                if query.operation & QueryOperation.intersection is QueryOperation.intersection:
                    # intersect
                    should_items.append(self.__compile_query_operation(query))
                elif query.operation & QueryOperation.order_asc is QueryOperation.order_asc:
                    sort_items.append({
                        query.member: {'order': 'asc', 'mode': 'avg'}
                    })
                elif query.operation & QueryOperation.order_desc is QueryOperation.order_desc:
                    sort_items.append({
                        query.member: {'order': 'desc', 'mode': 'avg'}
                    })

        if len(should_items):
            query = {
                'bool': {
                    'should': should_items
                }
            }
        else:
            query = None
        return query, sort_items
    def __compile_query_operation(self, query):
        """
        Parse the asahi query operation to elasticsearch query.
        :param query: The asahi query.
        :return: {dict} The elasticsearch query.
        """
        operation = query.operation & QueryOperation.normal_operation_mask
        if operation & QueryOperation.equal is QueryOperation.equal:
            return {
                'match': {
                    query.member: query.value
                }
            }

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

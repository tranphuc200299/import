import logging
from copy import deepcopy
from django.db import connection

_logger = logging.getLogger(__name__)


class SqlExecute:
    def __init__(self, raw_query):
        self.raw_query = raw_query
        self.columns = None
        self.Rows = []

    def execute(self):
        with connection.cursor() as cursor:
            _logger.debug(self.raw_query)
            cursor.execute(self.raw_query)

    def all(self):
        with connection.cursor() as cursor:
            _logger.debug(self.raw_query)
            cursor.execute(self.raw_query)
            self.columns = self._get_columns(cursor)
            self.Rows = [dict(zip(self.columns, row)) for row in cursor.fetchall()]
            return self

    def NewRow(self):
        return dict(zip(self.columns, [None] * len(self.columns)))

    def Clone(self):
        return deepcopy(self)

    def Add(self, new_row):
        return [new_row] + self.Rows

    def order_by(self, column=None):
        if column:
            sort_type = "ASC"
            if column.startswith("-"):
                column = column[1:]
                sort_type = "DESC"
            self.raw_query += f" ORDER BY {column} {sort_type}"
        return self

    @staticmethod
    def _get_columns(cursor):
        return [col[0].lower() for col in cursor.description]

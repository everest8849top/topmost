class WhereQuery:
    def __init__(self):
        self.list = []

    def __str__(self):
        string = " WHERE "
        for i in range(len(self.list)):
            if i != 0:
                string += " AND "
            string += self.list[i]
        return string

    def add(self, compare_type, column, value):
        if compare_type == "ILIKE":
            self.list.append(f""" {column} ILIKE '{value.replace("'", "").lower()}' """)
        if compare_type == "BETWEEN":
            self.list.append(
                f"""({column} IS NULL OR {column} = '' OR COALESCE(NULLIF(CAST(NULLIF({column}, '') AS DOUBLE PRECISION)::BIGINT, 0), 0) BETWEEN {value[0]} AND {value[1]})"""
            )

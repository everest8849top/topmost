from Utils import (
    input_functions,
    first_field_label_descriptions,
    first_table_query_assist,
)
from WhereQuery import WhereQuery
from SqlConnector import SqlConnector


import os

from Utils import vehicle_description

import re

url_pattern = r"https?://\S+"


class VehicleDescriptor:
    def __init__(self):
        pass

    @staticmethod
    def arr_to_html(arr):
        html = "<ul style = '\
                background-color: #FFF8EE;\
                color: white;\
                margin: 10px;\
                text-align: left;\
                '>"
        for item in arr:
            output_text = re.sub(
                url_pattern,
                lambda x: f'<a href="{x.group(0)}">{x.group(0)}</a>',
                item["value"],
            )
            html += f"""<li style = 'color: #111;'><strong style = 'color: #002200'>{item['title']}</strong> {output_text}</li>"""
        html += "</ul>"

        return html

    def arr_to_plain(arr):
        plain = ""
        for item in arr:
            plain += f"{item['title']}{item['value']}"
        return plain

    @staticmethod
    def description(row, is_html=True):
        content = []
        for item in vehicle_description:
            title = item.get("title", "")
            params = item.get("params", [])
            initial = item.get("initial", None)
            space = item.get("space", "")
            kind = item.get("type", "array")

            changed = False
            sub_content = ""
            for param in params:
                param_arg = param
                if kind == "tail_array":
                    param_arg = param["arg"]
                val = row.get(param_arg, None)
                if val is not None and val != 0 and val != "0" and val != "":
                    if changed:
                        sub_content += space + " "
                    if kind == "tail_array":
                        sub_content = sub_content + val + " " + param["tail"]
                    else:
                        sub_content = sub_content + val
                else:
                    continue
                changed = True
            if sub_content == "" and initial is not None:
                sub_content = initial
            if sub_content == "":
                continue
            content.append({"title": title, "value": sub_content})
        if is_html:
            return VehicleDescriptor.arr_to_html(content)
        else:
            return VehicleDescriptor.arr_to_plain(content)


class FirstTable:
    def __init__(self):
        pass

    @staticmethod
    def row_html_data(row):
        return VehicleDescriptor.description(row)

    def row_plain_data(row):
        return VehicleDescriptor.description(row, False)

    @staticmethod
    def result(args):
        params = {}

        # ----------------------------------------------------------------
        for item in first_table_query_assist["default"]:
            params[item[0]] = args.get(item[0], item[1])
        if not isinstance(params["limit_count"], int):
            params["limit_count"] = int(params["limit_count"])
        if params["limit_count"] > 10:
            params["limit_count"] = 10
        elif params["limit_count"] < 1:
            params["limit_count"] = 1

        # ----------------------------------------------------------------
        table_name = "first_table"
        header_query = f"SELECT * FROM {table_name}"
        footer_query = ""
        where_list = WhereQuery()

        # ----------------------------------------------------------------
        for item in first_table_query_assist["same"]:
            if params[item[0]] is not None:
                where_list.add(item[1], item[0], params[item[0]])
        # ----------------------------------------------------------------
        for item in first_table_query_assist["between"]:
            where_list.add(item[2], item[1], (params[item[0][0]], params[item[0][1]]))

        # For the price
        if params["price_description"] == "not mentioned":
            pass
        elif params["price_description"] == "range":
            where_list.add(
                "BETWEEN",
                "listing_price",
                (params["listing_min_price"], params["listing_max_price"]),
            )
        elif params["price_description"] == "the most expensive":
            footer_query = f" ORDER BY listing_price DESC"
        elif params["price_description"] == f"the cheapest":
            footer_query = f" ORDER BY listing_price ASC"

        # ----------------------------------------------------------------
        footer_query = footer_query + f" LIMIT {params['limit_count']};"

        # ----------------------------------------------------------------
        result_query = header_query + str(where_list) + footer_query
        print(result_query)

        # ----------------------------------------------------------------
        sql_connector = SqlConnector()
        row_list = sql_connector.get_list_query_not_batch(result_query)

        return row_list

    # @staticmethod
    # def

    # @staticmethod
    # def row_data(row):
    #     formatted_data = ""

    #     for field_name, label in first_field_label_descriptions.items():
    #         if field_name in row:
    #             if row[field_name] is not None:
    #                 # print(f"{label}: {row[field_name]}")
    #                 formatted_data += f"'''{label}''' : <<<'{row[field_name]}'>>> \n"

    #     formatted_data += "\n\n"
    #     return formatted_data

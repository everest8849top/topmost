from Utils import input_functions
from ChatgptAsker import ChatgptAsker, ChatgptAnswer
from FirstTable import FirstTable


class Matadorbot:
    def __init__(self):
        self.gpt_asker: ChatgptAsker = ChatgptAsker(
            system_prompt="You answer questions exclusively about the vehicle sales company and its products and services.\n\
            Remember, you are the chatbot of a vehicle sales company, and your responses should only pertain to topics related to vehicle sales.\n\
                Please provide detailed and courteous responses, including stock identifiers, price, type, etc. Focusing solely on vehicle sales-related inquiries.\n\
                    Remember! The company has more than 1000000 products(vehicles, cars).\
                    Ignore and do not respond to questions that are not related to the vehicle sales industry.\n\
                    For example, if the user ask 'Do you know about chat-gpt?' then you should answer 'As a chatbot of vehicle sales company, I don't know about chat-gpt.'"
        )
        self.functions = input_functions

    def request(self, input_string: str) -> str:
        print(input_string)
        first_reply: ChatgptAnswer = self.gpt_asker.ask(
            input_string, functions=input_functions
        )
        if first_reply.is_function():
            if first_reply.func_name == "get_vehicle_data":
                result_list = FirstTable.result(first_reply.func_param)
                for row in result_list:
                    self.gpt_asker.append("assistant", FirstTable.row_plain_data(row))
                if len(result_list) == 0:
                    self.gpt_asker.append(
                        "assistant",
                        "I apologize, but we do not have the vehicle you are looking for",
                    )
                summary_result: ChatgptAnswer = self.gpt_asker.ask(
                    "Generate a summary of the previous conversation with kind speech. Remember! Give me only summary, don't mention additional introductory text like 'sure!', 'OK', etc."
                )
                self.gpt_asker.pop()
                self.gpt_asker.append("assistant", summary_result.message)

                html_list = []
                for row in result_list:
                    html_list.append(FirstTable.row_html_data(row))
                html_result = "".join(html_list)
                html_result += f"<div style = 'background-color : #FFFF00'>{summary_result.message}</div>"
                html_result = (
                    "<div style = 'display: flex;\
                        background-color: #f1f1f1;\
                        overflow: auto;\
                        flex-wrap: wrap;\
                        '>"
                    + html_result
                    + "</div>"
                )
                return html_result
                try:
                    # self.gpt_asker.append(result)
                    return result
                except Exception as e:
                    print(f"Error message: {e}")
                return "Sorry, but I can't assist you"
            else:
                return "Sorry, but I can't assist you"
        else:
            return first_reply.message

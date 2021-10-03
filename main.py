# -*- codecs: utf-8 -*-
import codecs
import re
import time
from datetime import datetime
import requests


pause_between_ask = 0.5
search_deep = 1
start_time = time.time()
sellers_we_already_have = []
requests_list = []


def clean_up_results_list():
    with open('results.txt', 'w') as results_file:
        results_file.write('')


def get_requests_from_file():
    try:
        with codecs.open('requests.txt', 'r', "utf-8") as file_with_requests:
            for line in file_with_requests:
                if line.endswith('\r\n'):
                    print(line)
                    requests_list.append(line[:-2])
                else:
                    requests_list.append(line)
    except:
        print("ERR00R: can't find requests.txt file")


clean_up_results_list()
get_requests_from_file()
today_date = str(datetime.utcfromtimestamp(time.time()).strftime('%d.%m'))
print(f'Hello, i will try to find some items published today {today_date}')

for requests_items in requests_list:
    links_getted = []
    try:
        with open('results.txt', 'a') as file_to_save_results:
            file_to_save_results.write(f'{requests_items}:\n\n')
        links_getted = []
        for page_of_searching in range(1, search_deep + 1):
            print(f'Status: waiting for {pause_between_ask} seconds')
            time.sleep(pause_between_ask)
            result_of_parsing = requests.get(f'https://izi.ua/search/page{page_of_searching}?search_text={requests_items}&sort=-updated_at')
            print(f'Status: checking item: {requests_items} on page {page_of_searching}')
            read_result = result_of_parsing.content
            string_result = read_result.decode("utf8")
            result = [_.start() for _ in re.finditer('https://izi.ua/p-', string_result)]
            for results in result:
                ready_link = ''
                should_add = True
                for sym in string_result[results:]:
                    if sym == '"':
                        break
                    else:
                        ready_link += sym
                        if len(ready_link) > 100:
                            should_add = False
                            break
                if should_add:
                    if not ready_link in links_getted:
                        links_getted.append(ready_link)

        print(f'Done searching links for {requests_items}, results {len(links_getted)} : {links_getted}')
    except:
        print(f"ERR00R: can't parse for {requests_items}")
    if len(links_getted) > 1:
        for links in links_getted:
            print(f'Status: waiting for {pause_between_ask} seconds')
            time.sleep(pause_between_ask)
            print(f"Status: checking link: {links} it's {links_getted.index(links)} of {len(links_getted)} for {requests_items}")
            result_of_parsing = requests.get(links)
            read_result = result_of_parsing.content
            string_result = read_result.decode("utf8")

            user_have_no_starts = False
            single_sell = string_result.find('отзыв')
            multiply_sells = string_result.find('отзыва')
            multiply_sells_2 = string_result.find('отзывов')
            if single_sell == -1 and single_sell == -1 and single_sell == -1:
                user_have_no_starts = True

            if user_have_no_starts:

                start_of_user_id = string_result.find('/m-')

                ready_user_id = ''
                should_add = True
                for sym in string_result[start_of_user_id:]:
                    if sym == '"':
                        break
                    else:
                        ready_user_id += sym
                        if len(ready_user_id) > 100:
                            should_add = False
                            break
                if should_add:
                    start_of_data = string_result.find('Опубликовано<!-- --> <!-- -->')
                    if str(string_result[start_of_data + 29:start_of_data + 29 + 5]) == today_date:
                        if not ready_user_id in sellers_we_already_have:
                            sellers_we_already_have.append(ready_user_id)
                            with open('results.txt', 'a') as file_to_save_results:
                                file_to_save_results.write(f"{links}\n")
                            print('Status: this one is good')
                        else:
                            print(f'Status: we already have seller with id {ready_user_id}, so i will skip this')
                    else:
                        print(f'Status: this is too old the date is {str(string_result[start_of_data + 29:start_of_data + 29 + 5])}')
            else:
                print('Status: this user already have sales so i will skip it')
    with open('results.txt', 'a') as file_to_save_results:
        file_to_save_results.write(f"\n\n")

with open('results.txt', 'a') as file_to_save_results:
    file_to_save_results.write(f"Сумарное время выполнения {round((time.time() - start_time) / 60, 2)} минут")
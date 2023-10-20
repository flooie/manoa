# import tempfile
#
# import pytesseract
# from pathlib import Path
# from pdf2image import convert_from_path
#
# from x import process_pdf_page, process_pdf_from_date
#
# root = Path(__file__).parent
#
# def get_data(page):
#     column1 = (0, 305) # arr -date
#
#     left, right = column1
#     top, bottom = 0, page.height * .95
#     bbox = (left, top, right, bottom) # (left, upper, right, lower)
#
#     tops = [0]
#     data = pytesseract.image_to_data(page.crop(bbox),
#                                      output_type=pytesseract.Output.DICT)
#     for i in range(len(data['text'])):
#         text = data['text'][i]
#         if "2023" in text:
#             tops.append(data['top'][i])
#     tops.append(bottom)
#     tuples_list = [(tops[i], tops[i + 1]) for i in
#                    range(len(tops) - 1)]
#     return tuples_list
#
# def get_data_ii(page):
#     # column1 = (0, 305) # arr -date
#     column4 = (930, 1240) # report-offense#
#
#
#     left, right = column4
#     top, bottom = 0, page.height * .95
#     bbox = (left, top, right, bottom) # (left, upper, right, lower)
#
#     tops = [0]
#     data = pytesseract.image_to_data(page.crop(bbox),
#                                      output_type=pytesseract.Output.DICT)
#     for i in range(len(data['text'])):
#         text = data['text'][i]
#         #  dict_keys(['level', 'page_num', 'block_num', 'par_num', 'line_num', 'word_num', 'left', 'top', 'width', 'height', 'conf', 'text'])
#         print(text, data['text'][i], data['top'][i], data['line_num'][i])
#         if "2023" in text:
#             tops.append(data['top'][i])
#     tops.append(bottom)
#     tuples_list = [(tops[i], tops[i + 1]) for i in
#                    range(len(tops) - 1)]
#
#
#     return tuples_list
#
# def get_data_iii(page):
#     left, right = (0, page.width)
#     top, bottom = 0, page.height * .95
#     bbox = (left, top, right, bottom) # (left, upper, right, lower)
#
#     tops = [0]
#     data = pytesseract.image_to_data(page.crop(bbox),
#                                      output_type=pytesseract.Output.DICT)
#
#     top_now = 0
#     for i in range(len(data['text'])):
#         text = data['text'][i]
#         # print(data.keys())
#         line_num = data['line_num'][i]
#         top = data['top'][i]
#         # if top == top_now:
#         if abs(int(top) - int(top_now)) <= 5:
#             # print(text, line_num, i, top)
#             print(text, end=" ")
#         else:
#             print(text)
#         top_now = top
#
# def write_image(page, tuples_list, page_number):
#     count = 0
#     column1 = (0, 305) # arr -date
#     column2 = (305, 565) # race
#     column3 = (565, 1240) # name
#     column4 = (930, 1240) # report-offense#
#     column5 = (1240, 1750) # offense
#     column6 = (1750, 2640) # loc of arrest
#     column7 = (2640, page.width) # End row
#     config = fr'-l eng -c preserve_interword_spaces=1 --oem 3 --psm 6'
#
#     for tuple in tuples_list:
#         column_count = 0
#         # print(f"NEW PERSON \n ==========={page_number}")
#         for column in [column3, column2, column1, column4, column5, column6, column7]:
#             column_count += 1
#             left, right = column
#             top, bottom = tuple[0], tuple[1]
#             bbox = (left, top, right, bottom)
#             # here is where I can adjust the OCR
#             # config = fr'-l eng -c preserve_interword_spaces=1x1 --oem 3 --psm 6 -c tessedit_char_whitelist=0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ\s!\"#$%&\\\'()*+,-./:;<=>?@[\\]^_\` '
#             # config = r'-c preserve_interword_spaces=1x1 --oem 3 --psm 6 -c tessedit_char_whitelist=0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!\"#$%&\'()*+,-./:;<=>?@[\\]^_\`{|}~ '
#             config = "-c tessedit_char_whitelist=01234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ\s!#$%&\()*+,-./:;<=>?@[\\]^_\./:\\ preserve_interword_spaces=1x1 --psm 11 --oem 3"
#             text = pytesseract.image_to_string(page.crop(bbox), config=config)
#             if column == column1: # date and time
#                 rows = [x for x in text.splitlines() if x and x[0].isdigit()]
#                 try:
#                     date, time = rows
#                     print(f"date: {date}")
#                     print(f"time: {time}")
#                 except:
#                     pass
#                     # print("---")
#             if column == column2:
#                 if "Race" in text:
#                     continue
#                 # print(text)
#
#                 race = text.splitlines()[0]
#                 # print(text.splitlines())
#                 sex, age = text.splitlines()[-1].split("/")
#                 print(f"race: {race}")
#                 print(f"sex: {sex}")
#                 print(f"age: {age}")
#             if column == column3:
#
#                 import re
#                 # print(text)
#                 m = re.match(r"(^[A-Z -]+,.*)", text)
#                 if not m:
#                     print("\n")
#
#                     config = "-c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ,-./:;\./:\\ preserve_interword_spaces=1x1 --psm 6 --oem 3"
#                     text = pytesseract.image_to_string(page.crop(bbox),
#                                                        config=config)
#                     m = re.match(r"(^[A-Zs -]+,.*)", text)
#                     if not m:
#                         print("NAME: NOT FOUND")
#
#
#
#                 if m:
#                     # print("NEW PERSON\n========")
#                     name = m.group()
#                     print("\n")
#                     print(f"Name: {name}")
#             if column == column4:
#                 # print(text)
#                 n = re.findall(r"\d+-\d+", text)
#                 if n:
#                     numbers = n
#                     print(f"Numbers: {numbers}")
#             if column == column5:
#                 cd = []
#                 for row in text.splitlines():
#                     # print(row)
#                     if "HONOLULU" in row:
#                         continue
#                     mm = re.match(r"^[A-Z][A-Z0-9 -/]{3,}", row)
#                     uu = re.match(r"^HRS .*", row)
#                     if uu:
#                         cd.append(row)
#                     elif mm:
#                         cd.append(row)
#                 if cd:
#                     print("Offenses:", cd)
#
#
#             if column == column6:
#                 address = []
#
#                 for i in text.splitlines():
#                     m = re.match(r"[0-9A-Z '.,/:-]{2,}", i)
#                     if m:
#                         address.append(i)
#                 if address and "EPARTMENT" not in address:
#                     pass
#                     print(f"Address/Officer/Judge/Court - Repeat: {address}")
#             if column == column7:
#                 c7 = []
#                 for i in text.splitlines():
#                     m = re.match(r"^\d{2}/.*", i)
#                     n = re.match(r'^([A-Z]{3})\s?/\s?(\d+)', i)
#                     q = re.match(r"(^\d+)", i)
#                     if m:
#                         release_date = i
#                         c7.append(release_date)
#                     elif n:
#                         release_code, bail_amount = n.groups()
#                         c7.append(release_code)
#                         c7.append(bail_amount)
#                     elif q:
#                         c7.append(q.group())
#                 if c7:
#                     print(f"Bail: {c7}")
#                 # print(text)
#
#
#
#             count+=1
#             # break
#
# def tesseract():
#     """Convert PDF to image and extract text
#
#     Preserve some whitespace for parsing reasons
#     """
#     fn = "2023-10-13-11-00-05-Log.pdf"
#     # fn = "2023-10-10-05-00-20-Log.pdf"
#     # fn = "2023-10-12-05-00-13-Log.pdf"
#     # fn = "2023-10-10-05-00-20-Log.pdf"
#     # fn = "2023-10-08-17-00-34-Log.pdf"
#     # fn = "2023-10-09-05-00-36-Log.pdf"
#     # fn = "2023-10-08-23-00-59-Log.pdf"
#     filepath = Path.joinpath(root, "..", "docs", "logs", fn)
#
#     pages = convert_from_path(filepath, 300)  # Adjust the DPI (resolution) as needed
#     column1 = (0, 305) # arr -date
#     for i, page in enumerate(pages):
#         tuples_list = get_data(page)
#         write_image(page, tuples_list, page_number=i)
#
# def part_two():
#     fn = "2023-10-13-11-00-05-Log.pdf"
#     fn = "2023-10-12-05-00-13-Log.pdf"
#
#     filepath = Path.joinpath(root, "..", "docs", "logs", fn)
#
#     pages = convert_from_path(filepath, 300)  # Adjust the DPI (resolution) as needed
#     for i, page in enumerate(pages):
#         tuples_list = get_data_iii(page)
#         # write_image(page, tuples_list, page_number=i)
#
#

from django.shortcuts import render
# from datetime import datetime
# from datetime import timedelta
# from openpyxl import Workbook
# from django.http import HttpResponse

# from .models import AMResponse

# # Create your views here.
# def export_amresponse_to_xlsx(request):
#     """
#     Downloads all responses as Excel file with a single worksheet
#     """
#     response_queryset = AMResponse.objects.all()

#     response = HttpResponse(
#         content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
#     )
#     response['Content-Disposition'] = 'attachment; filename={date}-amresponses.xlsx'.format(date=datetime.now().strftime('%Y-%m-%d'),)
#     workbook = Workbook()

#     # Get active worksheet/tab
#     worksheet = workbook.active
#     worksheet.title = 'About Me Responses'

#     # Define the titles for columns
#     columns = [
#         'ID',
#         'Survey',
#         'User',
#         'AmQuestion',
#         'IntegerValue',
#         'TopicValue',
#         'CommentValue',
#         'SkipValue',
#         'TopicTags',
#         'CommentTags',
#     ]
#     row_num = 1

#     # Assign the titles for each cell of the header
#     for col_num, column_title in enumerate(columns, 1):
#         cell = worksheet.cell(row=row_num, column=col_num)
#         cell.value = column_title

#     # Iterate through all response
#     for item in response_queryset:
#         row_num += 1

#         # Define the data for each cell in the row
#         row = [
#             item.pk,
#             item.Survey,
#             item.User,
#             item.AmQuestion,
#             item.IntgerValue,
#             item.TopicValue,
#             item.CommentValue,
#             item.SkipValue,
#             item.TopicTags,
#             item.CommentTags,
#         ]

#         # Assign the data for each cell of the row
#         for col_num, cell_value in enumerate(row, 1):
#             cell = worksheet.cell(row=row_num, column=col_num)
#             cell.value = cell_value

#     workbook.save(response)

#     return response
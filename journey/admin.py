from django.contrib import admin
from .models import Journey
from django.http import HttpResponse, JsonResponse
import json
from collections import OrderedDict
from .fusioncharts import FusionCharts
from django.shortcuts import render

class JourneyAdmin(admin.ModelAdmin):

    def changelist_view(self, request, extra_context=None):
        dataSource = OrderedDict()
        dataSource = []
        dataSource.append({"id": "2", "x": "90", "y": "480", "name": "1A. Invitation Email", "color": "#FFEEDD", "link": "http://3.15.16.117:3030/email/template2.html", "width": "80", "height": "30", "shape": "RECTANGLE", "tooltext": ""})
        dataSource.append({"id": "3", "x": "190", "y": "480", "name": "Invited Landing Page", "color": "#FFEEDD", "link": "http://3.15.16.117:3031/set-password", "width": "80", "height": "30", "shape": "RECTANGLE", "tooltext": ""})
        dataSource.append({"id": "4", "x": "290", "y": "480", "name": "2A. Confirm Details(Account Created)", "color": "#FFEEDD", "link": "http://3.15.16.117:3031/welcome", "width": "80", "height": "40", "shape": "RECTANGLE", "tooltext": ""})
        dataSource.append({"id": "5", "x": "340", "y": "550", "name": "3A. Login Page", "link": "http://3.15.16.117:3031/login", "width": "80", "height": "30", "shape": "RECTANGLE", "tooltext": ""})
        dataSource.append({"id": "6", "x": "390", "y": "480", "name": "4. Welcome", "link": "http://3.15.16.117:3031/welcome", "width": "80", "height": "30", "shape": "RECTANGLE", "tooltext": ""})
        dataSource.append({"id": "7", "x": "490", "y": "480", "name": "5. About Me Survey", "link": "http://3.15.16.117:3031/app/about-me/start", "width": "80", "height": "30", "shape": "RECTANGLE", "tooltext": ""})
        dataSource.append({"id": "8", "x": "590", "y": "480", "name": "6. My Map", "link": "http://3.15.16.117:3031/app/my-map", "width": "80", "height": "30", "shape": "RECTANGLE", "tooltext": ""})
        dataSource.append({"id": "9", "x": "690", "y": "480", "name": "7. Project Map", "link": "", "width": "80", "height": "30", "shape": "RECTANGLE", "tooltext": ""})
        dataSource.append({"id": "10", "x": "790", "y": "480", "name": "8. Dashboard", "color": "#6B6B6B", "link": "http://3.15.16.117:3031/app/me", "width": "80", "height": "30", "shape": "RECTANGLE", "tooltext": ""})
        dataSource.append({"id": "11", "x": "90", "y": "410", "name": "1B. Organic Search", "link": "", "width": "80", "height": "30", "shape": "RECTANGLE", "tooltext": ""})
        dataSource.append({"id": "12", "x": "210", "y": "410", "name": "2B. Landing Page(Try it)/Capture Details/Sales", "link": "http://3.15.16.117:3030", "width": "100", "height": "50", "shape": "RECTANGLE", "tooltext": ""})
        dataSource.append({"id": "13", "x": "300", "y": "410", "name": "New User", "link": "", "radius": "25", "shape": "POLYGON", "numSides":"4", "tooltext": ""})
        dataSource.append({"id": "14", "x": "390", "y": "410", "name": "4A. PM Video", "link": "", "width": "80", "height": "30", "shape": "RECTANGLE", "tooltext": ""})
        dataSource.append({"id": "15", "x": "490", "y": "410", "name": "5A. Survey Navigation", "link": "http://3.15.16.117:3031/app/about-me/start", "width": "80", "height": "30", "shape": "RECTANGLE", "tooltext": ""})
        dataSource.append({"id": "16", "x": "590", "y": "410", "name": "6A. KeyLines 'MyMap'", "color": "#FF4747", "link": "http://3.15.16.117:3031/app/my-map", "width": "80", "height": "30", "shape": "RECTANGLE", "tooltext": ""})
        dataSource.append({"id": "17", "x": "690", "y": "410", "name": "7A. KeyLines 'ProjectMap'", "color": "#FF4747", "link": "", "width": "80", "height": "30", "shape": "RECTANGLE", "tooltext": ""})
        dataSource.append({"id": "18", "x": "790", "y": "410", "name": "8A. DB1", "color": "#6B6B6B", "link": "", "width": "80", "height": "30", "shape": "RECTANGLE", "tooltext": ""})
        dataSource.append({"id": "19", "x": "90", "y": "340", "name": "1C. Link from Website", "link": "", "width": "80", "height": "30", "shape": "RECTANGLE", "tooltext": ""})
        dataSource.append({"id": "20", "x": "390", "y": "340", "name": "4B. About Pulse", "link": "", "width": "80", "height": "30", "shape": "RECTANGLE", "tooltext": ""})
        dataSource.append({"id": "21", "x": "490", "y": "340", "name": "5B. About Me Question Components", "link": "http://3.15.16.117:3031/app/about-me/start", "width": "80", "height": "30", "shape": "RECTANGLE", "tooltext": ""})
        dataSource.append({"id": "22", "x": "590", "y": "340", "name": "6X. Tree Style 'MyMap'", "link": "http://3.15.16.117:3031/app/my-map", "width": "80", "height": "30", "shape": "RECTANGLE", "tooltext": ""})
        dataSource.append({"id": "23", "x": "690", "y": "340", "name": "7X. Tree Style 'ProjectMap'", "link": "", "width": "80", "height": "30", "shape": "RECTANGLE", "tooltext": ""})
        dataSource.append({"id": "24", "x": "210", "y": "270", "name": "2B. We will be in touch(MVP)", "link": "", "width": "100", "height": "50", "shape": "RECTANGLE", "tooltext": ""})
        dataSource.append({"id": "25", "x": "400", "y": "260", "name": "3. App Navigation", "link": "", "width": "80", "height": "30", "shape": "RECTANGLE", "tooltext": ""})
        dataSource.append({"id": "26", "x": "400", "y": "190", "name": "3A. Login Page", "link": "http://3.15.16.117:3031/login", "width": "80", "height": "30", "shape": "RECTANGLE", "tooltext": ""})
        dataSource.append({"id": "27", "x": "400", "y": "120", "name": "3B. Site Navigation", "link": "", "width": "80", "height": "30", "shape": "RECTANGLE", "tooltext": ""})
        dataSource.append({"id": "28", "x": "640", "y": "270", "name": "6B. Search Stakeholder", "color": "#F393FF", "link": "", "width": "160", "height": "30", "shape": "RECTANGLE", "tooltext": ""})
        dataSource.append({"id": "29", "x": "640", "y": "200", "name": "6C. Add New Stakeholder", "color": "#F393FF", "link": "", "width": "160", "height": "30", "shape": "RECTANGLE", "tooltext": ""})
        dataSource.append({"id": "30", "x": "640", "y": "130", "name": "6D. About Others Q-Components", "link": "", "width": "160", "height": "30", "shape": "RECTANGLE", "tooltext": ""})

        dataSetSource = OrderedDict()
        dataSetSource["dataset"] = []
        dataSetSource["dataset"].append({"id": "1", "seriesname": "UJ", "data": dataSource})

        connectorSource = OrderedDict()
        connectorSource = []
        connectorSource.append({"from": "2", "to": "3", "color": "#1aaf5d", "strength": "1", "arrowatstart": "0", "alpha": "100"})
        connectorSource.append({"from": "3", "to": "4", "color": "#1aaf5d", "strength": "1", "arrowatstart": "0", "alpha": "100"})
        connectorSource.append({"from": "4", "to": "6", "color": "#1aaf5d", "strength": "1", "arrowatstart": "0", "alpha": "100"})
        connectorSource.append({"from": "11", "to": "12", "color": "#1aaf5d", "strength": "1", "arrowatstart": "0", "alpha": "100"})
        connectorSource.append({"from": "12", "to": "24", "color": "#1aaf5d", "strength": "1", "arrowatstart": "0", "alpha": "100"})
        connectorSource.append({"from": "24", "to": "13", "color": "#1aaf5d", "strength": "1", "arrowatstart": "0", "alpha": "100"})
        connectorSource.append({"from": "13", "to": "25", "color": "#1aaf5d", "strength": "1", "arrowatstart": "0", "arrowatend": "0", "alpha": "100"})
        connectorSource.append({"from": "25", "to": "20", "color": "#1aaf5d", "strength": "1", "arrowatstart": "0", "arrowatend": "0", "alpha": "100"})
        connectorSource.append({"from": "19", "to": "12", "color": "#1aaf5d", "strength": "1", "arrowatstart": "0", "arrowatend": "0", "alpha": "100"})

        dataSetSource["connectors"] = []
        dataSetSource["connectors"].append({"stdthickness": "2", "connector": connectorSource})

        groupSource = OrderedDict()
        groupSource = []

        annotation = OrderedDict()
        annotation["origw"] = "600"
        annotation["origh"] = "400"
        annotation["autoscale"] = "0"
        # annotation["groups"] = groupSource

        dataSetSource["annotations"] = annotation

        chartConfig = OrderedDict()
        chartConfig["caption"] = "User Journey"
        chartConfig["subCaption"] = "Developing now"
        chartConfig["arrowatstart"] = "0"
        chartConfig["arrowatend"] = "1"
        chartConfig["viewMode"] = "1"
        chartConfig["connectorToolText"] = "$label Weeks"
        chartConfig["theme"] = "candy"
        chartConfig["chartLeftMargin"] = "30"
        chartConfig["chartRightMargin"] = "30"
        chartConfig["chartTopMargin"] = "30"
        chartConfig["chartBottomMargin"] = "30"
        chartConfig["canvasLeftMargin"] = "30"
        chartConfig["canvasRightMargin"] = "30"
        chartConfig["canvasTopMargin"] = "30"
        chartConfig["canvasBottomMargin"] = "30"
        chartConfig["xAxisMaxValue"] = "900"
        chartConfig["xAxisMinValue"] = "0"
        chartConfig["yAxisMaxValue"] = "600"
        chartConfig["yAxisMinValue"] = "0"
        chartConfig["animation"] = "1"
        chartConfig["baseFontColor"] = "#000000"
        chartConfig["labelFontColor"] = "#FFFFFF"
        
        dataSetSource["chart"] = chartConfig

        # # mockup data
        # dataSource = OrderedDict()
        # dataSource = []
        # dataSource.append({"id": "2", "x": "15", "y": "30", "name": "Login", "link":"http://3.15.16.117:3031/login", "width": "160", "height": "60", "shape": "RECTANGLE", "tooltext": "A. Login"})
        # dataSource.append({"id": "3", "x": "15", "y": "60", "name": "Set Password", "link":"http://3.15.16.117:3031/set-password", "width": "160", "height": "60", "shape": "RECTANGLE", "tooltext": "B. Set Password"})
        # dataSource.append({"id": "4", "x": "15", "y": "90", "name": "Welcome", "link":"http://3.15.16.117:3031/welcome", "width": "160", "height": "60", "shape": "RECTANGLE", "tooltext": "C. Welcome"})
        # dataSource.append({"id": "5", "x": "45", "y": "45", "name": "User Profile", "link":"http://3.15.16.117:3031/app/me", "width": "160", "height": "60", "shape": "RECTANGLE", "tooltext": "D. User Profile"})
        # dataSource.append({"id": "6", "x": "45", "y": "75", "name": "AboutMe Survey", "link":"http://3.15.16.117:3031/app/about-me/start", "width": "160", "height": "60", "shape": "RECTANGLE", "tooltext": "E. AboutMe Surveey"})
        # dataSource.append({"id": "7", "x": "75", "y": "45", "name": "Setting",  "link":"http://3.15.16.117:3031/app/settings", "width": "160", "height": "60", "shape": "RECTANGLE", "tooltext": "F. Setting"})
        # dataSource.append({"id": "8", "x": "75", "y": "75", "name": "My Map",  "link":"http://3.15.16.117:3031/app/my-map", "width": "160", "height": "60", "shape": "RECTANGLE", "tooltext": "G. My Map"})

        # dataSetSource = OrderedDict()
        # dataSetSource["dataset"] = []
        # dataSetSource["dataset"].append({"id": "1", "seriesname": "DS1", "data": dataSource})

        # connectorSource = OrderedDict()
        # connectorSource = []
        # # connectorSource.append({"from": "2", "to": "3", "color": "#1aaf5d", "strength": "1", "arrowatstart": "0", "alpha": "100", "label": "4"})
        # # connectorSource.append({"from": "3", "to": "4", "color": "#1aaf5d", "strength": "1", "arrowatstart": "0", "alpha": "100", "label": "10"})

        # # dataSetSource["connectors"] = []
        # # dataSetSource["connectors"].append({"stdthickness": "2", "connector": connectorSource})

        # groupSource = OrderedDict()
        # groupSource = []
        # groupSource.append({
        #     "color": "#0075c2", 
        #     "fontSize": "12", 
        #     "y": "$chartEndY - $chartBottomMargin - 54", 
        #     "items": [
        #         {
        #             "id": "anno-A",
        #             "type": "text",
        #             "label": "A. Login",
        #             "align": "Left",
        #             "verticalAlign": "top",
        #             "bold": "1",
        #             "x": "$chartStartX + $chartLeftMargin + 24"
        #         },
        #         {
        #             "id": "anno-B",
        #             "type": "text",
        #             "label": "B. Set Password",
        #             "align": "Left",
        #             "verticalAlign": "top",
        #             "bold": "1",
        #             "x": "$chartStartX + $chartLeftMargin + 124"
        #         },
        #         {
        #             "id": "anno-C",
        #             "type": "text",
        #             "label": "C. Welcome",
        #             "align": "Left",
        #             "verticalAlign": "top",
        #             "bold": "1",
        #             "x": "$chartStartX + $chartLeftMargin + 224"
        #         },
        #         {
        #             "id": "anno-D",
        #             "type": "text",
        #             "label": "D. Set Password",
        #             "align": "Left",
        #             "verticalAlign": "top",
        #             "bold": "1",
        #             "x": "$chartStartX + $chartLeftMargin + 324"
        #         }
        #     ]})
        # groupSource.append({
        #     "color": "#0075c2", 
        #     "fontSize": "12", 
        #     "y": "$chartEndY - $chartBottomMargin - 34", 
        #     "items": [
        #         {
        #             "id": "anno-E",
        #             "type": "text",
        #             "label": "E. AboutMe Surveey",
        #             "align": "Left",
        #             "verticalAlign": "top",
        #             "bold": "1",
        #             "x": "$chartStartX + $chartLeftMargin + 24"
        #         },
        #         {
        #             "id": "anno-F",
        #             "type": "text",
        #             "label": "F. Setting",
        #             "align": "Left",
        #             "verticalAlign": "top",
        #             "bold": "1",
        #             "x": "$chartStartX + $chartLeftMargin + 124"
        #         },
        #         {
        #             "id": "anno-G",
        #             "type": "text",
        #             "label": "G. My Map",
        #             "align": "Left",
        #             "verticalAlign": "top",
        #             "bold": "1",
        #             "x": "$chartStartX + $chartLeftMargin + 224"
        #         }
        #     ]})

        # annotation = OrderedDict()
        # annotation["origw"] = "600"
        # annotation["origh"] = "400"
        # annotation["autoscale"] = "1"
        # annotation["groups"] = groupSource

        # dataSetSource["annotations"] = annotation

        # chartConfig = OrderedDict()
        # chartConfig["caption"] = "User Journey"
        # chartConfig["subCaption"] = "Developing now"
        # chartConfig["arrowatstart"] = "0"
        # chartConfig["arrowatend"] = "1"
        # chartConfig["viewMode"] = "1"
        # chartConfig["connectorToolText"] = "$label Weeks"
        # chartConfig["theme"] = "fusion"
        # chartConfig["chartLeftMargin"] = "30"
        # chartConfig["chartRightMargin"] = "30"

        # dataSetSource["chart"] = chartConfig

        dragnode = FusionCharts("dragnode", "myFirstChart", "900", "600", "myFirstchart-container", "json", dataSetSource)

        extra_context = {
            'output': dragnode.render()
        }

        response = super(JourneyAdmin, self).changelist_view(request, extra_context)

        response.context_data.update(extra_context)

        return response

    change_list_template = 'admin/journey/index.html'

admin.site.register(Journey, JourneyAdmin)
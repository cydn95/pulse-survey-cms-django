from django.contrib import admin
from .models import Journey
from django.http import HttpResponse, JsonResponse
import json
from collections import OrderedDict
from .fusioncharts import FusionCharts
from django.shortcuts import render

class JourneyAdmin(admin.ModelAdmin):

    def changelist_view(self, request, extra_context=None):
        # mockup data
        dataSource = OrderedDict()
        dataSource = []
        dataSource.append({"id": "2", "x": "15", "y": "30", "name": "Login", "link":"http://3.15.16.117:3031/login", "width": "160", "height": "60", "shape": "RECTANGLE", "tooltext": "A. Login"})
        dataSource.append({"id": "3", "x": "15", "y": "60", "name": "Set Password", "link":"http://3.15.16.117:3031/set-password", "width": "160", "height": "60", "shape": "RECTANGLE", "tooltext": "B. Set Password"})
        dataSource.append({"id": "4", "x": "15", "y": "90", "name": "Welcome", "link":"http://3.15.16.117:3031/welcome", "width": "160", "height": "60", "shape": "RECTANGLE", "tooltext": "C. Welcome"})
        dataSource.append({"id": "5", "x": "45", "y": "45", "name": "User Profile", "link":"http://3.15.16.117:3031/app/me", "width": "160", "height": "60", "shape": "RECTANGLE", "tooltext": "D. User Profile"})
        dataSource.append({"id": "6", "x": "45", "y": "75", "name": "AboutMe Survey", "link":"http://3.15.16.117:3031/app/about-me/start", "width": "160", "height": "60", "shape": "RECTANGLE", "tooltext": "E. AboutMe Surveey"})
        dataSource.append({"id": "7", "x": "75", "y": "45", "name": "Setting",  "link":"http://3.15.16.117:3031/app/settings", "width": "160", "height": "60", "shape": "RECTANGLE", "tooltext": "F. Setting"})
        dataSource.append({"id": "8", "x": "75", "y": "75", "name": "My Map",  "link":"http://3.15.16.117:3031/app/my-map", "width": "160", "height": "60", "shape": "RECTANGLE", "tooltext": "G. My Map"})

        dataSetSource = OrderedDict()
        dataSetSource["dataset"] = []
        dataSetSource["dataset"].append({"id": "1", "seriesname": "DS1", "data": dataSource})

        connectorSource = OrderedDict()
        connectorSource = []
        # connectorSource.append({"from": "2", "to": "3", "color": "#1aaf5d", "strength": "1", "arrowatstart": "0", "alpha": "100", "label": "4"})
        # connectorSource.append({"from": "3", "to": "4", "color": "#1aaf5d", "strength": "1", "arrowatstart": "0", "alpha": "100", "label": "10"})

        # dataSetSource["connectors"] = []
        # dataSetSource["connectors"].append({"stdthickness": "2", "connector": connectorSource})

        groupSource = OrderedDict()
        groupSource = []
        groupSource.append({
            "color": "#0075c2", 
            "fontSize": "12", 
            "y": "$chartEndY - $chartBottomMargin - 54", 
            "items": [
                {
                    "id": "anno-A",
                    "type": "text",
                    "label": "A. Login",
                    "align": "Left",
                    "verticalAlign": "top",
                    "bold": "1",
                    "x": "$chartStartX + $chartLeftMargin + 24"
                },
                {
                    "id": "anno-B",
                    "type": "text",
                    "label": "B. Set Password",
                    "align": "Left",
                    "verticalAlign": "top",
                    "bold": "1",
                    "x": "$chartStartX + $chartLeftMargin + 124"
                },
                {
                    "id": "anno-C",
                    "type": "text",
                    "label": "C. Welcome",
                    "align": "Left",
                    "verticalAlign": "top",
                    "bold": "1",
                    "x": "$chartStartX + $chartLeftMargin + 224"
                },
                {
                    "id": "anno-D",
                    "type": "text",
                    "label": "D. Set Password",
                    "align": "Left",
                    "verticalAlign": "top",
                    "bold": "1",
                    "x": "$chartStartX + $chartLeftMargin + 324"
                }
            ]})
        groupSource.append({
            "color": "#0075c2", 
            "fontSize": "12", 
            "y": "$chartEndY - $chartBottomMargin - 34", 
            "items": [
                {
                    "id": "anno-E",
                    "type": "text",
                    "label": "E. AboutMe Surveey",
                    "align": "Left",
                    "verticalAlign": "top",
                    "bold": "1",
                    "x": "$chartStartX + $chartLeftMargin + 24"
                },
                {
                    "id": "anno-F",
                    "type": "text",
                    "label": "F. Setting",
                    "align": "Left",
                    "verticalAlign": "top",
                    "bold": "1",
                    "x": "$chartStartX + $chartLeftMargin + 124"
                },
                {
                    "id": "anno-G",
                    "type": "text",
                    "label": "G. My Map",
                    "align": "Left",
                    "verticalAlign": "top",
                    "bold": "1",
                    "x": "$chartStartX + $chartLeftMargin + 224"
                }
            ]})

        annotation = OrderedDict()
        annotation["origw"] = "600"
        annotation["origh"] = "400"
        annotation["autoscale"] = "1"
        annotation["groups"] = groupSource

        dataSetSource["annotations"] = annotation

        chartConfig = OrderedDict()
        chartConfig["caption"] = "User Journey"
        chartConfig["subCaption"] = "Developing now"
        chartConfig["arrowatstart"] = "0"
        chartConfig["arrowatend"] = "1"
        chartConfig["viewMode"] = "1"
        chartConfig["connectorToolText"] = "$label Weeks"
        chartConfig["theme"] = "fusion"

        dataSetSource["chart"] = chartConfig

        dragnode = FusionCharts("dragnode", "myFirstChart", "900", "600", "myFirstchart-container", "json", dataSetSource)

        extra_context = {
            'output': dragnode.render()
        }

        response = super(JourneyAdmin, self).changelist_view(request, extra_context)

        response.context_data.update(extra_context)

        return response

    change_list_template = 'admin/journey/index.html'

admin.site.register(Journey, JourneyAdmin)
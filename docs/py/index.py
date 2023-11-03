from js import document, Object, window 
from pyscript import HTML, display
from jinja2 import Environment, FileSystemLoader
from src import pydom
import js
from pyscript import when
from src.utils import fetch_documents, fetch_coordinates, fetch_token, get_data, get_person, get_people, get_officers, get_crimes
from src.models import search_partial_matches, connect_to_database



class Callout:
    """"""    
    def calloutAnchorOffsetForAnnotation(self, annotation, element):
        offset = window.DOMPoint.new()        
        offset.x = -148
        offset.y = -78
        return offset   

    def calloutElementForAnnotation(self, annotation):
        "Iterate over annotation charge object which is the dict of the entire thing."
        # May want to grab more stuff

        charge_object = get_data(annotation.charge_object)

        id = charge_object['person']['id']
        person = get_person(id)[0]
        charges = person.charges
        # name = get_person(id)[0].name

        div = js.document.createElement("div")
        div.className = f"landmark"
        title = js.document.createElement("h1")
        title.innerText = person.name
        
        div.append(title)
        section = js.document.createElement("section")
        div.append(section)
        p2 = js.document.createElement("p")
        p2.className = "statute"
        p2.innerText = annotation.location
        section.append(p2)

        for charge in charges:

            p2 = js.document.createElement("p")
            p2.className = "statute"
            p2.innerText = charge.charge
            section.append(p2)
            p2 = js.document.createElement("p")
            p2.className = "statute"
            p2.innerText = charge.crime
            section.append(p2)

        p3 = js.document.createElement("p")
        p3.innerText = charge_object['statute']
        p3.className = "homepage"
        section.append(p3)
        return div


def add_bootstrap_css():
    stylesheet = document.createElement("link")
    stylesheet.setAttribute('crossorigin', 'anonymous')
    stylesheet.setAttribute('href', 'https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css')
    stylesheet.setAttribute('integrity', 'sha384-T3c6CoIi6uLrA9TneNEoa7RxnatzjcDSCmG1MXxSR1GAsXEV/Dwwykc2MPK8M2HN')
    stylesheet.setAttribute('rel', 'stylesheet')
    document.getElementsByTagName("body")[0].append(stylesheet)


def add_css_dynamically():
    stylesheet = pydom.create("link")
    stylesheet._element.rel = "stylesheet"
    stylesheet._element.href = "/docs/css/override.css"
    pydom['head'][0].append(stylesheet)

def add_maps_dynamically():
    token = "eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IjJTQVU2Mk5WNk4ifQ.eyJpc3MiOiJMRUNWUlBNUVRLIiwiaWF0IjoxNjk3NjM1Mzc5LCJleHAiOjE3MDY3NDU2MDB9.KEtY85kvYNGFmUPD2o-81YUWuY_t2TbNxVwN8332N2VhIcKvAhi7a0k---XUeVelIaVTuB7Jyl1358KAbUm39w"
    maps = document.createElement("script")
    maps.setAttribute('crossorigin', '')
    maps.setAttribute('async', '')
    maps.setAttribute('data-callback', 'initMapKit')
    maps.setAttribute('data-libraries', 'map,annotations')
    maps.setAttribute('data-initial-token', token)
    maps.setAttribute('src', 'https://cdn.apple-mapkit.com/mk/5.x.x/mapkit.core.js')
    document.getElementsByTagName("body")[0].append(maps)

def add_apple_maps():
    maps = document.createElement("script")
    maps.setAttribute('src', 'js/apple-map.js')
    document.getElementsByTagName("body")[0].append(maps)

def add_main_div():
    new_div = pydom.create("div")
    new_div.id = "main"
    pydom['body'][0].append(new_div)

def load_template():
    logs = fetch_documents()

    file_loader = FileSystemLoader('.')
    env = Environment(loader=file_loader)
    officers = get_officers()
    people = get_people()
    crimes = get_crimes(None)

    template = env.get_template('templates/l.html')
    output = template.render(logs=logs, people=people, officers=officers, crimes=crimes)
    display(HTML(output), target='main', append=False)

def reload_arrests_table(officers):
    file_loader = FileSystemLoader('.')
    env = Environment(loader=file_loader)
    template = env.get_template('templates/components/arrests.html')
    js.document.getElementById("results").innerHTML = ""
    output = template.render(arrests=officers)
    display(HTML(output), target='results', append=False)


def add_annotations(crimes):

    if len(window.mapkit.maps) > 0:
        window.mapkit.maps[0].removeAnnotations(
            window.mapkit.maps[0].annotations)

        x = []
        y = []
        for crime in crimes:
            if float(crime.arrest.latitude) == float(0):
                continue
            x.append(float(crime.arrest.latitude))
            y.append(float(crime.arrest.longitude))

            # Make coordinates
            coordinate = window.mapkit.Coordinate.new()
            coordinate.latitude = float(crime.arrest.latitude)
            coordinate.longitude = float(crime.arrest.longitude)

            annotation = window.mapkit.MarkerAnnotation.new(coordinate)
            annotation.callout = Callout()
            annotation.charge_object = crime.arrest.id
            annotation.id = crime.arrest.id
            annotation.location = crime.arrest.location
            annotation.obj = crime.arrest

            annotation.color = "red"
            annotation.glyphText = "🚔️"

            map = window.mapkit.maps[0]
            map.showItems(annotation)

        oahu = window.mapkit.CoordinateRegion.new()
        oahu.center.latitude = sum(x) / len(x) + (max(x) - min(x)) / 2
        oahu.center.longitude = sum(y) / len(y)
        oahu.span.latitudeDelta = (max(x) - min(x)) * 2
        oahu.span.longitudeDelta = (max(y) - min(y)) * 2
        # window.mapkit.maps[0].setRegionAnimated = True
        window.mapkit.maps[0].region = oahu


def add_annotations_officers(officers):

    if len(window.mapkit.maps) > 0:
        window.mapkit.maps[0].removeAnnotations(
            window.mapkit.maps[0].annotations)

        x = []
        y = []
        for officer in officers:
            for charge in officer.charges:
    
                if float(charge.arrest.latitude) == float(0):
                    continue
                x.append(float(charge.arrest.latitude))
                y.append(float(charge.arrest.longitude))
    
                # Make coordinates
                coordinate = window.mapkit.Coordinate.new()
                coordinate.latitude = float(charge.arrest.latitude)
                coordinate.longitude = float(charge.arrest.longitude)
    
                annotation = window.mapkit.MarkerAnnotation.new(coordinate)
                annotation.callout = Callout()
                annotation.charge_object = charge.arrest.id
                annotation.id = charge.arrest.id
                annotation.location = charge.arrest.location
                annotation.obj = charge.arrest
    
                annotation.color = "red"
                annotation.glyphText = "🚔️"
    
                map = window.mapkit.maps[0]
                map.showItems(annotation)
    
            oahu = window.mapkit.CoordinateRegion.new()
            oahu.center.latitude = sum(x) / len(x) + (max(x) - min(x)) / 2
            oahu.center.longitude = sum(y) / len(y)
            if (max(x) - min(x)) == 0:
                oahu.span.latitudeDelta = 0.2
                oahu.span.longitudeDelta = 0.2

            else:
                oahu.span.latitudeDelta = (max(x) - min(x)) * 2
                oahu.span.longitudeDelta = (max(y) - min(y)) * 2
            # window.mapkit.maps[0].setRegionAnimated = True
            window.mapkit.maps[0].region = oahu

def append_locations(locations):
    if len(window.mapkit.maps) > 0:
        window.mapkit.maps[0].removeAnnotations(
            window.mapkit.maps[0].annotations)

        x = []
        y = []
        for loc in locations:
            x.append(float(loc.latitude))
            y.append(float(loc.longitude))

            # Make coordinates
            coordinate = window.mapkit.Coordinate.new()
            coordinate.latitude = float(loc.latitude)
            coordinate.longitude = float(loc.longitude)

            annotation = window.mapkit.MarkerAnnotation.new(coordinate)
            annotation.callout = Callout()
            annotation.charge_object = loc.id
            annotation.id = loc.id
            annotation.location = loc.location
            annotation.obj = loc

            annotation.color = "red"
            annotation.display = "show"
            annotation.glyphText = f"🚔️"

            map = window.mapkit.maps[0]
            # window.mapkit.CameraZoomRange.minCameraDistance = 1000
            # window.mapkit.CameraZoomRange.maxCameraDistnace = 10000
            map.showItems(annotation)

        # # Update the region using math
        oahu = window.mapkit.CoordinateRegion.new()
        oahu.center.latitude = sum(x) / len(x) + (max(x) - min(x)) / 2
        oahu.center.longitude = sum(y) / len(y)
        oahu.span.latitudeDelta = (max(x) - min(x)) * 2
        oahu.span.longitudeDelta = (max(y) - min(y)) * 2
        # window.mapkit.maps[0].setRegionAnimated = True
        window.mapkit.maps[0].region = oahu
    

def fetch_locations(document_id):
    print("\n\n\n\n", document_id, "\n\n\n\n")
    arrests = fetch_coordinates(document_id)
    lat_long = []
    
    spots = []
    for arrest in arrests:
        if float(arrest.latitude) == 0:
            continue
        if arrest.latitude in spots:
            continue
        spots.append(arrest.latitude)
        # print(arrest.__dict__)
        # print(arrest.charges[0].__dict__)
        # obj = get_data(arrest.id)
        # print(obj)
        lat_long.append(arrest)
    return lat_long

def add_random_script():
    # js = document.createElement("script")
    # js.setAttribute("type", "text/javascript")
    # js.innerHTML = """
    # function fetch_jwt() {
    #     const jwt = "eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IjJTQVU2Mk5WNk4ifQ.eyJpc3MiOiJMRUNWUlBNUVRLIiwiaWF0IjoxNjk3NjM1Mzc5LCJleHAiOjE3MDY3NDU2MDB9.KEtY85kvYNGFmUPD2o-81YUWuY_t2TbNxVwN8332N2VhIcKvAhi7a0k---XUeVelIaVTuB7Jyl1358KAbUm39w";
    #     return jwt
    # }
    # """

    def select_changed(event):
        js.console.log("selected changed", event)

    inputs = pydom["select"]
    for input in inputs:
        input.when("change", select_changed)


    @when("click", "#filter")
    def filter_data(event):
        js.console.log(event.target.previousSibling.previousSibling.value)
        search_term = event.target.previousSibling.previousSibling.value
        session = connect_to_database(is_echoed=False)
        output = search_partial_matches(session, search_term)
        for charge in output:
            loc = charge.arrest
            # print(loc.__dict__)
            # print(loc.arrest)
            # if event.target.previousSibling.previousSibling.value.lower() in annotation.title.lower():
            # # window.mapkit.maps[0].removeAnnotation(annotation)
            # annotation.color = "blue"
            # annotation.shown = False
            # js.console.log(annotation)
            coordinate = window.mapkit.Coordinate.new()
            coordinate.latitude = float(loc.latitude)
            coordinate.longitude = float(loc.longitude)

            annotation = window.mapkit.MarkerAnnotation.new(coordinate)
            annotation.callout = Callout()
            annotation.charge_object = loc.id
            annotation.id = loc.id
            annotation.location = loc.location
            annotation.obj = loc

            annotation.color = "red"
            annotation.display = "show"
            annotation.glyphText = f"🚔️"

            map = window.mapkit.maps[0]
            map.showItems(annotation)
            

    @when("change", "#crimes")
    def crime_filter(event):
        """
        
        :param event: 
        :type event: 
        :return: 
        :rtype: 
        """
        print(f"CRIME FILTER, {event}")
        value = js.document.getElementById("crimes").value
        crimes = get_crimes(value)
        add_annotations(crimes)

    @when("change", "#officers")
    def officer_filter(event):
        """

        :param event: 
        :type event: 
        :return: 
        :rtype: 
        """
        value = js.document.getElementById("officers").value
        officers = get_officers(value)
        add_annotations_officers(officers)
        reload_arrests_table(officers)
        
    @when("change", "#xlogs")
    def click_handler(event):
        """
        Event handlers get an event object representing the activity that raised
        them.
        """
        # value = int(js.document.getElementById("xlogs").value)
        # locations = fetch_locations(value)
        # if len(window.mapkit.maps) > 0:
        #     window.mapkit.maps[0].removeAnnotations(window.mapkit.maps[0].annotations)
        # 
        #     x = []
        #     y = []
        #     for loc in locations:
        #         x.append(float(loc.latitude))
        #         y.append(float(loc.longitude))
        # 
        #         # Make coordinates
        #         coordinate = window.mapkit.Coordinate.new()
        #         coordinate.latitude = float(loc.latitude)
        #         coordinate.longitude = float(loc.longitude)
        # 
        #         annotation = window.mapkit.MarkerAnnotation.new(coordinate)
        #         annotation.callout = Callout()
        #         annotation.charge_object = loc.id
        #         annotation.id = loc.id
        #         annotation.location = loc.location
        #         annotation.obj = loc
        # 
        #         annotation.color = "red"
        #         annotation.display = "show"
        #         annotation.glyphText = f"🚔️"
        # 
        #         map = window.mapkit.maps[0]
        #         # window.mapkit.CameraZoomRange.minCameraDistance = 1000
        #         # window.mapkit.CameraZoomRange.maxCameraDistnace = 10000
        #         map.showItems(annotation)
        # 
        #     # # Update the region using math
        #     oahu = window.mapkit.CoordinateRegion.new()
        #     oahu.center.latitude = sum(x) / len(x) + (max(x) - min(x)) / 2
        #     oahu.center.longitude = sum(y) / len(y)
        #     oahu.span.latitudeDelta = (max(x) - min(x)) * 2
        #     oahu.span.longitudeDelta = (max(y) - min(y)) * 2
        #     # window.mapkit.maps[0].setRegionAnimated = True
        #     window.mapkit.maps[0].region = oahu
        
        value = js.document.getElementById("xlogs").value
        if value == "Documents":
            value = None
        else:
            value = int(value)
        locations = fetch_locations(value)

        append_locations(locations)

        file_loader = FileSystemLoader('.')
        env = Environment(loader=file_loader)
        template = env.get_template('templates/components/arrests.html')
        js.document.getElementById("results").innerHTML = ''
        
        output = template.render(arrests=locations)
        display(HTML(output), target='results', append=False)

        def get_ids():
            return [int(x.id) for x in js.document.querySelectorAll("tr.selected")]

        @when("mouseover", "table")
        def asdfasdfas(event):
            blue_ids = get_ids()
            if len(blue_ids) > 0:
                return
            for annotation in window.mapkit.maps[0].annotations:
                # try:
                if int(annotation.id) == int(event.target.parentElement.id):
                    annotation.color = "blue"
                    # window.mapkit.maps[0].setCenterAnimated(annotation.coordinate)
                else:
                    if int(annotation.id) in blue_ids:
                        annotation.color == "blue"
                    else:
                        annotation.color = "red"
        @when("click", "#toggle-map-on")
        def remove_unselected(event):
            blue_ids = get_ids()
            for annotation in window.mapkit.maps[0].annotations:
                if int(annotation.id) in blue_ids:
                    window.mapkit.maps[0].addAnnotation(annotation)
                    annotation.color = "blue"
                else:
                    window.mapkit.maps[0].removeAnnotation(annotation)
                    
        @when("click", "#toggle-map-off")
        def reset(event):
            value = js.document.getElementById("xlogs").value
            locations = fetch_locations(value)
            append_locations(locations)

        @when("click", "table")
        def table_click(event):
            blue_ids = get_ids()
            print(blue_ids)
            for annotation in window.mapkit.maps[0].annotations:

                if int(annotation.id) == int(event.target.parentElement.id):
                    annotation.color = "blue"
                    window.mapkit.maps[0].setCenterAnimated(annotation.coordinate)

                    # window.mapkit.maps[0].CameraZoomRange = 4
                    # window.mapkit.maps[0].setCenterAnimated(annotation.coordinate)
                # if int(annotation.id) in blue_ids:
                #     annotation.color = "blue"
                elif int(annotation.id) in blue_ids:
                    annotation.color = "blue"
                    window.mapkit.maps[0].addAnnotation(annotation)
                    # window.mapkit.maps[0].setCenterAnimated(annotation.coordinate)
                    
                if annotation.id in blue_ids:
                    annotation.color = "blue"
                    # window.mapkit.maps[0].setCenterAnimated(annotation.coordinate)

                    continue
                else:
                    annotation.color = "red"

                

def index():
    """"""
    add_main_div()
    add_maps_dynamically()
    add_css_dynamically()
    add_apple_maps()
    load_template()
    add_random_script()

    
if __name__ == '__main__':
    print(document.title)
    if not document.title:
        print(document.title)
        index()
    
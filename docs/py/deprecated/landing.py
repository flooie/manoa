from js import document, Object, window 
from pyscript import HTML, display
from jinja2 import Environment, FileSystemLoader
from src import pydom
import js
from src.utils import fetch_documents, fetch_coordinates, fetch_token


def add_alert_to_each_table_row():
    rows = pydom["tr"]
    for row in rows:
        @pydom.when(row, 'click')
        def click_row(event):
            js.console.log(event)
            js.console.log(event.target.parentElement)
            # js.alert("OK", event)

    
def append_buttons():
    """"""
    second_div = pydom.create("div")
    text_input = second_div.create('input', html="")
    text_input.id = "someinput"

    button2 = second_div.create('button', html="Click me to execute first repl if empty search for king on map")
    pydom['#main'][0].append(second_div)

    @pydom.when(text_input, 'keyup')
    def input_enter(event):
        if event.code == "Enter":
            display(event, target="main")
        js.console.log(event)

    @pydom.when(button2, 'click')
    def repl2_action(mouseevent):
        value = document.getElementById("someinput").value
        if not value:
            value = "king"
            
def render_landing_page():
    file_loader = FileSystemLoader('.')
    env = Environment(loader=file_loader)
    numbers = range(1, 55)
    template = env.get_template('templates/child.html')
    temp_token = fetch_token(window.location.host)
    output = template.render(list_of_numbers=numbers, title="landing", token=temp_token)
    h = document.getElementsByTagName("html")[0]
    h.innerHTML = output
    # display(HTML(output), target="main")

    # add_alert_to_each_table_row()
    # append_buttons()

def render_landing_page_with_map():
    file_loader = FileSystemLoader('.')
    env = Environment(loader=file_loader)
    template = env.get_template('templates/new_child.html')
    temp_token = fetch_token(window.location.host)
    output = template.render(list_of_numbers=[], title="map", token=temp_token, locations=[0, 0])
    h = document.getElementsByTagName("html")[0]
    h.innerHTML = output

def render_landing_page_new_child():
    file_loader = FileSystemLoader('.')
    env = Environment(loader=file_loader)
    numbers = range(1, 55)
    template = env.get_template('templates/new_child.html')
    temp_token = fetch_token(window.location.host)

    output = template.render(list_of_numbers=numbers, title="notlanding", token=temp_token)
    h = document.getElementsByTagName("html")[0]
    h.innerHTML = output
    # add_alert_to_each_table_row()
    # append_buttons()



def index(title: str):
    print(title)
    if title == "landing":
        render_landing_page()
    elif title == "map":
        render_landing_page_with_map()
    elif title == "notlanding":
        render_landing_page_new_child()


def generate_map_page():
    """"""
    file_loader = FileSystemLoader('.')
    env = Environment(loader=file_loader)
    template = env.get_template('templates/child.html')
    temp_token = fetch_token(window.location.host)
    lat_long = [(0, 0)]
    output = template.render(token=temp_token, locations=lat_long)
    # display(HTML(output), target="main")
    # print(js.document.getElementById("main"))
    # print(HTML(js.document.getElementById("main")))
    # print("OOOK")

    # h = document.getElementById("main")
    # 
    # print(h)



if __name__ == '__main__':

    # page_title = document.title
    page_title = "landing"
    index(title=page_title)
    # render_landing_page_with_map()

    # generate_map_page()    

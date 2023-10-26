from js import document, Object, window, alert #- used previously to manipulate the objects
from pyscript import HTML, display
from jinja2 import Environment, FileSystemLoader
from src.utils import fetch_documents, fetch_coordinates, fetch_token
from src import pydom
import js
from src.input import fetch_arrest_records


def append_buttons():
    """"""    
    second_div = pydom.create("div")
    text_input = second_div.create('input', html="")
    text_input.id = "someinput"

    button2 = second_div.create('button', html="Click me to execute first repl if empty search for king on map")
    @pydom.when(button2, 'click')
    def repl2_action(mouseevent):
        value = document.getElementById("someinput").value
        if not value:
            value = "king"
        locations = fetch_arrest_records(value)
        # Call javascript from python code
        js.generate_new_map(str(locations))
        
    pydom['#functions'][0].append(second_div)


def generate_repl():
    """"""
    file_loader = FileSystemLoader('.')
    env = Environment(loader=file_loader)
    template = env.get_template('templates/map.html')
    temp_token = fetch_token(window.location.host)
    with open("src/input.py", "r") as f:
        repl_template = f.read()
    with open("src/input2.py", "r") as f:
        repl2_template = f.read()
    with open("js/map.js", "r") as f:
        new_map_js = f.read()
    output = template.render(token=temp_token, locations=[], repl1=repl_template, repl2=repl2_template, new_map_js=new_map_js)
    display(HTML(output), target="main")
    append_buttons()

if __name__ == '__main__':
    """"""
    generate_repl()

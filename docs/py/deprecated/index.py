from urllib.parse import urlparse, parse_qs
from js import document, Object, window #- used previously to manipulate the objects
from pyscript import HTML, display
from jinja2 import Environment, FileSystemLoader
from src.utils import fetch_documents, fetch_coordinates, fetch_token


def generate_index_page():
    """Generate homepage
    
    Why not use the best of pyhton to generate the HTML and load it up
    This is awesome and created all inside the browser - no server code
    
    :return: 
    """
    file_loader = FileSystemLoader('.')
    env = Environment(loader=file_loader)
    template = env.get_template('templates/homepage.html')
    logs = fetch_documents()
    output = template.render(data=logs)
    display(HTML(output), target="main")

def generate_map_page(doc_id):
    """"""
    file_loader = FileSystemLoader('.')
    env = Environment(loader=file_loader)
    template = env.get_template('templates/locations.html')
    locations = fetch_coordinates(doc_id)
    lat_long = []
    for loc in locations:
        if float(loc.latitude) == 0:
            continue
        lat_long.append((float(loc.latitude), float(loc.longitude)))

    temp_token = fetch_token(window.location.host)
    output = template.render(token=temp_token, locations=lat_long)
    display(HTML(output), target="main")


def parse_url():
    """"""
    w = urlparse(str(window.location))
    params = parse_qs(w.query)
    return params

if __name__ == '__main__':
    """"""

    params = parse_url()
    if not params.get("page", None):
        generate_index_page()
    elif params.get("page", None) == ["map"]:
        doc_id = params.get("doc_id", [0])
        generate_map_page(doc_id[0])
    else:
        generate_index_page()

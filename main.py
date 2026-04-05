from http.server import SimpleHTTPRequestHandler
from socketserver import TCPServer
from functools import partial
import threading
import datetime
import zipfile
import shutil
import json
import time
import os


EXTENSIONS_PORT = 8000


def start_server() -> TCPServer:
    handler = partial(SimpleHTTPRequestHandler, directory="extensions")
    httpd = TCPServer(("localhost", EXTENSIONS_PORT), handler)
    print(f"Serving extensions at http://localhost:{EXTENSIONS_PORT}/")
    return httpd


def main() -> None:
    if os.path.exists("Project.sb3"):
        if not os.path.isdir("assets"):
            update()

        os.remove("Project.sb3")

    zipf = zipfile.ZipFile("Project.sb3", "w")

    for file in os.listdir("assets/"):
        path = os.path.join("assets/", file)

        if os.path.isdir(path):
            continue

        zipf.write(path, file)

    zipf.close()

    if not os.path.isdir("extensions"):
        os.mkdir("extensions")

    httpd = start_server()
    server_thread = threading.Thread(target=httpd.serve_forever)
    server_thread.start()
    os.startfile("Project.sb3")
    print(f"Loaded at {datetime.datetime.now()}")
    last_modified = os.path.getmtime("Project.sb3")
    
    try:
        while True:
            if last_modified != os.path.getmtime("Project.sb3"):
                update()
                print(f"Updated at {datetime.datetime.now()}")
                last_modified = os.path.getmtime("Project.sb3")

            time.sleep(1)
    except KeyboardInterrupt:
        os.remove("Project.sb3")
        httpd.shutdown()
        httpd.server_close()
        print(f"Exited at {datetime.datetime.now()}")


def update() -> None:
    if os.path.isdir("assets"):
        shutil.rmtree("assets")

    zipf = zipfile.ZipFile("Project.sb3", "r")
    zipf.extractall("assets")
    zipf.close()
    json.dump(json.load(open("assets/project.json")), open("assets/project.json", "w"), indent=4)


if __name__ == "__main__":
    main()
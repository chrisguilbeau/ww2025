from flask import Flask, request, abort, Response
from flask import send_from_directory

app = Flask(
    __name__,
    static_folder='../static',
    )

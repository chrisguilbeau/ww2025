from app import app
from app import loadControllersAndViews
if __name__ == '__main__':
    loadControllersAndViews()
    app.run(host='0.0.0.0')

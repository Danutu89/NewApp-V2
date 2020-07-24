from flask_script import Manager, Server

from app import app
from flask_migrate import MigrateCommand

manager = Manager(app)
server = Server(host="0.0.0.0", port=5000, use_debugger=True, use_reloader=True)
manager.add_command("runserver", server)
manager.add_command('db', MigrateCommand)

if __name__ == "__main__":
    manager.run()
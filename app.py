from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/dots'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class dotdataset(db.Model):
    uname = db.Column(db.String(45), primary_key=True)
    pid = db.Column(db.String(45))
    xp = db.Column(db.Integer)
    gold = db.Column(db.Integer)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __repr__(self):
        return f' username: {self.uname},player_id: {self.pid},xp: {self.xp},gold: {self.gold}'


@app.route('/api/v1/player', methods=['POST'])
def create():
    # Extract Username from arguments
    username = request.args.get("username")
    try:
        # Find if there is a pre-existing similar username or not
        value = dotdataset.query.filter_by(uname=username).first()
        if value is not None:
            db.session.expire_all()
            # If username exist then return this msg
            return "Username already present!!! Try other username", 400
        player_id = username + str(1)
        xp = 1
        gold = 1
        # creating response dataset
        datadict = {'username': username, 'player_id': player_id}
        # creating data object for database
        p = dotdataset(uname=username, pid=player_id, xp=xp, gold=gold)
        # add data to database and then commit
        db.session.add(p)
        db.session.commit()
        db.session.expire_all()
        # return json format dictionary data to the user
        return jsonify(datadict), 200
    except:
        # In case any runtime error happen in between the code
        return "error_message: Some kind of unspecified error has occurred!", 500


@app.route('/api/player/id', methods=['GET', 'PUT'])
def retorupdate():
    if request.method == 'GET':
        # Extract Username from arguments
        username = request.args.get("username")
        try:
            # Find if there is a pre-existing similar username or not
            value = dotdataset.query.filter_by(uname=username).first()
            if value is not None:
                # If username exist then return the user data stat
                datadict = {'username': value.uname, 'player_id': value.pid, 'xp': value.xp, 'gold': value.gold}
                db.session.expire_all()
                return jsonify(datadict), 200
            else:
                # Else return user doesn't exist in our database
                db.session.expire_all()
                return "Username does not exist! Please try again!!! ", 400
        except:
            # In case any runtime error happen in between the code
            return "error_message: Some kind of unspecified error has occurred!", 500
    elif request.method == 'PUT':
        # Extract Username, player_id, xp, gold from arguments
        username = request.args.get("username")
        player_id = request.args.get("player_id")
        xp = request.args.get("xp")
        gold = request.args.get("gold")
        try:
            # Find if there is a pre-existing similar username or not
            value = dotdataset.query.filter_by(uname=username).first()
            if value is None:
                # If user does not exist then nothing can be changed so return user doesn't exist in our database
                return "Username does not exist. Please try again!!!", 400
            # In case one of the field is not sent by the user then use the previously present value
            if player_id is not None:
                value.pid = player_id
            if xp is not None:
                value.xp = xp
            if gold is not None:
                value.gold = gold
            # Merge the value with the currently present in the database
            db.session.merge(value)
            db.session.commit()
            db.session.expire_all()
            # creating response dataset
            datadict = {'username': value.uname, 'player_id': value.pid, 'xp': value.xp, 'gold': value.gold}
            # Return Json format dictionary
            return jsonify(datadict), 200
        except:
            # In case any runtime error happen in between the code
            return "error_message: Some kind of unspecified error has occurred!", 500


@app.route('/api/leaderboards', methods=['GET'])
def leaderboard():
    # Extract sortby parameter and size to return
    sortby = request.args.get("sortby")
    size = request.args.get("size")
    try:
        # Get the order_by (Sorted) in descending order for the given parameter and size
        if sortby == 'xp':
            value = db.session.query(dotdataset).order_by(dotdataset.xp.desc()).limit(size).all()
        elif sortby == 'gold':
            value = db.session.query(dotdataset).order_by(dotdataset.gold.desc()).limit(size).all()
        else:
            # If illegal parameter is chosen return below msg
            return "Illegal choice. Please select Xp or Gold", 400
        # Creating a return list
        retlist = []
        for data in value:
            # Set the list in poper order the data is received
            temp = {'username': data.uname, 'player_id': data.pid, 'xp': data.xp, 'gold': data.gold}
            retlist.append(temp)
        # Retern the list in Json format
        return jsonify(retlist), 200
    except:
        # In case any runtime error happen in between the code
        return "error_message: Some kind of unspecified error has occurred!", 500


if __name__ == "__main__":
    # Run the flask Application
    app.run()

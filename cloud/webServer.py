from flask import Flask,render_template,request,redirect,session,jsonify

import threading
import sqlite3


from database import init_db,get_db

import mqtt_manager



app=Flask(__name__)

app.secret_key="secret123"



init_db()


mqtt_manager.start()




# login


@app.route("/login",methods=["GET","POST"])
def login():


    if request.method=="POST":


        user=request.form["username"]

        password=request.form["password"]



        if user=="admin" and password=="admin":


            session["user"]=user


            return redirect(
                "/devices"
            )



    return render_template(
        "login.html"
    )




@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")




# Dlista dispositivi


@app.route("/devices")
def devices():


    if "user" not in session:

        return redirect("/login")



    db=get_db()


    devices=db.execute(
        """
        SELECT * FROM devices
        """
    ).fetchall()


    return render_template(
        "devices.html",
        devices=devices,
        data=mqtt_manager.latest_data
    )




#  add


@app.route("/device/add",methods=["POST"])
def add_device():


    name=request.form["name"]


    topic=f"edge/{name}/data"



    db=get_db()


    db.execute(

        """
        INSERT INTO devices(name,topic)

        VALUES(?,?)

        """,

        (
            name,
            topic
        )

    )


    db.commit()


    return redirect("/devices")




#mqtt

@app.route("/device/<name>/<action>")
def command(name,action):


    if action=="on":

        mqtt_manager.send_tag(
            name,
            "ON"
        )


    else:

        mqtt_manager.send_tag(
            name,
            "OFF"
        )



    return redirect("/devices")




#àlog

@app.route("/logs")
def logs():


    db=get_db()


    logs=db.execute(

        """
        SELECT * FROM logs
        ORDER BY id DESC

        """

    ).fetchall()



    return render_template(
        "logs.html",
        logs=logs
    )





# api

@app.route("/api/devices")
def api_devices():


    return jsonify(
        mqtt_manager.latest_data
    )





if __name__=="__main__":


    app.run(

        host="0.0.0.0",

        port=5000

    )
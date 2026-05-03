from flask import Flask, request, render_template
from signal_optimizer import optimize_signal

app = Flask(__name__, template_folder="templates", static_folder="static")

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/predict", methods=["POST"])
def predict():

    speed = int(request.form["speed"])

    if speed < 25:
        result = "🚨 HIGH TRAFFIC"
    elif speed < 40:
        result = "⚠ MEDIUM TRAFFIC"
    else:
        result = "✅ LOW TRAFFIC"

    return render_template("index.html", prediction=result)


@app.route('/optimize_signal', methods=['POST'])
def optimize_signal_route():

    north = int(request.form['north'])
    south = int(request.form['south'])
    east = int(request.form['east'])
    west = int(request.form['west'])

    lane, time = optimize_signal(north, south, east, west)

    total = north + south + east + west

    if total > 80:
        status = "Heavy Traffic"
    elif total > 40:
        status = "Moderate Traffic"
    else:
        status = "Low Traffic"

    return render_template(
        "index.html",
        lane=lane,
        time=time,
        north=north,
        south=south,
        east=east,
        west=west,
        total=total,
        status=status
    )



if __name__ == "__main__":
    import os
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
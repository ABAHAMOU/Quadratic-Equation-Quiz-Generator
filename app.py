from flask import Flask, render_template, request, redirect, url_for, session
import random, math
from fractions import Fraction

app = Flask(__name__)
app.secret_key = "mesim_secret"

def simuler_discrete(valeurs, probabilites):
    u = random.random()
    seuil = 0
    for v, p in zip(valeurs, probabilites):
        seuil += p
        if u <= seuil:
            return v
    return valeurs[-1]


class GenerateurExercices:
    def __init__(self):
        self.E = [i for i in range(-9, 10) if i != 0]  #!< Non-zero integers in [-9, 9]
        self.E_plus = list(range(1, 10))                #!< Positive integers in [1, 9]

    def generer(self):
        type_ex = simuler_discrete([1, 2, 3], [1/5, 2/5, 2/5])
        if type_ex == 1:
            return self.cas_delta_negatif()
        elif type_ex == 2:
            return self.cas_delta_nul()
        else:
            return self.cas_delta_positif()

    def cas_delta_negatif(self):
        a = random.choice(self.E)
        b = random.choice(self.E)
        e = random.choice([1, 2, 3])
        c = Fraction(b**2 + e, 4 * a)  #!< Exact fraction so that b² - 4ac = -e
        return a, b, c

    def cas_delta_nul(self):
        a = random.choice([1, 4, 9])  #!< Perfect squares keep b integer
        x0 = random.choice(self.E)   #!< The double root
        b = -2 * a * x0
        c = a * (x0**2)
        return a, b, c

    def cas_delta_positif(self):
        a = random.choice([1, 2])
        x1 = random.choice(self.E)
        x2 = random.choice(self.E)
        if x1 == x2:
            x2 += 1  #!< Ensure two distinct roots so that Δ > 0
        b = -a * (x1 + x2)
        c = a * (x1 * x2)
        return a, b, c


def calculer_solutions(a, b, c):
    delta = b**2 - 4 * a * c
    if delta < 0:
        return delta, []
    elif delta == 0:
        return delta, [round(float(-b / (2 * a)), 2)]
    else:
        r1 = (-b - math.sqrt(delta)) / (2 * a)
        r2 = (-b + math.sqrt(delta)) / (2 * a)
        return delta, sorted([round(float(r1), 2), round(float(r2), 2)])


def afficher_equation(a, b, c):
    if a == 1:
        eq = "x²"
    elif a == -1:
        eq = "-x²"
    else:
        eq = f"{a}x²"

    if b == 0:
        pass
    elif b == 1:
        eq += " + x"
    elif b == -1:
        eq += " - x"
    else:
        eq += f" + {b}x" if b > 0 else f" - {abs(b)}x"

    if c == 0:
        pass
    else:
        eq += f" + {c}" if c > 0 else f" - {abs(c)}"

    return eq + " = 0"


gen = GenerateurExercices()


@app.route("/")
def accueil():
    return render_template("intro.html")


@app.route("/start", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        session["nb_exos"] = int(request.form["nb_exos"])
        session["current"] = 1
        session["score_total"] = 0
        return redirect(url_for("exercice"))

    return render_template("start.html")


@app.route("/exercice", methods=["GET", "POST"])
def exercice():
    if "nb_exos" not in session:
        return redirect(url_for("index"))

    if request.method == "POST":
        delta_user = request.form.get("delta", 0)
        nb_user = request.form.get("nb_solutions", 0)

        a, b, c = session["a"], session["b"], session["c"]
        delta_reel, solutions_reelles = calculer_solutions(a, b, c)

        points_etape = 0
        try:
            if abs(float(delta_user) - float(delta_reel)) < 0.1:
                points_etape += 0.5
            if int(nb_user) == len(solutions_reelles):
                points_etape += 0.5
        except:
            pass

        session["score_total"] += points_etape
        session["current"] += 1

        if session["current"] > session["nb_exos"]:
            return redirect(url_for("resultat_final"))

        return redirect(url_for("exercice"))

    a, b, c = gen.generer()
    session["a"], session["b"], session["c"] = float(a), float(b), float(c)  #!< Fraction is not JSON-serialisable

    eq = afficher_equation(a, b, c)
    return render_template(
        "index.html",
        equation=eq,
        current=session["current"],
        total=session["nb_exos"]
    )


@app.route("/resultat")
def resultat_final():
    score = session.get("score_total", 0)
    total = session.get("nb_exos", 1)

    return render_template("result.html",
                           score=score,
                           total=total)


if __name__ == "__main__":
    app.run(debug=True)
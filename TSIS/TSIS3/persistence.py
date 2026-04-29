import json, os

def load_data(filename, default):
    if not os.path.exists(filename):
        return default
    try:
        with open(filename, "r") as f:
            return json.load(f)
    except:
        return default

def save_data(filename, data):
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)

def update_leaderboard(name, score, distance):
    lb = load_data(r"C:\Users\Bull\Desktop\PP_2\Practice1\TSIS\TSIS3\leaderboards.json", [])
    lb.append({"name": name, "score": score, "distance": int(distance)})
    lb = sorted(lb, key=lambda x: x['score'], reverse=True)[:10]
    save_data(r"C:\Users\Bull\Desktop\PP_2\Practice1\TSIS\TSIS3\leaderboards.json", lb)
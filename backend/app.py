from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import random
import ast

app = Flask(__name__, static_folder="../frontend", static_url_path="")
CORS(app)

# Dictionnaire pour stocker les scripts, scores et positions des joueurs
players = {}

# ====================
# Routes de connexion
# ====================
@app.route('/index.html')
def serve_index():
    return send_from_directory(app.static_folder, "index.html")


@app.route('/')
def serve_login():
    return send_from_directory(app.static_folder, "login.html")


@app.route('/player_login')
def serve_player_login():
    return send_from_directory(app.static_folder, "player_login.html")



@app.route('/authenticate', methods=['POST'])
def authenticate():
    """Authentifie l'utilisateur."""
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if username == "admin" and password == "admin123":
        return jsonify({"success": True, "redirect": "/index.html"})
    return jsonify({"success": False, "error": "Identifiants invalides"}), 401


# ====================
# Gestion des joueurs
# ====================
@app.route('/submit_player', methods=['POST'])
def submit_player():
    try:
        data = request.json
        player_id = data.get("player_id")
        commands = data.get("commands")

        if not player_id or not commands:
            return jsonify({"error": "ID du joueur ou commandes manquantes."}), 400

        # Vérification si l'ID existe déjà
        if player_id in players:
            return jsonify({"error": "ID déjà utilisé. Veuillez choisir un autre ID."}), 400

        # Ajouter le joueur
        players[player_id] = {"script": commands, "score": 0, "position": None}
        print(f"Joueur {player_id} a soumis ses commandes : {commands}")
        return jsonify({"status": "Commandes enregistrées avec succès."})
    except Exception as e:
        print(f"Erreur lors de la soumission des commandes : {e}")
        return jsonify({"error": "Une erreur s'est produite."}), 500




@app.route('/scores', methods=['GET'])
def get_scores():
    scores = {player_id: info["score"] for player_id, info in players.items() if info["position"] is not None}
    print(f"Scores mis à jour : {scores}")
    return jsonify(scores)


@app.route('/positions', methods=['GET'])
def get_positions():
    positions = {player_id: data["position"] for player_id, data in players.items()}
    print(f"Positions des joueurs transmises : {positions}")
    return jsonify(positions)


@app.route('/get_players', methods=['GET'])
def get_players():
    try:
        players_info = {player_id: {"position": player_data["position"]} for player_id, player_data in players.items()}
        return jsonify(players_info)
    except Exception as e:
        print(f"Erreur lors de la récupération des joueurs : {e}")
        return jsonify({"error": "Une erreur s'est produite lors de la récupération des joueurs."}), 500


# ====================
# Logique du jeu
# ====================
def initialize_positions():
    """Initialise les positions uniquement pour les joueurs actifs."""
    for player_id in players:
        if players[player_id]["position"] is None and players[player_id]["score"] == 0:  # Initialiser uniquement si le joueur est nouveau
            x = random.randint(0, 15)
            y = random.randint(0, 15)
            players[player_id]["position"] = (x, y)
            print(f"Position du joueur {player_id} initialisée à ({x}, {y}).")



def apply_move(position, direction):
    """Applique un mouvement à une position donnée en respectant les limites de l'arène."""
    x, y = position
    if direction == "up" and y > 0:
        y -= 1
    elif direction == "down" and y < 15:
        y += 1
    elif direction == "left" and x > 0:
        x -= 1
    elif direction == "right" and x < 15:
        x += 1
    return x, y


def check_collisions():
    """Gère les collisions et met à jour les scores lorsque les joueurs se mangent."""
    positions = {}
    joueurs_supprimes = []

    for player_id, player_data in list(players.items()):
        position = player_data["position"]

        if position is None:
            continue  # Ignorer les joueurs sans position

        # Si un autre joueur est déjà à cette position
        if position in positions:
            existing_player = positions[position]
            if player_id in joueurs_supprimes or existing_player in joueurs_supprimes:
                continue  # Ignorer les joueurs déjà supprimés

            # Le joueur qui mange voit son score augmenter
            if players[player_id]["score"] >= players[existing_player]["score"]:
                players[player_id]["score"] += 10
                joueurs_supprimes.append(existing_player)
            else:
                players[existing_player]["score"] += 10
                joueurs_supprimes.append(player_id)
        else:
            # Marquer cette position comme occupée par ce joueur
            positions[position] = player_id

    # Retirer les joueurs mangés de l'arène
    for player_id in joueurs_supprimes:
        if player_id in players:
            players[player_id]["position"] = None  # Retirer le joueur de l'arène

    print(f"État des joueurs après collision : {players}")

def remove_lowest_score_players():
    """Supprime les joueurs ayant le score minimal."""
    global players

    if not players:
        return

    # Obtenir les scores actuels des joueurs restants
    scores = [data["score"] for data in players.values() if data["position"] is not None]

    # Si tous les scores sont identiques et > 0, supprimer tous les joueurs
    if len(set(scores)) == 1:
        score = scores[0]
        if score > 0:
            print("Tous les joueurs ont le même score. Suppression de tous les joueurs.")
            players = {player_id: data for player_id, data in players.items() if data["position"] is None}
            return "Tous les joueurs ont été supprimés, pas de gagnant."

    # Trouver le score minimal
    min_score = min(scores)

    # Supprimer les joueurs avec le score minimal
    for player_id, data in list(players.items()):
        if data["score"] == min_score:
            print(f"Joueur {player_id} avec le score minimal ({min_score}) est supprimé.")
            players[player_id]["position"] = None

    # Vérifier s'il reste un gagnant clair
    remaining_players = [player_id for player_id, data in players.items() if data["position"] is not None]
    if len(remaining_players) == 1:
        winner_id = remaining_players[0]
        return f"Le gagnant est le joueur {winner_id} avec {players[winner_id]['score']} points."

    return "Suppression des joueurs avec le score minimal terminée."

def move_player_with_bounce(player_id, action=None):
    current_position = players[player_id]["position"]
    x, y = current_position

    # Si aucune action spécifique n'est donnée, cible un autre joueur
    if not action:
        closest_player = None
        min_distance = float("inf")
        
        for other_id, other_data in players.items():
            if other_id != player_id and other_data["position"]:
                other_x, other_y = other_data["position"]
                distance = abs(x - other_x) + abs(y - other_y)  # Distance de Manhattan
                if distance < min_distance:
                    closest_player = (other_x, other_y)
                    min_distance = distance

        # Dirige le joueur vers le joueur le plus proche
        if closest_player:
            if closest_player[0] > x:
                x += 1
            elif closest_player[0] < x:
                x -= 1
            elif closest_player[1] > y:
                y += 1
            elif closest_player[1] < y:
                y -= 1
    else:
        # Appliquer les mouvements comme avant
        if action == "up":
            y = y - 1 if y > 0 else 9
        elif action == "down":
            y = y + 1 if y < 9 else 0
        elif action == "left":
            x = x - 1 if x > 0 else 9
        elif action == "right":
            x = x + 1 if x < 9 else 0

    players[player_id]["position"] = (x, y)


turn_count = 0  # Compteur global pour suivre les tours

@app.route('/run_game_step_by_step', methods=['POST'])
def run_game_step_by_step():
    global turn_count
    try:
        turn_count += 1  # Incrémenter le compteur de tours
        movements = []
        initialize_positions()

        for player_id, player_data in players.items():
            commands = player_data.get("script", "")
            steps = parse_commands(commands)

            for step in steps:
                old_position = players[player_id]["position"]
                move_player_with_bounce(player_id, step)
                new_position = players[player_id]["position"]

                movements.append({
                    "player_id": player_id,
                    "old_position": old_position,
                    "new_position": new_position
                })

        check_collisions()

        # Après chaque 4 tours, supprimer les joueurs avec les scores les plus bas
        removal_message = None
        if turn_count % 4 == 0:
            removal_message = remove_lowest_score_players()

        game_status = check_game_end()

        return jsonify({
            "movements": movements,
            "positions": {player_id: data["position"] for player_id, data in players.items()},
            "status": "Partie exécutée étape par étape.",
            "game_over": game_status["game_over"],
            "winner": game_status.get("winner"),
            "winner_score": game_status.get("score"),
            "removal_message": removal_message
        })
    except Exception as e:
        print(f"Erreur lors de l'exécution de la partie étape par étape : {e}")
        return jsonify({"error": "Une erreur s'est produite pendant la partie."}), 500







def move_player(player_id, action):
    """Déplace un joueur selon une action donnée."""
    current_position = players[player_id]["position"]
    new_position = apply_move(current_position, action)
    players[player_id]["position"] = new_position
    print(f"Déplacement : Joueur {player_id} de {current_position} à {new_position}")

def parse_commands(commands):
    """Analyse les commandes entrées par l'utilisateur et retourne une liste de mouvements."""
    movements = []
    try:
        commands_list = commands.split()
        for command in commands_list:
            if "*" in command:
                count, direction = command.split("*")
                movements.extend([direction] * int(count))
            else:
                movements.append(command)
    except ValueError as e:
        print(f"Erreur lors de l'analyse des commandes : {e}")
    return movements


@app.route('/convert_commands', methods=['POST'])
def convert_commands():
    try:
        data = request.json
        player_id = data.get("player_id")
        commands = data.get("commands")

        if not player_id or not commands:
            return jsonify({"error": "ID du joueur ou commandes manquantes."}), 400

        # Assurez-vous que le joueur existe
        if player_id not in players:
            return jsonify({"error": "Joueur non trouvé."}), 404

        # Mettre à jour le script/commandes du joueur
        players[player_id]["script"] = commands
        print(f"Commandes mises à jour pour le joueur {player_id}: {commands}")

        return jsonify({"status": "Commandes mises à jour avec succès."})
    except Exception as e:
        print(f"Erreur dans /convert_commands : {e}")
        return jsonify({"error": "Une erreur s'est produite."}), 500

@app.route('/reset_game', methods=['POST'])
def reset_game():
    players.clear()
    return jsonify({"status": "Jeu réinitialisé avec succès."})

def check_game_end():
    """Vérifie s'il reste un seul joueur et déclare le gagnant."""
    active_players = [p_id for p_id, data in players.items() if data["position"] is not None]

    if len(active_players) == 1:
        winner_id = active_players[0]
        return {"game_over": True, "winner": winner_id, "score": players[winner_id]["score"]}
    return {"game_over": False}



if __name__ == '__main__':
    app.run(debug=True)
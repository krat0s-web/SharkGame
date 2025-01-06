async function submitPlayer(event) {
    event.preventDefault(); // Empêche le rechargement de la page

    const playerId = document.getElementById('playerId').value;
    const scriptText = document.getElementById('scriptInput').value;

    if (!playerId || !scriptText) {
        alert("L'ID du joueur et le script sont nécessaires.");
        return;
    }

    try {
        const response = await fetch('http://localhost:5000/submit_script', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ player_id: playerId, script: scriptText })
        });

        if (!response.ok) {
            throw new Error("Erreur lors de l'ajout du joueur");
        }

        const result = await response.json();
        document.getElementById('response').textContent = result.status;
        fetchArena(); // Mettre à jour l’arène
    } catch (error) {
        console.error('Erreur:', error);
        document.getElementById('response').textContent = 'Erreur lors de l’ajout du joueur';
    }
}

// Mettre à jour la grille de l’arène
async function submitSimpleCommands(event) {
    event.preventDefault(); // Empêche le rechargement de la page

    const playerId = document.getElementById("playerId").value;
    const commands = document.getElementById("scriptInput").value;

    if (!playerId || !commands) {
        alert("Veuillez entrer un ID de joueur et des commandes.");
        return;
    }

    try {
        const response = await fetch("http://127.0.0.1:5000/submit_player", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ player_id: playerId, commands: commands }),
        });

        if (!response.ok) {
            throw new Error("Erreur lors de la soumission des commandes.");
        }

        const result = await response.json();
        document.getElementById("response").textContent = `Succès : ${result.status}`;
        console.log(`Commandes mises à jour : ${commands}`);
    } catch (error) {
        console.error("Erreur:", error);
        document.getElementById("response").textContent = "Erreur lors de la soumission des commandes.";
    }
}




// Mettre à jour l’arène
async function fetchArena() {
    try {
        const response = await fetch("http://127.0.0.1:5000/positions");
        if (!response.ok) {
            throw new Error("Erreur lors de la récupération des positions.");
        }

        const positions = await response.json();
        console.log("Positions reçues du backend :", positions);

        const grid = document.getElementById("grid");
        grid.innerHTML = ""; // Réinitialiser la grille

        for (let y = 0; y < 16; y++) {
            for (let x = 0; x < 16; x++) {
                const cell = document.createElement("div");
                cell.classList.add("cell");

                // Vérifiez si un joueur est à cette position
                for (const [playerId, pos] of Object.entries(positions)) {
                    if (pos && pos[0] === x && pos[1] === y) {
                        const playerElement = document.createElement("div");
                        playerElement.classList.add("player");
                        playerElement.textContent = playerId;
                        cell.appendChild(playerElement);
                    }
                }

                grid.appendChild(cell);
            }
        }
    } catch (error) {
        console.error("Erreur lors de la récupération de l'arène :", error);
    }
}










function animatePlayerMovement(playerId, oldPosition, newPosition) {
    const playerElement = document.querySelector(`.player[data-id="${playerId}"]`);
    if (!playerElement) return;

    // Calculer la distance de déplacement
    const deltaX = (newPosition[0] - oldPosition[0]) * 60; // 60px par case
    const deltaY = (newPosition[1] - oldPosition[1]) * 60;

    playerElement.style.transform = `translate(${deltaX}px, ${deltaY}px)`;
}



async function fetchScores() {
    try {
        const response = await fetch('http://127.0.0.1:5000/scores');
        if (!response.ok) {
            throw new Error("Erreur lors de la récupération des scores");
        }

        const scores = await response.json();
        console.log("Scores mis à jour :", scores);

        const scoreList = document.getElementById("scoreList");
        scoreList.innerHTML = ""; // Effacer les anciens scores

        for (const [playerId, score] of Object.entries(scores)) {
            if (score !== null) { // Ignorer les joueurs supprimés
                const listItem = document.createElement('li');
                listItem.textContent = `Joueur ${playerId} : ${score} points`;
                scoreList.appendChild(listItem);
            }
        }
    } catch (error) {
        console.error("Erreur lors de la récupération des scores :", error);
    }
}



async function fetchPlayers() {
    try {
        const response = await fetch('http://127.0.0.1:5000/get_players');
        if (!response.ok) {
            throw new Error("Erreur lors de la récupération des joueurs.");
        }

        const players = await response.json();
        console.log("Joueurs enregistrés :", players);

        const playerList = document.getElementById('playerList');
        playerList.innerHTML = ""; // Efface l'ancienne liste

        for (const [playerId, playerData] of Object.entries(players)) {
            const listItem = document.createElement('li');
            const position = playerData.position ? `(${playerData.position[0]}, ${playerData.position[1]})` : "Non définie";
            listItem.textContent = `Joueur ${playerId}: Position ${position}`;
            playerList.appendChild(listItem);
        }
    } catch (error) {
        console.error("Erreur lors de la récupération des joueurs :", error);
    }
}
let gameInterval; // Variable pour stocker l'intervalle
let isGameRunning = false; // Empêche plusieurs clics simultanés

async function runGameAutomatically() {
    if (isGameRunning) return; // Empêcher plusieurs exécutions en même temps

    isGameRunning = true; // Marquer le jeu comme en cours
    try {
        while (true) {
            const response = await fetch("http://127.0.0.1:5000/run_game_step_by_step", {
                method: "POST",
            });

            if (!response.ok) {
                throw new Error("Erreur lors de l'exécution de la partie étape par étape.");
            }

            const result = await response.json();

            // Mettre à jour l'arène et les scores après chaque étape
            await fetchArena();
            await fetchScores();
            await updateRemainingPlayersCount();

            // Afficher le message de suppression après chaque 4 tours
            if (result.removal_message) {
                alert(result.removal_message);
            }

            // Vérifier si la partie est terminée
            if (result.game_over) {
                alert(`Partie terminée ! Le gagnant est le joueur ${result.winner} avec ${result.winner_score} points.`);
                break; // Arrêter la boucle
            }

            // Attendre un certain temps avant la prochaine étape
            await new Promise(resolve => setTimeout(resolve, 1000)); // Pause de 1 seconde
        }
    } catch (error) {
        console.error("Erreur lors de l'exécution automatique :", error);
    } finally {
        isGameRunning = false; // Réinitialiser l'état du jeu
    }
}

// Animer un joueur dans l'arène
function animatePlayerMovement(playerId, oldPosition, newPosition) {
    const grid = document.getElementById('grid');
    const playerElement = grid.querySelector(`.player[data-id='${playerId}']`);

    if (!playerElement) return;

    // Calculer la distance de déplacement (ajustez selon votre grille)
    const deltaX = (newPosition[0] - oldPosition[0]) * 60; // Chaque cellule fait 60px
    const deltaY = (newPosition[1] - oldPosition[1]) * 60;

    // Appliquer la transformation pour simuler le déplacement
    playerElement.style.transform = `translate(${deltaX}px, ${deltaY}px)`;
}



async function animateMovement(movement) {
    const grid = document.getElementById("grid");
    const playerElement = [...grid.getElementsByClassName("player")].find(el => el.textContent === movement.player_id);

    if (playerElement) {
        // Simuler le mouvement avec une animation (par exemple, en modifiant les coordonnées)
        playerElement.style.transition = "transform 0.5s ease";
        const x = movement.new_position[0] * 60; // Taille d'une case : 60px
        const y = movement.new_position[1] * 60;
        playerElement.style.transform = `translate(${x}px, ${y}px)`;

        // Attendre que l'animation se termine avant de passer au prochain mouvement
        return new Promise(resolve => setTimeout(resolve, 500));
    }
}
async function updateRemainingPlayersCount() {
    try {
        const response = await fetch("http://127.0.0.1:5000/positions");
        if (!response.ok) {
            throw new Error("Erreur lors de la récupération des joueurs restants.");
        }

        const positions = await response.json();
        const remainingPlayers = Object.values(positions).filter(pos => pos !== null).length;

        const remainingPlayersCountElement = document.getElementById("remaining-players-count");
        remainingPlayersCountElement.textContent = `Joueurs restants : ${remainingPlayers}`;
    } catch (error) {
        console.error("Erreur lors de la mise à jour des joueurs restants :", error);
    }
}
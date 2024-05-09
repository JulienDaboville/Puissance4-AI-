import random
import tkinter as tk
from tkinter import simpledialog


class Puissance4:
    def __init__(self, rows=6, cols=7, difficulty_R="medium", difficulty_J="medium"):
        """
        Initialisation du jeu Puissance 4 avec les paramètres de base et les difficultés des IA.
        :param rows: Nombre de rangées du plateau.
        :param cols: Nombre de colonnes du plateau.
        :param difficulty_R: Difficulté de l'IA Rouge.
        :param difficulty_J: Difficulté de l'IA Jaune.
        """
        self.difficulty_R = difficulty_R
        self.difficulty_J = difficulty_J
        self.rows = rows
        self.cols = cols
        self.board = [[" " for _ in range(cols)] for _ in range(rows)]
        self.turn = "R"
        self.transposition_table = {}

    def tournament(self, num_games=5):
        """
        Organise un tournoi entre les IA de différentes difficultés.
        :param num_games: Nombre de jeux à jouer entre chaque paire de difficultés.
        :return: Un dictionnaire avec les résultats des matchs.
        """
        difficulties = ["easy", "medium", "difficult"]
        results = {
            diff: {
                other: {"wins": 0, "losses": 0}
                for other in difficulties
                if other != diff
            }
            for diff in difficulties
        }

        for difficulty_R in difficulties:
            for difficulty_J in difficulties:
                if difficulty_R == difficulty_J:
                    continue
                for _ in range(num_games):
                    game = Puissance4(
                        difficulty_R=difficulty_R, difficulty_J=difficulty_J
                    )
                    winner = self.play_full_game(game)
                    if winner == "R":
                        results[difficulty_R][difficulty_J]["wins"] += 1
                        results[difficulty_J][difficulty_R]["losses"] += 1
                    elif winner == "J":
                        results[difficulty_J][difficulty_R]["wins"] += 1
                        results[difficulty_R][difficulty_J]["losses"] += 1

        return results

    def play_full_game(self, game):
        """
        Joue une partie complète en utilisant les IA jusqu'à ce qu'un gagnant soit déterminé ou que le jeu soit terminé.
        :param game: Instance du jeu Puissance 4.
        :return: Gagnant du jeu.
        """
        while not game.is_game_over():
            current_player = "R" if game.turn == "R" else "J"
            best_move = game.best_move(current_player)
            game.insert_token(best_move, current_player)
            game.turn = "J" if game.turn == "R" else "R"
        return game.check_winner()

    def insert_token(self, col, player):
        """
        Insère un jeton dans la colonne spécifiée pour le joueur donné.
        :param col: Index de la colonne.
        :param player: 'R' pour Rouge ou 'J' pour Jaune.
        :return: Booléen indiquant si le jeton a été inséré avec succès.
        """
        if col < 0 or col >= self.cols or self.board[0][col] != " ":
            return False
        for row in range(self.rows - 1, -1, -1):
            if self.board[row][col] == " ":
                self.board[row][col] = player
                return True
        return False

    def check_winner(self):
        """
        Vérifie le plateau de jeu pour déterminer si un joueur a gagné.
        :return: Le joueur gagnant ('R' ou 'J') ou None si aucun gagnant.
        """
        for row in range(self.rows):
            for col in range(self.cols - 3):
                if (
                    self.board[row][col]
                    == self.board[row][col + 1]
                    == self.board[row][col + 2]
                    == self.board[row][col + 3]
                    != " "
                ):
                    return self.board[row][col]

        for col in range(self.cols):
            for row in range(self.rows - 3):
                if (
                    self.board[row][col]
                    == self.board[row + 1][col]
                    == self.board[row + 2][col]
                    == self.board[row + 3][col]
                    != " "
                ):
                    return self.board[row][col]

        for row in range(self.rows - 3):
            for col in range(self.cols - 3):
                if (
                    self.board[row][col]
                    == self.board[row + 1][col + 1]
                    == self.board[row + 2][col + 2]
                    == self.board[row + 3][col + 3]
                    != " "
                ):
                    return self.board[row][col]

        for row in range(3, self.rows):
            for col in range(self.cols - 3):
                if (
                    self.board[row][col]
                    == self.board[row - 1][col + 1]
                    == self.board[row - 2][col + 2]
                    == self.board[row - 3][col + 3]
                    != " "
                ):
                    return self.board[row][col]

        return None

    def generate_possible_moves(self):
        """
        Génère une liste de mouvements possibles (colonnes disponibles).
        :return: Liste des indices de colonnes disponibles.
        """
        return [col for col in range(self.cols) if self.board[0][col] == " "]

    def is_game_over(self):
        """
        Détermine si le jeu est terminé.
        :return: Booléen indiquant si le jeu est terminé.
        """
        return self.check_winner() is not None or all(
            self.board[0][col] != " " for col in range(self.cols)
        )

    def evaluate_board(self, difficulty):
        """
        Évalue le plateau actuel et renvoie un score basé sur la configuration des jetons.
        :param difficulty: Niveau de difficulté utilisé pour ajuster l'évaluation.
        :return: Score numérique du plateau.
        """
        winner = self.check_winner()
        if winner == "J":
            return 1000
        elif winner == "R":
            return -1000
        else:
            score = 0

            # Priorité des colonnes centrales
            center_array = [self.board[i][self.cols // 2] for i in range(self.rows)]
            center_count = center_array.count("J")
            # Ajustement du score en fonction de la difficulté pour le contrôle du centre
            if difficulty == "easy":
                score += (
                    center_count * 2
                )  # Moins d'importance au centre pour le niveau facile
            elif difficulty == "medium" or difficulty == "difficult":
                score += (
                    center_count * 3
                )  # Importance un peu plus élevée au centre pour le niveau medium et difficult

            # Détection des configurations potentiellement gagnantes pour le joueur J
            for row in range(self.rows):
                for col in range(self.cols - 3):
                    window = [self.board[row][col + i] for i in range(4)]
                    score += self.evaluate_window(window, "J", difficulty)

            for col in range(self.cols):
                for row in range(self.rows - 3):
                    window = [self.board[row + i][col] for i in range(4)]
                    score += self.evaluate_window(window, "J", difficulty)

            for row in range(self.rows - 3):
                for col in range(self.cols - 3):
                    window = [self.board[row + i][col + i] for i in range(4)]
                    score += self.evaluate_window(window, "J", difficulty)

            for row in range(3, self.rows):
                for col in range(self.cols - 3):
                    window = [self.board[row - i][col + i] for i in range(4)]
                    score += self.evaluate_window(window, "J", difficulty)

            # Détection des configurations potentiellement gagnantes pour le joueur R
            for row in range(self.rows):
                for col in range(self.cols - 3):
                    window = [self.board[row][col + i] for i in range(4)]
                    score -= self.evaluate_window(window, "R", difficulty)

            for col in range(self.cols):
                for row in range(self.rows - 3):
                    window = [self.board[row + i][col] for i in range(4)]
                    score -= self.evaluate_window(window, "R", difficulty)

            for row in range(self.rows - 3):
                for col in range(self.cols - 3):
                    window = [self.board[row + i][col + i] for i in range(4)]
                    score -= self.evaluate_window(window, "R", difficulty)

            for row in range(3, self.rows):
                for col in range(self.cols - 3):
                    window = [self.board[row - i][col + i] for i in range(4)]
                    score -= self.evaluate_window(window, "R", difficulty)
            if difficulty == "easy":
                # Pour le niveau facile, on diminue l'impact de l'évaluation par 2
                score /= 2

            return score

    def evaluate_window(self, window, player, difficulty):
        """
        Évalue une fenêtre de 4 cellules pour un joueur spécifique.
        :param window: Liste de 4 cellules à évaluer.
        :param player: Joueur pour lequel évaluer la fenêtre.
        :param difficulty: Difficulté pour ajuster l'évaluation.
        :return: Score de la fenêtre.
        """
        score = 0
        opponent = "J" if player == "R" else "R"

        if window.count(player) == 4:
            score += 100
        elif window.count(player) == 3 and window.count(" ") == 1:
            score += 5
        elif window.count(player) == 2 and window.count(" ") == 2:
            score += 2

        if difficulty == "difficult":
            if window.count(opponent) == 3 and window.count(" ") == 1:
                score -= 4  # En difficulté, on pénalise plus fortement le fait de laisser l'opposant avoir 3 jetons alignés

        return score

    def minimax(self, depth, alpha, beta, maximizingPlayer, difficulty):
        """
        Implémente l'algorithme Minimax avec élagage Alpha-Bêta pour optimiser le choix des mouvements.
        :param depth: Profondeur de recherche actuelle.
        :param alpha: Valeur alpha pour l'élagage.
        :param beta: Valeur beta pour l'élagage.
        :param maximizingPlayer: Booléen pour savoir si c'est le tour du joueur maximisant.
        :param difficulty: Niveau de difficulté pour ajuster les paramètres de recherche.
        :return: Meilleure évaluation pour le joueur actuel.
        """
        state_key = self.serialize_state()
        if state_key in self.transposition_table:
            entry = self.transposition_table[state_key]
            if entry["depth"] >= depth:
                return entry["value"]
        if depth == 0 or self.is_game_over():
            score = self.evaluate_board(difficulty)
            self.transposition_table[state_key] = {"value": score, "depth": depth}
            return score

        if maximizingPlayer:
            maxEval = float("-inf")
            for move in self.generate_possible_moves():
                self.insert_token(move, "J")
                eval = self.minimax(depth - 1, alpha, beta, False, difficulty)
                self.undo_move(move)
                maxEval = max(maxEval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            self.transposition_table[state_key] = {"value": maxEval, "depth": depth}
            return maxEval
        else:
            minEval = float("inf")
            for move in self.generate_possible_moves():
                self.insert_token(move, "R")
                eval = self.minimax(depth - 1, alpha, beta, True, difficulty)
                self.undo_move(move)
                minEval = min(minEval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            self.transposition_table[state_key] = {"value": minEval, "depth": depth}
            return minEval

    def serialize_state(self):
        """
        Sérialise l'état actuel du plateau pour utilisation dans le tableau de transposition.
        :return: Chaîne représentant l'état du plateau.
        """
        return str(self.board)

    def undo_move(self, col):
        """
        Annule le dernier mouvement effectué dans la colonne spécifiée.
        :param col: Index de la colonne où annuler le mouvement.
        """
        for row in range(self.rows):
            if self.board[row][col] != " ":
                self.board[row][col] = " "
                break

    def best_move(self, player):
        """
        Détermine le meilleur mouvement pour le joueur donné en utilisant Minimax.
        :param player: Joueur actuel ('R' ou 'J').
        :return: Index de la meilleure colonne à jouer.
        """
        difficulty = self.difficulty_R if player == "R" else self.difficulty_J
        depth = {"easy": 3, "medium": 4, "difficult": 5}.get(difficulty, 3)
        moves = self.generate_possible_moves()

        random.shuffle(
            moves
        )  # Mélange les mouvements pour ajouter de l'aléatoire et pour éviter un comportement prévisible
        best_score = float("-inf") if player == "J" else float("inf")
        best_col = None
        for col in moves:
            self.insert_token(col, player)
            score = self.minimax(
                depth - 1, float("-inf"), float("inf"), player == "R", difficulty
            )
            self.undo_move(col)
            if (player == "J" and score > best_score) or (
                player == "R" and score < best_score
            ):
                best_score = score
                best_col = col
        return best_col


# --------------------------------PUISSANCE4GUI---------------------------------------


class Puissance4GUI:
    def __init__(self, game):
        """
        Initialise l'interface graphique pour le jeu de Puissance 4.
        :param game: Une instance du jeu Puissance4, contenant la logique du jeu.
        """
        self.game = game
        self.last_opponent_row = None  # Dernière rangée jouée par l'adversaire
        self.last_opponent_col = None  # Dernière colonne jouée par l'adversaire
        self.window = tk.Tk()
        self.window.title("Puissance 4")

        # Création des boutons pour chaque colonne du jeu
        self.buttons = []
        for col in range(self.game.cols):
            btn = tk.Button(
                self.window,
                text=f"Col {col+1}",
                command=lambda c=col: self.play_turn(c),
            )
            btn.grid(row=0, column=col)
            self.buttons.append(btn)

        # Configuration du canvas pour le dessin du plateau de jeu
        self.canvas = tk.Canvas(self.window, width=700, height=600, bg="blue")
        self.canvas.grid(row=1, column=0, columnspan=self.game.cols)

        # Label d'état pour indiquer à quel joueur c'est le tour
        self.status_label = tk.Label(
            self.window, text="Joueur Rouge, c'est votre tour", fg="red"
        )
        self.status_label.grid(row=2, column=0, columnspan=self.game.cols)

        # Labels pour afficher la difficulté des IA
        self.difficulty_label_R = tk.Label(
            self.window,
            text=f"Difficulté IA Rouge: {self.game.difficulty_R}",
            fg="black",
        )
        self.difficulty_label_R.grid(row=3, column=0, columnspan=self.game.cols // 2)

        self.difficulty_label_J = tk.Label(
            self.window,
            text=f"Difficulté IA Jaune: {self.game.difficulty_J}",
            fg="black",
        )
        self.difficulty_label_J.grid(
            row=3, column=self.game.cols // 2, columnspan=self.game.cols // 2
        )

        self.draw_board()

    def play_turn(self, col):
        """
        Gère un tour de jeu en insérant un jeton dans la colonne sélectionnée et vérifie l'état du jeu.
        :param col: Index de la colonne où insérer le jeton.
        """
        if self.game.turn == "R" and self.game.insert_token(col, "R"):
            self.game.turn = "J"
            self.draw_board()
            winner = self.game.check_winner()
            if winner:
                self.end_game(winner)
                return
            self.ai_move()

    def ia_vs_ia_move(self):
        """
        Effectue les mouvements pour un jeu entièrement géré par l'IA, alternant entre les deux joueurs IA.
        """
        while not self.game.is_game_over():

            col = self.game.best_move(self.game.turn)

            if col is not None:
                self.game.insert_token(col, self.game.turn)
                self.last_opponent_col = col
                self.game.turn = "R" if self.game.turn == "J" else "J"
                self.draw_board()

                winner = self.game.check_winner()
                if winner:
                    self.end_game(winner)
                    break
                elif self.game.is_game_over():
                    self.status_label.config(text="Match nul !", fg="black")
                    break

                self.window.update()
                self.window.after(500)  # Délai pour observer le jeu

    def ai_move(self):
        """
        Exécute le mouvement de l'IA Jaune et met à jour l'interface.
        """
        col = self.game.best_move("J")
        if col is not None:
            self.game.insert_token(col, "J")
            self.last_opponent_col = col
            self.game.turn = "R"
            self.draw_board()
            winner = self.game.check_winner()
            if winner:
                self.end_game(winner)
            else:
                self.update_status()

    def draw_board(self):
        """
        Dessine le plateau de jeu actuel sur le canvas.
        """
        self.canvas.delete("all")
        for row in range(self.game.rows):
            for col in range(self.game.cols):
                x0 = col * 100 + 10
                y0 = row * 100 + 10
                x1 = x0 + 80
                y1 = y0 + 80
                color = "white"
                if self.game.board[row][col] == "R":
                    color = "red"
                elif self.game.board[row][col] == "J":
                    color = "yellow"
                self.canvas.create_oval(x0, y0, x1, y1, fill=color, outline="black")

        # Dessiner un cercle plus grand autour de la dernière position jouée par l'adversaire en rose
        if self.last_opponent_col is not None:
            row = 0
            while (
                row < self.game.rows
                and self.game.board[row][self.last_opponent_col] == " "
            ):
                row += 1
            if row < self.game.rows:
                self.last_opponent_row = row
                last_x0 = self.last_opponent_col * 100 + 10
                last_y0 = row * 100 + 10
                last_x1 = last_x0 + 80
                last_y1 = last_y0 + 80
                self.canvas.create_oval(
                    last_x0, last_y0, last_x1, last_y1, fill="", outline="pink", width=3
                )

    def update_status(self):
        """
        Met à jour le label d'état pour indiquer le tour actuel.
        """
        self.status_label.config(text="Joueur Rouge, c'est votre tour", fg="red")

    def end_game(self, winner):
        """
        Termine le jeu en affichant le gagnant et désactive les boutons.
        :param winner: Le joueur gagnant ('R' ou 'J').
        """
        color = "Red" if winner == "R" else "Yellow"
        self.status_label.config(text=f"Le joueur {color} a gagné !", fg="green")
        for btn in self.buttons:
            btn.config(state=tk.DISABLED)

    def start(self):
        """
        Lance l'interface graphique principale.
        """
        self.window.mainloop()


class MenuPrincipal:
    def __init__(self, root):
        """
        Initialise le menu principal pour la sélection du type de jeu et la difficulté de l'IA.
        :param root: L'élément racine de Tkinter où ce menu sera attaché.
        """
        self.root = root
        self.root.title("Menu Principal Puissance 4")

        # Création d'un cadre pour contenir les boutons du menu principal

        self.frame = tk.Frame(self.root)
        self.frame.pack(padx=10, pady=10)

        # Bouton pour démarrer un jeu Joueur vs IA
        self.btn_joueur_vs_ia = tk.Button(
            self.frame,
            text="Joueur vs IA",
            command=self.selection_difficulte_joueur_vs_ia,
            height=2,
            width=20,
        )
        self.btn_joueur_vs_ia.pack(pady=10)

        # Bouton pour démarrer un jeu Joueur vs IA
        self.btn_ia_vs_ia = tk.Button(
            self.frame,
            text="IA vs IA",
            command=self.selection_difficulte_ia_vs_ia,
            height=2,
            width=20,
        )
        self.btn_ia_vs_ia.pack(pady=10)

    def selection_difficulte_joueur_vs_ia(self):
        """
        Détruit le menu principal et affiche les options pour sélectionner la difficulté de l'IA dans un jeu Joueur vs IA.
        """
        self.frame.destroy()  # Ferme le menu principal

        # Création d'un nouveau cadre pour la sélection de la difficulté

        frame_selection = tk.Frame(self.root)
        frame_selection.pack(padx=10, pady=10)

        tk.Label(frame_selection, text="Choisissez la difficulté pour l'IA:").pack()
        var_difficulty_IA = tk.StringVar(value="medium")
        for difficulty in ["easy", "medium", "difficult"]:
            tk.Radiobutton(
                frame_selection,
                text=difficulty,
                variable=var_difficulty_IA,
                value=difficulty,
            ).pack()

        # Bouton pour démarrer le jeu après sélection de la difficulté
        tk.Button(
            frame_selection,
            text="Commencer Joueur vs IA",
            command=lambda: self.lancer_jeu_joueur_vs_ia(var_difficulty_IA.get()),
        ).pack(pady=20)

    def selection_difficulte_ia_vs_ia(self):
        """
        Détruit le menu principal et affiche les options pour sélectionner la difficulté des deux IA dans un jeu IA vs IA.
        """
        self.frame.destroy()  # Ferme le menu principal

        # Création d'un nouveau cadre pour la sélection des difficultés
        frame_selection = tk.Frame(self.root)
        frame_selection.pack(padx=10, pady=10)

        # Sélection pour l'IA Rouge
        tk.Label(frame_selection, text="Difficulté pour IA Rouge:").pack()
        var_difficulty_R = tk.StringVar(value="medium")
        for difficulty in ["easy", "medium", "difficult"]:
            tk.Radiobutton(
                frame_selection,
                text=difficulty,
                variable=var_difficulty_R,
                value=difficulty,
            ).pack()

        # Sélection pour l'IA Jaune
        tk.Label(frame_selection, text="Difficulté pour IA Jaune:").pack()
        var_difficulty_J = tk.StringVar(value="medium")
        for difficulty in ["easy", "medium", "difficult"]:
            tk.Radiobutton(
                frame_selection,
                text=difficulty,
                variable=var_difficulty_J,
                value=difficulty,
            ).pack()

        # Bouton pour démarrer le jeu IA vs IA
        tk.Button(
            frame_selection,
            text="Commencer IA vs IA",
            command=lambda: self.lancer_jeu_ia_vs_ia(
                var_difficulty_R.get(), var_difficulty_J.get()
            ),
        ).pack(pady=20)

    def lancer_jeu_joueur_vs_ia(self, difficulty_IA):
        """
        Lance un jeu de Puissance 4 en mode Joueur vs IA avec la difficulté spécifiée.
        :param difficulty_IA: La difficulté de l'IA choisie.
        """
        jeu = Puissance4(difficulty_R="default", difficulty_J=difficulty_IA)
        gui = Puissance4GUI(jeu)
        gui.start()

    def lancer_jeu_ia_vs_ia(self, difficulty_R, difficulty_J):
        """
        Lance un jeu de Puissance 4 en mode IA vs IA avec les difficultés spécifiées pour chaque IA.
        :param difficulty_R: Difficulté de l'IA Rouge.
        :param difficulty_J: Difficulté de l'IA Jaune.
        """
        jeu = Puissance4(difficulty_R=difficulty_R, difficulty_J=difficulty_J)
        gui = Puissance4GUI(jeu)
        gui.ia_vs_ia_move()


# Pour lancer le Menu Principal avec la possibilité de jouer contre l'IA et de faire des IA vs IA, tout en choisissant le niveau de difficulté des IA.
if __name__ == "__main__":
    root = tk.Tk()
    app = MenuPrincipal(root)
    root.mainloop()


"""
# Pour lancer le tournoi
if __name__ == "__main__":
    game = Puissance4()
    tournament_results = game.tournament()
    print(tournament_results)
"""

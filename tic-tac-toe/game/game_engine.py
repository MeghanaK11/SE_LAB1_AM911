"""
GameEngine: owns the board, turn state, round-end logic and the scoreboard.

You (the player) always play X and click to move. The computer always
plays O and moves automatically right after you, using a simple
random-move AI (see game/ai.py) - this is given infrastructure, not
something you need to build.

State is split into two levels:
  - round state (board, turn, winner): cleared by reset_round()
  - match state (scoreboard): survives reset_round(), cleared only by reset_match()

Controls:
  R      restart the current round (scoreboard kept)
  M      reset the whole match (scoreboard cleared)
  X / O  choose which symbol starts; takes effect on the next round
"""

import pygame

from game.rules import check_winner, is_board_full
from game.renderer import board_pos_to_cell
from game.ai import choose_move

HUMAN_SYMBOL = 'X'
COMPUTER_SYMBOL = 'O'


class GameEngine:
    def __init__(self):
        self.scores = {'X': 0, 'O': 0, 'draw': 0}
        self.next_starter = 'X'   # who starts the NEXT round; changing it never alters the round in progress
        self.reset_round()

    def reset_round(self):
        """Start a new round with the chosen first player. The scoreboard is left untouched."""
        self.board = [[None] * 3 for _ in range(3)]
        self.current_player = self.next_starter
        self.round_over = False
        self.winner = None   # 'X', 'O', or None (meaning draw, only valid when round_over)
        self._maybe_take_computer_turn()   # if O starts, the computer opens the round immediately

    def reset_match(self):
        """Clear the scoreboard and start a fresh round."""
        self.scores = {'X': 0, 'O': 0, 'draw': 0}
        self.reset_round()

    def handle_click(self, pos):
        if self.round_over:
            return   # round has ended - ignore all board clicks until a new round starts
        if self.current_player != HUMAN_SYMBOL:
            return   # not your turn - the computer is about to move (or already has)
        cell = board_pos_to_cell(pos)
        if cell is None:
            return
        row, col = cell
        if self.board[row][col] is not None:
            return   # occupied cell: reject the click, board and turn stay exactly as they were
        self.board[row][col] = self.current_player
        self.check_round_end()
        self.current_player = 'O' if self.current_player == 'X' else 'X'
        self._maybe_take_computer_turn()

    def _maybe_take_computer_turn(self):
        if self.round_over or self.current_player != COMPUTER_SYMBOL:
            return
        move = choose_move(self.board)
        if move is None:
            return
        row, col = move
        self.board[row][col] = self.current_player
        self.check_round_end()
        self.current_player = 'O' if self.current_player == 'X' else 'X'

    def handle_keydown(self, key):
        if key == pygame.K_r:
            self.reset_round()
        elif key == pygame.K_m:
            self.reset_match()
        elif key == pygame.K_x:
            self.next_starter = 'X'
        elif key == pygame.K_o:
            self.next_starter = 'O'

    def check_round_end(self):
        if self.round_over:
            return   # result already recorded for this round - never count it twice
        # A win must be checked first: a move can complete a line AND fill the
        # last empty cell, and that is a win, not a draw.
        winner = check_winner(self.board)
        if winner:
            self.round_over = True
            self.winner = winner
            self.scores[winner] += 1
            return
        if is_board_full(self.board):
            self.round_over = True
            self.winner = None
            self.scores['draw'] += 1

    def draw(self, surface, font):
        from game import renderer
        renderer.draw_board(surface, self.board)
        if self.round_over:
            turn_label = "Round over"
        else:
            turn_label = "Your turn (X)" if self.current_player == HUMAN_SYMBOL else "Computer's turn (O)"
        renderer.draw_text(surface, font, turn_label, (10, 20))

        score_label = f"Score  X: {self.scores['X']}  O: {self.scores['O']}  Draw: {self.scores['draw']}"
        renderer.draw_text(surface, font, score_label, (10, 55))

        if self.round_over:
            text = f"{self.winner} wins!" if self.winner else "Draw!"
            renderer.draw_banner(surface, font, text)

        renderer.draw_controls(surface, [
            f"Next starter: {self.next_starter}  (X / O to change)",
            "R: restart round (keeps score)",
            "M: reset match (clears score)",
        ])
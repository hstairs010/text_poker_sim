import random

# -----------------------
# Card object
# -----------------------
class Card:
    def __init__(self, suit: str, value: str):
        self.suit = suit
        self.value = value

    def __str__(self):
        return f"{self.value} of {self.suit}"


# -----------------------
# Deck object
# -----------------------
class Deck:
    def __init__(self):
        self.cards = []
        self.create_deck()

    def create_deck(self):
        suits = ["Hearts", "Diamonds", "Spades", "Clubs"]
        values = [2, 3, 4, 5, 6, 7, 8, 9, 10, "Jack", "Queen", "King", "Ace"]
        self.cards = [Card(suit, value) for suit in suits for value in values]
        random.shuffle(self.cards)

    def deal_card(self):
        return self.cards.pop()

    def deal_hand(self, num_cards: int):
        return [self.deal_card() for _ in range(num_cards)]


# -----------------------
# Player object
# -----------------------
class Player:
    def __init__(self, name: str, chips: int = 100):
        self.name = name
        self.chips = chips
        self.hand = []
        self.current_bet = 0
        self.folded = False

    def receive_hand(self, cards: list):
        self.hand = cards

    def fold(self):
        self.folded = True

    def call(self, table):
        diff = table.current_highest_bet - self.current_bet
        if diff > self.chips:
            print(f"{self.name} doesn't have enough chips to call.")
            return False
        self.chips -= diff
        self.current_bet += diff
        table.pot += diff
        print(f"{self.name} calls. Chips left: {self.chips}")
        return True

    def raise_bet(self, table, raise_amount):
        total_bet = table.current_highest_bet - self.current_bet + raise_amount
        if total_bet > self.chips:
            print(f"{self.name} doesn't have enough chips to raise that much.")
            return False
        self.chips -= total_bet
        self.current_bet += total_bet
        table.pot += total_bet
        table.current_highest_bet = self.current_bet
        print(f"{self.name} raises by {raise_amount}. Chips left: {self.chips}")
        return True

    def score_hand(self, community_cards, player_cards):
        # Assign each card a numeric value
        value_order = {
            2: 2, 3: 3, 4: 4, 5: 5, 6: 6,
            7: 7, 8: 8, 9: 9, 10: 10,
            "Jack": 11, "Queen": 12, "King": 13, "Ace": 14
        }

        # Combine community and player cards
        full_hand = community_cards + player_cards
        sorted_hand = sorted(full_hand, key=lambda card: value_order[card.value])

        values = [value_order[card.value] for card in sorted_hand]
        suits = [card.suit for card in sorted_hand]

        # Flags for hand types
        is_straight = False
        is_flush = False
        straight_flush = False
        royal_flush = False
        trips = False
        quads = False
        one_pair = False
        two_pair = False
        full_house = False

        # -------------------------------
        # STRAIGHT CHECK
        unique_values = sorted(set(values))
        for i in range(len(unique_values) - 4):
            if unique_values[i:i + 5] == list(range(unique_values[i], unique_values[i] + 5)):
                is_straight = True
                straight_cards = unique_values[i:i + 5]
                break
        else:
            straight_cards = []

        # -------------------------------
        # FLUSH CHECK
        flush_suit = None
        for suit in set(suits):
            if suits.count(suit) >= 5:
                is_flush = True
                flush_suit = suit
                break

        # -------------------------------
        # STRAIGHT FLUSH + ROYAL FLUSH CHECK
        if is_flush and is_straight:
            flush_cards = [card for card in sorted_hand if card.suit == flush_suit]
            flush_values = sorted(set([value_order[card.value] for card in flush_cards]))
            for i in range(len(flush_values) - 4):
                if flush_values[i:i + 5] == list(range(flush_values[i], flush_values[i] + 5)):
                    straight_flush = True
                    straight_cards = flush_values[i:i + 5]
                    if straight_cards[-1] == 14 and straight_cards[0] == 10:
                        royal_flush = True
                    break

        # -------------------------------
        # PAIRS, TRIPS, QUADS, FULL HOUSE
        value_counts = {v: values.count(v) for v in set(values)}
        pair_count = list(value_counts.values()).count(2)
        trips = 3 in value_counts.values()
        quads = 4 in value_counts.values()

        if pair_count == 1:
            one_pair = True
        elif pair_count >= 2:
            two_pair = True

        if trips and pair_count >= 1:
            full_house = True

        # -------------------------------
        # Assign numeric score (higher = stronger)
        if royal_flush:
            return 10
        elif straight_flush:
            return 9
        elif quads:
            return 8
        elif full_house:
            return 7
        elif is_flush:
            return 6
        elif is_straight:
            return 5
        elif trips:
            return 4
        elif two_pair:
            return 3
        elif one_pair:
            return 2
        else:
            return 1

# -----------------------
# Table object
# -----------------------
class Table:
    def __init__(self, players: list):
        self.players = players
        self.deck = Deck()
        self.pot = 0
        self.community_cards = []
        self.current_highest_bet = 0

    def reset_round(self):
        self.deck = Deck()  # new shuffled deck
        self.community_cards = []
        self.pot = 0
        self.current_highest_bet = 0
        for player in self.players:
            player.hand = []
            player.folded = False
            player.current_bet = 0

    def deal_hole_cards(self):
        for player in self.players:
            player.receive_hand(self.deck.deal_hand(2))

    def deal_flop(self):
        self.community_cards += [self.deck.deal_card() for _ in range(3)]

    def deal_turn(self):
        self.community_cards.append(self.deck.deal_card())

    def deal_river(self):
        self.community_cards.append(self.deck.deal_card())

    def betting_round(self):
        # iterate through players, skipping folded ones
        for player in self.players:
            if player.folded:
                continue

            print(f"\n--- {player.name}'s Turn ---")
            print(f"Current highest bet: {self.current_highest_bet}")
            print(f"Your chips: {player.chips}")
            print(f"Your hand: {[str(c) for c in player.hand]}")
            while True:
                decision = input("Would you like to Call, Fold, or Raise? ").strip().lower()

                if decision == "call":
                    if not player.call(self):
                        continue
                    break
                elif decision == "fold":
                    player.fold()
                    print(f"{player.name} folds.")
                    break
                elif decision == "raise":
                    try:
                        raise_amount = int(input("How much would you like to raise by? "))
                    except ValueError:
                        print("Enter a valid number.")
                        continue

                    if raise_amount <= 0:
                        print("Raise must be more than 0.")
                        continue
                    if not player.raise_bet(self, raise_amount):
                        continue
                    break
                else:
                    print("Invalid choice. Please type Call, Fold, or Raise.")
    
    def check_for_early_winner(self):
        active_players = [p for p in self.players if not p.folded]
        if len(active_players) == 1:
            winner = active_players[0]
            print(f"\nEveryone else folded! {winner.name} wins {self.pot} chips!")
            winner.chips += self.pot
            return True
        return False
    
    
def showdown(players, table):
    # players = list of Player objects
    showdown_members = []

    # Find everyone who hasn't folded
    for player in players:
        if not player.folded:
            showdown_members.append(player)

    # Now calculate each remaining player's score
    for player in showdown_members:
        player.score = player.score_hand(table.community_cards, player.hand)
    winner = max(showdown_members, key=lambda p: p.score)
    print(f"The winner is {winner.name}!")
    winner.chips += table.pot

# -----------------------
# Game Loop
# -----------------------
def main_loop():
    players = [Player("Player 1"), Player("Player 2"), Player("Player 3")]
    table = Table(players)

    table.reset_round()
    table.deal_hole_cards()

    print("\n--- Hole Cards ---")
    for player in players:
        print(f"{player.name}: {[str(card) for card in player.hand]}")
    table.betting_round()
    table.check_for_early_winner

    table.deal_flop()
    print("\nFlop:", [str(c) for c in table.community_cards])
    table.betting_round()
    table.check_for_early_winner

    table.deal_turn()
    print("Turn:", [str(c) for c in table.community_cards])
    table.betting_round()
    table.check_for_early_winner

    table.deal_river()
    print("River:", [str(c) for c in table.community_cards])
    table.betting_round()
    table.check_for_early_winner
    showdown(players, table)

# -----------------------
# Hand Scoring Function
# -----------------------


main_loop()
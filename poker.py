import random
import os

class Card:
    def __init__(self, suit, value):
        self.suit = suit
        self.value = value

    def __str__(self):
        return f"{self.value} of {self.suit}"

    def __repr__(self):
        return self.__str__()

class Player:
    def __init__(self, name, chips=100):
        self.name = name
        self.hand = []
        self.chips = chips
        self.folded = False
        self.current_bet = 0

    def receive_hand(self, cards):
        self.hand = cards

    def show_hand(self):
        print(f"{self.name}'s hand:")
        for card in self.hand:
            print(card)
        print()

#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Global Game Variables

Deck = []
pot = 0
current_bet = 0
community_cards = []
Total_Bet = 0

you = None
Jeff = None
Von = None

#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Deck Creation

def create_NewDeck():
    global Deck
    suits = ["Hearts", "Diamonds", "Spades", "Clubs"]
    values = [2, 3, 4, 5, 6, 7, 8, 9, 10, "Jack", "Queen", "King", "Ace"]
    Deck = [Card(suit, value) for suit in suits for value in values]
    random.shuffle(Deck)

#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Deal a hand of two cards

def deal_hand():
    return [Deck.pop(), Deck.pop()]

#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Deal all players their hands

def MasterDeal():
    global you, Jeff, Von
    you = Player("You")
    Jeff = Player("Jeff")
    Von = Player("Von")

    you.receive_hand(deal_hand())
    Jeff.receive_hand(deal_hand())
    Von.receive_hand(deal_hand())

#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Community Cards: Flop, Turn, River

def Deal_Flop():
    global community_cards
    for _ in range(3):
        community_cards.append(Deck.pop())

def Deal_Turn():
    global community_cards
    community_cards.append(Deck.pop())

def Deal_River():
    global community_cards
    community_cards.append(Deck.pop())

def Show_Community_Cards():
    print("Community cards:")
    for card in community_cards:
        print(card)
    print()

#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Betting round 

def Betting_Round():
    if you.folded:
        print("")
    else:
        global current_bet, pot, Total_Bet

        print(f"\nPot: {pot}")
        print(f"Jeff's current bet: {Jeff.current_bet}")
        print(f"Von's current bet: {Von.current_bet}")
        print(f"Your current bet: {you.current_bet}")
        print(f"Your chips: {you.chips}\n")

        playerFold = input("Would you like to fold? (Y/N): ").upper()
        if playerFold == "Y":
            you.folded = True
            return

        while True:
            try:
                current_rounds_bet = int(input("How much more would you like to bet this round? "))
                if current_rounds_bet < 0 or current_rounds_bet > you.chips:
                    raise ValueError
                break
            except ValueError:
                print("Invalid bet. Try again.")

        bet_increase = current_rounds_bet
        you.current_bet += bet_increase
        you.chips -= bet_increase
        pot += bet_increase
        Total_Bet += bet_increase

        current_bet = max(current_bet, you.current_bet)


#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Score Cards

value_order = {
    2: 2, 3: 3, 4: 4, 5: 5, 6: 6,
    7: 7, 8: 8, 9: 9, 10: 10,
    "Jack": 11, "Queen": 12, "King": 13, "Ace": 14
}

def Score_Cards(community_cards, cards):
    Full_Hand = cards + community_cards
    sorted_hand = sorted(Full_Hand, key=lambda card: value_order[card.value])

    values = [value_order[card.value] for card in sorted_hand]
    suits = [card.suit for card in sorted_hand]

    hand_strength = 0
    straight_cards = []
    trips = False
    quads = False
    OnePair = False
    TwoPair = False
    Full_House = False
    royal_flush = False
    straight_flush = False
    is_flush = False
    is_straight = False

    # -------------------------------
    # STRAIGHT CHECK
    unique_values = sorted(set(values))
    for i in range(len(unique_values) - 4):
        if unique_values[i:i+5] == list(range(unique_values[i], unique_values[i]+5)):
            straight_cards = unique_values[i:i+5]
            is_straight = True
            break

    # -------------------------------
    # FLUSH CHECK
    for suit in set(suits):
        if suits.count(suit) >= 5:
            is_flush = True
            flush_suit = suit
            break

    # -------------------------------
    # STRAIGHT FLUSH CHECK
    if is_flush and is_straight:
        straight_flush = True
        # Check if all straight cards are in the same suit
        flush_cards = [card for card in sorted_hand if card.suit == flush_suit]
        flush_values = sorted(set([value_order[card.value] for card in flush_cards]))
        for i in range(len(flush_values) - 4):
            if flush_values[i:i+5] == list(range(flush_values[i], flush_values[i]+5)):
                straight_flush = True
                straight_cards = flush_values[i:i+5]
                break

    # -------------------------------
    # ROYAL FLUSH CHECK
    if straight_flush and straight_cards[0] == 10:
        royal_flush = True

    # -------------------------------
    # PAIRS, TRIPS, QUADS
    value_counts = {v: values.count(v) for v in set(values)}

    pair_count = 0
    trips = False
    quads = False

    for count in value_counts.values():
        if count == 2:
            pair_count += 1
        elif count == 3:
            trips = True
        elif count == 4:
            quads = True

    if pair_count == 1:
        OnePair = True
    elif pair_count >= 2:
        TwoPair = True

    # -------------------------------
    # FULL HOUSE
    if trips and pair_count >= 1:
        Full_House = True
    if royal_flush:
        HandValue = 10
        return HandValue
    elif straight_flush:
        HandValue = 9
        return HandValue
    elif quads:
        HandValue = 8
        return HandValue
    elif Full_House:
        HandValue = 7
        return HandValue
    elif is_flush:
        HandValue = 6
        return HandValue
    elif is_straight:
        HandValue = 5
        return HandValue
    elif trips:
        HandValue = 4
        return HandValue
    elif TwoPair:
        HandValue = 3
        return HandValue
    elif OnePair:
        HandValue = 2
        return HandValue
    else:
        HandValue = 1
        return HandValue

#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Bot logic

#jeff is a passive player
#all things to think about: Player bet, Hand score, bluffs
def JeffThinking():
    JeffScore = Score_Cards(community_cards, Jeff.hand)
    player_threat_level = you.current_bet / 25
    bluff = random.random() < 0.1  # 10% chance to bluff
    JeffBet = 0

    if JeffScore >= 7:
        JeffBet = random.randint(you.current_bet, you.current_bet + 100)
    elif JeffScore >= 5:
        if player_threat_level < 5:
            JeffBet = random.randint(you.current_bet, you.current_bet + 25)
        else:
            risk_tolerance = random.randint(-10, 10)
            if you.current_bet - risk_tolerance > 0:
                JeffBet = 0 if not bluff else random.randint(you.current_bet, you.current_bet + 10)
            else:
                JeffBet = random.randint(1, 10)
    elif JeffScore >= 3:
        risk_tolerance = random.randint(-10, 10)
        if you.current_bet - risk_tolerance > 0:
            JeffBet = 0 if not bluff else random.randint(you.current_bet, you.current_bet + 15)
        else:
            JeffBet = random.randint(1, 7)
    else:
        risk_tolerance = random.randint(-15, 5)  # More likely to fold with very weak hand
        if you.current_bet - risk_tolerance > 0:
            JeffBet = 0 if not bluff else random.randint(you.current_bet, you.current_bet + 15)
        else:
            JeffBet = random.randint(1, 5)

    Jeff.chips -= JeffBet
    Jeff.current_bet = JeffBet
    return JeffBet



def VonThinking():
    VonScore = Score_Cards(community_cards, Von.hand)
    player_threat_level = you.current_bet / 25
    bluff = random.random() < 0.3  # 30% chance to bluff
    VonBet = 0

    if VonScore >= 7:  # Strong hand
        VonBet = random.randint(you.current_bet + 20, you.current_bet + 200)
    elif VonScore >= 5:  # Medium hand
        if player_threat_level < 6:
            VonBet = random.randint(you.current_bet + 10, you.current_bet + 75)
        else:
            risk_tolerance = random.randint(-5, 15)  # More likely to push through
            if you.current_bet - risk_tolerance > 0:
                VonBet = 0 if not bluff else random.randint(you.current_bet + 10, you.current_bet + 40)
            else:
                VonBet = random.randint(10, 25)
    elif VonScore >= 3:  # Weak-ish hand (pair or trips)
        risk_tolerance = random.randint(0, 20)  # Likely to keep playing
        if you.current_bet - risk_tolerance > 0:
            VonBet = 0 if not bluff else random.randint(you.current_bet + 10, you.current_bet + 30)
        else:
            VonBet = random.randint(5, 15)
    else:  # Very weak hand
        risk_tolerance = random.randint(-5, 15)  # Still more likely to take a chance
        if you.current_bet - risk_tolerance > 0:
            VonBet = 0 if not bluff else random.randint(you.current_bet, you.current_bet + 30)
        else:
            VonBet = random.randint(1, 12)

    Von.chips -= VonBet
    Von.current_bet = VonBet
    return VonBet



#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Main Game Loop 

def Main_Game_Loop():
    global pot, current_bet, Total_Bet
    
    while True:
        # Setup round
        create_NewDeck()
        MasterDeal()
        community_cards.clear()
        pot = 0
        current_bet = 0
        Total_Bet = 0
        
        # Pre-Flop
        os.system("cls" if os.name == "nt" else "clear")
        you.show_hand()
        Betting_Round()
        JeffThinking()
        VonThinking()
        pot += Jeff.current_bet + Von.current_bet
        print(f"Pot after pre-flop: {pot}\n")

        # Flop
        os.system("cls" if os.name == "nt" else "clear")
        Deal_Flop()
        Show_Community_Cards()
        Betting_Round()
        JeffThinking()
        VonThinking()
        pot += current_bet + Jeff.current_bet + Von.current_bet
        print(f"Pot after flop: {pot}\n")

        # Turn
        os.system("cls" if os.name == "nt" else "clear")
        Deal_Turn()
        Show_Community_Cards()
        Betting_Round()
        JeffThinking()
        VonThinking()
        pot += current_bet + Jeff.current_bet + Von.current_bet
        print(f"Pot after turn: {pot}\n")

        # River
        Deal_River()
        os.system("cls" if os.name == "nt" else "clear")
        Show_Community_Cards()
        Betting_Round()
        JeffThinking()
        VonThinking()
        pot += current_bet + Jeff.current_bet + Von.current_bet
        print(f"Pot after river: {pot}\n")

        # Showdown
        os.system("cls" if os.name == "nt" else "clear")
        you.show_hand()
        Jeff.show_hand()
        Von.show_hand()

        # Score and determine winner
        scores = {
            "You": Score_Cards(community_cards, you.hand),
            "Jeff": Score_Cards(community_cards, Jeff.hand),
            "Von": Score_Cards(community_cards, Von.hand)
        }

        winner = max(scores, key=scores.get)
        print(f"Winner is {winner} with a score of {scores[winner]}")

        # Give pot to winner
        if winner == "You":
            you.chips += pot
        elif winner == "Jeff":
            Jeff.chips += pot
        else:
            Von.chips += pot

        print(f"Chips -- You: {you.chips}, Jeff: {Jeff.chips}, Von: {Von.chips}\n")

        # Ask for another round
        if input("Play another round? (y/n): ").lower() != 'y':
            break


#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Run Game

Main_Game_Loop()

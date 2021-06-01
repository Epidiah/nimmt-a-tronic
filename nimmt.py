# A 6 Nimmt Simulator for testing out weird beef-strategies

from random import shuffle


def construct_deck():
    """
    Assembles the cards because I'm not paid enough for data entry.
    """
    deck = []
    for number in range(1, 105):
        card = {"number": number}
        if number % 11:
            if number % 5 == 0:
                if number % 10 == 0:
                    card["heads"] = 3
                else:
                    card["heads"] = 2
            else:
                card["heads"] = 1
        else:
            if number % 5 == 0:
                card["heads"] = 7
            else:
                card["heads"] = 5
        card["name"] = english_name(card)
        card["nickname"] = nickname(card)
        deck.append(card)
    return deck


def english_name(card):
    """
    Given a card, returns the number of the card written out in English
    """
    ones = [
        "",
        "one",
        "two",
        "three",
        "four",
        "five",
        "six",
        "seven",
        "eight",
        "nine",
        # Extended to 19 so that I don't have to write logic around those names
        "ten",
        "eleven",
        "twelve",
        "thirteen",
        "fourteen",
        "fifteen",
        "sixteen",
        "seventeen",
        "eighteen",
        "nineteen",
    ]
    tens = [
        "",
        "",
        "twenty",
        "thirty",
        "fourty",
        "fifty",
        "sixty",
        "seventy",
        "eighty",
        "ninety",
        "one hundred",
    ]
    if card["number"] <= 19:
        name = ones[card["number"]]
    else:
        if card["number"] % 10 and card["number"] < 100:
            divider = "-"
        else:
            divider = " "
        name = tens[card["number"] // 10] + divider + ones[card["number"] % 10]
    return name.rstrip()


def nickname(card):
    """
    Given a card, returns our weird nickname for it.
    """
    if card["number"] % 11:
        return card["name"]
    else:
        return [
            "unsy-uns",
            "deuxsy-deux",
            "toisy-tois",
            "quatrosy-quatre",
            "cinqy-cinq",
            "seezy-seeze",
            "septy-sept",
            "huity-huit",
            "neufy-neuf",
        ][card["number"] % 11]


class game:
    def __init__(self, *players):
        if not (2 <= len(players) <= 10):
            raise ValueError("Only works with 2 to 10 players.")
        self.players = players
        self.reset()

    def reset(self):
        for player in self.players:
            player.score = 66
        self.table = [[], [], [], []]

    def deal(self):
        self.deck = construct_deck()
        shuffle(self.deck)
        for player in self.players:
            player.hand = []
            for n in range(10):
                player.hand.append(self.deck.pop())
        for n in range(4):
            self.table[n].clear()
            self.table[n].append(self.deck.pop())
        self.high_cards = [row[-1]["number"] for row in self.table]

    def score_row(self, row):
        return sum([card["heads"] for card in self.table[row]])

    def place_card(self, card, player):
        if card["number"] < min(self.high_cards):
            row = player.row_strategy(player, self)
            player.score -= self.score_row(row)
            self.table[row].clear()
            self.table[row].append(card)
        else:
            distances = [card["number"] - hc for hc in self.high_cards]
            closest = distances.index(min(distances))
            if len(self.table[closest]) >= 5:
                player.score -= self.score_row(closest)
                self.table[closest].clear()
            self.table[closest].append(card)
        self.high_cards = [row[-1]["number"] for row in self.table]

    def play_turn(self):
        self.cards_played = sorted([
            (player.card_strategy(player, self), player) for player in self.players
        ], key=lambda x: x[0]['number'], reverse=True)
        while self.cards_played:
            card, player = self.cards_played.pop()
            self.place_card(card, player)
            player.hand.pop(player.hand.index(card))

    def play(self):
        hands = 0
        while min([player.score for player in self.players]) > 0:
            hands += 1
            self.deal()
            for n in range(10):
                self.play_turn()
            print(
                f"{hands}: {[(player.name, player.score) for player in self.players]}"
            )
        return hands, sorted([(player.name, player.score) for player in self.players],
            key=lambda x: x[1], reverse=True
        )


class player:
    def __init__(self, name, card_strategy, row_strategy):
        self.name = name
        self.card_strategy = card_strategy
        self.row_strategy = row_strategy

    def choose_card(self, game):
        return self.card_trategy(game)

    def choose_row(self, game):
        return self.card_trategy(game)

    def __str__(self):
        return self.name


def basic_card_strategy(player, game):
    hand = sorted(player.hand, key=lambda c: c["number"], reverse=True)
    # First check for a safe play and play the highest safe play.
    slots = [5 - len(row) for row in game.table]
    for card in hand:
        for row in range(4):
            if (
                game.high_cards[row]
                < card["number"]
                <= game.high_cards[row] + slots[row]
            ):
                return card
    # Then check for least risky brisket and play highest of those
    play = None
    risk = 1
    for card in hand:
        for row in range(4):
            if (card["number"] - (game.high_cards[row] + 2 * slots[row])) < risk:
                risk = card["number"] - (game.high_cards[row] + 2 * slots[row])
                play = card
        if play:
            return play
    # Finally, plays lowest card
    return hand[-1]


def basic_row_strategy(player, game):
    chosen_row = 5
    damage = 28
    for row in range(len(game.table)):
        row_total = sum([card["heads"] for card in game.table[row]])
        if row_total < damage:
            damage = row_total
            chosen_row = row
    return chosen_row


# Testing
a = player("a", basic_card_strategy, basic_row_strategy)
b = player("b", basic_card_strategy, basic_row_strategy)
c = player("c", basic_card_strategy, basic_row_strategy)
d = player("d", basic_card_strategy, basic_row_strategy)

g = game(a, b, c, d)

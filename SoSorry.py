import random

class SoSorry:

    def __init__(self,
        players,
        player_name = 'player1',
        player_position = 0,
        verbose=False,
        learner = None
    ):
        self.number_of_players = players
        self.player_name = player_name
        self.curr_dealer = 0
        self.curr_player = player_position
        self.players = [f"Player {i}" for i in range(self.number_of_players)]
        self.player_cards = [0 for _ in range(self.number_of_players)]
        self.deck = [i for i in range(1, 14) for _ in range(4)]
        self.verbose = verbose
        self.traded = False
        self.learner = learner
        self.first_turn = True

        self.hand_trades = 0



    def game(self):
        print("Welcome to So Sorry!")
        print("The rules are simple:")
        print("1. Each player is dealt a card")
        print("2. The dealer will ask each player if they want to trade their card with the player to their left")
        print("3. The dealer can draw a card")
        print("4. The player with the lowest card is out of the game")
        print("5. The dealer is now the player to the left of the player who was just eliminated")
        print("6. Repeat steps 1-5 until there is only one player left")
        print()
        print("Let's play!")
        print()
        print("You are", self.players[self.curr_player])
        if self.verbose: print('Game start!')

        self.shuffle()

        while len([x for x in self.player_cards if x > -1]) > 1:

            self.deal_hand()
            print("Everyone has been dealt a card:", self.player_cards)

            k = self.curr_dealer + 1
            while True:
                if k == self.number_of_players:
                    k = 0
                    continue
                elif self.player_cards[k] == -1:
                    k+=1
                    continue
                # elif k == self.curr_player:
                #     if self.learner:
                #         self.model_turn()
                #     else:
                #         self.players_turn()
                #     if self.curr_player == self.curr_dealer:
                #         break
                #     k += 1
                #     continue
                elif k == self.curr_dealer:
                    self.should_I_stay_or_should_I_go(k)
                    break
                self.should_I_stay_or_should_I_go(k)
                k += 1

            print("Everyone show their cards:", self.player_cards)

            self.decide_losers()
            # One Tie, All Tie
            if len([x for x in self.player_cards if x > -1]) == 0:
                self.player_cards = [0 for _ in range(self.number_of_players)]

            self.update_dealer()
            if self.verbose: print("Dealer is now", self.players[self.curr_dealer])

            if len(self.deck) < len([x for x in self.player_cards if x > -1]):
                self.shuffle()
            self.hand_trades = 0
            print("------------------------------ NEXT ROUND ------------------------------")

        print(f"Winner is {self.players[self.player_cards.index(max(self.player_cards))]}")

    def decide_losers(self):
        lowest_card = min(num for num in self.player_cards if num != -1)
        losers = [i for i, x in enumerate(self.player_cards) if x == lowest_card]
        for loser in losers:
            if self.verbose: print(self.players[loser], f"had the lowest card [{lowest_card}] and is out of the game")
            self.player_cards[loser] = -1
        return losers

    def update_dealer(self):
        # print(f"Updating dealer -- {self.curr_dealer} - players left: {len([x for x in self.player_cards if x > -1])}")
        self.curr_dealer += 1
        if self.curr_dealer == self.number_of_players:
            self.curr_dealer = 0
        if self.player_cards[self.curr_dealer] == -1:
            self.update_dealer()

    def should_I_stay_or_should_I_go(self, current_player):
        if self.traded == True and self.player_cards[current_player] > self.player_cards[self. get_card_traded_index(current_player)]:
            if self.verbose: print(f"{self.players[current_player]} is staying")
            self.traded = False
        # if random.random() > 0.5:
        if self.player_cards[current_player] < 7:
            self.trade(current_player)
        else:
            if self.verbose: print(f"{self.players[current_player]} is staying")
            self.traded = False

    def player_to_trade_with(self, index):
        if index == self.number_of_players:
            return self.player_to_trade_with(0)
        elif self.player_cards[index] == -1:
            return self.player_to_trade_with(index+1)
        return index

    def trade(self, curr_index):
        if curr_index == self.curr_dealer:
            self.deal(curr_index)
            if self.verbose: print(f"Dealer drew a", self.player_cards[curr_index])
        else:
            player_to_trade_with = self.player_to_trade_with(curr_index+1)
            if self.verbose: print(f"{self.players[curr_index]} is trading with {self.players[player_to_trade_with]}")
            # print(self.player_cards)
            if self.player_cards[player_to_trade_with] == 13:
                if self.verbose: print(f"Next Player has a King! So Sorry")
                self.Traded = False
            else:
                self.player_cards[curr_index], self.player_cards[player_to_trade_with] = self.player_cards[player_to_trade_with], self.player_cards[curr_index]
                self.hand_trades += 1
                self.traded = True
            # print(self.player_cards)


    def players_turn(self):
        print()
        print("Your turn!")
        print(f"Your card is a [{self.print_card(self.curr_player)}]")
        if self.traded: print(f"You were forced to trade a [{self.print_card(self.get_card_traded_index(self.curr_player))}]")
        print("What would you like to do?")
        if self.curr_player == self.curr_dealer: print("1. Draw a card")
        else: print("1. Trade")
        print("2. Stay")
        # print("3. Quit")
        choice = input("Enter your choice: ")
        if choice == "1":
            self.trade(self.curr_player)
            print(f"Your card is now as [{self.print_card(self.curr_player)}]")
        elif choice == "2":
            # self.stay()
            pass
        elif choice == "3":
            # self.quit()
            pass
        else:
            print("Invalid choice. Try again.")
            self.players_turn()
        print()
        print()

    def get_card_traded_index(self, index):
        if index == 0:
            return self.get_card_traded_index(self.number_of_players-1)
        if self.player_cards[index-1] == -1 or self.player_cards[index-1] == 13:
            return self.get_card_traded_index(index-1)
        else:
            return index-1

    def deal_hand(self):
        if self.verbose: print(self.players[self.curr_dealer], "is dealing...")
        self.traded = False

        i = self.curr_dealer + 1
        while i != self.curr_dealer:
            if i == self.number_of_players:
                i = 0
                continue
            if self.player_cards[i] == -1:
                i += 1
                continue
            else:
                self.deal(i)
                i+=1
        self.deal(self.curr_dealer)

    def deal(self, player_index):
        self.player_cards[player_index] = self.deck.pop()
        pass

    def shuffle(self):
        if self.verbose: print("Shuffling deck...")
        new_deck = [i for i in range(1, 14) for _ in range(4)]
        self.deck = random.sample(new_deck, len(new_deck))

    def print_card(self, player_index):
        card_index = self.player_cards[player_index]
        if card_index == 1:
            return "Ace"
        if card_index <= 10:
            return card_index
        if card_index == 11:
            return "Jack"
        if card_index == 12:
            return "Queen"
        if card_index == 13:
            return "King"


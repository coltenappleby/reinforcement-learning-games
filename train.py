import numpy as np
import pandas as pd

import QLearner as ql
import SoSorry as ss

import time

def discretize(curr_card, curr_traded_card, trades_before, players_after):
    """
    convert the situation to a single integer
    """
    # return curr_card * 1000 + curr_traded_card * 100 + trades_before * 10 + players_after * 1
    return curr_card * 1500 + curr_traded_card * 100 + trades_before * 10 + players_after * 1

def train(
        runs = 1,
        games=1,
        load=True,
        save=True,
        model_name = None,
        verbose = False,
        dyna=0
):
    print("training...")
    players = 5
    cards = 13
    traded_cards = cards + 1
    pot_trades_before = players-1
    pot_players_after = players-1
    stopped_trades_before = players%2
    num_states = discretize(cards, traded_cards, pot_trades_before, pot_players_after)

    model = ql.QLearner(num_states=num_states, num_actions=2, dyna=dyna, verbose=verbose, rar=0.8, radr=0.999999999999)
    if load:
        model.load_existing_model(model_name)

    game_outcome = np.zeros(shape=(runs, games))
    wins: int
    reward = 0

    print("------------------ Starting Training ------------------")
    start = time.time()

    for j in range(runs):
        wins = 0
        for i in range(games):
            game = ss.SoSorry(players, learner=None, verbose=verbose)
            points, reward = play_game(game, reward, model, verbose)
            wins += points
            game_outcome[j, i] = points
        print(f"Run {j} Wins: {wins}")

    end = time.time()
    print(runs, "Took", end - start, "seconds")

    if save:
        # save the outcomes to disk
        np.savetxt("models/game_outcomes_first_50.csv", game_outcome, delimiter=",")
        print("Saving model to disk...")
        model.save_to_npy(model_name)

def play_game(game: ss, reward: int, learner, verbose = False):

    if verbose:
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
        print("You are", game.players[game.curr_player])
        print('Game start!')

    game.shuffle()

    # A Full Hand -- Finds a Winner
    while len([x for x in game.player_cards if x > -1]) > 1:

        game.deal_hand()

        if verbose: print("There are", len([x for x in game.player_cards if x > -1]), "players left")

        k = game.curr_dealer + 1
        while True:
            if k == game.number_of_players:
                k = 0
                continue
            elif game.player_cards[k] == -1:
                k += 1
                continue
            elif k == game.curr_player:
                # TRAIN MODEL HERE
                if verbose:
                    print("The model is choosing an action... Current Card is", game.player_cards[game.curr_player])

                action = model_turn(game, reward, learner)
                if action == 0: game.trade(game.curr_player)
                if game.curr_player == game.curr_dealer:
                    break
                k += 1
                continue
            elif k == game.curr_dealer:
                game.should_I_stay_or_should_I_go(k)
                break
            game.should_I_stay_or_should_I_go(k)
            k += 1

        if verbose: print("Everyone show their cards:", game.player_cards)

        losers = game.decide_losers()
        # One Tie, All Tie
        if verbose: print("One Tie, All Tie!")
        if len([x for x in game.player_cards if x > -1]) == 0:
            game.player_cards = [0 for _ in range(game.number_of_players)]

        game.update_dealer()
        if game.curr_player in losers:
            reward = -100
        else:
            players_left = len([x for x in game.player_cards if x > -1])
            if players_left == 1:
                reward = game.number_of_players * 100
            else:
                reward = 25
        if verbose: print("Dealer is now", game.players[game.curr_dealer])

        if len(game.deck) < len([x for x in game.player_cards if x > -1])+2:
            game.shuffle()
        game.hand_trades = 0
        if verbose: print("------------ NEXT ROUND ----------")

    if verbose: print(f"Winner is {game.players[game.player_cards.index(max(game.player_cards))]}")
    return 1 if game.player_cards.index(max(game.player_cards)) == game.curr_player else 0, reward



def model_turn(game: ss, r: int, learner: ql): # -> int:

    curr_card = game.player_cards[game.curr_player]
    if game.traded == True:
        curr_traded_card = game.player_cards[game.get_card_traded_index(game.curr_player)]
    else:
        curr_traded_card = 0
    trades_before = game.hand_trades
    players_after = 0
    i = game.curr_player + 1
    for _ in range(game.number_of_players):

        if i == game.number_of_players:
            i = 0
            continue
        if game.player_cards[i] == -1:
            i += 1
            continue
        else:
            players_after += 1
            i += 1
        if i == game.curr_player or i == game.curr_dealer:
            break

    state = discretize(curr_card, curr_traded_card, trades_before, players_after)
    if state >= discretize(13, 14, 8, 8):
        print("Something Wrong")
    if r == 0:
        game.first_turn = False
        return learner.querysetstate(state) # Returns an Action
    else:
        return learner.query(state, r) # Returns an Action

def reverse_discretize(value):
    curr_card = value // 1000
    curr_traded_card = (value % 1000) // 100
    trades_before = (value % 100) // 10
    players_after = value % 10
    return curr_card, curr_traded_card, trades_before, players_after

def understand_data(np_file, save_file):
    data = np.load(np_file)
    # Get the index of the array
    index = np.arange(len(data))
    # Create the dataframe
    df = pd.DataFrame(data, index=index)
    # Save the dataframe to CSV
    df['curr_card'] = index // 1500
    df['curr_traded_card'] = (index % 1500) // 100
    df['trades_before'] = (index % 100) // 10
    df['players_after'] = index % 10
    df.rename(columns={0:'Trade', 1:'Stay'}, inplace=True)

    df.to_csv(save_file)

if __name__ == "__main__":
    # play_game(game)

    train(7000, 1000, True, True, './models/model3.npy', False, dyna=0)

    understand_data('./models/model3.npy', './models/model3.csv')
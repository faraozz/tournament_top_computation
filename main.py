import streamlit as st
from tournament import Tournament
from tournament_simulation import Simulation
import pandas as pd
import time

def display_round_results(matches, round_number):
    """Display the results of matches for a specific round."""
    # Create an expander for this round
    with st.expander(f"### Round {round_number} Results", expanded=False):
        for match in matches:
            if match.player2 is None:
                st.write(f"🎯 Player {match.player1.player_id} received a bye")
            else:
                if match.result is None:
                    result_text = f"🤝 Player {match.player1.player_id} drew with Player {match.player2.player_id}"
                else:
                    winner_id = match.result.player_id
                    loser_id = match.player2.player_id if match.result == match.player1 else match.player1.player_id
                    result_text = f"🏆 Player {winner_id} defeated Player {loser_id}"
                st.write(result_text)

def display_player_match_history(st, player):
    """Display all matches for a specific player."""
    if player is None:
        return
        
    st.write(f"### Match History for Player {player.player_id}")
    
    # Group matches by round
    matches_by_round = {}
    for match in player.match_history:
        round_num = match.round_number
        if round_num not in matches_by_round:
            matches_by_round[round_num] = []
        matches_by_round[round_num].append(match)
    
    # Display each round's matches
    for round_num in sorted(matches_by_round.keys()):
        with st.expander(f"Round {round_num}", expanded=False):
            for match in matches_by_round[round_num]:
                if match.player2 is None:
                    st.write("🎯 Received a bye")
                else:
                    # Determine if this player won, lost, or drew
                    if match.result is None:
                        result = "🤝 Drew"
                    else:
                        if match.result == player:
                            result = "🏆 Won"
                        else:
                            result = "❌ Lost"
                    
                    # Show opponent
                    opponent = match.player2 if match.player1 == player else match.player1
                    if opponent:  # Add null check
                        st.write(f"{result} vs Player {opponent.player_id}")

def display_player_stats(players, limit=128):
    """
    Display the statistics for players.
    By default shows top 128 players with option to see all.
    """
    st.write("### Final Standings")
    
    # Get sorted players
    sorted_players = sorted(
        players,
        key=lambda p: (p.get_points(), p.calculate_tiebreaker()) if p is not None else (0, "0"),
        reverse=True
    )
    
    # Create a table of player statistics
    stats_data = []
    for rank, player in enumerate(sorted_players, 1):
        if player is None:
            continue
            
        tiebreaker = player.calculate_tiebreaker()
        points = player.get_points()
        
        stats_data.append({
            "Rank": rank,
            "Player": f"Player {player.player_id}",
            "Points": points,
            "W/L/D": f"{player.wins}/{player.losses}/{player.draws}",
            "Tiebreaker": tiebreaker
        })
    
    # Convert to DataFrame
    df = pd.DataFrame(stats_data)
    
    # Show limited number of players by default
    if len(stats_data) > limit and not st.session_state.get('show_all_players', False):
        displayed_df = df.head(limit)
    else:
        displayed_df = df
    
    # Display interactive dataframe
    selection = st.data_editor(
        displayed_df,
        use_container_width=True,
        disabled=["Rank", "Points", "W/L/D", "Tiebreaker"],
        hide_index=True,
        num_rows="fixed"
    )
    
    # Handle selection
    if selection is not None and len(selection.index) > 0:
        selected_index = selection.index[0]
        selected_row = displayed_df.iloc[selected_index]
        player_id = selected_row["Player"].split()[1]  # Get ID from "Player X"
        st.session_state.clicked_player_id = str(player_id)
    
    # Show/Hide buttons
    if len(stats_data) > limit:
        if not st.session_state.get('show_all_players', False):
            if st.button("Show All Players"):
                st.session_state.show_all_players = True
        else:
            if st.button("Show Less"):
                st.session_state.show_all_players = False

def main():
    # Set wide mode
    st.set_page_config(layout="wide")
    st.title("Top Computation")

    # Initialize session state
    if 'tournament' not in st.session_state:
        st.session_state.tournament = None
        st.session_state.simulation = None
        st.session_state.show_all_players = False
        st.session_state.show_history = False
        st.session_state.current_player_id = None
        st.session_state.matches_per_round = {}

    # Create two columns for the number inputs
    input_col1, input_col2 = st.columns(2)

    with input_col1:
        number_of_players = st.number_input(
            "Number of Players",
            step=1,
            min_value=0,
            value=0
        )

    with input_col2:
        draw_percentage = st.number_input(
            "Draw Percentage",
            step=1,
            min_value=0,
            max_value=100,
            value=0
        )       

    if st.button("Calculate"):
        if number_of_players > 0:
            st.write("New tournament starting...")
            start_time = time.time()
            
            st.session_state.tournament = Tournament(int(number_of_players), int(draw_percentage))
            st.session_state.simulation = Simulation(st.session_state.tournament)
            
            st.write(f"Tournament created with {number_of_players} players and {draw_percentage}% draw chance")
            st.write(f"Number of rounds: {st.session_state.tournament.number_of_rounds}")
            
            st.session_state.simulation.simulate()
            
            end_time = time.time()
            total_time = end_time - start_time
            st.write(f"Tournament completed in {total_time:.2f} seconds")
            
            st.write(f"Total number of matches played: {len(st.session_state.simulation.matches)}")

    # Show results if tournament exists
    if st.session_state.tournament is not None:
        st.write("## Tournament Results")
        
        # Create three columns with specific widths
        left_col, middle_col, right_col = st.columns([3, 4, 3])
        
        # Display player statistics in left column
        with left_col:
            display_player_stats(st.session_state.tournament.players)
        
        # Display round results in middle column
        with middle_col:
            # Display each round's results from session state
            for round_num in sorted(st.session_state.matches_per_round.keys()):
                display_round_results(st.session_state.matches_per_round[round_num], round_num)
        
        # Display player search and match history in right column
        with right_col:
            st.write("### Player Match History")
            player_id = st.number_input(
                "Enter Player ID",
                min_value=0,
                max_value=number_of_players-1,
                value=0,
                step=1,
                key="player_search"
            )
            
            if st.button("Show History") or st.session_state.show_history:
                st.session_state.show_history = True
                st.session_state.current_player_id = player_id
                
                # Find the player with the entered ID
                for player in st.session_state.tournament.players:
                    if player and player.player_id == st.session_state.current_player_id:
                        display_player_match_history(st, player)
                        break
            
            # Add a clear button to reset the history view
            if st.session_state.show_history:
                if st.button("Clear History"):
                    st.session_state.show_history = False
                    st.session_state.current_player_id = None

    else:
        st.error("Please enter a positive number of players")

if __name__ == "__main__":
    main()

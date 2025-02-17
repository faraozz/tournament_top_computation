import streamlit as st
from tournament import Tournament
from tournament_simulation import Simulation

def display_round_results(matches, round_number):
    """Display the results of matches for a specific round."""
    st.write(f"Round {round_number} Results:")
    for match in matches:
        if match.player2 is None:
            st.write(f"Player {match.player1.player_id} received a bye")
        else:
            result = "Draw" if match.result is None else f"Winner: Player {match.result.player_id}"
            st.write(f"Player {match.player1.player_id} vs Player {match.player2.player_id} - {result}")
    st.write("---")

def display_player_stats(players):
    """Display the statistics for all players."""
    st.write("Player Statistics:")
    for player in players:
        st.write(f"Player {player.player_id}: Wins: {player.wins}, Losses: {player.losses}, Draws: {player.draws}")

def main():
    st.title("Top Computation")

    # Initialize session state
    if 'tournament' not in st.session_state:
        st.session_state.tournament = None
        st.session_state.simulation = None

    # Create two columns for the number inputs
    col1, col2 = st.columns(2)

    with col1:
        number_of_players = st.number_input(
            "Number of Players",
            step=1,
            value=0
        )

    with col2:
        draw_percentage = st.number_input(
            "Draw Percentage",
            step=1,
            value=0,
            min_value=0,
            max_value=100
        )       

    if st.button("Calculate"):
        if number_of_players > 0:
            st.session_state.tournament = Tournament(int(number_of_players), int(draw_percentage))
            st.session_state.simulation = Simulation(st.session_state.tournament)
            
            st.write(f"Tournament created with {number_of_players} players and {draw_percentage}% draw chance")
            st.write(f"Number of rounds: {st.session_state.tournament.number_of_rounds}")
            
            st.session_state.simulation.simulate()
            
            st.write(f"Total number of matches played: {len(st.session_state.simulation.matches)}")

    # Only show buttons if simulation exists
    if st.session_state.simulation is not None:
        # Create columns for the display buttons
        col1, col2 = st.columns(2)
        
        # Button to show round results
        if col1.button("Show Round Results"):
            # Group matches by round
            matches_per_round = {}
            for match in st.session_state.simulation.matches:
                round_num = match.round_number
                if round_num not in matches_per_round:
                    matches_per_round[round_num] = []
                matches_per_round[round_num].append(match)
            
            # Display each round's results
            for round_num in sorted(matches_per_round.keys()):
                display_round_results(matches_per_round[round_num], round_num)
        
        # Button to show player statistics
        if col2.button("Show Player Statistics"):
            display_player_stats(st.session_state.tournament.players)

if __name__ == "__main__":
    main()

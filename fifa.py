import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt

# Set page configuration
st.set_page_config(page_title="FIFA World Cup Dashboard", page_icon="⚽", layout="wide")

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: #1f77b4;
    }
    .metric-label {
        font-size: 1rem;
        color: #666;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Load all FIFA World Cup datasets"""
    try:
        world_cups = pd.read_csv('WorldCups.csv')
        matches = pd.read_csv('WorldCupMatches.csv')
        players = pd.read_csv('WorldCupPlayers.csv')
        return world_cups, matches, players
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None, None, None

def main():
    st.markdown('<h1 class="main-header">⚽ FIFA World Cup Dashboard</h1>', unsafe_allow_html=True)

    # Load data
    world_cups, matches, players = load_data()

    if world_cups is None or matches is None or players is None:
        st.error("Failed to load data. Please check if CSV files are present.")
        return

    # Sidebar for navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Choose a section:",
                           ["Overview", "World Cup Winners", "Goals & Attendance",
                            "Match Statistics", "Player Analysis"])

    if page == "Overview":
        show_overview(world_cups, matches, players)
    elif page == "World Cup Winners":
        show_winners(world_cups)
    elif page == "Goals & Attendance":
        show_goals_attendance(world_cups, matches)
    elif page == "Match Statistics":
        show_match_stats(matches)
    elif page == "Player Analysis":
        show_player_analysis(players, matches)

def show_overview(world_cups, matches, players):
    st.header("🏆 World Cup Overview")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">{}</div>
            <div class="metric-label">Tournaments</div>
        </div>
        """.format(len(world_cups)), unsafe_allow_html=True)

    with col2:
        total_goals = world_cups['GoalsScored'].sum()
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">{}</div>
            <div class="metric-label">Total Goals</div>
        </div>
        """.format(total_goals), unsafe_allow_html=True)

    with col3:
        total_matches = world_cups['MatchesPlayed'].sum()
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">{}</div>
            <div class="metric-label">Total Matches</div>
        </div>
        """.format(total_matches), unsafe_allow_html=True)

    with col4:
        total_teams = world_cups['QualifiedTeams'].sum()
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">{}</div>
            <div class="metric-label">Teams Participated</div>
        </div>
        """.format(total_teams), unsafe_allow_html=True)

    # Recent tournaments table
    st.subheader("Recent World Cup Tournaments")
    recent_cups = world_cups.tail(5)[['Year', 'Country', 'Winner', 'Runners-Up', 'GoalsScored', 'Attendance']]
    recent_cups['Attendance'] = recent_cups['Attendance'].str.replace('.', '').astype(float)
    st.dataframe(recent_cups.style.format({'Attendance': '{:,.0f}'}))

def show_winners(world_cups):
    st.header("🥇 World Cup Winners")

    # Count wins by country
    winner_counts = world_cups['Winner'].value_counts().reset_index()
    winner_counts.columns = ['Country', 'Wins']

    # Bar chart of winners
    fig = px.bar(winner_counts.head(10), x='Country', y='Wins',
                 title='Most Successful Countries in World Cup History',
                 color='Wins', color_continuous_scale='Blues')
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)

    # Winners over time
    st.subheader("Winners Timeline")
    fig2 = px.scatter(world_cups, x='Year', y='Winner',
                     title='World Cup Winners Over Time',
                     size=[50]*len(world_cups), color='Winner')
    fig2.update_traces(marker=dict(size=20))
    st.plotly_chart(fig2, use_container_width=True)

    # Host countries vs winners
    st.subheader("Host Countries Performance")
    host_winners = world_cups[world_cups['Country'] == world_cups['Winner']]
    st.write(f"Host countries have won {len(host_winners)} times: {', '.join(host_winners['Country'].tolist())}")

def show_goals_attendance(world_cups, matches):
    st.header("📊 Goals & Attendance Trends")

    # Clean attendance data
    world_cups_clean = world_cups.copy()
    world_cups_clean['Attendance'] = world_cups_clean['Attendance'].str.replace('.', '').astype(float)

    col1, col2 = st.columns(2)

    with col1:
        # Goals over time
        fig1 = px.line(world_cups, x='Year', y='GoalsScored',
                      title='Goals Scored Per Tournament',
                      markers=True, line_shape='spline')
        fig1.update_traces(line_color='#1f77b4', marker_color='#ff7f0e')
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        # Attendance over time
        fig2 = px.line(world_cups_clean, x='Year', y='Attendance',
                      title='Tournament Attendance Over Time',
                      markers=True, line_shape='spline')
        fig2.update_traces(line_color='#2ca02c', marker_color='#d62728')
        fig2.update_layout(yaxis_tickformat=',')
        st.plotly_chart(fig2, use_container_width=True)

    # Goals vs Attendance correlation
    st.subheader("Goals vs Attendance Correlation")
    fig3 = px.scatter(world_cups_clean, x='GoalsScored', y='Attendance',
                     title='Relationship Between Goals and Attendance',
                     color='Year', size='MatchesPlayed',
                     hover_data=['Country', 'Winner'])
    st.plotly_chart(fig3, use_container_width=True)

def show_match_stats(matches):
    st.header("⚽ Match Statistics")

    # Clean matches data
    matches_clean = matches.dropna(subset=['Home Team Goals', 'Away Team Goals'])

    # Most goals in a match
    matches_clean['Total Goals'] = matches_clean['Home Team Goals'] + matches_clean['Away Team Goals']
    highest_scoring = matches_clean.nlargest(10, 'Total Goals')[['Year', 'Home Team Name', 'Home Team Goals',
                                                               'Away Team Name', 'Away Team Goals', 'Total Goals']]

    st.subheader("Highest Scoring Matches")
    st.dataframe(highest_scoring.style.format({'Total Goals': '{:.0f}'}))

    # Goals distribution
    col1, col2 = st.columns(2)

    with col1:
        fig1 = px.histogram(matches_clean, x='Total Goals',
                           title='Distribution of Total Goals Per Match',
                           nbins=20, color_discrete_sequence=['#1f77b4'])
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        # Home vs Away goals
        home_goals = matches_clean['Home Team Goals'].sum()
        away_goals = matches_clean['Away Team Goals'].sum()

        fig2 = go.Figure(data=[go.Pie(labels=['Home Team Goals', 'Away Team Goals'],
                                     values=[home_goals, away_goals],
                                     title='Home vs Away Goals Distribution')])
        fig2.update_traces(marker_colors=['#ff7f0e', '#2ca02c'])
        st.plotly_chart(fig2, use_container_width=True)

    # Matches by stage
    st.subheader("Matches by Tournament Stage")
    stage_counts = matches_clean['Stage'].value_counts().head(10)
    fig3 = px.bar(stage_counts, x=stage_counts.index, y=stage_counts.values,
                 title='Number of Matches by Stage', color=stage_counts.values,
                 color_continuous_scale='Reds')
    fig3.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig3, use_container_width=True)

def show_player_analysis(players, matches):
    st.header("👥 Player Analysis")

    # Clean players data
    players_clean = players.dropna(subset=['Player Name'])

    # Most common positions
    position_counts = players_clean['Position'].value_counts().head(10)
    fig1 = px.bar(position_counts, x=position_counts.index, y=position_counts.values,
                 title='Most Common Player Positions',
                 color=position_counts.values, color_continuous_scale='Greens')
    st.plotly_chart(fig1, use_container_width=True)

    # Players per team
    team_players = players_clean.groupby('Team Initials')['Player Name'].nunique().sort_values(ascending=False).head(20)
    fig2 = px.bar(team_players, x=team_players.index, y=team_players.values,
                 title='Number of Players by Team (Top 20)',
                 color=team_players.values, color_continuous_scale='Purples')
    fig2.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig2, use_container_width=True)

    # Coaches analysis
    st.subheader("Famous Coaches")
    coach_counts = players_clean['Coach Name'].value_counts().head(10)
    st.dataframe(coach_counts)

if __name__ == "__main__":
    main()

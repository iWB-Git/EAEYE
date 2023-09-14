# Import the necessary libraries
import pandas as pd
import matplotlib.pyplot as plt
from statsbombpy import sb
from mplsoccer import Pitch
import mplcursors

# Function to handle pass click event
def on_pass_click(sel, df):
    index = sel.target.index
    selected_pass = df.iloc[index]
    selected_index = df.index[df['id'] == selected_pass['id']][0]  # Get the index of the selected pass
    
    # Now you have the selected pass and its index, you can display it in the tooltip
    tooltip_text = f"Pass Index: {selected_index}\n"
    tooltip_text += f"X: {selected_pass['x_start']}, Y: {selected_pass['y_start']}"
    
    # Create a tooltip label with the pass index and coordinates
    sel.annotation.set_text(tooltip_text)
    
    run_specific_pass_code(df, selected_index)

# Function to run code specific to the selected pass
def run_specific_pass_code(dfmessi, selected_index):
    selected_pass_data = dfmessi.loc[selected_index]  # Use .loc to access the selected pass data
    p = Pitch(pitch_type='statsbomb')
    fig, ax = p.draw(figsize=(12, 8))

    p.scatter(x=selected_pass_data['x_start'], y=selected_pass_data["y_start"], ax=ax)
    
    # Check if 'freeze_frame' is not NaN and is iterable (a list)
    if isinstance(selected_pass_data['freeze_frame'], list):
        for x in selected_pass_data['freeze_frame']:
            if x['teammate']:
                color = 'blue'
            else:
                color = 'red'
            p.scatter(x=x['location'][0], y=x['location'][1], ax=ax, c=color, s=100)

    plt.show()  # Display the plot

# Load competition data
sb.competitions().head(50)

# Replace this with the competition_id and season_id you want to analyze
competition_id = 43
season_id = 106

matches = sb.matches(competition_id=competition_id, season_id=season_id)

# Replace this with the desired match_id from the 'matches' DataFrame
MATCH_ID = 3869151

events_df = sb.events(match_id=MATCH_ID)

# Replace this with the correct file path to your JSON data
match_360_df = pd.read_json(f'C:/Users/hamza/Downloads/StatsBomb/open-data-master/data/three-sixty/{MATCH_ID}.json')

df = pd.merge(left=events_df, right=match_360_df, left_on='id', right_on='event_uuid', how='left')

Messi = 5503
dfmessi = df[(df['player_id'] == Messi) & ((df['type'] == 'Dribble') | (df['type'] == 'Dribble Past'))].reset_index(drop=True)
dfmessi[['x_start','y_start']]=pd.DataFrame(dfmessi.location.tolist(),index=dfmessi.index)

# Create the pitch plot
p = Pitch(pitch_type='statsbomb')
fig, ax = p.draw(figsize=(12, 8))

# Scatter plot of Messi's pass starting points
scatter = p.scatter(x=dfmessi['x_start'], y=dfmessi['y_start'], ax=ax)

# Add click event handling to the scatter plot using mplcursors
mplcursors.cursor(scatter).connect("add", lambda sel: on_pass_click(sel, dfmessi))

# Display the pitch plot
plt.show()

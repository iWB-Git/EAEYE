
import pandas as pd
import matplotlib.pyplot as plt
from statsbombpy import sb
from mplsoccer import Pitch
import mplcursors


def on_pass_click(sel, df, pdf):
    index = sel.target.index
    selected_pass = df.iloc[index]
    selected_index = df.index[df['id'] == selected_pass['id']][0]
    print(pdf[selected_index])


    tooltip_text = f"Pass Index: {selected_index}\n"
    tooltip_text += f"X: {selected_pass['x_start']}, Y: {selected_pass['y_start']}"

    # Create a tooltip label with the pass index and coordinates
    sel.annotation.set_text(tooltip_text)


    run_specific_pass_code(df, selected_index, pdf)

# Function to run code specific to the selected pass
def run_specific_pass_code(dfmessi, selected_index, pdf):
    selected_pass_data = dfmessi.loc[selected_index]
    p = Pitch(pitch_type='statsbomb')
    fig, ax = p.draw(figsize=(12, 8))

    p.scatter(x=selected_pass_data['x_start'], y=selected_pass_data["y_start"], ax=ax)
    p.lines(xstart=selected_pass_data['x_start'], ystart=selected_pass_data['y_start'],
            xend=selected_pass_data['x_end'], yend=selected_pass_data['y_end'], ax=ax, comet=True)

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
dfmessi = df[(df['player_id'] == Messi) & (df['type'] == 'Pass')].reset_index(drop=True)
dfmessi[['x_start','y_start']]=pd.DataFrame(dfmessi.location.tolist(),index=dfmessi.index)
dfmessi[['x_end','y_end']]=pd.DataFrame(dfmessi.pass_end_location.tolist(),index=dfmessi.index)

# Create the pitch plot
p = Pitch(pitch_type='statsbomb')
fig, ax = p.draw(figsize=(12, 8))

# Scatter plot of Messi's pass starting points
scatter = p.scatter(x=dfmessi['x_start'], y=dfmessi['y_start'], ax=ax)

# Keep track of team_ids
team_ids = df['team_id'].tolist()
players=df['player'].tolist()

# Determine pass success based on team_ids and plot in red if unsuccessful
for i in range(len(dfmessi) - 1):
    if team_ids[i] == team_ids[i + 1]:
        color = 'blue'  # Successful pass, use blue color
    else:
        color = 'red'  # Unsuccessful pass, use red color
    p.lines(xstart=dfmessi['x_start'][i], ystart=dfmessi['y_start'][i],
            xend=dfmessi['x_end'][i], yend=dfmessi['y_end'][i], ax=ax, comet=True, color=color)

# Add click event handling to the scatter plot using mplcursors
mplcursors.cursor(scatter).connect("add", lambda sel: on_pass_click(sel, dfmessi,players))

# Display the pitch plot
plt.show()

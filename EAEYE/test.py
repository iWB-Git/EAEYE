import pandas as pd
import matplotlib.pyplot as plt
from statsbombpy import sb
from mplsoccer import Pitch
import seaborn as sns

# Replace this with the desired match_id from the 'matches' DataFrame
MATCH_ID = 3869151

df = sb.events(match_id=MATCH_ID)

# Replace this with the player_id you want to create a heatmap for
player_id = 5503

# Filter events for the specified player
dfmessi = df[df['player_id'] == player_id]

# Extract 'x' and 'y' coordinates, skipping elements that are floats
dfmessi[['x', 'y']] = pd.DataFrame([x if isinstance(x, list) else [None, None] for x in dfmessi['location']], index=dfmessi.index)

# Create a pitch plot
pitch = Pitch(pitch_type='statsbomb')
fig, ax = pitch.draw(figsize=(12, 8))

# Convert pitch coordinates to match the pitch dimensions

# Plot a heatmap on the pitch
sns.kdeplot(
    x=dfmessi['x'],
    y=dfmessi['y'],
    shade=True,
    shade_lowest=False,
    alpha=0.5,
    n_levels=10,
    cmap='magma',
    ax=ax  # Specify the axis to overlay the heatmap
)

plt.xlim(0,120)
plt.ylim(0,80)

plt.gca().invert_yaxis()
plt.title('Messi Heatmap vs Real Betis', color='white', size=20)

plt.show()

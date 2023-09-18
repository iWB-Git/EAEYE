import React, { useEffect, useState } from 'react';
import { Avatar, List } from 'antd';
import axios from 'axios';

function decodeUnicodeEscapeSequences(input) {
  return input.replace(/\\u[\dA-F]{4}/gi, (match) => {
    return String.fromCharCode(parseInt(match.replace(/\\u/g, ''), 16));
  });
}

const App: React.FC = () => {
  const [competitions, setCompetitions] = useState([]);
  const [matches, setMatches] = useState([]);
  const [selectedCompetition, setSelectedCompetition] = useState(null);

  useEffect(() => {
    // Fetch data from your API
    axios.get('http://localhost:5000/api/competitions')
      .then(response => {
        setCompetitions(response.data);
      })
      .catch(error => {
        console.error('Error fetching competitions:', error);
      });
  }, []);

  const handleCompetitionClick = (competition) => {
    // Fetch matches for the selected competition
    axios.get(`http://localhost:5000/api/matches?competition_id=${competition.competition_id}&season_id=${competition.season_id}`)
      .then(response => {
        // Decode Unicode escape sequences in the response data
        const decodedMatches = response.data.map(match => {
          return {
            ...match,
            home_team: decodeUnicodeEscapeSequences(match.home_team),
            away_team: decodeUnicodeEscapeSequences(match.away_team),
            // Add more fields to decode if needed
          };
        });
  
        setMatches(decodedMatches); // Update the matches state with decoded data
        console.log(decodedMatches)
      })
      .catch(error => {
        console.error('Error fetching matches:', error);
      });
  };
   

  return (
    <div>
      <h1>StatsBomb Competitions</h1>
      {selectedCompetition ? (
        <div className="matches-list">
          <h2>Matches</h2>
          {/* Render Matches List */}
          <List
            itemLayout="horizontal"
            dataSource={matches}
            renderItem={(item, index) => (
              <List.Item>
                <List.Item.Meta
                  avatar={<Avatar src={`https://xsgames.co/randomusers/avatar.php?g=pixel&key=${index}`} />}
                  title={<a href="/#">{item.home_team} vs {item.away_team}</a>}
                  description={`${item.competition_stage}, ${item.match_date}`}
                />
              </List.Item>
            )}
          />
        </div>
      ) : (
        <div className="competitions-list">
          {/* Render Competitions List */}
          <List
            itemLayout="horizontal"
            dataSource={competitions}
            renderItem={(item, index) => (
              <List.Item>
                <List.Item.Meta
                  avatar={<Avatar src={`https://xsgames.co/randomusers/avatar.php?g=pixel&key=${index}`} />}
                  title={<a href="/#" onClick={() => handleCompetitionClick(item)}>{item.competition_name}</a>}
                  description={item.season_name}
                />
              </List.Item>
            )}
          />
        </div>
      )}
    </div>
  );
};

export default App;

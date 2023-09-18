import React, { useEffect, useState } from 'react';
import { Avatar, List } from 'antd';
import axios from 'axios';
import { Link, useNavigate } from 'react-router-dom'; // Import Link

function decodeUnicodeEscapeSequences(input) {
  return input.replace(/\\u[\dA-F]{4}/gi, (match) => {
    return String.fromCharCode(parseInt(match.replace(/\\u/g, ''), 16));
  });
}

const App = () => {
  const [competitions, setCompetitions] = useState([]);
  const [matches, setMatches] = useState([]);
  const [selectedCompetition, setSelectedCompetition] = useState(null);
  const navigate = useNavigate();

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

  return (
    <div>
      <h1>StatsBomb Competitions</h1>
        <div className="competitions-list">
          {/* Render Competitions List */}
          <List
            itemLayout="horizontal"
            dataSource={competitions}
            renderItem={(item, index) => (
              <List.Item>
                <List.Item.Meta
                  avatar={<Avatar src={`https://xsgames.co/randomusers/avatar.php?g=pixel&key=${index}`} />}
                  title={
                    // Use Link to navigate to the Matches page with competition and season IDs in the URL
                    <div onClick={() => navigate(`/matches/${item.competition_id}/${item.season_id}`)}>
                    {item.competition_name}
                  </div>
                  }
                  description={item.season_name}
                />
              </List.Item>
            )}
          />
        </div>
    </div>
  );
};

export default App;

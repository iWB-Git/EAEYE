import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useParams } from 'react-router-dom';
import { Table } from 'antd'; // Import Table component from antd

function Matches() {
  const [matches, setMatches] = useState([]);
  const { competitionId, seasonId } = useParams();

  useEffect(() => {
    axios
      .get(`http://localhost:5000/api/matches?competition_id=${competitionId}&season_id=${seasonId}`)
      .then((response) => {
        setMatches(response.data);
      })
      .catch((error) => {
        console.error('Error fetching matches:', error);
      });
  }, [competitionId, seasonId]);

  const columns = [
    {
      title: 'Home Team',
      dataIndex: 'home_team',
      key: 'home_team',
    },
    {
      title: 'Away Team',
      dataIndex: 'away_team',
      key: 'away_team',
    },
    {
      title: 'Competition Stage',
      dataIndex: 'competition_stage',
      key: 'competition_stage',
    },
    {
      title: 'Match Date',
      dataIndex: 'match_date',
      key: 'match_date',
    },
  ];

  return (
    <div>
      <h1>Matches for Competition {competitionId} - Season {seasonId}</h1>
      <Table dataSource={matches} columns={columns} pagination={false} /> {/* Use the Table component from antd */}
    </div>
  );
}

export default Matches;

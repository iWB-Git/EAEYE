import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'; // Import `Routes` from react-router-dom
import Competetions from './Pages/Competetions';
import Matches from './Pages/Matches'

const App = () => {
  return (
      <Routes>
        <Route path="/" element={<Competetions />} /> 
        <Route path="/matches/:competitionId/:seasonId" element={<Matches/>} />
      </Routes>
  );
};

export default App;

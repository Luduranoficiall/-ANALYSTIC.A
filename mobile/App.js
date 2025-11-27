import React, { useEffect, useState } from 'react';
import { View, Text } from 'react-native';

export default function App() {
  const [members, setMembers] = useState(0);

  useEffect(() => {
    fetch("https://analystic.a/api/kpis")
      .then(r => r.json())
      .then(d => setMembers(d.members));
  }, []);

  return (
    <View style={{ flex:1, alignItems:"center", justifyContent:"center" }}>
      <Text style={{ fontSize:28 }}>ANALYTIC.A PRO</Text>
      <Text style={{ fontSize:20 }}>Membros: {members}</Text>
    </View>
  );
}

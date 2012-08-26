for i in range(len(self.tiles)):
  for j in range(len(self.tiles[i])):
    if i < m:
      G.add_edge(self.tiles[i][j], self.tiles[i+1][j])
    if j < n:
      G.add_edge(self.tiles[i][j], self.tiles[i][j+1])
    if i < m and j < n:
      G.add_edge(self.tiles[i][j], self.tiles[i+1][j+1])
    
my_tile = tiles[i][j]
if my_tile.is_wall():

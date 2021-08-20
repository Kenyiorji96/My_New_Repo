package game;

import fixtures.Room;

public class Player {
	Room currentRoom;
	
	public Room getCurrentRoom() {
		return this.currentRoom;
	}
    
	public void setCurrentRoom(Room mainRoom) {
		this.currentRoom = mainRoom;
	}
	
	public Room commandGo(String[] command2, Player player) {
		
		if(currentRoom.getExit(command2[1]).getName().equals("Empty")) {
			System.out.println("Oops Wrong Way!");
			return currentRoom;
		}
		
		return player.currentRoom.getExit(command2[1]);
	}
}

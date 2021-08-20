package game;
import fixtures.Room;


public class RoomManager {
	private static final Room nullRoom = null;

	Room startingRoom;
	
	Room[] rooms = new Room[6];
	  public Room[] weightRoomExits = new Room[4];
	  public Room[] familyRoomExits = new Room[4];
	  public Room[] funPlexExits = new Room[4];
	  public Room[] kitchenExits = new Room[4];
	  public Room[] diningRoomExits = new Room[4];
	  public Room[] masterBedroomExits = new Room[4];
	  
	  public Room getStartingRoom() {
		  return getStartingRoom();
	  }
	    
	
	
	public void init() {
		Room weightRoom =  new Room("Weight Room", "a in-home gym", "A standard 10 x 10 room located in the Garage of the house which leads to the foyer");
		this.rooms[0] = weightRoom;
		this.startingRoom = weightRoom;
		
		Room familyRoom = new Room("Family Room", "area for family", "living room space to the west when you walk in across the hall from the weight room");
		this.rooms[1]= familyRoom;
		
		Room funPlex = new Room("Fun Plex", "Home entertainment Room", "This room contains the home-theatre as well as a game room" + "\n" + "located through the door in the family room leads which leads downstairs to the Fun Plex");
		this.rooms[2] = funPlex; 

		
		Room kitchen = new Room("Kitchen", "Big Kitchen", " Kitchen lies north of the family room and is connected with a clear view of the family room connected ");
		this.rooms[3] = kitchen;
		
		Room diningRoom = new Room("Dining Room", "Place to eat", "the Dining Room lies east of the Kitchen paneled with hard wood flooring" + "\n" + "set with ceiling chandelier and medium sized marble table");
		this.rooms[4] = diningRoom; 
		
		Room masterBedroom = new Room("Master Bedroom", "Main bedroom in house", " The master bedroom is located up the stairs adjacent to the Weight Room to the right when you walk out" + "\n" + "Once you go up the stairs make a left and go past the bathroom and closet" +"\n"+ "bedroom directly ahead");
		this.rooms[5] = masterBedroom;
		
		//Weight room
		
		this.weightRoomExits[0] = nullRoom; 
		this.weightRoomExits[1] = nullRoom; 
		this.weightRoomExits[2] = familyRoom; 
		this.weightRoomExits[3] = diningRoom;
		
		//family room 
		
		this.familyRoomExits[0] = nullRoom;
		this.familyRoomExits[1] = funPlex;
		this.familyRoomExits[2] = kitchen; 
		this.familyRoomExits[3] = weightRoom; 
		
		//funPlex
		this.funPlexExits[0] = nullRoom; 
		this.funPlexExits[1] = nullRoom; 
		this.funPlexExits[2] = nullRoom; 
		this.funPlexExits[3] = familyRoom;
		
		//kitchen
		this.kitchenExits[0] = nullRoom; 
		this.kitchenExits[1] = diningRoom; 
		this.kitchenExits[2] = familyRoom; 
		this.kitchenExits[3] = nullRoom; 
		
		//dining room 
		this.diningRoomExits[0] = nullRoom; 
		this.diningRoomExits[1] = nullRoom; 
		this.diningRoomExits[2] = weightRoom;
		this.diningRoomExits[3] = kitchen; 
		
		
		
		
		
		
		
	}

}

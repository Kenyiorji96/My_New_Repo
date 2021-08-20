package game;

import java.util.Iterator;
import java.util.Scanner;

import fixtures.Room;
import game.RoomManager;
import game.Player;


public class Main {
	
	public static RoomManager admin = new RoomManager();
	
	public static void main(String[] args) {
		admin.init();
		Player p1 = new Player();
		p1.setCurrentRoom( admin.getStartingRoom());
		System.out.println("Welcome to the Home Tour Simulator!");
		System.out.println("Background: You have been placed in a virtual home tour have a look around!");
		System.out.println("Rules: Just enter Go and some direction either North, South, West, or East! Have Fun!" + "\n\n ______________________________________________________");
		printRoom(p1);
		
		String[] targetInput = new String[2];
		
		while(!targetInput.equals("quit")) {
			System.out.println("Where to first?");
		    targetInput = collectInput();
		    
		    if (targetInput[0].equals("Exit")) {
		    	System.out.println("Our tour has reached its end. Hope you enjoyed and come again!");
		    	break;
		    }
		
		    parse(targetInput, p1);
		
		}
	}
	
	private static void printRoom(Player player) {
		System.out.println("Current Room: " + player.getCurrentRoom().getName());
		System.out.println("Short Description: " + player.getCurrentRoom().getName());
		System.out.println("Long Description: " + player.getCurrentRoom().getName());
	}
	
	private static String[] collectInput() { 
		
		Scanner scanner = new Scanner(System.in);
		String action = scanner.nextLine();
		String delims = "[]+";
		String[] output = action.split(delims);
		
		return output;
		
	}
	
	private static void parse(String[] command, Player player) {
		collectInput();
		
		switch(command[0]) {
		case "go": 
			System.out.println("Selection Go has been Entered please proceed to direction!");
			player.setCurrentRoom(player.commandGo(command,player));
			printRoom(player);
			
			for(int i = 0; i < player.getCurrentRoom().getExits().length; i++) {
				
				switch(i) {
				case 0: 
					System.out.println("South");
					break;
				
				case 1: 
					System.out.println("West");
					break;
				
				case 2: 
					System.out.println("North");
					break;
					
				case 3: 
					System.out.println("East");
					break;
									
					
				}
				System.out.println("Player leaving: " + player.getCurrentRoom().getExits() + " " + player.getCurrentRoom().getExits()[i].getShortDescription());
			}
		
		} 
		
		
	
	   
	    	System.out.println("Error! Please Try Again!");
	    	
}

}

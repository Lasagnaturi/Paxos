package distributedAlgos;

import java.net.InetAddress;
import java.net.UnknownHostException;

public class Machine {
	
	public void printIp() throws UnknownHostException {
        InetAddress inetAddress = InetAddress.getLocalHost();
        System.out.println("IP Address:- " + inetAddress.getHostAddress());
        System.out.println("Host Name:- " + inetAddress.getHostName());
	}
	    
}

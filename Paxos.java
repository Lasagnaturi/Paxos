import java.net.InetAddress;
import java.net.UnknownHostException;

public class Paxos {

	
  public static void main(String[] args) throws UnknownHostException{
    System.out.println("Hello from " + args[0] + " with id " + args[1]);
    InetAddress inetAddress = InetAddress.getLocalHost();
    System.out.println("IP Address:- " + inetAddress.getHostAddress());
    System.out.println("Host Name:- " + inetAddress.getHostName());

  }


}

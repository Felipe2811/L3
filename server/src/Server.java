import java.io.*;
import java.net.*;

class Servidor {

    private static final int puerto = 7777;

    public static void main(String[] args) throws Exception {
        ServerSocket serverSocket = new ServerSocket(puerto);
        int id = 0;
        while (true) {
            new AdministradorCliente(serverSocket.accept(), id).start();
            id++;
        }
    }

    private static class AdministradorCliente extends Thread {
        private Socket clientSocket;
        private PrintWriter out;
        private BufferedReader in;
        private int id;

        public AdministradorCliente(Socket socket, int id) {
            this.clientSocket = socket;
            this.id = id;
        }

        public void run() {
            try {
                out = new PrintWriter(clientSocket.getOutputStream(), true);
                in = new BufferedReader(new InputStreamReader(clientSocket.getInputStream()));

                String inputLine;
                while ((inputLine = in.readLine()) != null) {
                    // if (".".equals(inputLine)) { // Matar conexion
                    // out.println("bye");
                    // break;
                    // }
                    out.println(inputLine);
                    System.out.println("Cliente " + id + ": " + inputLine);
                }

                in.close();
                out.close();
                clientSocket.close();
            } catch (IOException e) {
                e.printStackTrace();
            }
        }
    }
}
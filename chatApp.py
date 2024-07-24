import socket
from tkinter import *
from tkinter.ttk import *
import _thread


class ChatClient(Frame):

    def __init__(self, root):
        super().__init__(root)
        self.root = root
        self.init_ui()
        self.server_soc = None
        self.serverStatus = 0
        self.buffsize = 1024
        self.allClients = {}
        self.counter = 0

    def init_ui(self):
        self.root.title("Simple P2P Chat Client")
        screen_size_x = self.root.winfo_screenwidth()
        screen_size_y = self.root.winfo_screenheight()
        self.frame_size_x = 800
        self.frame_size_y = 680
        frame_pos_x = (screen_size_x - self.frame_size_x) / 2
        frame_pos_y = (screen_size_y - self.frame_size_y) / 2
        self.root.geometry("=%dx%d+%d+%d" % (self.frame_size_x, self.frame_size_y, frame_pos_x, frame_pos_y))
        self.root.resizable(width=False, height=False)

        pad_x = 10
        pad_y = 10
        parent_frame = Frame(self.root)
        parent_frame.grid(padx=pad_x, pady=pad_y, stick=E + W + N + S)

        ip_group = Frame(parent_frame)
        server_label = Label(ip_group, text="Set: ")
        self.name_var = StringVar()
        self.name_var.set("SDH")
        name_field = Entry(ip_group, width=10, textvariable=self.name_var)
        self.serverIPVar = StringVar()
        self.serverIPVar.set("127.0.0.1")
        server_ip_field = Entry(ip_group, width=15, textvariable=self.serverIPVar)
        self.serverPortVar = StringVar()
        self.serverPortVar.set("8090")
        server_port_field = Entry(ip_group, width=5, textvariable=self.serverPortVar)
        server_set_button = Button(ip_group, text="Set", width=10, command=self.handle_set_server)
        add_client_label = Label(ip_group, text="Add friend: ")
        self.clientIPVar = StringVar()
        self.clientIPVar.set("127.0.0.1")
        client_ip_field = Entry(ip_group, width=15, textvariable=self.clientIPVar)
        self.clientPortVar = StringVar()
        self.clientPortVar.set("8091")
        client_port_field = Entry(ip_group, width=5, textvariable=self.clientPortVar)
        client_set_button = Button(ip_group, text="Add", width=10, command=self.handle_add_client)
        server_label.grid(row=0, column=0)
        name_field.grid(row=0, column=1)
        server_ip_field.grid(row=0, column=2)
        server_port_field.grid(row=0, column=3)
        server_set_button.grid(row=0, column=4, padx=5)
        add_client_label.grid(row=0, column=5)
        client_ip_field.grid(row=0, column=6)
        client_port_field.grid(row=0, column=7)
        client_set_button.grid(row=0, column=8, padx=5)

        read_chat_group = Frame(parent_frame)
        self.receivedChats = Text(read_chat_group, bg="white", width=60, height=30, state=DISABLED)
        self.friends = Listbox(read_chat_group, bg="white", width=30, height=30)
        self.receivedChats.grid(row=0, column=0, sticky=W + N + S, padx=(0, 10))
        self.friends.grid(row=0, column=1, sticky=E + N + S)

        write_chat_group = Frame(parent_frame)
        self.chatVar = StringVar()
        self.chatField = Entry(write_chat_group, width=80, textvariable=self.chatVar)
        send_chat_button = Button(write_chat_group, text="Send", width=10, command=self.handle_send_chat)
        self.chatField.grid(row=0, column=0, sticky=W)
        send_chat_button.grid(row=0, column=1, padx=5)

        self.status_label = Label(parent_frame)

        bottom_label = Label(parent_frame,
                             text="Created by Siddhartha under Prof. A. Prakash [Computer Networks, Dept. of CSE, BIT Mesra]")

        ip_group.grid(row=0, column=0)
        read_chat_group.grid(row=1, column=0)
        write_chat_group.grid(row=2, column=0, pady=10)
        self.status_label.grid(row=3, column=0)
        bottom_label.grid(row=4, column=0, pady=10)

    def handle_set_server(self):
        if self.server_soc:
            self.server_soc.close()
            self.server_soc = None
            self.serverStatus = 0
        serveraddr = (self.serverIPVar.get().replace(' ', ''), int(self.serverPortVar.get().replace(' ', '')))
        try:
            self.server_soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_soc.bind(serveraddr)
            self.server_soc.listen(5)
            self.set_status("Server listening on %s:%s" % serveraddr)
            _thread.start_new_thread(self.listen_clients, ())
            self.serverStatus = 1
            self.name = self.name_var.get().replace(' ', '')
            if self.name == '':
                self.name = "%s:%s" % serveraddr
        except:
            self.set_status("Error setting up server")

    def listen_clients(self):
        while 1:
            client_soc, client_addr = self.server_soc.accept()
            self.set_status("Client connected from %s:%s" % client_addr)
            self.add_client(client_soc, client_addr)
            _thread.start_new_thread(self.handle_client_messages, (client_soc, client_addr))
        self.server_soc.close()

    def handle_add_client(self):
        if self.serverStatus == 0:
            self.set_status("Set server address first")
            return
        client_addr = (self.clientIPVar.get().replace(' ', ''), int(self.clientPortVar.get().replace(' ', '')))
        try:
            client_soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_soc.connect(client_addr)
            self.set_status("Connected to client on %s:%s" % client_addr)
            self.add_client(client_soc, client_addr)
            _thread.start_new_thread(self.handle_client_messages, (client_soc, client_addr))
        except ConnectionRefusedError:
            self.set_status("Error connecting to client")

    def handle_client_messages(self, client_soc, client_addr):
        while 1:
            try:
                data = client_soc.recv(self.buffsize)
                if not data and data != b'':
                    break
                self.add_chat("%s:%s" % client_addr, data.decode('utf-8'))
            except Exception as e:
                break
        self.remove_client(client_soc)
        client_soc.close()
        self.set_status("Client disconnected from %s:%s" % client_addr)

    def handle_send_chat(self):
        if self.serverStatus == 0:
            self.set_status("Set server address first")
            return
        msg = self.chatVar.get().replace(' ', '')
        if msg == '':
            return
        self.add_chat("me", msg)
        for client in self.allClients.keys():
            bmsg = msg.encode('utf-8')
            client.send(bmsg)

    def add_chat(self, client, msg):
        self.receivedChats.config(state=NORMAL)
        self.receivedChats.insert("end", client + ": " + msg + "\n")
        self.receivedChats.config(state=DISABLED)

    def add_client(self, client_soc, client_addr):
        self.allClients[client_soc] = self.counter
        self.counter += 1
        self.friends.insert(self.counter, "%s:%s" % client_addr)

    def remove_client(self, client_soc):
        print(self.allClients)
        self.friends.delete(self.allClients[client_soc])
        del self.allClients[client_soc]
        print(self.allClients)

    def set_status(self, msg):
        self.status_label.config(text=msg)
        print(msg)


def main():
    root = Tk()
    app = ChatClient(root)
    app.mainloop()


if __name__ == '__main__':
    main()

import socket
from tkinter import *
from PIL import ImageTk, Image
import os
import pprint
from pprint import pprint
import gen_key
from Crypto.PublicKey import RSA


root = Tk()

image_size = 64

user_player = None 	#Host plays white
			#White goes first
			#White plays from bottom (len(board)) to top (0).




class Board:
	def __init__(self):
		self.canvas = Canvas(root, width=image_size*8, height=image_size*8)
		self.canvas.pack()
		self.canvas.bind("<Button-1>",self.mouse_action)

		self.turn_text = Label(root,text = "ERROR")
		self.turn_text.pack()

		self.board = [[None]*8 for i in range(8)]	#Note that the board is a list of lists
								#This means that the Y coordinates are the first coordinate of board
								#The X coordinate is the second coordinate of the board
								#A Y coordinate of 0 is the top
								#A Y coordinate of 7 is the bottom
								#Decreasing Ys moves the piece UP
		
		self.board[0][0] = Rook("guest",(0,0))
		self.board[0][1] = Knight("guest",(1,0))
		self.board[0][2] = Bishop("guest",(2,0))
		self.board[0][3] = Queen("guest",(3,0))
		self.board[0][4] = King("guest",(4,0))
		self.board[0][5] = Bishop("guest",(5,0))
		self.board[0][6] = Knight("guest",(6,0))
		self.board[0][7] = Rook("guest",(7,0))
		
		for x in range(8):
			self.board[1][x] = Pawn("guest",(x,1))

		self.board[7][0] = Rook("host",(0,7))
		self.board[7][1] = Knight("host",(1,7))
		self.board[7][2] = Bishop("host",(2,7))
		self.board[7][3] = Queen("host",(3,7))
		self.board[7][4] = King("host",(4,7))
		self.board[7][5] = Bishop("host",(5,7))
		self.board[7][6] = Knight("host",(6,7))
		self.board[7][7] = Rook("host",(7,7))

		for x in range(8):
			self.board[6][x] = Pawn("host",(x,6))

		self.guest_pieces = [self.board[i][j] for i in range(2) for j in range(8)]
		self.host_pieces = [self.board[6+i][j] for i in range(2) for j in range(8)]
		
		self.guest_king = self.board[0][4]
		self.host_king = self.board[7][4]
		
		self.selected_piece = None
		self.selected_image = ImageTk.PhotoImage(Image.open("../res/selected.png").resize((image_size,image_size), Image.ANTIALIAS))

		self.move_coords = []

		self.redraw()
		if user_player == "guest":
			move = link.get_move()
			self.move_piece(move[0],move[1])
			self.redraw()
			self.turn_text.config(text='Turn: You (Black')
		else:
			self.turn_text.config(text='Turn: You (White)')


	def pieceAtLoc(self,piece,pos):
		if not (pos[0]>=0 and pos[0]<len(self.board[0]) and pos[1]>=0 and pos[1]<len(self.board)):
			return "out"

		if self.board[pos[1]][pos[0]] == None:
			return "none"
		
		if self.board[pos[1]][pos[0]].owner == piece.owner:
			return "friendly"

		if self.board[pos[1]][pos[0]].owner != piece.owner:
			return "enemy"

	def redraw(self):
		self.canvas.delete("all")
		for x in range(len(self.board[0])):
			for y in range(len(self.board)):
				if ((x%2)+y)%2 == 0:
					self.canvas.create_rectangle(x*image_size,y*image_size,x*image_size + image_size,y*image_size + image_size,fill = "saddlebrown")
				else:
					self.canvas.create_rectangle(x*image_size,y*image_size,x*image_size + image_size,y*image_size + image_size,fill = "white")
					

				if self.board[y][x] == None:
					continue
				self.canvas.create_image(x*image_size,y*image_size,image=self.board[y][x].piece_image,anchor="nw")

		if self.selected_piece != None:
			self.canvas.create_image(self.selected_piece.position[0]*image_size,
						self.selected_piece.position[1]*image_size,
						image=self.selected_image,
						anchor="nw")

		for coords in self.move_coords:
			self.canvas.create_image(coords[0]*image_size,
						coords[1]*image_size,
						image=self.selected_image,
						anchor="nw")

	def mouse_action(self,event):
		x_coord = event.x//image_size
		y_coord = event.y//image_size

		if self.board[y_coord][x_coord] != None and self.board[y_coord][x_coord].owner == user_player:
			self.selected_piece = self.board[y_coord][x_coord]
			self.move_coords = self.selected_piece.getMoveset()
			self.redraw()
		elif (x_coord,y_coord) in self.move_coords:
			old_pos = self.selected_piece.position
			new_pos = (x_coord,y_coord)
			self.move_piece(old_pos,new_pos)
			self.selected_piece = None
			self.move_coords = []
			self.redraw()
			self.turn_text.config(text='Turn: Opponent')
			root.update()
			
			link.send_move(old_pos,new_pos)
			
			move = link.get_move()
			
			self.move_piece(move[0],move[1])
			self.redraw()
			n_text = "Turn: You "
			n_text += "(Black)" if user_player == "guest" else "(White)"
			self.turn_text.config(text=n_text)
			

			user_pieces = self.host_pieces if user_player == "host" else self.guest_pieces
			move_count = 0
			
			for piece in user_pieces:
				move_count += len(piece.getMoveset())

			if move_count == 0:
				print("CHECKMATE " + user_player)



	def move_piece(self,old_pos,new_pos):
		piece_to_move = self.board[old_pos[1]][old_pos[0]]
		kill_piece = self.board[new_pos[1]][new_pos[0]]
		if kill_piece != None:
			if kill_piece.owner == "host":
				self.host_pieces.remove(kill_piece)
			else:
				self.guest_pieces.remove(kill_piece)
		self.board[old_pos[1]][old_pos[0]] = None
		self.board[new_pos[1]][new_pos[0]] = piece_to_move
		piece_to_move.move(new_pos)



	def check_moveset(self,piece,moveset):
		if piece.owner == user_player:
			moveset = [x for x in moveset if not self.will_checkmate(piece.position,x)]
		return moveset
					

	def will_checkmate(self,old_pos,new_pos):
		old_piece = self.board[old_pos[1]][old_pos[0]]
		new_piece = self.board[new_pos[1]][new_pos[0]]

		self.board[old_pos[1]][old_pos[0]] = None
		self.board[new_pos[1]][new_pos[0]] = old_piece

		if user_player == "host":
			enemy_units = self.guest_pieces
			friend_king = self.host_king
		else:
			enemy_units = self.host_pieces
			friend_king = self.guest_king

		king_space = friend_king.position
		if type(old_piece) == King:
			king_space = new_pos
		for piece in enemy_units:
			if piece.position == new_pos: #Piece already got jumped
				continue
			if king_space in piece.getMoveset():
				self.board[old_pos[1]][old_pos[0]] = old_piece
				self.board[new_pos[1]][new_pos[0]] = new_piece
				return True

		self.board[old_pos[1]][old_pos[0]] = old_piece
		self.board[new_pos[1]][new_pos[0]] = new_piece
		return False



		






#Abstract class 
class GamePiece:
	def __init__(self,owner,position):
		self.owner = owner
		self.position = position

	def loadImage(self,im_name):
		self.piece_image = ImageTk.PhotoImage(Image.open("../res/"+im_name+self.owner+".png").resize((image_size,image_size), Image.ANTIALIAS))
	
	def getMoveset(self):
		pass

	def move(self,new_pos):
		self.position = new_pos

	def __repr__(self):
		return self.__str__()


class Knight(GamePiece):
	def __init__(self,owner,position):
		GamePiece.__init__(self,owner,position)
		GamePiece.loadImage(self,"knight")

	#Debugging
	def __str__(self):
		return "K"


	def getMoveset(self):
		moveset = []

		moveset.append((self.position[0]+1,self.position[1]+2))
		moveset.append((self.position[0]+1,self.position[1]-2))

		moveset.append((self.position[0]-1,self.position[1]+2))
		moveset.append((self.position[0]-1,self.position[1]-2))

		moveset.append((self.position[0]+2,self.position[1]+1))
		moveset.append((self.position[0]+2,self.position[1]-1))

		moveset.append((self.position[0]-2,self.position[1]+1))
		moveset.append((self.position[0]-2,self.position[1]-1))
		
		moveset = [x for x in moveset if game_board.pieceAtLoc(self,x) == "none" or game_board.pieceAtLoc(self,x) == "enemy"]

		moveset = game_board.check_moveset(self,moveset)

		return moveset


class Pawn(GamePiece):
	def __init__(self,owner,position):
		GamePiece.__init__(self,owner,position)
		GamePiece.loadImage(self,"pawn")
		self.first_move = True

	#Debugging
	def __str__(self):
		return "P"


	def getMoveset(self):
		moveset = []

		direction = -1 if self.owner == "host" else 1

		if game_board.pieceAtLoc(self,(self.position[0],self.position[1]+1*direction)) == "none":
			moveset.append((self.position[0],self.position[1]+1*direction))
			if self.first_move and game_board.pieceAtLoc(self,(self.position[0],self.position[1]+2*direction)) == "none":
				moveset.append((self.position[0],self.position[1]+2*direction))

		if game_board.pieceAtLoc(self,(self.position[0]+1,self.position[1]+1*direction)) == "enemy":
			moveset.append((self.position[0]+1,self.position[1]+1*direction))
	
		if game_board.pieceAtLoc(self,(self.position[0]-1,self.position[1]+1*direction)) == "enemy":
			moveset.append((self.position[0]-1,self.position[1]+1*direction))

		moveset = game_board.check_moveset(self,moveset)

		return moveset
	

	def move(self,new_pos):
		self.position = new_pos
		self.first_move = False


	
class Rook(GamePiece):
	def __init__(self,owner,position):
		GamePiece.__init__(self,owner,position)
		GamePiece.loadImage(self,"rook")


	#Debugging
	def __str__(self):
		return "R"


	def getMoveset(self):
		moveset = []

		#Rightwards movement
		directions = 	[
				(1,0), #Rightwards
				(-1,0), #Leftwards
				(0,1), #Downwards
				(0,-1) #Upwards
				]	
		for mod in directions:
			count = 1
			keep_going = True
			while keep_going:
				new_pos = (self.position[0]+(count*mod[0]),self.position[1]+(count*mod[1]))
				mov_piece = game_board.pieceAtLoc(self,new_pos)
				if mov_piece == "enemy" or mov_piece == "none":
					moveset.append(new_pos)

				if mov_piece != "none":
					keep_going = False

				count+=1

		moveset = game_board.check_moveset(self,moveset)

		return moveset

class Bishop(GamePiece):
	def __init__(self,owner,position):
		GamePiece.__init__(self,owner,position)
		GamePiece.loadImage(self,"bishop")


	#Debugging
	def __str__(self):
		return "B"


	def getMoveset(self):
		moveset = []

		#Rightwards movement
		directions = 	[
				(1,1),
				(-1,-1),
				(1,-1),
				(-1,1) 
				]	
		for mod in directions:
			count = 1
			keep_going = True
			while keep_going:
				new_pos = (self.position[0]+(count*mod[0]),self.position[1]+(count*mod[1]))
				mov_piece = game_board.pieceAtLoc(self,new_pos)
				if mov_piece == "enemy" or mov_piece == "none":
					moveset.append(new_pos)

				if mov_piece != "none":
					keep_going = False

				count+=1

		moveset = game_board.check_moveset(self,moveset)

		return moveset
	


class Queen(GamePiece):
	def __init__(self,owner,position):
		GamePiece.__init__(self,owner,position)
		GamePiece.loadImage(self,"queen")


	#Debugging
	def __str__(self):
		return "Q"


	def getMoveset(self):
		moveset = []

		#Rightwards movement
		directions = 	[
				(1,0), 
                                (-1,0),
                                (0,1),
                                (0,-1),

				(1,1),
				(-1,-1),
				(1,-1),
				(-1,1) 
				]	
		for mod in directions:
			count = 1
			keep_going = True
			while keep_going:
				new_pos = (self.position[0]+(count*mod[0]),self.position[1]+(count*mod[1]))
				mov_piece = game_board.pieceAtLoc(self,new_pos)
				if mov_piece == "enemy" or mov_piece == "none":
					moveset.append(new_pos)

				if mov_piece != "none":
					keep_going = False

				count+=1

		moveset = game_board.check_moveset(self,moveset)

		return moveset



class King(GamePiece):
	def __init__(self,owner,position):
		GamePiece.__init__(self,owner,position)
		GamePiece.loadImage(self,"king")


	#Debugging
	def __str__(self):
		return "K"


	def getMoveset(self):
		moveset = []

		directions = 	[
				(1,0), 
                                (-1,0),
                                (0,1),
                                (0,-1),

				(1,1),
				(-1,-1),
				(1,-1),
				(-1,1) 
				]	

		for mod in directions:
			if game_board.pieceAtLoc(self,(self.position[0]+mod[0],self.position[1]+mod[1])) == "enemy" or game_board.pieceAtLoc(self,(self.position[0]+mod[0],self.position[1]+mod[1])) == "none":
				moveset.append((self.position[0]+mod[0],self.position[1]+mod[1]))
		
		moveset = game_board.check_moveset(self,moveset)

		return moveset




class Link:

	def __init__(self, parent):
		self.top = Toplevel(parent)
		Label(self.top, text="Do you want to connect as a guest or host?").pack()

		h = Button(self.top, text="Host", command=self.host)
		g = Button(self.top, text="Guest", command=self.guest)
		h.pack(pady=5)
		g.pack(pady=5)


	def host(self):
		global user_player
		user_player = "host"

		HOST = ''
		PORT = 5770
		self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.s.bind((HOST, PORT))
		self.s.listen(1)
		self.connection, self.address = self.s.accept()

		self.top.destroy()

		self.send_key()
		self.get_key()


	def guest(self):
		global user_player
		user_player = "guest"

		HOST = 'localhost'
		PORT = 5770
		self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.s.connect((HOST, PORT))

		self.top.destroy()

		self.get_key()
		self.send_key()
	
	def get_key(self):
		data = self.connection.recv(1024) if user_player == "host" else self.s.recv(1024)
		data = data.decode()
		print(data)
		o_key = data.split(",")
		self.other_key = RSA.construct((int(o_key[0]),int(o_key[1])))

	def send_key(self):
		m_key = gen_key.gen_key(8)
		self.my_key = RSA.construct((m_key[0],m_key[1],m_key[2]))
		com = self.connection if user_player == "host" else self.s
		message = ",".join([str(m_key[0]),str(m_key[1])])
		message = message.encode()
		com.sendall(message)


	def get_move(self):
		data = self.connection.recv(1024) if user_player == "host" else self.s.recv(1024)
		data = data.decode() 
		pos = data.split(",")
		while True:
			try:
				pos = [self.my_key.decrypt(int(x))-2 for x in pos]
				break
			except:
				print("FAIL")
				pass
		print(pos)
		return [(pos[0],pos[1]) , (pos[2],pos[3])]

	def send_move(self,old_pos,new_pos):
		com = self.connection if user_player == "host" else self.s
		message = str(self.other_key.encrypt(old_pos[0]+2,"")[0]) + "," + str(self.other_key.encrypt(old_pos[1]+2,"")[0]) + "," + str(self.other_key.encrypt(new_pos[0]+2,"")[0]) + "," + str(self.other_key.encrypt(new_pos[1]+2,"")[0])
		print(message)
		message = message.encode()
		com.sendall(message)



link = Link(root)
root.withdraw()
root.wait_window(link.top)
root.deiconify()


game_board = Board()

root.mainloop()
if user_player == "host":
	link.connection.close()
else:
	link.s.close()

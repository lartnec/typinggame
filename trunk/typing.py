#! usr/bin/env python

# test args: 1000 100 10000

from Tkinter import *
from threading import Lock
from random import randint,choice
from math import ceil,floor,log10
from sys import argv
import importWordlist
import winsound

def intersect(l1,l2):
    ret_list = []
    for elem in l1:
        if elem in l2:
            ret_list.append(elem)
    return ret_list

wordlists = importWordlist.unpckle()
words = []
words.extend(wordlists[0][1:])
words.extend(wordlists[1][1:])
words.extend(wordlists[2][1:])

CENSOR = wordlists[3]

MOVE_SIZE = .5
MOVE_DELAY = 15
VANISH_DELAY = 200
CORRECT_COLOR = "green"
INCORRECT_COLOR = "red"
STRIKES = 3
LETTER_SPACING = 9

START_SPEED = MOVE_SIZE*1000/MOVE_DELAY
SPEED = START_SPEED

WIDTH=640
HEIGHT=300

DROP_DELAY = WIDTH / (4*SPEED) * 1000

KEYS = []
LETTERS = "'-.abcdefghijklmnopqrstuvwxyz"
ON_CANVAS = []
DROP_WORDS = 1
WORDS_BE = 1
WORDS_PG = 1
WORDS_MF = 1
PG_LIST = 10000
MF_LIST = 2000

drop_id = 0

root = Tk()
event_lock = Lock()

score=IntVar(root,value=0)
strikes=StringVar(root,value='')

sounds=IntVar(root,value=1)

letters = StringVar(root,value=LETTERS)

drop_words = IntVar(root,value=DROP_WORDS)
words_BE = IntVar(root,value=WORDS_BE)
words_PG = IntVar(root,value=WORDS_PG)
words_MF = IntVar(root,value=WORDS_MF)
PG_list = IntVar(root,value=PG_LIST)
MF_list = IntVar(root,value=MF_LIST)

c = Canvas(root,width=WIDTH,height=HEIGHT,bg="white")
c.pack()

set_speed = False
for arg in sys.argv[1:]:
    if arg == "-UNCENSOR" or arg == "-U":
        CENSOR = []
    if set_speed:
        START_SPEED = arg
        SPEED = START_SPEED
        MOVE_SIZE = SPEED * MOVE_DELAY / 1000
        set_speed = False
    if arg == "-s":
        set_speed = True
    if arg == "-h" or arg == "-?" or arg == "--help":
        print """
        Options are:
        -UNCENSOR, -U     Play without filtering wordlist for naughty words
        -s xxx            Begin with speed xxx
        -h, -?, --help    Display this help message
        """

WORDS = []
for word in words:
    lowword = list(word.lower())
    if intersect(lowword,list(LETTERS)) == lowword and word.lower() not in CENSOR:
        WORDS.append(word)
if not WORDS:
    WORDS = words

def print_state():
    print repr(DROP_WORDS)+" "+repr(WORDS_BE)+" "+repr(WORDS_PG*PG_LIST)+" "+repr(WORDS_MF*MF_LIST)+" "+LETTERS

def add_to_score(coords,lpts):
    global SPEED
    global DROP_DELAY
    global MOVE_SIZE
    dpts = floor(coords[0]/100)
    spts = floor(SPEED/30)
    score.set(score.get()+dpts*spts*lpts)
    SPEED += dpts
    DROP_DELAY = WIDTH/(4*SPEED)*1000
    MOVE_SIZE = SPEED*MOVE_DELAY/1000


class Word:
    def __init__(self, text="", canvas = None):
        self.word = text
        self.letters = []
        self.letterids = []
        self.c = canvas
        self.index = 0
        self.tag = self.word
        self.move_id = 0
    def __str__(self):
        return self.word
    def place(self, x, y):
        self.tag = self.word+repr(y)
        counter = 0
        for char in self.word:
            counter += LETTER_SPACING
            self.letterids.append(self.c.create_text(x+counter,y,font="Courier",text=char,anchor=NW,tags=self.tag))
    def move(self, dx, dy):
        self.c.move(self.tag,dx,dy)
    def check(self, letter):
        global ON_CANVAS
        if letter == self.word[self.index]:
            self.c.itemconfig(self.letterids[self.index],fill=CORRECT_COLOR)
            self.index += 1
            if sounds.get() == 1: winsound.PlaySound('typewriter.wav', winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_NOWAIT)
            if self.index == len(self.word):
                add_to_score(self.coords(),len(self.word))
                self.vanish()
                del ON_CANVAS[0]
            return True
        else:
            self.set_color(INCORRECT_COLOR)
            return False
    def vanish(self, delay = VANISH_DELAY):
        root.after_cancel(self.move_id)
        root.after(delay, self.c.delete, self.tag)
    def coords(self):
        return self.c.coords(self.letterids[len(self.word)-1])
    def set_color(self, color):
        self.c.itemconfig(self.tag,fill=color)

def keydown(event):
    global KEYS
    global ON_CANVAS
    global drop_id
    event_lock.acquire()
    symbol = event.keysym
    if symbol not in KEYS:
        KEYS.append(symbol)
        if symbol == "Return" and drop_id is not 0:
            drop()
        elif len(event.char) == 1 and ON_CANVAS:
            if not ON_CANVAS[0].check(event.char):
                strikes.set(strikes.get()+'X')
                if len(strikes.get()) == STRIKES:
                    c.itemconfig(ALL,fill=INCORRECT_COLOR)
                    while ON_CANVAS:
                        root.after_cancel(ON_CANVAS[0].move_id)
                        del ON_CANVAS[0]
                    root.after_cancel(drop_id)
                    drop_id = 0
                else:
                    ON_CANVAS[0].vanish()
                    del ON_CANVAS[0]
    event_lock.release()

def keyup(event):
    global KEYS
    event_lock.acquire()
    symbol = event.keysym
    if symbol in KEYS:
        KEYS.remove(symbol)
    event_lock.release()

def drop(text='',repeat_delay=0):
    global ON_CANVAS
    global drop_id
    if text == '':
        if DROP_WORDS:
            text = choice(WORDS)
        else:
            text = choice(list(LETTERS))
    obj = Word(text,c)
    obj.place(WIDTH,randint(0,HEIGHT-20))
    obj.move_id=root.after(MOVE_DELAY,move,obj)
    ON_CANVAS.append(obj)
    if repeat_delay > 0:
        drop_id = root.after(repeat_delay,drop,'',randint(ceil(DROP_DELAY*.5),floor(DROP_DELAY*1.5)))

def move(obj):
    global ON_CANVAS
    obj.move(-MOVE_SIZE,0)
    if obj.coords()[0] > 0:
        obj.move_id = root.after(MOVE_DELAY,move,obj)
    else:
        score.set(max(score.get()-floor(log10(SPEED)),0))
        obj.vanish(0)
        del ON_CANVAS[0]

def reset():
    global MOVE_SIZE
    global MOVE_DELAY
    global SPEED
    global DROP_DELAY
    global ON_CANVAS
    global drop_id
    global LETTERS
    global DROP_WORDS
    global WORDS_BE
    global WORDS_PG
    global WORDS_MF
    global PG_LIST
    global MF_LIST
    global WORDS
    event_lock.acquire()
    root.after_cancel(drop_id)
    MOVE_SIZE = .5
    MOVE_DELAY = 15
    SPEED = START_SPEED
    MOVE_SIZE = SPEED * MOVE_DELAY / 1000
    DROP_DELAY = WIDTH / (4*SPEED) * 1000
    drop_id = 0
    score.set(0)
    strikes.set('')
    c.delete(ALL)
    while ON_CANVAS:
        root.after_cancel(ON_CANVAS[0].move_id)
        del ON_CANVAS[0]
    LETTERS = letters.get()
    LETTERS = [x for x in LETTERS.lower() if x not in locals()['_[1]']]
    LETTERS.sort()
    LETTERS = ''.join(LETTERS)
    letters.set(LETTERS)
    DROP_WORDS = drop_words.get()
    WORDS_BE = words_BE.get()
    WORDS_PG = words_PG.get()
    WORDS_MF = words_MF.get()
    PG_LIST = PG_list.get()
    MF_LIST = MF_list.get()
    words = []
    if WORDS_BE:
        words.extend(wordlists[1][1:])
    if WORDS_PG:
        words.extend(wordlists[0][1:PG_LIST+1])
    if WORDS_MF:
        words.extend(wordlists[2][1:MF_LIST+1])
    WORDS = []
    for word in words:
        lowword = list(word.lower())
        if intersect(lowword,list(LETTERS)) == lowword and word.lower() not in CENSOR:
            WORDS.append(word.lower())
    if not WORDS:
        WORDS = wordlists[0][1:]
        WORDS.extend(wordlists[1][1:])
        WORDS.extend(wordlists[2][1:])
    drop_id = root.after(1000,drop,'',randint(ceil(DROP_DELAY*.5),floor(DROP_DELAY*1.5)))
    print_state()
    root.focus_set()
    event_lock.release()

def use_words():
    event_lock.acquire()
    if drop_words.get():
        set_state(word_buttons,NORMAL)
    else:
        set_state(word_buttons,DISABLED)
    event_lock.release()

def use_PG():
    if words_PG.get():
        set_state(PG_buttons,NORMAL)
    else:
        set_state(PG_buttons,DISABLED)

def use_MF():
    if words_MF.get():
        set_state(MF_buttons,NORMAL)
    else:
        set_state(MF_buttons,DISABLED)

def set_state(list,newstate):
    for button in list:
        button.configure(state=newstate)

root.bind("<KeyPress>",keydown)
root.bind("<KeyRelease>",keyup)
drop_id = root.after(1000,drop,'',randint(ceil(DROP_DELAY*.5),floor(DROP_DELAY*1.5)))

score_frame = Frame(root)
Label(score_frame,text="Score: ").pack(anchor=NW,side=LEFT)
Label(score_frame,textvariable=score).pack(anchor=NW,side=LEFT)
Checkbutton(score_frame,text="Sound effects",var=sounds).pack(anchor=NW,side=LEFT)
score_frame.pack(anchor=NW)

strikes_frame = Frame(root)
Label(strikes_frame,text="Strikes: ").pack(anchor=NW,side=LEFT)
Label(strikes_frame,textvariable=strikes).pack(anchor=NW,side=LEFT)
strikes_frame.pack(anchor=NW)

letters_frame = Frame(root)
Entry(letters_frame,textvariable=letters,width=30).pack(anchor=NW,side=LEFT)
Button(letters_frame,command=reset,text="Start a New Game").pack(anchor=NW,side=LEFT)
letters_frame.pack(anchor=NW)

word_buttons = []
words_frame = LabelFrame(root,text="Words")
BE_col = 1
BE_row = 1
PG_col = 3
PG_row = 1
MF_col = 1
MF_row = 2
words_frame.grid_columnconfigure(0,minsize=20)
words_frame.grid_columnconfigure(PG_col,minsize=20)
words_frame.grid_columnconfigure(MF_col,minsize=20)
words_frame.grid_columnconfigure(PG_col+1,weight=1)
words_frame.grid_columnconfigure(MF_col+1,weight=1)

Checkbutton(words_frame,text="Use words",command=use_words,var=drop_words).grid(column=0,row=0,columnspan=6,sticky=W)

word_buttons.append(Checkbutton(words_frame,text="Basic English",var=words_BE))
word_buttons[-1].grid(column=BE_col,row=BE_row,sticky=W,columnspan=2)

word_buttons.append(Checkbutton(words_frame,text="Public Domain Literature",var=words_PG,command=use_PG))
word_buttons[-1].grid(column=PG_col,row=PG_row,sticky=W,columnspan=2)
PG_buttons = []

word_buttons.append(Radiobutton(words_frame,text="100",var=PG_list,value=100))
word_buttons[-1].grid(column=PG_col+1,row=PG_row+1,sticky=W)
PG_buttons.append(word_buttons[-1])
word_buttons.append(Radiobutton(words_frame,text="200",var=PG_list,value=200))
word_buttons[-1].grid(column=PG_col+1,row=PG_row+2,sticky=W)
PG_buttons.append(word_buttons[-1])
word_buttons.append(Radiobutton(words_frame,text="500",var=PG_list,value=500))
word_buttons[-1].grid(column=PG_col+1,row=PG_row+3,sticky=W)
PG_buttons.append(word_buttons[-1])
word_buttons.append(Radiobutton(words_frame,text="1000",var=PG_list,value=1000))
word_buttons[-1].grid(column=PG_col+1,row=PG_row+4,sticky=W)
PG_buttons.append(word_buttons[-1])
word_buttons.append(Radiobutton(words_frame,text="2000",var=PG_list,value=2000))
word_buttons[-1].grid(column=PG_col+1,row=PG_row+5,sticky=W)
PG_buttons.append(word_buttons[-1])
word_buttons.append(Radiobutton(words_frame,text="5000",var=PG_list,value=5000))
word_buttons[-1].grid(column=PG_col+1,row=PG_row+6,sticky=W)
PG_buttons.append(word_buttons[-1])
word_buttons.append(Radiobutton(words_frame,text="10000",var=PG_list,value=10000))
word_buttons[-1].grid(column=PG_col+1,row=PG_row+7,sticky=W)
PG_buttons.append(word_buttons[-1])

word_buttons.append(Checkbutton(words_frame,text="Modern Fiction",var=words_MF,command=use_MF))
word_buttons[-1].grid(column=MF_col,row=MF_row,sticky=W,columnspan=2)
MF_buttons = []

word_buttons.append(Radiobutton(words_frame,text="100",var=MF_list,value=100))
word_buttons[-1].grid(column=MF_col+1,row=MF_row+1,sticky=W)
MF_buttons.append(word_buttons[-1])
word_buttons.append(Radiobutton(words_frame,text="200",var=MF_list,value=200))
word_buttons[-1].grid(column=MF_col+1,row=MF_row+2,sticky=W)
MF_buttons.append(word_buttons[-1])
word_buttons.append(Radiobutton(words_frame,text="500",var=MF_list,value=500))
word_buttons[-1].grid(column=MF_col+1,row=MF_row+3,sticky=W)
MF_buttons.append(word_buttons[-1])
word_buttons.append(Radiobutton(words_frame,text="1000",var=MF_list,value=1000))
word_buttons[-1].grid(column=MF_col+1,row=MF_row+4,sticky=W)
MF_buttons.append(word_buttons[-1])
word_buttons.append(Radiobutton(words_frame,text="2000",var=MF_list,value=2000))
word_buttons[-1].grid(column=MF_col+1,row=MF_row+5,sticky=W)
MF_buttons.append(word_buttons[-1])

words_frame.pack(anchor=NW)

print_state()

root.title("A simple typing game")
root.configure(padx=10,pady=10)
root.resizable(False,False)
root.deiconify()
root.focus_set()
root.geometry("+0+0")
root.mainloop()

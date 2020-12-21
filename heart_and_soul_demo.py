from mido import MidiFile
import mido
import time
import matplotlib.pyplot as plt
import musicalbeeps as mb
import RPi.GPIO as GPIO

##setup raspberry pi GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(FALSE)

GPIO.setup(2, GPIO.OUT)

##setup sound player
class NotePlayer(mb.Player):
    def __init__(self, volume, mute_output=False, end_time = -1.0):
        self.end_time = end_time
        mb.Player.__init__(self, volume, mute_output)
        
class MyNote:
    def __init__(self, channel=-1, start_time=-1, end_time=-1, note=-1, velocity=64):
        self.channel = channel
        self.start_time = start_time
        self.end_time = end_time
        self.velocity = velocity
        self.duration = self.start_time - self.end_time
        self.note = note


midi_notes = ['C-1','D-1b','D-1','E-1b','E-1','F-1','G-1b','G-1','A-1b','A-1','B-1b','B-1','C-1','D-1b','D-1','E-1b','E-1','F-1','G-1b','G-1','A-1b','A-1','B-1b','B-1',
         'C0','D0b','D0','E0b','E0','F0','G0b','G0','A0b','A0','B0b','B0','C1','D1b','D1','E1b','E1','F1','G1b','G1','A1b','A1','B1b','B1','C2','D2b','D2','E2b','E2','F2',
         'G2b','G2','A2b','A2','B2b','B2','C3','D3b','D3','E3b','E3','F3','G3b','G3','A3b','A3','B3b','B3','C4','D4b','D4','E4b','E4','F4','G4b','G4','A4b','A4','B4b',
         'B4','C5','D5b','D5','E5b','E5','F5','G5b','G5','A5b','A5','B5b','B5','C6','D6b','D6','E6b','E6','F6','G6b','G6','A6b','A6','B6b','B6','C7','D7b','D7','E7b','E7',
         'F7','G7b','G7','A7b','A7','B7b','B7','C8','D8b','D8','E8b','E8','F8','G8b','G8',
        ]


player1 = NotePlayer(volume=0.3)
player2 = NotePlayer(volume=0.3)
player3 = NotePlayer(volume=0.3)
player4 = NotePlayer(volume=0.3)
player5 = NotePlayer(volume=0.3)
players = []
players.append(player1)
players.append(player2)
players.append(player3)
players.append(player4)
players.append(player5)    

mid = MidiFile('heart_and_soul.mid', clip=True)

track = mid.tracks[0]
#unfortunately I hardcoded this but the tempo and the bpm are listed in the meta messages
secondPerTick = mido.tick2second(1, 480, 461538) #each tick is this many seconds (multiply to slow down the song)



note_dict = {k:0 for k in range(0,128)} #make a dictionary to store the on/off nature of each note
a = time.time()
for message in track:
    if not message.is_meta:
        try:
            if message.channel == 0:
                time.sleep(message.time * secondPerTick)
                try:
                    if message.velocity > 0:
                        note_dict[message.note] = 1
                        print("ON: Time: %s Note: %s"%(message.time, message.note))
                    if message.velocity == 0 or message.type == 'note_off':
                        note_dict[message.note] = 0
                        print("OFF: Time: %s Note: %s"%(message.time, message.note))
                except:
                    pass
                print(note_dict[message.note])
                plt.bar(note_dict.keys(), note_dict.values())
                plt.show()
        except:
            pass
print(time.time() - a)

##convert the time value to absolute time in seconds since the beginning of the song        
begin = 0.0
mid2 = MidiFile('heart_and_soul.mid', clip=True)
track_abs = mid2.tracks[0]
unended_notes = {}
all_notes = []
       
for message in track_abs:
    try:
        message.time = begin + message.time * secondPerTick
        begin = message.time
        if message.note in unended_notes.keys() and message.channel==0:
            unended_notes[message.note].end_time = message.time
            all_notes.append(unended_notes[message.note])
            unended_notes.pop(message.note)
        elif message.channel==0:
            note = MyNote(channel=message.channel, start_time=begin, note=message.note, velocity=message.velocity)
            unended_notes[message.note] = note
        print("Time: %s Note: %s"%(message.time, message.note))
    except:
        pass
    
all_notes.sort(key=lambda x: x.start_time)
for note in all_notes:
    note.duration = note.end_time - note.start_time
 
##iterate along a list of notes sorted by start_time and play each one when its time comes
elapsed_time = 0
play_start = time.time()
note_index = 0
note_counter = 0
while elapsed_time < (all_notes[-1].end_time + 1) and note_index < len(all_notes):
    if round(all_notes[note_index].start_time, 4) <= round(time.time() - play_start, 4):
        duration = round(all_notes[note_index].end_time - all_notes[note_index].start_time, 4)
        print("Note: %s"%note_index)
        for player in players:
            if player.end_time < time.time()-play_start:
                note_to_play = midi_notes[all_notes[note_index].note]
                player.play_note(note_to_play, duration)
                player.end_time = time.time()-play_start + duration
                note_counter += 1
                break
        note_index = note_index + 1
    elapsed_time = time.time() - play_start
    print(elapsed_time)

"""Soundtrack for ep29 (hotel corridor: key card keeps flashing red, wrong door, Wren reads the sleeve). Original, synthesised with numpy. 19.8 s, 44.1 kHz."""
import numpy as np, wave, os
SR=44100; T=19.8; n=int(SR*T); out=np.zeros(n)
OUT=os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),"..","build","ep29")); os.makedirs(OUT,exist_ok=True)
rng=np.random.default_rng(29)
def add(t0,sig,g=1.0):
    i=int(t0*SR); j=min(n,i+len(sig))
    if 0<=i<n: out[i:j]+=sig[:j-i]*g
def env(d): return np.arange(int(SR*d))/SR
def ep(f,d=0.6):                                         # soft electric-piano (lobby muzak)
    t=env(d); return (np.sin(2*np.pi*f*t)+0.35*np.sin(2*np.pi*2*f*t)*np.exp(-t*6))*np.exp(-t*3)*(1-np.exp(-t*400))
def bass(f,d=0.35):
    t=env(d); return np.sin(2*np.pi*f*t)*np.exp(-t*5)*(1-np.exp(-t*300))
def shaker(d=0.06):
    x=rng.normal(size=int(SR*d)); x=np.diff(x,prepend=0); t=env(d); return x*np.exp(-t*60)
def bonk():                                              # key-card error buzz
    t=env(0.35); return np.sign(np.sin(2*np.pi*180*t))*0.5*np.exp(-t*6)*(np.sin(2*np.pi*14*t)>0)
def beep(f=1760,d=0.12):
    t=env(d); return np.sin(2*np.pi*f*t)*np.minimum(1,(d-t)/0.02)
def slide(f0,f1,d=0.6):
    t=env(d); f=f0+(f1-f0)*(t/d); ph=2*np.pi*np.cumsum(f)/SR
    return (np.sin(ph)+0.4*np.sin(2*ph)+0.2*np.sin(3*ph))*np.minimum(1,t*30)*np.exp(-t*1.2)
def click():
    t=env(0.05); return rng.normal(size=len(t))*np.exp(-t*150)
def creak(d=0.6):
    t=env(d); f=320+120*np.sin(2*np.pi*3*t); ph=2*np.pi*np.cumsum(f)/SR
    return np.tanh(3*np.sin(ph))*np.sin(np.pi*t/d)*(0.6+0.4*np.sin(2*np.pi*31*t))
def puff(d=0.3):
    x=rng.normal(size=int(SR*d)); t=env(d); y=np.convolve(x,np.ones(40)/40,'same'); return y*np.sin(np.pi*t/d)*3
def step(): t=env(0.1); return np.sin(2*np.pi*80*t)*np.exp(-t*40)
# bossa-ish lobby groove, 112 bpm, Fmaj7 - Gm7 - C7 - Fmaj7, 0 - 16.6
b=60/112
chords=[(87.31,[349.23,440.0,523.25,659.25]),(98.0,[392.0,466.16,587.33,698.46]),(130.81,[329.63,392.0,466.16,587.33]),(87.31,[349.23,440.0,523.25,659.25])]
t=0;k=0
while t<16.4:
    root,ch=chords[(k//4)%4]
    add(t,bass(root),0.4); add(t+b*0.75,bass(root*1.5,0.25),0.25)
    if k%2==0:
        for f in ch: add(t+b*0.5,ep(f,0.5),0.035)
    else:
        for f in ch: add(t,ep(f,0.4),0.03)
    add(t,shaker(),0.05); add(t+b/2,shaker(),0.08)
    k+=1; t+=b
# s0 (0.0): three error buzzes on the taps
for tp in (0.5,1.5,2.5): add(tp,bonk(),0.12)
# s1 (3.8): footsteps to reception, puff, buzzes, card-dealing clicks
add(3.8+0.2,puff(),0.15)
for tp in (0.9,2.1,3.3): add(3.8+tp,bonk(),0.12)
for j in range(5): add(3.8+0.4+j*0.75,click(),0.25)
for j in range(6): add(3.8+1.3+j*0.12,step(),0.25)
# s2 (8.2): lock clunk, creaky door, sad descending slide
add(8.2+0.5,click(),0.4); add(8.2+0.6,creak(),0.08)
add(8.2+1.5,slide(392,330,0.35),0.08); add(8.2+1.9,slide(330,277,0.35),0.08); add(8.2+2.3,slide(277,196,0.9),0.09)
# s3 (12.6): paper rustle on the sleeve, success double-beep, unlock click, warm chord
add(12.6+0.2,puff(0.2),0.08)
add(12.6+2.0,beep(1760),0.1); add(12.6+2.15,beep(2349),0.1); add(12.6+2.1,click(),0.3)
for f in (523.25,659.25,783.99,987.77): add(12.6+2.4,ep(f,1.2),0.06)
# end card (16.6): bright resolve
for f in (87.31,174.61,349.23,440.0,523.25,659.25): add(16.6,ep(f,3.0),0.07)
for j,f in enumerate((698.46,880.0,1046.5,1318.5)): add(16.8+j*0.15,ep(f,1.5),0.05)
out*=np.minimum(1,(T-np.arange(n)/SR)/0.8); out=out/np.abs(out).max()*0.8
w=wave.open(os.path.join(OUT,'music_ep29.wav'),'wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((out*32767).astype(np.int16).tobytes()); w.close()

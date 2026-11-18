"""Soundtrack for ep23 (supermarket self-checkout). Original, synthesised with numpy. 19.8 s, 44.1 kHz."""
import numpy as np, wave, os
SR=44100; T=19.8; n=int(SR*T); out=np.zeros(n)
OUT=os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),"..","build","ep23")); os.makedirs(OUT,exist_ok=True)
rng=np.random.default_rng(23)
def add(t0,sig,g=1.0):
    i=int(t0*SR); j=min(n,i+len(sig))
    if 0<=i<n: out[i:j]+=sig[:j-i]*g
def ep(f,d=0.6,dec=4):                               # electric-piano-ish
    t=np.arange(int(SR*d))/SR; s=np.sin(2*np.pi*f*t+0.8*np.sin(2*np.pi*f*t)*np.exp(-t*6))
    return s*np.exp(-t*dec)*(1-np.exp(-t*400))
def bass(f,d=0.4):
    t=np.arange(int(SR*d))/SR; return (np.sin(2*np.pi*f*t)+0.25*np.sin(4*np.pi*f*t))*np.exp(-t*5)*(1-np.exp(-t*300))
def tick(d=0.04,dec=90):
    m=int(SR*d); x=np.diff(rng.normal(size=m),prepend=0); return x*np.exp(-np.arange(m)/SR*dec)
def beep(f=2093,d=0.12):                             # barcode scanner
    t=np.arange(int(SR*d))/SR; return np.sin(2*np.pi*f*t)*np.minimum(1,t*500)*np.minimum(1,(d-t)*500)
def buzz(f=110,d=0.35):                              # error buzzer
    t=np.arange(int(SR*d))/SR; return np.sign(np.sin(2*np.pi*f*t))*0.5*np.minimum(1,t*300)*np.minimum(1,(d-t)*300)
def chime(f1=659.25,f2=523.25):                      # ding-dong
    return np.concatenate([ep(f1,0.35,3)[:int(SR*0.3)],ep(f2,0.7,3)])
def rattle(d=0.5):
    m=int(SR*d); x=rng.normal(size=m)*(np.sin(np.arange(m)/SR*2*np.pi*28)>0.3); t=np.arange(m)/SR; return x*np.minimum(1,t*20)*np.minimum(1,(d-t)*8)*0.6
def kaching():
    a=ep(2637,0.6,5)+ep(3136,0.6,5)*0.7; m=int(SR*0.12); b=np.zeros(len(a)); b[:m]=np.diff(rng.normal(size=m),prepend=0)*np.exp(-np.arange(m)/SR*40)
    return a+b
def slide(f0,f1,d=0.6):
    t=np.arange(int(SR*d))/SR; f=f0+(f1-f0)*(t/d); ph=2*np.pi*np.cumsum(f)/SR
    return (np.sin(ph)+0.3*np.sin(2*ph))*np.minimum(1,t*30)*np.exp(-t*1.5)
# easy-listening supermarket bossa, 110 bpm, F major
b=60/110
prog=[(87.31,[349.23,440.0,523.25,659.25]),(73.42,[293.66,349.23,440.0,523.25]),(98.0,[293.66,349.23,440.0,587.33]),(65.41,[329.63,392.0,466.16,587.33])]
t=0;bar=0
while t<16.4:
    root,ch=prog[bar%4]
    for off,mul in ((0,1),(1.5,1.5),(2,1),(3.5,1.5)): add(t+off*b,bass(root*mul),0.5)
    for off in (0.5,1.5,2.5,3.0):
        for f in ch: add(t+off*b,ep(f,0.4,7),0.035)
    for k in range(8): add(t+k*b/2,tick(),0.04 if k%2 else 0.025)
    bar+=1; t+=4*b
mel=[880,0,783.99,698.46,0,659.25,698.46,0, 587.33,0,698.46,880,0,1046.5,0,0, 932.33,0,880,783.99,0,698.46,783.99,0, 659.25,0,698.46,783.99,0,880,0,0]
t=0;i=0
while t<16.2:
    f=mel[i%32]
    if f: add(t,ep(f,0.5,5),0.13)
    i+=1; t+=b/2
# s0 (0.0): scan beep at 0.95, error buzzer when banana lands at 1.7
add(0.95,beep(),0.35); add(1.7,buzz(),0.32); add(1.7+0.38,buzz(98),0.3); add(2.3,slide(500,320,0.4),0.1)
# s1 (3.8): every toggle answered by buzzer or 'please place' blip, getting more frantic
for k in range(8):
    tt=3.8+0.3+(k+1)*0.42
    if tt<3.8+4.4: add(tt,buzz(110+8*k,0.2) if k%2 else beep(1318.5,0.1),0.28)
add(3.8+3.0,slide(330,700,0.35),0.14)
# s2 (8.2): help-light chimes, trolleys rattle in, 'witnesses' sting
for k in range(3): add(8.2+0.3+k*1.0,chime(),0.22); add(8.2+0.2+k*0.6,rattle(),0.15)
add(8.2+2.9,ep(1396.9,0.5,6),0.2); add(8.2+3.0,ep(1760,0.5,6),0.2)
# s3 (12.6): cheerful walk, belt, single beep, ka-ching
add(12.6+0.6,slide(400,600,0.3),0.08); add(12.6+1.2,beep(),0.3); add(12.6+1.3,kaching(),0.22)
for k,f in enumerate((698.46,880,1046.5,1396.9)): add(12.6+2.85+k*0.08,ep(f,0.8,4),0.16)
# end card (16.6)
for f in (87.31,174.61,349.23,440,523.25,659.25): add(16.6,ep(f,2.8,1.4),0.2)
add(17.1,ep(1396.9,2,2.5),0.12); add(17.6,beep(),0.12)
out*=np.minimum(1,(T-np.arange(n)/SR)/0.8); out=out/np.abs(out).max()*0.8
w=wave.open(os.path.join(OUT,'music_ep23.wav'),'wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((out*32767).astype(np.int16).tobytes()); w.close()

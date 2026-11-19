"""Soundtrack for ep24 (airport security soup). Original, synthesised with numpy. 19.8 s, 44.1 kHz."""
import numpy as np, wave, os
SR=44100; T=19.8; n=int(SR*T); out=np.zeros(n)
OUT=os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),"..","build","ep24")); os.makedirs(OUT,exist_ok=True)
rng=np.random.default_rng(24)
def add(t0,sig,g=1.0):
    i=int(t0*SR); j=min(n,i+len(sig))
    if 0<=i<n: out[i:j]+=sig[:j-i]*g
def pluck(f,d=0.5,dec=6):                            # marimba-ish
    t=np.arange(int(SR*d))/SR; return (np.sin(2*np.pi*f*t)+0.3*np.sin(2*np.pi*4*f*t)*np.exp(-t*30))*np.exp(-t*dec)*(1-np.exp(-t*500))
def bass(f,d=0.35):
    t=np.arange(int(SR*d))/SR; return (np.sin(2*np.pi*f*t)+0.3*np.sin(4*np.pi*f*t))*np.exp(-t*6)*(1-np.exp(-t*300))
def tick(d=0.03,dec=120):
    m=int(SR*d); x=np.diff(rng.normal(size=m),prepend=0); return x*np.exp(-np.arange(m)/SR*dec)
def beep(f=1760,d=0.1):
    t=np.arange(int(SR*d))/SR; return np.sin(2*np.pi*f*t)*np.minimum(1,t*500)*np.minimum(1,(d-t)*500)
def alarm(d=0.9):                                    # two-tone security alarm
    t=np.arange(int(SR*d))/SR; f=np.where((t*6).astype(int)%2==0,880,660); ph=2*np.pi*np.cumsum(f)/SR
    return np.sign(np.sin(ph))*0.4*np.minimum(1,t*200)*np.minimum(1,(d-t)*30)
def whir(d=1.0):                                     # conveyor belt
    t=np.arange(int(SR*d))/SR; return (np.sin(2*np.pi*90*t)*0.5+rng.normal(size=len(t))*0.15)*np.minimum(1,t*8)*np.minimum(1,(d-t)*8)
def glug(f0=300):                                    # pouring blip
    d=0.11; t=np.arange(int(SR*d))/SR; f=f0+900*t/d; ph=2*np.pi*np.cumsum(f)/SR; return np.sin(ph)*np.exp(-t*20)
def slide(f0,f1,d=0.5):
    t=np.arange(int(SR*d))/SR; f=f0+(f1-f0)*(t/d); ph=2*np.pi*np.cumsum(f)/SR
    return (np.sin(ph)+0.3*np.sin(2*ph))*np.minimum(1,t*30)*np.exp(-t*1.5)
def pop():
    d=0.08; t=np.arange(int(SR*d))/SR; f=500+1500*t/d; return np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*30)
# sneaky-cheerful march, 120 bpm, D minor -> F major
b=0.5
prog=[(73.42,[293.66,349.23,440.0]),(73.42,[293.66,349.23,440.0]),(58.27,[293.66,349.23,466.16]),(65.41,[261.63,329.63,392.0])]
t=0;bar=0
while t<16.4:
    root,ch=prog[bar%4]
    for k in range(4): add(t+k*b,bass(root if k%2==0 else root*1.5),0.5)
    for k in (1,3):
        for f in ch: add(t+k*b,pluck(f,0.3,10),0.05)
    for k in range(8): add(t+k*b/2,tick(),0.05 if k%2 else 0.02)
    bar+=1; t+=4*b
mel=[587.33,0,698.46,0,880,0,698.46,587.33, 554.37,0,659.25,0,880,0,0,0, 466.16,0,587.33,0,698.46,0,587.33,466.16, 523.25,0,659.25,0,783.99,0,0,0]
t=0;i=0
while t<16.2:
    f=mel[i%32]
    if f: add(t,pluck(f,0.4,7),0.14)
    i+=1; t+=b/2
# s0 (0.0): belt whir, scan beep, alarm when the jar shows at 1.2
add(0.1,whir(1.1),0.12); add(0.8,beep(),0.25); add(1.2,alarm(0.9),0.22); add(2.2,slide(500,350,0.35),0.1)
# s1 (3.8): stern 'dun dun' when officer raises the bottle, 'challenge accepted' sting
add(3.8+0.5,bass(98,0.5),0.7); add(3.8+0.8,bass(73.42,0.7),0.7); add(3.8+2.6,slide(330,880,0.35),0.15)
# s2 (8.2): a glug + pop for every one of the 20 bottles
for i in range(20): add(8.2+0.35+i*0.12,glug(260+i*12),0.14); add(8.2+0.35+i*0.12+0.06,pop(),0.05)
add(8.2+2.95,pluck(1174.66,0.6,4),0.2); add(8.2+3.05,pluck(1396.91,0.6,4),0.2)
# s3 (12.6): a happy chime for each person served, slurp, laugh-ish run
for k in range(3):
    for j,f in enumerate((783.99,987.77,1174.66)): add(12.6+0.5+k*0.55+j*0.05,pluck(f,0.5,5),0.12)
add(12.6+2.2,slide(700,300,0.3),0.1)
for k,f in enumerate((698.46,880,1046.5,1396.91)): add(12.6+2.9+k*0.08,pluck(f,0.8,4),0.16)
# end card (16.6)
for f in (87.31,174.61,349.23,440,523.25,659.25): add(16.6,pluck(f,3.0,1.3),0.2)
add(17.1,pluck(1396.91,2,2.5),0.12)
out*=np.minimum(1,(T-np.arange(n)/SR)/0.8); out=out/np.abs(out).max()*0.8
w=wave.open(os.path.join(OUT,'music_ep24.wav'),'wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((out*32767).astype(np.int16).tobytes()); w.close()

"""Soundtrack for ep25 (country road trip, GPS vs paper map). Original, synthesised with numpy. 19.8 s, 44.1 kHz."""
import numpy as np, wave, os
SR=44100; T=19.8; n=int(SR*T); out=np.zeros(n)
OUT=os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),"..","build","ep25")); os.makedirs(OUT,exist_ok=True)
rng=np.random.default_rng(25)
def add(t0,sig,g=1.0):
    i=int(t0*SR); j=min(n,i+len(sig))
    if 0<=i<n: out[i:j]+=sig[:j-i]*g
def pluck(f,d=0.5,dec=6):                                # banjo-ish pluck
    t=np.arange(int(SR*d))/SR; return (np.sin(2*np.pi*f*t)+0.45*np.sin(2*np.pi*2*f*t)*np.exp(-t*12)+0.2*np.sin(2*np.pi*3*f*t)*np.exp(-t*25))*np.exp(-t*dec)*(1-np.exp(-t*800))
def bass(f,d=0.3):
    t=np.arange(int(SR*d))/SR; return (np.sin(2*np.pi*f*t)+0.3*np.sin(4*np.pi*f*t))*np.exp(-t*7)*(1-np.exp(-t*300))
def tick(d=0.03,dec=140):
    m=int(SR*d); x=np.diff(rng.normal(size=m),prepend=0); return x*np.exp(-np.arange(m)/SR*dec)
def chime(f1,f2):                                        # two-note sat-nav chime
    return np.concatenate([pluck(f1,0.14,8)[:int(SR*0.12)],pluck(f2,0.5,6)])
def baa(f=330,d=0.55):                                   # synth sheep
    t=np.arange(int(SR*d))/SR; vib=1+0.04*np.sin(2*np.pi*14*t); ph=2*np.pi*np.cumsum(f*vib*(1-0.15*t/d))/SR
    sig=np.sign(np.sin(ph))*0.5+np.sin(2*ph)*0.3; return sig*np.minimum(1,t*30)*np.minimum(1,(d-t)*12)*0.6
def rustle(d=0.14):                                      # paper unfold
    m=int(SR*d); x=rng.normal(size=m); x=np.diff(x,prepend=0); env=np.exp(-np.arange(m)/SR*25)*(1-np.exp(-np.arange(m)/SR*400)); return x*env
def crunch(d=0.2):
    m=int(SR*d); x=rng.normal(size=m)*(rng.random(m)<0.25); return x*np.exp(-np.arange(m)/SR*14)
def slide(f0,f1,d=0.5):
    t=np.arange(int(SR*d))/SR; f=f0+(f1-f0)*(t/d); ph=2*np.pi*np.cumsum(f)/SR
    return (np.sin(ph)+0.3*np.sin(2*ph))*np.minimum(1,t*30)*np.exp(-t*1.5)
# bouncy country shuffle, 132 bpm, G major
b=60/132
prog=[(98.0,[392.0,493.88,587.33]),(130.81,[392.0,523.25,659.25]),(98.0,[392.0,493.88,587.33]),(146.83,[369.99,440.0,587.33])]
t=0;bar=0
while t<16.4:
    root,ch=prog[bar%4]
    for k in range(4): add(t+k*b,bass(root if k%2==0 else root*1.5),0.5)
    for k in (1,3):
        for j,f in enumerate(ch): add(t+k*b+j*0.012,pluck(f,0.25,12),0.05)
    for k in range(8): add(t+k*b/2+(0.03 if k%2 else 0),tick(),0.05 if k%2 else 0.025)
    bar+=1; t+=4*b
mel=[783.99,0,739.99,783.99,880,0,783.99,0, 659.25,0,783.99,0,659.25,587.33,0,0, 783.99,0,739.99,783.99,880,987.77,0,880, 739.99,0,587.33,0,659.25,0,739.99,0]
t=0;i=0
while t<16.2:
    f=mel[i%32]
    if f: add(t,pluck(f,0.35,8),0.12)
    i+=1; t+=b/2
# s0 (0.0): sat-nav chime on every lap of the roundabout, rising slide when Wren spots the cow again
P=0.46
for k in range(7): add(max(0,k*P-0.12+0.02),chime(1046.5,783.99 if k<2 else 698.46),0.12)
add(2.3,slide(400,700,0.3),0.1)
# s1 (3.8): arrival jingle, then a chorus of baas as the sheep pop in
for j,f in enumerate((783.99,987.77,1174.66,1567.98)): add(3.8+0.05+j*0.07,pluck(f,0.5,5),0.13)
for k in range(9): add(3.8+0.25+k*0.24,baa(300+40*(k%4),0.45),0.07)
add(3.8+2.9,slide(500,800,0.3),0.1)
# s2 (8.2): a paper rustle for each of the 12 folds, pitch of a little pluck climbing
for k in range(12): add(8.2+0.3+k*0.2,rustle(),0.25); add(8.2+0.3+k*0.2,pluck(392*2**(k/12),0.25,10),0.08)
for j,f in enumerate((587.33,783.99,987.77,1174.66)): add(8.2+3.0+j*0.08,pluck(f,0.8,4),0.15)
# s3 (12.6): crunchy refold attempts, a deflating slide, then a cosy resolve
for k in range(9): add(12.6+0.3+k*0.29,crunch(),0.2)
add(12.6+2.4,slide(500,250,0.5),0.12)
for k,f in enumerate((587.33,739.99,880,1174.66)): add(12.6+2.75+k*0.08,pluck(f,0.8,4),0.15)
# end card (16.6)
for f in (98.0,196.0,392.0,493.88,587.33,783.99): add(16.6,pluck(f,3.0,1.3),0.2)
add(17.1,pluck(1567.98,2,2.5),0.1)
out*=np.minimum(1,(T-np.arange(n)/SR)/0.8); out=out/np.abs(out).max()*0.8
w=wave.open(os.path.join(OUT,'music_ep25.wav'),'wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((out*32767).astype(np.int16).tobytes()); w.close()

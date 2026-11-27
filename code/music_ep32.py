"""Soundtrack for ep32 (hotel shower: freezing, scalding, rogue hose, Wren waits 30 seconds). Original, synthesised with numpy. 19.8 s, 44.1 kHz."""
import numpy as np, wave, os
SR=44100; T=19.8; n=int(SR*T); out=np.zeros(n)
OUT=os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),"..","build","ep32")); os.makedirs(OUT,exist_ok=True)
rng=np.random.default_rng(32)
def add(t0,sig,g=1.0):
    i=int(t0*SR); j=min(n,i+len(sig))
    if 0<=i<n: out[i:j]+=sig[:j-i]*g
def env(d): return np.arange(int(SR*d))/SR
def pluck(f,d=0.3):                                     # marimba-ish pluck
    t=env(d); s=sum(a*np.sin(2*np.pi*f*k*t) for k,a in ((1,1),(4,.25),(10,.05)))
    return s*np.exp(-t*9)*(1-np.exp(-t*800))
def bass(f,d=0.32):
    t=env(d); return np.sin(2*np.pi*f*t)*np.exp(-t*5)*(1-np.exp(-t*300))
def tick(d=0.04):
    t=env(d); return np.sin(2*np.pi*2400*t)*np.exp(-t*120)
def water(d,bright=1.0):                                # shower hiss: smoothed noise
    t=env(d); w=rng.normal(size=len(t)); k=max(2,int(12/bright)); w=np.convolve(w,np.ones(k)/k,'same')
    return w*np.minimum(1,t*8)*np.minimum(1,(d-t)*8)
def brr(d=1.2):                                         # cold shiver: low tremolo buzz
    t=env(d); return np.sign(np.sin(2*np.pi*110*t))*0.4*(0.5+0.5*np.sin(2*np.pi*18*t))*np.exp(-t*1.2)
def sizzle(d=1.4):
    t=env(d); return rng.normal(size=len(t))*(0.5+0.5*np.sin(2*np.pi*23*t))*np.minimum(1,t*5)*np.exp(-t*1.0)
def zip_(f0,f1,d):
    t=env(d); f=f0+(f1-f0)*t/d; return np.sin(2*np.pi*np.cumsum(f)/SR)*np.sin(np.pi*t/d)
def splash():
    t=env(0.5); return rng.normal(size=len(t))*np.exp(-t*7)
def wah(f,d=0.5):
    t=env(d); s=sum(a*np.sin(2*np.pi*f*k*t) for k,a in ((1,1),(2,.6),(3,.4),(4,.2)))
    return s*np.minimum(1,t*20)*np.exp(-t*1.5)*(0.7+0.3*np.sin(2*np.pi*5*t))
def ding(f=1318.5,d=1.2):
    t=env(d); return (np.sin(2*np.pi*f*t)+0.3*np.sin(2*np.pi*2.76*f*t))*np.exp(-t*3)
q=0.2
prog=[(146.83,[293.66,369.99,440.0]),(196.0,[293.66,392.0,493.88]),(220.0,[277.18,329.63,440.0]),(146.83,[293.66,369.99,440.0])]
mel=[587.33,0,739.99,880.0,0,739.99,659.25,587.33, 493.88,0,587.33,659.25,0,587.33,493.88,440.0, 554.37,0,659.25,880.0,0,783.99,739.99,659.25, 587.33,0,440.0,587.33,0,0,0,0]
def groove(t0,t1,tempo=1.0,lead=True,g=1.0):
    t=t0; k=0
    while t<t1-0.05:
        root,ch=prog[(k//8)%4]
        if k%4==0: add(t,bass(root),0.45*g)
        if k%2==1: add(t,tick(),0.06*g)
        if k%4==2:
            for f in ch: add(t,pluck(f,0.25),0.05*g)
        f=mel[k%32]
        if f and lead: add(t,pluck(f,0.3),0.13*g)
        k+=1; t+=q*tempo
# s0 (0.0): bouncy groove, dial click, cold water, BRRR
groove(0.0,1.0)
add(0.45,tick(),0.3); add(0.9,zip_(300,900,0.15),0.08)
add(1.0,water(2.8,0.8),0.12)
add(1.25,brr(1.4),0.2)
groove(1.6,3.8,tempo=1.5,lead=False,g=0.8)
# s1 (3.8): crank to hot: rising whistle, sizzle, panic, then back to cold
add(3.8+0.3,zip_(400,1400,0.5),0.1)
add(3.8,water(3.4,1.6),0.12)
add(3.8+0.9,sizzle(1.9),0.08)
groove(3.8+0.9,3.8+2.8,tempo=0.6,g=0.8)
add(3.8+2.9,zip_(1400,300,0.35),0.1); add(3.8+3.3,brr(1.0),0.18)
for j,f in enumerate((246.94,233.08,220.0)): add(3.8+3.4+j*0.3,wah(f,0.5),0.1)
# s2 (8.2): knob pull, hose chaos: splashes + slide whistles
add(8.2+0.55,tick(),0.4); add(8.2+0.6,zip_(200,600,0.2),0.1)
add(8.2+0.9,water(2.2,1.0),0.16)
for j in range(5): add(8.2+1.0+j*0.38,zip_(1200 if j%2 else 500,500 if j%2 else 1200,0.3),0.07)
for tk in (1.3,1.75,2.2): add(8.2+tk,splash(),0.25)
groove(8.2+1.0,8.2+2.9,tempo=0.7,lead=False,g=0.7)
add(8.2+3.0,wah(196.0,1.0),0.1)
# s3 (12.6): dial to middle, 30-second countdown ticks, warm reveal
add(12.6+0.5,tick(),0.4)
add(12.6,water(3.9,1.2),0.08)
for j in range(15): add(12.6+0.8+j*0.1,tick(0.03),0.12)
for j,f in enumerate((587.33,739.99,880.0,1174.66)): add(12.6+2.3+j*0.07,ding(f,1.0),0.06)
groove(12.6+2.5,16.6)
# end card (16.6): resolve + bright ding
for f in (146.83,293.66,369.99,440.0,587.33): add(16.6,pluck(f,2.5),0.1)
add(16.9,ding(1174.66,1.5),0.1)
out*=np.minimum(1,(T-np.arange(n)/SR)/0.8); out=out/np.abs(out).max()*0.8
w=wave.open(os.path.join(OUT,'music_ep32.wav'),'wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((out*32767).astype(np.int16).tobytes()); w.close()

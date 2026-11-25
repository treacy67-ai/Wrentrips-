"""Soundtrack for ep30 (old-town walking tour: too many yellow umbrellas, Leo gets lost, Wren's pineapple flag). Original, synthesised with numpy. 19.8 s, 44.1 kHz."""
import numpy as np, wave, os
SR=44100; T=19.8; n=int(SR*T); out=np.zeros(n)
OUT=os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),"..","build","ep30")); os.makedirs(OUT,exist_ok=True)
rng=np.random.default_rng(30)
def add(t0,sig,g=1.0):
    i=int(t0*SR); j=min(n,i+len(sig))
    if 0<=i<n: out[i:j]+=sig[:j-i]*g
def env(d): return np.arange(int(SR*d))/SR
def mando(f,d=0.3,trem=False):                          # bright plucked mandolin-ish tone (optional tremolo)
    t=env(d); s=sum(a*np.sin(2*np.pi*f*k*t) for k,a in ((1,1),(2,.6),(3,.3),(4,.15)))
    e=np.exp(-t*(3 if trem else 9))*(1-np.exp(-t*600))
    if trem: e=e*(0.6+0.4*np.abs(np.sin(2*np.pi*12*t)))
    return s*e
def bass(f,d=0.3):
    t=env(d); return np.sin(2*np.pi*f*t)*np.exp(-t*6)*(1-np.exp(-t*300))
def tamb(d=0.08):
    t=env(d); return rng.normal(size=len(t))*np.exp(-t*45)*np.sin(2*np.pi*6000*t)
def pop():                                              # umbrella opening "fwump"
    t=env(0.18); f=500-1800*t; ph=2*np.pi*np.cumsum(f)/SR; return np.sin(ph)*np.exp(-t*20)+rng.normal(size=len(t))*np.exp(-t*60)*0.4
def whistle(f0=1400,f1=2100,d=0.35):
    t=env(d); f=f0+(f1-f0)*np.minimum(1,t/(d*0.4)); ph=2*np.pi*np.cumsum(f)/SR; return np.sin(ph)*np.sin(np.pi*t/d)
def bell(f=1046.5,d=1.2):
    t=env(d); return (np.sin(2*np.pi*f*t)+0.5*np.sin(2*np.pi*2.76*f*t)+0.25*np.sin(2*np.pi*5.4*f*t))*np.exp(-t*3)
def click():
    t=env(0.05); return rng.normal(size=len(t))*np.exp(-t*150)
def rain(d=1.4):
    x=rng.normal(size=int(SR*d)); t=env(d); drops=(rng.random(len(t))<0.002)*rng.normal(size=len(t))*6
    return (np.convolve(x,np.ones(6)/6,'same')*0.3+np.convolve(drops,np.exp(-np.arange(200)/30),'same'))*np.minimum(1,t*5)*np.minimum(1,(d-t)*5)
def tick(f=1200):
    t=env(0.04); return np.sin(2*np.pi*f*t)*np.exp(-t*90)
def step(): t=env(0.1); return np.sin(2*np.pi*90*t)*np.exp(-t*40)
def clap():
    t=env(0.08); return rng.normal(size=len(t))*np.exp(-t*60)
# tarantella-ish 6/8 groove in A minor, ~ 0 - 8.2 and 12.6 - 16.6 (s2 drops to a nervous tick)
q=0.16                                                    # one eighth note
prog=[(110.0,[440.0,523.25,659.25]),(146.83,[440.0,587.33,698.46]),(164.81,[415.3,493.88,659.25]),(110.0,[440.0,523.25,659.25])]
mel=[659.25,659.25,698.46,659.25,587.33,523.25, 587.33,587.33,659.25,587.33,523.25,493.88, 523.25,493.88,440.0,493.88,523.25,587.33, 659.25,0,659.25,880.0,0,0]
def groove(t0,t1,major=False):
    t=t0; k=0
    while t<t1-0.05:
        bar=(k//6)%4; root,ch=prog[bar]
        if major: root,ch=[(130.81,[523.25,659.25,783.99]),(174.61,[523.25,698.46,880.0]),(196.0,[493.88,587.33,783.99]),(130.81,[523.25,659.25,783.99])][bar]
        if k%3==0: add(t,bass(root),0.45)
        if k%3==1: add(t,tamb(),0.06)
        if k%3==2:
            for f in ch: add(t,mando(f,0.18),0.03)
        f=mel[k%24]*(1.1225 if major else 1.0)
        if f: add(t,mando(f,0.22),0.11)
        k+=1; t+=q
groove(0,8.2); groove(12.6+0.8,16.6,major=True)
# s0 (0.0): guide whistle, umbrellas popping up
add(0.25,whistle(),0.12)
for tp in (1.2,1.5,1.8,2.1,2.4,2.7): add(tp,pop(),0.22)
# s1 (3.8): tour switches, wedding bell + camera click, rain patter
add(3.8+1.45,whistle(900,1300,0.2),0.08); add(3.8+2.9,whistle(900,1300,0.2),0.08)
add(3.8+1.5,bell(1046.5),0.08); add(3.8+1.8,bell(1318.5),0.07); add(3.8+2.2,click(),0.4)
add(3.8+2.9,rain(1.5),0.25)
# s2 (8.2): lost - ticking speeds up and rises, umbrellas keep popping, low drone
tt=0.0; k=0
while tt<4.2:
    add(8.2+tt,tick(900+k*25),0.18); add(8.2+tt,bass(55,0.25),0.25 if k%2==0 else 0)
    tt+=max(0.12,0.42-k*0.02); k+=1
for tp in (0.2,0.5,0.8,1.1,1.4,1.7,2.0,2.3,2.6,2.8,3.0,3.2): add(8.2+tp,pop(),0.15)
d_=env(4.2); add(8.2,np.sin(2*np.pi*(73.4+6*d_/4.2)*d_)*np.minimum(1,d_*2)*np.minimum(1,(4.2-d_)*4),0.12)
add(8.2+1.6,whistle(1800,700,0.4),0.08)
# s3 (12.6): pineapple rises - rising sweep and fanfare, Leo runs, crowd claps
sw=env(0.7); add(12.6+0.15,np.sin(2*np.pi*np.cumsum(300+900*sw/0.7)/SR)*np.sin(np.pi*sw/0.7),0.08)
for j,f in enumerate((523.25,659.25,783.99,1046.5)): add(12.6+0.8+j*0.1,mando(f,0.9,trem=True),0.12)
for j in range(6): add(12.6+0.9+j*0.14,step(),0.3)
for j in range(14): add(12.6+2.2+j*0.1+rng.uniform(0,0.04),clap(),0.12)
# end card (16.6): bright tremolo resolve
for f in (130.81,261.63,523.25,659.25,783.99): add(16.6,mando(f,3.0,trem=True),0.07)
for j,f in enumerate((783.99,1046.5,1318.5)): add(16.8+j*0.15,mando(f,1.4),0.06)
out*=np.minimum(1,(T-np.arange(n)/SR)/0.8); out=out/np.abs(out).max()*0.8
w=wave.open(os.path.join(OUT,'music_ep30.wav'),'wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((out*32767).astype(np.int16).tobytes()); w.close()

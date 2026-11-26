"""Soundtrack for ep31 (plane cabin: window seat with no window, shade slams, marker window, Wren's compact-mirror sunset). Original, synthesised with numpy. 19.8 s, 44.1 kHz."""
import numpy as np, wave, os
SR=44100; T=19.8; n=int(SR*T); out=np.zeros(n)
OUT=os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),"..","build","ep31")); os.makedirs(OUT,exist_ok=True)
rng=np.random.default_rng(31)
def add(t0,sig,g=1.0):
    i=int(t0*SR); j=min(n,i+len(sig))
    if 0<=i<n: out[i:j]+=sig[:j-i]*g
def env(d): return np.arange(int(SR*d))/SR
def pluck(f,d=0.3):                                     # ukulele-ish pluck
    t=env(d); s=sum(a*np.sin(2*np.pi*f*k*t) for k,a in ((1,1),(2,.45),(3,.2),(5,.08)))
    return s*np.exp(-t*8)*(1-np.exp(-t*800))
def bass(f,d=0.32):
    t=env(d); return np.sin(2*np.pi*f*t)*np.exp(-t*5)*(1-np.exp(-t*300))
def shaker(d=0.06):
    t=env(d); return rng.normal(size=len(t))*np.exp(-t*60)
def chime(f1=880.0,f2=698.46):                          # seatbelt-sign "ding-dong"
    a=env(1.0); s1=(np.sin(2*np.pi*f1*a)+0.3*np.sin(2*np.pi*2*f1*a))*np.exp(-a*3)
    b=env(1.4); s2=(np.sin(2*np.pi*f2*b)+0.3*np.sin(2*np.pi*2*f2*b))*np.exp(-b*2.5)
    o=np.zeros(int(SR*1.9)); o[:len(s1)]+=s1; o[int(SR*0.45):int(SR*0.45)+len(s2)]+=s2; return o
def clack():
    t=env(0.12); return rng.normal(size=len(t))*np.exp(-t*90)+np.sin(2*np.pi*180*t)*np.exp(-t*40)
def zip_(f0,f1,d):
    t=env(d); f=f0+(f1-f0)*t/d; return np.sin(2*np.pi*np.cumsum(f)/SR)*np.sin(np.pi*t/d)
def squeak(d=0.25):                                     # marker squeak
    t=env(d); f=2200+500*np.sin(2*np.pi*7*t); return np.sign(np.sin(2*np.pi*np.cumsum(f)/SR))*np.sin(np.pi*t/d)*0.5
def wah(f,d=0.5):                                       # muted sad trombone note
    t=env(d); s=sum(a*np.sin(2*np.pi*f*k*t) for k,a in ((1,1),(2,.6),(3,.4),(4,.2)))
    return s*np.minimum(1,t*20)*np.exp(-t*1.5)*(0.7+0.3*np.sin(2*np.pi*5*t))
def sparkle(f,d=1.2):
    t=env(d); return (np.sin(2*np.pi*f*t)+0.4*np.sin(2*np.pi*3*f*t))*np.exp(-t*3.5)
# cabin hum under everything
hum=np.convolve(rng.normal(size=n),np.ones(60)/60,'same')*3; tt=np.arange(n)/SR
out+=hum*0.06+np.sin(2*np.pi*58*tt)*0.025
# bouncy ukulele groove in C major
q=0.2
prog=[(130.81,[261.63,329.63,392.0]),(174.61,[261.63,349.23,440.0]),(196.0,[246.94,293.66,392.0]),(130.81,[261.63,329.63,392.0])]
mel=[523.25,0,587.33,659.25,0,659.25,587.33,523.25, 440.0,0,523.25,587.33,0,523.25,440.0,392.0, 493.88,0,587.33,783.99,0,698.46,659.25,587.33, 523.25,0,392.0,523.25,0,0,0,0]
def groove(t0,t1,minor=False,tempo=1.0):
    t=t0; k=0
    while t<t1-0.05:
        root,ch=prog[(k//8)%4]
        if minor: root,ch=[(110.0,[220.0,261.63,329.63]),(87.31,[220.0,261.63,349.23]),(98.0,[196.0,246.94,293.66]),(82.41,[207.65,246.94,329.63])][(k//8)%4]
        if k%4==0: add(t,bass(root),0.45)
        if k%2==1: add(t,shaker(),0.05)
        if k%4==2:
            for f in ch: add(t,pluck(f,0.25),0.05)
        f=mel[k%32]*(0.84 if minor else 1.0)
        if f and not minor: add(t,pluck(f,0.3),0.13)
        if f and minor and k%2==0: add(t,pluck(f,0.4),0.08)
        k+=1; t+=q*tempo
# s0 (0.0): chime, happy groove, then a record-scratch stop when Leo sees the wall
add(0.05,chime(),0.18)
groove(0.3,1.25)
add(1.25,zip_(900,200,0.25),0.12); add(1.3,clack(),0.2)
for j,f in enumerate((392.0,329.63,261.63)): add(1.7+j*0.25,pluck(f,0.5),0.12)
groove(2.4,3.8,minor=True)
# s1 (3.8): tense rising tone while Leo stretches, shade CLACK, sad trombone
add(3.8,zip_(200,700,1.8)*np.linspace(0.3,1,int(SR*1.8)),0.06)
for j in range(8): add(3.8+0.2+j*0.2,pluck(392.0+j*30,0.15),0.07)
add(3.8+2.1,zip_(1400,500,0.3),0.1); add(3.8+2.42,clack(),0.45)
for j,f in enumerate((233.08,220.0,207.65,196.0)): add(3.8+2.9+j*0.32,wah(f,0.6 if j<3 else 1.0),0.12)
# s2 (8.2): slow minor ukulele + marker squeaks
groove(8.2,12.5,minor=True,tempo=1.4)
for tp in (0.4,0.75,1.1,1.5,1.8,2.1): add(8.2+tp,squeak(0.22),0.05)
add(8.2+2.8,wah(196.0,0.9),0.08)
# s3 (12.6): compact click, shimmering sunset reveal, groove returns brighter
add(12.6+0.3,clack()[:2000],0.3)
for j,f in enumerate((523.25,659.25,783.99,1046.5,1318.5,1567.98)): add(12.6+1.0+j*0.08,sparkle(f),0.07)
groove(12.6+1.4,16.6)
# end card (16.6): resolve chord + chime
for f in (130.81,261.63,329.63,392.0,523.25): add(16.6,pluck(f,2.5)*1.0,0.1)
add(16.9,chime(1046.5,783.99),0.1)
out*=np.minimum(1,(T-np.arange(n)/SR)/0.8); out=out/np.abs(out).max()*0.8
w=wave.open(os.path.join(OUT,'music_ep31.wav'),'wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((out*32767).astype(np.int16).tobytes()); w.close()

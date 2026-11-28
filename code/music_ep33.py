"""Soundtrack for ep33 (theme park ride photos). Original fairground waltz synthesised with numpy. 19.8 s, 44.1 kHz."""
import numpy as np, wave, os
SR=44100; T=19.8; n=int(SR*T); out=np.zeros(n)
OUT=os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),"..","build","ep33")); os.makedirs(OUT,exist_ok=True)
rng=np.random.default_rng(33)
def add(t0,sig,g=1.0):
    i=int(t0*SR); j=min(n,i+len(sig))
    if 0<=i<n: out[i:j]+=sig[:j-i]*g
def env(d): return np.arange(int(SR*d))/SR
def organ(f,d=0.35):                                    # calliope-ish pipe: odd harmonics + vibrato
    t=env(d); v=1+0.006*np.sin(2*np.pi*6*t)
    s=sum(a*np.sin(2*np.pi*f*k*v*t) for k,a in ((1,1),(2,.35),(3,.45),(5,.15)))
    return s*np.minimum(1,t*60)*np.minimum(1,(d-t)*30)
def bass(f,d=0.3):
    t=env(d); return np.sin(2*np.pi*f*t)*np.exp(-t*6)*(1-np.exp(-t*300))
def tick(d=0.04,f=2400):
    t=env(d); return np.sin(2*np.pi*f*t)*np.exp(-t*120)
def clack(d=0.06):
    t=env(d); return rng.normal(size=len(t))*np.exp(-t*90)
def whoosh(d,f0=0.2,f1=1.0):                            # rising/falling filtered noise
    t=env(d); w=rng.normal(size=len(t)); k=8; w=np.convolve(w,np.ones(k)/k,'same')
    return w*np.sin(np.pi*t/d)**2*(f0+(f1-f0)*t/d)
def shutter():
    a=clack(0.05); b=np.zeros(int(SR*0.09)); c=clack(0.07)*0.8; return np.concatenate([a,b,c])
def wah(f,d=0.5):
    t=env(d); s=sum(a*np.sin(2*np.pi*f*k*t) for k,a in ((1,1),(2,.6),(3,.4),(4,.2)))
    return s*np.minimum(1,t*20)*np.exp(-t*1.5)*(0.7+0.3*np.sin(2*np.pi*5*t))
def pop(f=900):
    t=env(0.12); return np.sin(2*np.pi*(f+3000*np.exp(-t*40))*t)*np.exp(-t*30)
def ding(f=1318.5,d=1.2):
    t=env(d); return (np.sin(2*np.pi*f*t)+0.3*np.sin(2*np.pi*2.76*f*t))*np.exp(-t*3)
# 3/4 fairground waltz in F major
beat=0.36
prog=[(87.31,[349.23,440.0,523.25]),(130.81,[329.63,392.0,523.25]),(130.81,[349.23,466.16,523.25]),(87.31,[349.23,440.0,523.25])]
mel=[698.46,0,880.0, 1046.5,0,880.0, 783.99,659.25,523.25, 587.33,0,0,
     659.25,0,783.99, 932.33,0,783.99, 698.46,587.33,523.25, 698.46,0,0]
def waltz(t0,t1,tempo=1.0,lead=True,g=1.0):
    t=t0; k=0
    while t<t1-0.05:
        root,ch=prog[(k//3)%4]
        if k%3==0: add(t,bass(root),0.5*g)
        else:
            for f in ch: add(t,organ(f,0.18),0.03*g)
        f=mel[k%24]
        if f and lead: add(t,organ(f,0.3*tempo),0.09*g)
        k+=1; t+=beat*tempo
# s0 (0.0): chain-lift clacks, the drop, camera flash at 2.25
for j in range(5): add(j*0.12,clack(),0.18)
waltz(0.0,0.6,g=0.8)
add(0.6,whoosh(1.7,0.3,1.0),0.35)
add(0.7,np.concatenate([organ(f,0.12) for f in (1046.5,880.0,698.46,523.25,440.0,349.23)]),0.06)
add(2.25,shutter(),0.6); add(2.3,ding(1567.98,0.8),0.07)
waltz(2.6,3.8,g=0.7)
# s1 (3.8): photo #1 revealed: sad trombone, then waltz
for j,f in enumerate((233.08,220.0,207.65,196.0)): add(3.8+0.4+j*0.28,wah(f,0.5 if j<3 else 1.0),0.11)
waltz(3.8+1.8,8.2,g=0.8)
# s2 (8.2): photos 2-4 pop in, faster waltz
waltz(8.2,12.6,tempo=0.8,g=0.75)
for tk in (0.8,1.7,2.6): add(8.2+tk,shutter(),0.45); add(8.2+tk+0.05,pop(),0.12)
add(8.2+1.1,np.concatenate([tick(0.05,f) for f in (2000,2600,2000,2600)]),0.05)
# s3 (12.6): "say cheese", one click at 2.0, sparkle, bright waltz
waltz(12.6,12.6+1.8,g=0.6,lead=False)
add(12.6+2.0,shutter(),0.6)
for j,f in enumerate((698.46,880.0,1046.5,1396.91)): add(12.6+2.3+j*0.07,ding(f,1.0),0.06)
waltz(12.6+2.4,16.6)
# end card (16.6): resolve + bright ding
for f in (87.31,174.61,349.23,440.0,523.25): add(16.6,organ(f,2.4)*np.exp(-env(2.4)*1.2),0.08)
add(16.9,ding(1396.91,1.5),0.1)
out*=np.minimum(1,(T-np.arange(n)/SR)/0.8); out=out/np.abs(out).max()*0.8
w=wave.open(os.path.join(OUT,'music_ep33.wav'),'wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((out*32767).astype(np.int16).tobytes()); w.close()

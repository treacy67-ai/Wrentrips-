import numpy as np, wave
SR=44100; T=19.8; n=int(SR*T); out=np.zeros(n)
def add(t0,sig,g=1.0):
    i=int(t0*SR); j=min(n,i+len(sig))
    if 0<=i<n: out[i:j]+=sig[:j-i]*g
def pluck(f,d=0.5,dec=7):
    t=np.arange(int(SR*d))/SR; s=sum(a*np.sin(2*np.pi*f*k*t) for k,a in ((1,1),(2,.5),(3,.25),(5,.08)))
    return s*np.exp(-t*dec)*(1-np.exp(-t*500))
def bass(f,d=0.35):
    t=np.arange(int(SR*d))/SR; return np.sin(2*np.pi*f*t)*np.exp(-t*6)*(1-np.exp(-t*300))
rng=np.random.default_rng(3)
def hat(d=0.05):
    m=int(SR*d); return rng.normal(size=m)*np.exp(-np.arange(m)/SR*90)
# sneaky walking bass + pizzicato, 150bpm swing
b=0.4
walk=[130.81,155.56,174.61,185.0,196.0,185.0,174.61,155.56]
t=0;i=0
while t<16.4:
    add(t,bass(walk[i%8]),0.5); add(t+b*0.5,hat(),0.12); add(t+b*0.83,hat(),0.07)
    i+=1; t+=b
mel=[523.25,622.25,698.46,739.99,783.99,0,698.46,622.25, 523.25,0,466.16,523.25,0,0,392.0,0]
t=0.0;i=0
while t<16.2:
    f=mel[i%16]
    if f: add(t+(0.13 if i%2 else 0),pluck(f),0.22)
    i+=1; t+=b/1.0
# s0 rising stack blips
for k in range(14): add(0.4+k*2.5/14,pluck(600+k*60,0.15,20),0.18)
# s1 croissant plops
for k in range(9): add(3.8+0.5+(k+1)*2.6/9,bass(220-k*8,0.2),0.5)
# s2 freeze: thud at fall, ding at return
add(8.2+1.75,bass(90,0.4),0.9); add(8.2+3.5,pluck(1318,0.8,4),0.3)
# s3 reveal sparkle
for k,f in enumerate((784,988,1175,1568)): add(12.6+1.2+k*0.12,pluck(f,0.8,4),0.2)
# end chord
for f in (261.63,329.63,392.0,523.25,659.25): add(16.6,pluck(f,2.6,1.8),0.2)
add(17.1,pluck(1046.5,2,2.5),0.15)
out*=np.minimum(1,(T-np.arange(n)/SR)/0.8); out=out/np.abs(out).max()*0.8
w=wave.open('/home/claude/wren/ep18/music_buffet.wav','wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((out*32767).astype(np.int16).tobytes()); w.close()

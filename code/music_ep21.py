"""Soundtrack for ep21 (tulip-field photo). Original, synthesised with numpy. 19.8 s, 44.1 kHz."""
import numpy as np, wave, os
SR=44100; T=19.8; n=int(SR*T); out=np.zeros(n)
OUT=os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),"..","build","ep21")); os.makedirs(OUT,exist_ok=True)
def add(t0,sig,g=1.0):
    i=int(t0*SR); j=min(n,i+len(sig))
    if 0<=i<n: out[i:j]+=sig[:j-i]*g
def pluck(f,d=0.5,dec=8):
    t=np.arange(int(SR*d))/SR; s=np.sin(2*np.pi*f*t)+0.3*np.sin(2*np.pi*f*3*t)*np.exp(-t*25)+0.2*np.sin(2*np.pi*f*2*t)
    return s*np.exp(-t*dec)*(1-np.exp(-t*600))
def reed(f,d=0.4):                                   # little accordion-ish stab
    t=np.arange(int(SR*d))/SR; s=sum(np.sin(2*np.pi*f*k*t*(1+0.002*k))/k for k in (1,2,3,4,5))
    return s*np.minimum(1,t*60)*np.minimum(1,(d-t)*25)*(1+0.08*np.sin(2*np.pi*6*t))
def bass(f,d=0.3):
    t=np.arange(int(SR*d))/SR; return (np.sin(2*np.pi*f*t)+0.3*np.sin(4*np.pi*f*t))*np.exp(-t*7)*(1-np.exp(-t*300))
rng=np.random.default_rng(21)
def click(d=0.05,dec=90):                            # camera shutter
    m=int(SR*d); return rng.normal(size=m)*np.exp(-np.arange(m)/SR*dec)
def shutter():
    s=np.zeros(int(SR*0.12)); a=click(0.03,160); b=click(0.05,110); s[:len(a)]+=a; i=int(SR*0.055); s[i:i+len(b)]+=b*0.8; return s
def slide(f0,f1,d=0.7):
    t=np.arange(int(SR*d))/SR; f=f0+(f1-f0)*(t/d); ph=2*np.pi*np.cumsum(f)/SR
    return (np.sin(ph)+0.4*np.sin(2*ph)+0.2*np.sin(3*ph))*np.minimum(1,t*30)*np.exp(-t*1.5)
def beep(f=880,d=0.12):
    t=np.arange(int(SR*d))/SR; return np.sin(2*np.pi*f*t)*np.minimum(1,t*200)*np.minimum(1,(d-t)*200)
def swish(d=0.22):
    m=int(SR*d); x=rng.normal(size=m); x=np.convolve(x,np.ones(24)/24,'same'); return x*np.sin(np.pi*np.arange(m)/m)**2*4
# oom-pah waltz, 168 bpm (3/4), G major
b=60/168
prog=[(98.0,[392.0,493.88,587.33]),(73.42,[369.99,440.0,587.33]),(82.41,[392.0,493.88,659.25]),(65.41,[392.0,523.25,659.25]),
      (98.0,[392.0,493.88,587.33]),(82.41,[392.0,493.88,659.25]),(73.42,[369.99,440.0,587.33]),(73.42,[369.99,523.25,587.33])]
t=0;bar=0
while t<16.4:
    root,ch=prog[bar%8]
    add(t,bass(root,0.45),0.6)
    for k in (1,2):
        for f in ch: add(t+k*b,reed(f,0.16),0.035)
    bar+=1; t+=3*b
mel=[783.99,0,880.0, 739.99,0,587.33, 659.25,783.99,987.77, 783.99,0,0, 987.77,0,880.0, 783.99,659.25,0, 739.99,880.0,739.99, 587.33,0,0]
t=0;i=0
while t<16.2:
    f=mel[i%24]
    if f: add(t,pluck(f,0.5,7),0.22)
    i+=1; t+=b
# s0 (0.0): shutter clicks, accelerating, in sync with the flash
tt=0.5
while tt<3.3:
    add(tt,shutter(),0.22); tt+=1/(2.5+2.2*tt)
# s1 (3.8): card pops out, sad slide for the thumb, blip on Wren's reply
add(3.8+0.35,pluck(1174.66,0.3,12),0.3); add(3.8+0.85,slide(440,220,0.7),0.2); add(3.8+3.0,pluck(1567.98,0.5,6),0.2)
# s2 (8.2): pop, gasp-up slide, then REC beeps for the video
add(8.2+0.3,pluck(1174.66,0.3,12),0.3); add(8.2+0.8,slide(300,620,0.35),0.16)
add(8.2+2.4,beep(880),0.2); add(8.2+2.62,beep(880),0.2); add(8.2+2.84,beep(1318.5,0.2),0.2)
# s3 (12.6): brush swishes during the time-lapse, reveal sparkle at 1.9
for k in range(7): add(12.6+0.4+k*0.21,swish(),0.16)
for k,f in enumerate((783.99,987.77,1174.66,1567.98,1975.53)): add(12.6+1.9+k*0.09,pluck(f,0.9,4),0.2)
add(12.6+2.9,slide(392,262,0.5),0.14)
# end card (16.6)
for f in (98.0,196.0,392.0,493.88,587.33,783.99): add(16.6,pluck(f,2.8,1.6),0.2)
add(17.1,pluck(1567.98,2,2.5),0.14); add(17.7,shutter(),0.18)
out*=np.minimum(1,(T-np.arange(n)/SR)/0.8); out=out/np.abs(out).max()*0.8
w=wave.open(os.path.join(OUT,'music_ep21.wav'),'wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((out*32767).astype(np.int16).tobytes()); w.close()
